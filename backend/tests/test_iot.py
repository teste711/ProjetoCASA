"""Testes do fluxo do IoT: app → API → Firestore (base64) → sinal no Realtime Database → aparelho → concluído → limpeza."""
import base64
import hashlib
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.deps import Limitador, get_auth, get_db, get_rtdb, get_rtdb_opcional
from app.main import app
from tests.fakes import FakeAuth, FakeFirestore, FakeRTDB

MAC = "24:62:AB:E4:C1:0C"
OUTRO_MAC = "AA:BB:CC:DD:EE:01"


def H(uid="u1"):
    return {"Authorization": f"Bearer tok:{uid}:{uid}@x.com:1"}


def png(tam=(800, 400)) -> bytes:
    b = io.BytesIO()
    Image.new("RGB", tam, (30, 120, 200)).save(b, "PNG")
    return b.getvalue()


def wav(n_bytes=2000) -> bytes:
    return b"RIFF" + (n_bytes).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * n_bytes


@pytest.fixture()
def ctx():
    db, fb, rtdb = FakeFirestore(), FakeAuth(), FakeRTDB()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_auth] = lambda: fb
    app.dependency_overrides[get_rtdb] = lambda: rtdb
    app.dependency_overrides[get_rtdb_opcional] = lambda: rtdb
    Limitador._hits.clear()
    yield TestClient(app, raise_server_exceptions=False), db, rtdb
    app.dependency_overrides.clear()


@pytest.fixture()
def cenario(ctx):
    """u1 com uma categoria, um botão e um dispositivo pareado."""
    c, db, rtdb = ctx
    cid = c.post("/categorias", json={"nome": "Casa"}, headers=H()).json()["id"]
    botao = c.post(f"/categorias/{cid}/botoes", json={"rotulo": "Água"}, headers=H()).json()
    token = c.post("/dispositivos", json={"mac": MAC}, headers=H()).json()["device_token"]
    return c, db, rtdb, botao["id"], {"X-Device-Token": token}


def enviar(c, arquivo=None, nome="foto.png", mime="image/png", mac=MAC, botao_id=None, uid="u1"):
    data = {"dispositivo": mac, **({"botao_id": botao_id} if botao_id else {})}
    return c.post("/iot/midias", files={"arquivo": (nome, arquivo if arquivo is not None else png(), mime)}, data=data, headers=H(uid))


def doc_fila(db, mid, mac=MAC):
    return db.data.get(("dispositivos", mac, "fila", mid))


# ───────────────────────── caminho feliz ─────────────────────────
def test_fluxo_completo_envio_sinal_busca_conclusao_e_limpeza(cenario):
    c, db, rtdb, botao, dh = cenario
    r = enviar(c, botao_id=botao)
    assert r.status_code == 201, r.text
    env = r.json()
    mid = env["id"]
    assert (env["tipo"], env["estado"], env["largura"], env["altura"]) == ("imagem", "pendente", 240, 240)

    # 3) Firestore guarda o BASE64 de um JPEG 240x240 (a imagem original foi convertida)
    doc = doc_fila(db, mid)
    jpeg = base64.b64decode(doc["base64"])
    img = Image.open(io.BytesIO(jpeg))
    assert img.format == "JPEG" and img.size == (240, 240) and not img.info.get("progressive")
    assert doc["sha256"] == hashlib.sha256(jpeg).hexdigest() == env["sha256"] and doc["owner_uid"] == "u1"
    assert doc["rotulo"] == "Água" and doc["categoria_ordem"] == 0 and doc["botao_ordem"] == 0

    # 4) o SINAL no Realtime Database é pequeno e não carrega o conteúdo
    sinal = rtdb.get(f"dispositivos/{MAC}/sync/{mid}")
    assert sinal["estado"] == "pendente" and sinal["botao_id"] == botao and "base64" not in str(sinal)

    # 5) o aparelho vê o item pendente
    assert [i["id"] for i in c.get("/device/iot/pendentes", headers=dh).json()] == [mid]
    # 6) busca o conteúdo
    baixado = c.get(f"/device/iot/midias/{mid}", headers=dh).json()
    assert baixado["base64"] == doc["base64"] and baixado["mime"] == "image/jpeg" and baixado["botao_ordem"] == 0
    assert rtdb.get(f"dispositivos/{MAC}/sync/{mid}")["estado"] == "baixando"
    # 7) confirma com o hash do que decodificou
    ok = c.post(f"/device/iot/midias/{mid}/concluido", json={"sha256": hashlib.sha256(base64.b64decode(baixado["base64"])).hexdigest()}, headers=dh)
    assert ok.status_code == 200 and ok.json()["estado"] == "concluido"
    # 8) sinal "concluído" e Firestore LIMPO
    assert rtdb.get(f"dispositivos/{MAC}/sync/{mid}")["estado"] == "concluido"
    assert doc_fila(db, mid) is None
    assert c.get(f"/device/iot/midias/{mid}", headers=dh).status_code == 404
    assert c.get("/device/iot/pendentes", headers=dh).json() == []
    # confirmação repetida (resposta se perdeu) continua OK
    assert c.post(f"/device/iot/midias/{mid}/concluido", json={}, headers=dh).status_code == 200
    # o app acompanha o estado
    assert c.get(f"/iot/midias/{mid}", params={"dispositivo": MAC}, headers=H()).json()["estado"] == "concluido"


def test_audio_wav_e_limite_de_tamanho(cenario):
    c, db, rtdb, _, dh = cenario
    r = enviar(c, wav(2000), "agua.wav", "audio/wav")
    assert r.status_code == 201 and r.json()["tipo"] == "audio"
    assert base64.b64decode(doc_fila(db, r.json()["id"])["base64"]).startswith(b"RIFF")
    assert enviar(c, wav(600 * 1024), "grande.wav", "audio/wav").status_code == 413      # > 500 KB


# ───────────────────────── falhas do aparelho ─────────────────────────
def test_hash_diferente_mantem_o_conteudo(cenario):
    c, db, rtdb, _, dh = cenario
    mid = enviar(c).json()["id"]
    r = c.post(f"/device/iot/midias/{mid}/concluido", json={"sha256": "0" * 64}, headers=dh)
    assert r.status_code == 422 and r.json()["codigo"] == "hash_diferente"
    assert doc_fila(db, mid) is not None and rtdb.get(f"dispositivos/{MAC}/sync/{mid}")["estado"] == "pendente"


def test_erro_do_aparelho_conta_tentativas_e_para_no_limite(cenario, monkeypatch):
    c, db, rtdb, _, dh = cenario
    monkeypatch.setattr("app.config.settings.iot_max_tentativas", 2)
    mid = enviar(c).json()["id"]
    r1 = c.post(f"/device/iot/midias/{mid}/erro", json={"mensagem": "SD cheio"}, headers=dh).json()
    assert (r1["tentativas"], r1["pode_tentar_novamente"]) == (1, True)
    assert [i["id"] for i in c.get("/device/iot/pendentes", headers=dh).json()] == [mid]      # volta a aparecer
    assert c.get(f"/device/iot/midias/{mid}", headers=dh).status_code == 200                  # e pode ser rebuscado
    r2 = c.post(f"/device/iot/midias/{mid}/erro", json={"mensagem": "SD cheio"}, headers=dh).json()
    assert (r2["tentativas"], r2["pode_tentar_novamente"]) == (2, False)
    assert c.get("/device/iot/pendentes", headers=dh).json() == []                            # desiste de oferecer
    assert doc_fila(db, mid)["erro"] == "SD cheio"                                            # mas o app ainda vê o motivo


def test_falha_do_rtdb_ao_concluir_nao_apaga_o_conteudo(cenario):
    c, db, rtdb, _, dh = cenario
    mid = enviar(c).json()["id"]
    rtdb.falhar_em = "update"
    assert c.post(f"/device/iot/midias/{mid}/concluido", json={}, headers=dh).status_code == 500
    rtdb.falhar_em = None
    assert doc_fila(db, mid) is not None                                                     # nada foi perdido
    assert c.post(f"/device/iot/midias/{mid}/concluido", json={}, headers=dh).status_code == 200   # nova tentativa funciona
    assert doc_fila(db, mid) is None


# ───────────────────────── falhas do envio ─────────────────────────
def test_falha_do_rtdb_no_envio_desfaz_o_firestore(cenario):
    c, db, rtdb, _, _ = cenario
    rtdb.falhar_em = "set"
    r = enviar(c)
    assert r.status_code == 502 and r.json()["codigo"] == "rtdb_indisponivel"
    assert [k for k in db.data if k[:3] == ("dispositivos", MAC, "fila")] == []              # nenhum documento órfão


def test_rejeita_arquivos_invalidos(cenario):
    c, *_ = cenario
    assert enviar(c, b"MZ nao sou imagem", "virus.png").status_code == 415                    # nome/tipo mentem
    assert enviar(c, b"").status_code == 422
    b = io.BytesIO()
    Image.new("1", (8000, 8000)).save(b, "PNG")                                              # 64 milhões de pixels
    assert enviar(c, b.getvalue()).status_code == 413
    assert enviar(c, b"\x00" * (6 * 1024 * 1024)).status_code == 413                         # > 5 MB
    assert enviar(c, mac="zz").status_code == 422
    assert enviar(c, botao_id="nao-existe").json()["codigo"] == "botao_invalido"


def test_limite_de_base64_do_firestore(cenario, monkeypatch):
    c, *_ = cenario
    monkeypatch.setattr("app.config.settings.iot_max_base64_bytes", 100)
    assert enviar(c).status_code == 413


def test_fila_cheia(cenario, monkeypatch):
    c, *_ = cenario
    monkeypatch.setattr("app.config.settings.iot_max_pendentes", 3)
    assert [enviar(c).status_code for _ in range(3)] == [201, 201, 201]
    r = enviar(c)
    assert r.status_code == 409 and r.json()["codigo"] == "fila_cheia"


def test_cancelar_remove_conteudo_e_sinal(cenario):
    c, db, rtdb, _, dh = cenario
    mid = enviar(c).json()["id"]
    assert c.delete(f"/iot/midias/{mid}", params={"dispositivo": MAC}, headers=H()).status_code == 204
    assert doc_fila(db, mid) is None and rtdb.get(f"dispositivos/{MAC}/sync/{mid}") is None
    assert c.get(f"/device/iot/midias/{mid}", headers=dh).status_code == 404


# ───────────────────────── segurança ─────────────────────────
def test_isolamento_entre_contas_e_dispositivos(cenario):
    c, db, rtdb, _, dh = cenario
    mid = enviar(c).json()["id"]
    # outra conta não envia, não lista, não vê, não cancela
    assert enviar(c, uid="u2").status_code == 404
    assert c.get("/iot/midias", params={"dispositivo": MAC}, headers=H("u2")).status_code == 404
    assert c.get(f"/iot/midias/{mid}", params={"dispositivo": MAC}, headers=H("u2")).status_code == 404
    assert c.delete(f"/iot/midias/{mid}", params={"dispositivo": MAC}, headers=H("u2")).status_code == 404
    # o aparelho de outra conta não alcança o item do primeiro
    tok2 = c.post("/dispositivos", json={"mac": OUTRO_MAC}, headers=H("u2")).json()["device_token"]
    dh2 = {"X-Device-Token": tok2}
    assert c.get(f"/device/iot/midias/{mid}", headers=dh2).status_code == 404
    assert c.post(f"/device/iot/midias/{mid}/concluido", json={}, headers=dh2).status_code == 404
    assert c.get("/device/iot/pendentes", headers=dh2).json() == []
    assert doc_fila(db, mid) is not None
    # sem credenciais
    assert c.get("/device/iot/pendentes").status_code == 401
    assert c.get(f"/device/iot/midias/{mid}", headers={"X-Device-Token": "casa_errado"}).status_code == 401
    assert c.post("/iot/midias", files={"arquivo": ("a.png", png(), "image/png")}, data={"dispositivo": MAC}).status_code == 401


def test_sem_database_url_as_rotas_do_iot_respondem_503(cenario, monkeypatch):
    c, *_ = cenario
    app.dependency_overrides.pop(get_rtdb)                        # usa o get_rtdb de verdade
    monkeypatch.setattr("app.config.settings.firebase_database_url", "")
    r = enviar(c)
    assert r.status_code == 503 and r.json()["codigo"] == "rtdb_nao_configurado"


# ───────────────────────── limpeza de itens esquecidos ─────────────────────────
def test_limpeza_de_itens_vencidos_no_proximo_envio(cenario):
    c, db, rtdb, _, _ = cenario
    agora = int(__import__("time").time() * 1000)
    velho_pend = agora - 8 * 24 * 3600 * 1000       # 8 dias
    velho_conc = agora - 25 * 3600 * 1000           # 25 h
    recente_conc = agora - 1 * 3600 * 1000          # 1 h
    for mid, no in (("pendvelho", {"estado": "pendente", "criado_em": velho_pend}),
                    ("concvelho", {"estado": "concluido", "criado_em": velho_conc, "concluido_em": velho_conc}),
                    ("concnovo", {"estado": "concluido", "criado_em": recente_conc, "concluido_em": recente_conc})):
        rtdb.set(f"dispositivos/{MAC}/sync/{mid}", no)
        db.data[("dispositivos", MAC, "fila", mid)] = {"base64": "x", "estado": "pendente"}
    assert enviar(c).status_code == 201
    assert rtdb.get(f"dispositivos/{MAC}/sync/pendvelho") is None and doc_fila(db, "pendvelho") is None
    assert rtdb.get(f"dispositivos/{MAC}/sync/concvelho") is None and doc_fila(db, "concvelho") is None
    assert rtdb.get(f"dispositivos/{MAC}/sync/concnovo") is not None                        # ainda dentro do prazo


# ───────────────────────── limpeza ao remover o dispositivo / excluir a conta ─────────────────────────
def test_remover_dispositivo_apaga_a_fila_e_os_sinais(cenario):
    """Regressão: no Firestore apagar o documento NÃO apaga a subcoleção; o base64 ficava órfão."""
    c, db, rtdb, botao, dh = cenario
    mid = enviar(c, botao_id=botao).json()["id"]
    assert doc_fila(db, mid) and rtdb.get(f"dispositivos/{MAC}/sync/{mid}")
    assert c.delete(f"/dispositivos/{MAC}", headers=H()).status_code == 204
    assert doc_fila(db, mid) is None
    assert not [k for k in db.data if k[0] == "dispositivos"]            # nenhum documento do aparelho restou
    assert rtdb.get(f"dispositivos/{MAC}") is None                         # nenhum sinal restou
    assert c.get("/device/iot/pendentes", headers=dh).status_code == 401  # o token parou de valer


def test_excluir_conta_nao_deixa_base64_nem_sinais(cenario):
    c, db, rtdb, botao, dh = cenario
    enviar(c, botao_id=botao)
    enviar(c, botao_id=botao)
    assert c.delete("/me", headers=H()).status_code == 204
    assert db.data == {}                                                   # nada restou no Firestore (nem a fila)
    assert rtdb.dados == {} or rtdb.get(f"dispositivos/{MAC}") is None     # nem no Realtime Database


def test_remover_dispositivo_funciona_sem_realtime_database_configurado(ctx, monkeypatch):
    """Limpar não pode exigir que o recurso opcional esteja configurado."""
    c, db, _ = ctx
    from app.config import settings
    app.dependency_overrides.pop(get_rtdb_opcional, None)                 # usa a real: sem URL → None
    monkeypatch.setattr(settings, "firebase_database_url", "")
    c.post("/dispositivos", json={"mac": OUTRO_MAC}, headers=H())
    assert c.delete(f"/dispositivos/{OUTRO_MAC}", headers=H()).status_code == 204

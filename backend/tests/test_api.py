import pytest
from fastapi.testclient import TestClient

from app.deps import get_auth, get_db
from app.main import app
from tests.fakes import FakeAuth, FakeFirestore


@pytest.fixture(autouse=True)
def _isolar(tmp_path, monkeypatch):
    """Cada teste usa uma pasta de uploads própria e zera o limitador de requisições."""
    from app import storage
    from app.deps import Limitador
    monkeypatch.setattr(storage, "RAIZ", tmp_path / "uploads")
    Limitador._hits.clear()


@pytest.fixture()
def ctx():
    db, fb = FakeFirestore(), FakeAuth()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_auth] = lambda: fb
    yield TestClient(app), db, fb
    app.dependency_overrides.clear()


def H(uid="u1", verificado=1):
    return {"Authorization": f"Bearer tok:{uid}:{uid}@exemplo.com:{verificado}"}


def test_auth_exige_token_valido_e_email_verificado(ctx):
    c, *_ = ctx
    assert c.get("/me").status_code == 401
    assert c.get("/me", headers={"Authorization": "Bearer lixo"}).json()["codigo"] == "token_invalido"
    r = c.get("/me", headers=H(verificado=0))
    assert r.status_code == 403 and r.json()["codigo"] == "email_nao_verificado"
    assert c.get("/me", headers=H()).status_code == 200


def test_perfil_criado_no_primeiro_acesso_e_preferencias(ctx):
    c, db, _ = ctx
    p = c.get("/me", headers=H()).json()
    assert p["uid"] == "u1" and p["email"] == "u1@exemplo.com" and p["tamanho_fonte"] == 10
    r = c.patch("/me", json={"nome": "Zeus Alves", "modo_escuro": True, "tamanho_fonte": 14}, headers=H()).json()
    assert r["nome"] == "Zeus Alves" and r["modo_escuro"] is True and r["tamanho_fonte"] == 14
    assert c.patch("/me", json={"tamanho_fonte": 99}, headers=H()).status_code == 422


def test_categorias_e_botoes_com_limites_e_isolamento(ctx):
    c, *_ = ctx
    ids = [c.post("/categorias", json={"nome": n}, headers=H()).json()["id"] for n in ("Escola", "Casa", "Objetos")]
    assert c.post("/categorias", json={"nome": "Quarta"}, headers=H()).json()["codigo"] == "limite_categorias"
    for i in range(5):
        assert c.post(f"/categorias/{ids[0]}/botoes", json={"rotulo": f"B{i}", "audio_nome": "a.mp3"}, headers=H()).status_code == 201
    assert c.post(f"/categorias/{ids[0]}/botoes", json={"rotulo": "x"}, headers=H()).json()["codigo"] == "limite_botoes"
    cats = c.get("/categorias?busca=esc", headers=H()).json()
    assert len(cats) == 1 and len(cats[0]["botoes"]) == 5 and cats[0]["slug"] == "escola"
    bid = cats[0]["botoes"][0]["id"]
    assert c.patch(f"/categorias/{ids[0]}/botoes/{bid}", json={"rotulo": "Novo"}, headers=H()).json()["rotulo"] == "Novo"
    assert c.delete(f"/categorias/{ids[0]}/botoes/{bid}", headers=H()).status_code == 204
    # outro usuário não enxerga nada
    assert c.get("/categorias", headers=H("u2")).json() == []
    assert c.delete(f"/categorias/{ids[0]}", headers=H("u2")).status_code == 404


def test_dispositivo_esp32_config_telemetria_e_historico(ctx):
    c, *_ = ctx
    cid = c.post("/categorias", json={"nome": "Casa"}, headers=H()).json()["id"]
    agua = c.post(f"/categorias/{cid}/botoes", json={"rotulo": "Água"}, headers=H()).json()["id"]
    tv = c.post(f"/categorias/{cid}/botoes", json={"rotulo": "TV"}, headers=H()).json()["id"]

    assert c.post("/dispositivos", json={"mac": "zz"}, headers=H()).status_code == 422
    d = c.post("/dispositivos", json={"mac": "24-62-ab-e4-c1-0c"}, headers=H()).json()
    assert d["mac"] == "24:62:AB:E4:C1:0C" and d["device_token"].startswith("casa_")
    assert c.post("/dispositivos", json={"mac": "24:62:AB:E4:C1:0C"}, headers=H("u2")).status_code == 409
    assert "device_token" not in c.get("/dispositivos", headers=H()).json()[0]
    assert c.get("/dispositivos", headers=H("u2")).json() == []

    dh = {"X-Device-Token": d["device_token"]}
    assert c.get("/device/config").status_code == 401
    assert c.get("/device/config", headers={"X-Device-Token": "casa_errado"}).status_code == 401
    cfg = c.get("/device/config", headers=dh).json()
    assert cfg["alterado"] and cfg["layout"]["categorias"][0]["botoes"][0]["rotulo"] == "Água"
    v = cfg["config_versao"]
    assert c.get(f"/device/config?versao_atual={v}", headers=dh).json() == {"alterado": False, "config_versao": v}
    c.patch("/dispositivos/24:62:AB:E4:C1:0C", json={"volume": 30}, headers=H())
    assert c.get(f"/device/config?versao_atual={v}", headers=dh).json()["ajustes"]["volume"] == 30

    lote = {"bateria_pct": 80, "firmware": "v1", "acionamentos": [
        {"botao_id": agua, "uid_local": f"a{i}", "ha_segundos": 60 * i} for i in range(3)]
        + [{"botao_id": tv, "uid_local": "t1"}, {"botao_id": "fantasma", "uid_local": "f"}]}
    r = c.post("/device/telemetria", json=lote, headers=dh).json()
    assert (r["recebidos"], r["duplicados"], r["ignorados"]) == (4, 0, 1)
    r = c.post("/device/telemetria", json=lote, headers=dh).json()  # reenvio não duplica
    assert (r["recebidos"], r["duplicados"], r["ignorados"]) == (0, 4, 1)
    assert c.get("/dispositivos", headers=H()).json()[0]["bateria_pct"] == 80

    h = c.get("/historico", headers=H()).json()
    assert h["total_acionamentos"] == 4 and h["mais_acionados"][0]["nome"] == "Água" and h["mais_acionados"][0]["total"] == 3
    assert h["menos_acionados"][0]["nome"] == "TV"
    assert c.get("/historico", headers=H("u2")).json()["tem_dados"] is False


def test_excluir_conta_apaga_tudo(ctx):
    c, db, fb = ctx
    cid = c.post("/categorias", json={"nome": "Casa"}, headers=H()).json()["id"]
    d = c.post("/dispositivos", json={"mac": "AA:BB:CC:DD:EE:FF"}, headers=H()).json()
    c.get("/me", headers=H())
    assert c.delete("/me", headers=H()).status_code == 204
    assert fb.apagados == ["u1"] and db.data == {}
    assert c.get("/device/config", headers={"X-Device-Token": d["device_token"]}).status_code == 401


# ───────────────────────── Pacote: histórico completo, desempenho, notificações ─────────────────────────
from datetime import datetime, timedelta, timezone


def _semear(db, uid, itens):
    """itens: (botão, categoria, dias_atrás, uid_doc)"""
    for nome, cat, dias, did in itens:
        db.data[("usuarios", uid, "acionamentos", did)] = {
            "botao_id": "x", "botao_nome": nome, "categoria_nome": cat, "dispositivo": None, "origem": "app",
            "acionado_em": (datetime.now(timezone.utc) - timedelta(days=dias, minutes=1)).isoformat()}


def test_historico_periodo_busca_e_remocao(ctx):
    c, db, _ = ctx
    _semear(db, "u1", [("Água", "Casa", 0, "a1"), ("Água", "Casa", 0, "a2"), ("Água", "Casa", 3, "a3"),
                       ("TV", "Casa", 0, "t1"), ("Escola", "Rotina", 20, "e1")])
    todos = c.get("/historico", headers=H()).json()
    assert todos["total_acionamentos"] == 5 and todos["mais_acionados"][0]["nome"] == "Água"
    assert todos["mais_acionados"][0]["total"] == 3 and todos["mais_acionados"][0]["data"] in ("Hoje", "Ontem")
    assert c.get("/historico?periodo=dia", headers=H()).json()["total_acionamentos"] == 3
    assert c.get("/historico?periodo=semana", headers=H()).json()["total_acionamentos"] == 4
    assert c.get("/historico?periodo=mes", headers=H()).json()["total_acionamentos"] == 5
    assert c.get("/historico?periodo=ano", headers=H()).status_code == 422
    busca = c.get("/historico?busca=tv", headers=H()).json()
    assert [i["nome"] for i in busca["mais_acionados"] + busca["menos_acionados"]] == ["TV"]
    # remover o histórico de um botão pelo id do item
    item = todos["mais_acionados"][0]
    assert c.delete(f"/historico/{item['id']}", headers=H()).status_code == 200
    assert c.get("/historico", headers=H()).json()["total_acionamentos"] == 2
    assert c.delete(f"/historico/{item['id']}", headers=H()).status_code == 404
    assert c.get("/historico", headers=H("u2")).json()["tem_dados"] is False
    assert c.delete("/historico", headers=H()).status_code == 200
    assert c.get("/historico", headers=H()).json()["tem_dados"] is False


def test_toque_no_app_desempenho_e_pdf(ctx):
    c, db, _ = ctx
    assert c.get("/desempenho?periodo=dia", headers=H()).json()["tem_dados"] is False
    cid = c.post("/categorias", json={"nome": "Casa"}, headers=H()).json()["id"]
    bid = c.post(f"/categorias/{cid}/botoes", json={"rotulo": "Água"}, headers=H()).json()["id"]
    assert c.post("/historico/acionamentos", json={"botao_id": "nao-existe"}, headers=H()).status_code == 404
    for _ in range(3):
        assert c.post("/historico/acionamentos", json={"botao_id": bid}, headers=H()).status_code == 201
    d = c.get("/desempenho?periodo=semana", headers=H()).json()
    assert d["total"] == 3 and len(d["serie"]) == 7 and sum(p["valor"] for p in d["serie"]) == 3
    assert d["top_botoes"][0] == {"name": "Água", "valor": 3} and d["por_categoria"][0]["name"] == "Casa"
    assert len(c.get("/desempenho?periodo=dia", headers=H()).json()["serie"]) == 24
    assert len(c.get("/desempenho?periodo=mes", headers=H()).json()["serie"]) == 30
    pdf = c.get("/desempenho/relatorio?periodo=semana", headers=H())
    assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf" and pdf.content.startswith(b"%PDF")
    vazio = c.get("/desempenho/relatorio?periodo=dia", headers=H("u2"))
    assert vazio.status_code == 200 and vazio.content.startswith(b"%PDF")


def test_notificacoes_pareamento_bateria_e_preferencia(ctx):
    c, *_ = ctx
    c.post("/dispositivos", json={"mac": "11:22:33:44:55:66", "nome": "Meu ESP"}, headers=H())
    n = c.get("/notificacoes", headers=H()).json()
    assert n["nao_lidas"] == 1 and n["itens"][0]["titulo"] == "Dispositivo Conectado"
    tok = c.post("/dispositivos", json={"mac": "11:22:33:44:55:77"}, headers=H()).json()["device_token"]
    dh = {"X-Device-Token": tok}
    c.post("/device/telemetria", json={"bateria_pct": 90}, headers=dh)
    c.post("/device/telemetria", json={"bateria_pct": 15}, headers=dh)
    c.post("/device/telemetria", json={"bateria_pct": 10}, headers=dh)  # já estava baixa: não repete
    baixas = [i for i in c.get("/notificacoes", headers=H()).json()["itens"] if i["tipo"] == "bateria_baixa"]
    assert len(baixas) == 1
    assert c.post("/notificacoes/lidas", headers=H()).status_code == 200
    assert c.get("/notificacoes", headers=H()).json()["nao_lidas"] == 0
    assert c.get("/notificacoes?apenas_nao_lidas=true", headers=H()).json()["itens"] == []
    assert c.post("/notificacoes/inexistente/lida", headers=H()).status_code == 404
    assert c.delete("/notificacoes", headers=H()).status_code == 200
    # preferência desligada = sem notificações
    c.patch("/me", json={"notificacoes_ativas": False}, headers=H())
    c.post("/dispositivos", json={"mac": "11:22:33:44:55:88"}, headers=H())
    assert c.get("/notificacoes", headers=H()).json()["itens"] == []


def test_online_ordenacao_url_e_exportacao(ctx):
    c, *_ = ctx
    d = c.post("/dispositivos", json={"mac": "AA:AA:AA:AA:AA:01"}, headers=H()).json()
    assert d["online"] is False
    c.get("/device/config", headers={"X-Device-Token": d["device_token"]})
    assert c.get("/dispositivos", headers=H()).json()[0]["online"] is True

    ids = [c.post("/categorias", json={"nome": n}, headers=H()).json()["id"] for n in ("A", "B", "C")]
    r = c.put("/categorias/ordem", json={"ids": ids[::-1]}, headers=H())
    assert [x["id"] for x in r.json()] == ids[::-1]
    assert c.put("/categorias/ordem", json={"ids": ids[:2]}, headers=H()).status_code == 422
    bs = [c.post(f"/categorias/{ids[0]}/botoes", json={"rotulo": f"B{i}"}, headers=H()).json()["id"] for i in range(3)]
    r = c.put(f"/categorias/{ids[0]}/botoes/ordem", json={"ids": bs[::-1]}, headers=H())
    assert [b["id"] for b in r.json()] == bs[::-1]

    assert c.patch(f"/categorias/{ids[0]}/botoes/{bs[0]}", json={"rotulo": None}, headers=H()).status_code == 422
    assert c.post(f"/categorias/{ids[0]}/botoes", json={"rotulo": "X", "imagem_id": "naoexiste"}, headers=H()).status_code == 422

    exp = c.get("/me/exportar", headers=H()).json()
    assert len(exp["categorias"]) == 3 and exp["dispositivos"][0]["mac"] == "AA:AA:AA:AA:AA:01"
    assert "token_hash" not in str(exp)


# ───────────────────────── Cadastro só com e-mail confirmado ─────────────────────────
import io
import os

from PIL import Image

from app import emailer

SENHA = "Senha@123"


def _codigo():
    return emailer.outbox[-1]["corpo"].split("Seu código: ")[1][:6]


def test_conta_so_e_criada_depois_do_codigo(ctx, monkeypatch):
    c, db, fb = ctx
    monkeypatch.setattr("app.config.settings.codigo_reenvio_segundos", 0)
    r = c.post("/auth/cadastro", json={"nome": "Maria", "email": "Maria@Exemplo.com", "senha": SENHA})
    assert r.status_code == 202 and r.json()["email"] == "maria@exemplo.com"
    assert fb.usuarios == {}                       # NADA criado no Firebase ainda
    assert emailer.outbox[-1]["para"] == "maria@exemplo.com"
    assert SENHA not in str(db.data)               # senha não é gravada na etapa pendente
    assert "codigo_hash" in str(db.data) and _codigo() not in str(db.data)  # código só como hash
    # código errado não cria
    assert c.post("/auth/confirmar", json={"email": "maria@exemplo.com", "codigo": "000000", "senha": SENHA}).status_code == 400
    assert fb.usuarios == {}
    # código certo cria, com e-mail verificado
    r = c.post("/auth/confirmar", json={"email": "maria@exemplo.com", "codigo": _codigo(), "senha": SENHA})
    assert r.status_code == 201 and fb.usuarios["maria@exemplo.com"]["email_verified"] is True
    assert fb.usuarios["maria@exemplo.com"]["nome"] == "Maria"
    assert db.data == {}                           # pendência apagada
    # reusar o código ou cadastrar o mesmo e-mail de novo
    assert c.post("/auth/confirmar", json={"email": "maria@exemplo.com", "codigo": "123456", "senha": SENHA}).status_code == 400
    assert c.post("/auth/cadastro", json={"nome": "Maria", "email": "maria@exemplo.com", "senha": SENHA}).status_code == 409


def test_cadastro_validacoes_expiracao_e_tentativas(ctx, monkeypatch):
    c, db, fb = ctx
    monkeypatch.setattr("app.config.settings.codigo_reenvio_segundos", 0)
    assert c.post("/auth/cadastro", json={"nome": "A", "email": "x@x.com", "senha": SENHA}).status_code == 422
    r = c.post("/auth/cadastro", json={"nome": "Ana", "email": "ana@x.com", "senha": "fraca"})
    assert r.status_code == 422 and "maiúscula" in r.json()["mensagem"]
    assert c.post("/auth/cadastro", json={"nome": "Ana", "email": "invalido", "senha": SENHA}).status_code == 422
    # tentativas: após 5 erros o código é invalidado, mesmo o certo
    c.post("/auth/cadastro", json={"nome": "Ana", "email": "ana@x.com", "senha": SENHA})
    certo = _codigo()
    errado = "111111" if certo != "111111" else "222222"
    for _ in range(5):
        c.post("/auth/confirmar", json={"email": "ana@x.com", "codigo": errado, "senha": SENHA})
    r = c.post("/auth/confirmar", json={"email": "ana@x.com", "codigo": certo, "senha": SENHA})
    assert r.status_code == 429 and fb.usuarios == {}
    # expiração
    c.post("/auth/cadastro", json={"nome": "Ana", "email": "ana@x.com", "senha": SENHA})
    cod = _codigo()
    chave = next(iter(db.data))
    db.data[chave]["expira_em"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    r = c.post("/auth/confirmar", json={"email": "ana@x.com", "codigo": cod, "senha": SENHA})
    assert r.status_code == 400 and r.json()["codigo"] == "codigo_expirado" and fb.usuarios == {}


def test_reenvio_com_cooldown(ctx):
    c, *_ = ctx
    c.post("/auth/cadastro", json={"nome": "Bia", "email": "bia@x.com", "senha": SENHA})
    r = c.post("/auth/cadastro", json={"nome": "Bia", "email": "bia@x.com", "senha": SENHA})
    assert r.status_code == 429 and r.json()["codigo"] == "aguarde_reenvio"
    assert c.post("/auth/reenviar-codigo", json={"email": "bia@x.com"}).status_code == 429
    r = c.post("/auth/reenviar-codigo", json={"email": "ninguem@x.com"})   # não revela se existe
    assert r.status_code == 202


def test_limite_de_requisicoes_no_cadastro(ctx, monkeypatch):
    c, *_ = ctx
    monkeypatch.setattr("app.config.settings.codigo_reenvio_segundos", 0)
    codigos = [c.post("/auth/cadastro", json={"nome": "Zé", "email": f"z{i}@x.com", "senha": SENHA}).status_code for i in range(12)]
    assert codigos[:10] == [202] * 10 and 429 in codigos[10:]


# ───────────────────────── Mídia ─────────────────────────
def _png(lado=(500, 300)):
    b = io.BytesIO()
    Image.new("RGB", lado, (200, 30, 30)).save(b, "PNG")
    return b.getvalue()


def _wav():
    return b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 32


def test_midia_botao_e_download_pelo_aparelho(ctx):
    c, db, _ = ctx
    cid = c.post("/categorias", json={"nome": "Casa"}, headers=H()).json()["id"]
    img = c.post("/midias", files={"arquivo": ("foto.png", _png(), "image/png")}, headers=H())
    aud = c.post("/midias", files={"arquivo": ("agua.wav", _wav(), "audio/wav")}, headers=H())
    assert img.status_code == 201 and img.json()["tipo"] == "imagem" and img.json()["mime"] == "image/jpeg"
    assert aud.status_code == 201 and aud.json()["tipo"] == "audio"
    # imagem foi reduzida para 240x240
    baixada = c.get(f"/midias/{img.json()['id']}/arquivo", headers=H())
    assert baixada.status_code == 200 and Image.open(io.BytesIO(baixada.content)).size == (240, 240)
    assert c.get(f"/midias/{img.json()['id']}/arquivo").status_code == 401
    assert c.get(f"/midias/{img.json()['id']}/arquivo", headers=H("u2")).status_code == 404
    # conteúdo falso é recusado, mesmo com extensão/Content-Type enganosos
    assert c.post("/midias", files={"arquivo": ("v.png", b"MZ\x90 nao sou imagem", "image/png")}, headers=H()).status_code == 415
    assert c.post("/midias", files={"arquivo": ("x.wav", _png(), "audio/wav")}, data={"tipo": "audio"}, headers=H()).status_code == 415

    b = c.post(f"/categorias/{cid}/botoes", json={"rotulo": "Água", "imagem_id": img.json()["id"], "audio_id": aud.json()["id"]}, headers=H())
    assert b.status_code == 201 and b.json()["audio"] == "agua.wav" and b.json()["imagem"] == "foto.png"
    assert c.patch(f"/categorias/{cid}/botoes/{b.json()['id']}", json={"imagem_id": aud.json()["id"]}, headers=H()).json()["codigo"] == "midia_tipo_errado"

    # aparelho: config traz os arquivos e permite baixar; token de outra pessoa não baixa
    tok = c.post("/dispositivos", json={"mac": "AA:BB:CC:DD:EE:01"}, headers=H()).json()["device_token"]
    dh = {"X-Device-Token": tok}
    cfg = c.get("/device/config", headers=dh).json()
    assert {a["tipo"] for a in cfg["arquivos"]} == {"imagem", "audio"} and all(len(a["sha256"]) == 64 for a in cfg["arquivos"])
    f = c.get(cfg["arquivos"][0]["url"], headers=dh)
    assert f.status_code == 200 and f.headers["x-content-sha256"] == cfg["arquivos"][0]["sha256"]
    tok2 = c.post("/dispositivos", json={"mac": "AA:BB:CC:DD:EE:02"}, headers=H("u2")).json()["device_token"]
    assert c.get(cfg["arquivos"][0]["url"], headers={"X-Device-Token": tok2}).status_code == 404

    # excluir a mídia limpa o botão e apaga o arquivo do disco
    from app import storage
    antes = len(list(storage.RAIZ.iterdir()))
    assert c.delete(f"/midias/{aud.json()['id']}", headers=H()).status_code == 204
    assert len(list(storage.RAIZ.iterdir())) == antes - 1
    cats = c.get("/categorias", headers=H()).json()
    assert cats[0]["botoes"][0]["audio_id"] is None and cats[0]["botoes"][0]["audio"] is None


def test_excluir_conta_apaga_arquivos_do_disco(ctx):
    c, db, fb = ctx
    from app import storage
    c.post("/midias", files={"arquivo": ("agua.wav", _wav(), "audio/wav")}, headers=H())
    assert len(list(storage.RAIZ.iterdir())) == 1
    assert c.delete("/me", headers=H()).status_code == 204
    assert list(storage.RAIZ.iterdir()) == [] and db.data == {}


def test_dispositivo_codigo_ssid_e_sinal(ctx):
    c, *_ = ctx
    d = c.post("/dispositivos", json={"mac": "24:62:ab:e4:c1:0c"}, headers=H()).json()
    assert d["codigo"] == "ESP32-C10C"
    c.post("/device/telemetria", json={"ssid": "casa_2G", "sinal_wifi": 80, "ip": "192.168.0.9"}, headers={"X-Device-Token": d["device_token"]})
    info = c.get("/dispositivos", headers=H()).json()[0]
    assert info["ssid"] == "casa_2G" and info["sinal_wifi"] == 80 and info["online"] is True


def test_excluir_botao_e_categoria_libera_arquivos(ctx):
    c, db, _ = ctx
    from app import storage
    cid = c.post("/categorias", json={"nome": "Casa"}, headers=H()).json()["id"]
    def novo(rotulo):
        a = c.post("/midias", files={"arquivo": ("a.wav", _wav(), "audio/wav")}, headers=H()).json()["id"]
        return c.post(f"/categorias/{cid}/botoes", json={"rotulo": rotulo, "audio_id": a}, headers=H()).json()
    b1, b2 = novo("Água"), novo("TV")
    assert len(list(storage.RAIZ.iterdir())) == 2
    assert c.delete(f"/categorias/{cid}/botoes/{b1['id']}", headers=H()).status_code == 204
    assert len(list(storage.RAIZ.iterdir())) == 1                      # arquivo do botão apagado
    assert c.get("/midias", headers=H()).json()[0]["id"] == b2["audio_id"]
    assert c.delete(f"/categorias/{cid}", headers=H()).status_code == 204
    assert list(storage.RAIZ.iterdir()) == [] and c.get("/midias", headers=H()).json() == []


def test_renomear_categoria_preserva_a_cor(ctx):
    c, *_ = ctx
    cid = c.post("/categorias", json={"nome": "Casa", "cor": "#112233"}, headers=H()).json()["id"]
    r = c.patch(f"/categorias/{cid}", json={"nome": "Minha Casa"}, headers=H()).json()
    assert r["nome"] == "Minha Casa" and r["slug"] == "minha-casa" and r["cor"] == "#112233"


def test_perfil_usa_o_nome_informado_no_cadastro(ctx, monkeypatch):
    c, db, fb = ctx
    monkeypatch.setattr("app.config.settings.codigo_reenvio_segundos", 0)
    c.post("/auth/cadastro", json={"nome": "Zeus Alves", "email": "zeus@x.com", "senha": SENHA})
    c.post("/auth/confirmar", json={"email": "zeus@x.com", "codigo": _codigo(), "senha": SENHA})
    uid = fb.usuarios["zeus@x.com"]["uid"]
    perfil = c.get("/me", headers={"Authorization": f"Bearer tok:{uid}:zeus@x.com:1"}).json()
    assert perfil["nome"] == "Zeus Alves"          # e não "zeus" (começo do e-mail)

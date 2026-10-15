import pytest
from fastapi.testclient import TestClient

from app.deps import get_auth, get_db
from app.main import app
from tests.fakes import FakeAuth, FakeFirestore


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

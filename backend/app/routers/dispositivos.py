"""Pareamento do ESP32 (app) + API do aparelho (/device/*) + histórico de uso."""
from datetime import datetime, timedelta, timezone

from ..config import settings

from fastapi import APIRouter, Depends

from ..deps import dispositivo_atual, erro, get_db, usuario_atual
from ..schemas import DispositivoIn, DispositivoUpdate, Telemetria
from ..security import novo_token_dispositivo
from ..util import agora_iso, filtro, notificar

router = APIRouter(tags=["Dispositivos e histórico"])

PUBLICO = ("mac", "nome", "ssid", "sinal_wifi", "nome_paciente", "modo", "ip", "firmware", "bateria_pct", "carregando",
           "ultima_sincronizacao", "volume", "brilho_leds", "brilho_telas", "tempo_inatividade_s", "config_versao")


def _online(d: dict) -> bool:
    ult = d.get("ultima_sincronizacao")
    if not ult:
        return False
    return datetime.now(timezone.utc) - datetime.fromisoformat(ult) <= timedelta(minutes=settings.device_offline_minutos)


def _publico(d: dict) -> dict:
    return {**{k: d.get(k) for k in PUBLICO}, "online": _online(d),
            "codigo": "ESP32-" + d["mac"].replace(":", "")[-4:]}


def _meu(db, uid, mac):
    ref = db.collection("dispositivos").document(mac.replace("-", ":").upper())
    snap = ref.get()
    if not snap.exists or snap.to_dict().get("owner_uid") != uid:
        raise erro(404, "nao_encontrado", "Dispositivo não encontrado.")
    return ref


# ───────────── app do responsável ─────────────
@router.post("/dispositivos", status_code=201, summary="Pareia um ESP32 pelo MAC; devolve o device_token UMA vez")
def parear(dados: DispositivoIn, u=Depends(usuario_atual), db=Depends(get_db)):
    ref = db.collection("dispositivos").document(dados.mac)
    if ref.get().exists:
        raise erro(409, "dispositivo_ja_pareado", "Este dispositivo já está pareado a uma conta.")
    token, token_hash = novo_token_dispositivo()
    doc = {"mac": dados.mac, "owner_uid": u["uid"], "token_hash": token_hash, "nome": dados.nome or "ESP32 - C.A.S.A.",
           "nome_paciente": dados.nome_paciente, "modo": "casa", "volume": 70, "brilho_leds": 70, "brilho_telas": 80,
           "tempo_inatividade_s": 60, "config_versao": 1, "criado_em": agora_iso()}
    ref.set(doc)
    notificar(db, u["uid"], "dispositivo_conectado", "Dispositivo Conectado", f"{doc['nome']} pareado com sucesso")
    return {**_publico(doc), "device_token": token}


@router.get("/dispositivos")
def listar(u=Depends(usuario_atual), db=Depends(get_db)):
    return [_publico(d.to_dict()) for d in db.collection("dispositivos").where(filter=filtro("owner_uid", u["uid"])).stream()]


@router.patch("/dispositivos/{mac}", summary="Volume, brilho, tempo de inatividade, nome, modo")
def configurar(mac: str, dados: DispositivoUpdate, u=Depends(usuario_atual), db=Depends(get_db)):
    ref = _meu(db, u["uid"], mac)
    campos = dados.model_dump(exclude_none=True)
    ref.update({**campos, "config_versao": ref.get().to_dict()["config_versao"] + 1})
    return _publico(ref.get().to_dict())


@router.delete("/dispositivos/{mac}", status_code=204)
def remover(mac: str, u=Depends(usuario_atual), db=Depends(get_db)):
    _meu(db, u["uid"], mac).delete()


# ───────────── aparelho (ESP32) — cabeçalho X-Device-Token ─────────────
@router.get("/device/config", tags=["API do aparelho (ESP32)"], summary="Layout + ajustes (ou {alterado:false})")
def device_config(versao_atual: int | None = None, d=Depends(dispositivo_atual), db=Depends(get_db)):
    ref, disp = d
    ref.update({"ultima_sincronizacao": agora_iso()})
    if versao_atual == disp["config_versao"]:
        return {"alterado": False, "config_versao": disp["config_versao"]}
    cats = sorted(({"id": s.id, **s.to_dict()} for s in
                   db.collection("usuarios").document(disp["owner_uid"]).collection("categorias").stream()),
                  key=lambda c: c.get("ordem", 0))
    midias = {m.id: m.to_dict() for m in
              db.collection("usuarios").document(disp["owner_uid"]).collection("midias").stream()}
    arquivos, vistos = [], set()
    for c in cats:
        for b in c.get("botoes", []):
            for k in ("imagem_id", "audio_id"):
                mid = b.get(k)
                if mid and mid in midias and mid not in vistos:
                    vistos.add(mid)
                    m = midias[mid]
                    arquivos.append({"id": mid, "tipo": m["tipo"], "mime": m["mime"], "tamanho": m["tamanho"],
                                     "sha256": m["sha256"], "url": f"/device/midias/{mid}"})
    return {"alterado": True, "config_versao": disp["config_versao"], "modo": disp["modo"], "arquivos": arquivos,
            "ajustes": {k: disp[k] for k in ("volume", "brilho_leds", "brilho_telas", "tempo_inatividade_s")},
            "layout": {"categorias": cats}}


@router.post("/device/telemetria", tags=["API do aparelho (ESP32)"], summary="Bateria, IP e usos feitos offline")
def device_telemetria(dados: Telemetria, d=Depends(dispositivo_atual), db=Depends(get_db)):
    ref, disp = d
    estado = dados.model_dump(exclude={"acionamentos"}, exclude_none=True)
    antes, carregando = disp.get("bateria_pct"), estado.get("carregando", disp.get("carregando"))
    ref.update({**estado, "ultima_sincronizacao": agora_iso()})
    # Notifica só ao CRUZAR o limite (evita repetir a cada sincronização)
    nova = dados.bateria_pct
    if nova is not None and nova <= settings.bateria_baixa_pct and not carregando \
            and (antes is None or antes > settings.bateria_baixa_pct):
        notificar(db, disp["owner_uid"], "bateria_baixa", "Bateria do ESP32", f"Nível em {nova}%")

    botoes = {}
    for s in db.collection("usuarios").document(disp["owner_uid"]).collection("categorias").stream():
        for b in s.to_dict().get("botoes", []):
            botoes[b["id"]] = (b["rotulo"], s.to_dict()["nome"])
    col = db.collection("usuarios").document(disp["owner_uid"]).collection("acionamentos")
    recebidos = duplicados = ignorados = 0
    agora = datetime.now(timezone.utc)
    for a in dados.acionamentos:
        if a.botao_id not in botoes:
            ignorados += 1
            continue
        doc = col.document(f"{disp['mac'].replace(':', '')}_{a.uid_local}")  # id determinístico = idempotente
        if doc.get().exists:
            duplicados += 1
            continue
        nome, cat = botoes[a.botao_id]
        doc.set({"botao_id": a.botao_id, "botao_nome": nome, "categoria_nome": cat, "dispositivo": disp["mac"],
                 "origem": "dispositivo", "acionado_em": (agora - timedelta(seconds=a.ha_segundos)).isoformat()})
        recebidos += 1
    return {"recebidos": recebidos, "duplicados": duplicados, "ignorados": ignorados,
            "config_versao": disp["config_versao"]}


@router.get("/device/midias/{mid}", tags=["API do aparelho (ESP32)"], summary="Baixa imagem/áudio de um botão")
def device_midia(mid: str, d=Depends(dispositivo_atual), db=Depends(get_db)):
    from fastapi.responses import FileResponse
    from .. import storage
    snap = db.collection("usuarios").document(d[1]["owner_uid"]).collection("midias").document(mid).get()
    if not snap.exists:
        raise erro(404, "nao_encontrado", "Arquivo não encontrado.")
    m = snap.to_dict()
    return FileResponse(storage.caminho(m["arquivo"]), media_type=m["mime"],
                        headers={"X-Content-SHA256": m["sha256"], "X-Content-Type-Options": "nosniff"})

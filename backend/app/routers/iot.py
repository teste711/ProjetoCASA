"""Fluxo do IoT: envio de imagens (e áudios) do app para o dispositivo.

    1. App envia o arquivo à API                      POST /iot/midias        (login do responsável)
    2. API converte: imagem → JPEG 240×240 (baseline, sem EXIF); áudio MP3/WAV é validado
    3. API converte para BASE64 e grava no Firestore  dispositivos/{MAC}/fila/{id}
    4. API acende o SINAL no Realtime Database        dispositivos/{MAC}/sync/{id}   (estado "pendente")
    5. Dispositivo percebe o sinal (ou consulta)      GET  /device/iot/pendentes     (token do aparelho)
    6. Dispositivo busca o conteúdo                   GET  /device/iot/midias/{id}   → base64 + sha256
    7. Dispositivo confirma                           POST /device/iot/midias/{id}/concluido
    8. API marca "concluido" no Realtime Database e APAGA o base64 do Firestore (limpeza)

Ordem das gravações (importa): Firestore ANTES do sinal, para o aparelho nunca ver um sinal sem conteúdo;
na conclusão, sinal ANTES da limpeza, para um erro no meio nunca apagar o conteúdo sem avisar.
Se o sinal falhar no envio, o documento do Firestore é desfeito (nada fica órfão).
"""
import base64
import hashlib
import logging
import re
import time
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile

from .. import storage
from ..config import settings
from ..deps import Limitador, dispositivo_atual, erro, get_db, get_rtdb, usuario_atual
from ..schemas import ConclusaoIn, ErroIn, normalizar_mac
from ..util import agora_iso

log = logging.getLogger("uvicorn.error")
router = APIRouter(tags=["IoT: imagens e áudios para o dispositivo"])

ABERTOS = ("pendente", "baixando", "erro")  # itens que ainda ocupam a fila
_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
MB = 1024 * 1024


def agora_ms() -> int:
    return int(time.time() * 1000)


def _fila(db, mac: str):
    return db.collection("dispositivos").document(mac).collection("fila")


def _no(mac: str, mid: str | None = None) -> str:
    return f"dispositivos/{mac}/sync" + (f"/{mid}" if mid else "")


def _mac_ou_422(valor: str) -> str:
    try:
        return normalizar_mac(valor)
    except ValueError as e:
        raise erro(422, "validacao", str(e))


def _dispositivo_do_usuario(db, uid: str, mac: str) -> None:
    snap = db.collection("dispositivos").document(mac).get()
    if not snap.exists or snap.to_dict().get("owner_uid") != uid:
        raise erro(404, "nao_encontrado", "Dispositivo não encontrado.")


def _achar_botao(db, uid: str, botao_id: str) -> dict:
    for s in db.collection("usuarios").document(uid).collection("categorias").stream():
        cat = s.to_dict()
        for b in cat.get("botoes", []):
            if b["id"] == botao_id:
                return {"botao_id": b["id"], "rotulo": b["rotulo"], "botao_ordem": b.get("ordem"),
                        "categoria_ordem": cat.get("ordem"), "categoria_nome": cat.get("nome")}
    raise erro(422, "botao_invalido", "Botão não encontrado nas suas categorias.")


def _limpar_vencidos(db, rtdb, mac: str) -> dict:
    """Remove itens esquecidos (aparelho nunca buscou, ou sinais 'concluido' antigos). Devolve os nós atuais."""
    nos = rtdb.get(_no(mac)) or {}
    agora = agora_ms()
    lim_pend = settings.iot_pendente_expira_horas * 3600 * 1000
    lim_conc = settings.iot_concluido_expira_horas * 3600 * 1000
    for mid, n in list(nos.items()):
        if not isinstance(n, dict) or not _ID.match(str(mid)):
            continue
        criado = n.get("criado_em", 0)
        vencido = (n.get("estado") in ABERTOS and agora - criado > lim_pend) or \
                  (n.get("estado") == "concluido" and agora - n.get("concluido_em", criado) > lim_conc)
        if vencido:
            _fila(db, mac).document(mid).delete()
            rtdb.delete(_no(mac, mid))
            nos.pop(mid, None)
    return nos


# ═══════════════════════ APP DO RESPONSÁVEL (Bearer do Firebase) ═══════════════════════
@router.post("/iot/midias", status_code=201, dependencies=[Depends(Limitador(30, 60))],
             summary="Envia imagem (PNG/JPEG/WEBP) ou áudio (MP3/WAV) para o dispositivo")
def enviar_midia(arquivo: UploadFile = File(...), dispositivo: str = Form(..., description="MAC do dispositivo"),
                 botao_id: str | None = Form(default=None, description="botão que usará a mídia (opcional)"),
                 u=Depends(usuario_atual), db=Depends(get_db), rtdb=Depends(get_rtdb)):
    mac = _mac_ou_422(dispositivo)
    _dispositivo_do_usuario(db, u["uid"], mac)
    botao = _achar_botao(db, u["uid"], botao_id) if botao_id else {}

    limite = max(settings.max_imagem_mb, settings.max_audio_mb) * MB
    dados = arquivo.file.read(limite + 1)
    if not dados:
        raise erro(422, "arquivo_vazio", "O arquivo enviado está vazio.")
    if len(dados) > limite:
        raise erro(413, "arquivo_grande", "Arquivo muito grande.")

    # CONVERTE para o formato do aparelho (o tipo é detectado pelo CONTEÚDO, não pelo nome)
    audio = storage.detectar_audio(dados)
    largura = altura = None
    if audio:
        if len(dados) > settings.iot_max_audio_kb * 1024:
            raise erro(413, "audio_grande", f"O áudio excede {settings.iot_max_audio_kb} KB. Use um trecho mais curto ou menor taxa.")
        tipo, mime = "audio", audio[0]
    else:
        if len(dados) > settings.max_imagem_mb * MB:
            raise erro(413, "arquivo_grande", f"A imagem excede {settings.max_imagem_mb} MB.")
        dados = storage.processar_imagem(dados)          # JPEG 240×240 baseline (valida que é imagem de verdade)
        tipo, mime, largura, altura = "imagem", "image/jpeg", settings.imagem_lado_px, settings.imagem_lado_px

    # BASE64 (precisa caber no limite de 1 MiB de um documento do Firestore)
    b64 = base64.b64encode(dados).decode("ascii")
    if len(b64) > settings.iot_max_base64_bytes:
        raise erro(413, "arquivo_grande", "O conteúdo, em base64, excede o limite do banco de dados.")

    nos = _limpar_vencidos(db, rtdb, mac)
    abertos = sum(1 for n in nos.values() if isinstance(n, dict) and n.get("estado") in ABERTOS)
    if abertos >= settings.iot_max_pendentes:
        raise erro(409, "fila_cheia", f"O dispositivo já tem {abertos} itens aguardando. Espere ele sincronizar.")

    mid = uuid.uuid4().hex[:16]
    sha = hashlib.sha256(dados).hexdigest()
    doc = {"tipo": tipo, "mime": mime, "base64": b64, "sha256": sha, "tamanho": len(dados),
           "largura": largura, "altura": altura, "estado": "pendente", "tentativas": 0, "erro": None,
           "owner_uid": u["uid"], "criado_em": agora_iso(), **botao}
    sinal = {"tipo": tipo, "estado": "pendente", "tamanho": len(dados), "criado_em": agora_ms(),
             "botao_id": botao.get("botao_id"), "categoria_ordem": botao.get("categoria_ordem"),
             "botao_ordem": botao.get("botao_ordem")}

    _fila(db, mac).document(mid).set(doc)                     # 1º o conteúdo...
    try:
        rtdb.set(_no(mac, mid), sinal)                        # 2º o sinal
    except Exception as e:
        _fila(db, mac).document(mid).delete()                 # desfaz: nada fica órfão
        log.error("Realtime Database indisponível ao sinalizar %s/%s: %s: %s", mac, mid, type(e).__name__, e)
        raise erro(502, "rtdb_indisponivel", "Não foi possível avisar o dispositivo agora. Tente novamente.")
    return {"id": mid, "dispositivo": mac, "tipo": tipo, "estado": "pendente", "tamanho": len(dados),
            "base64_bytes": len(b64), "largura": largura, "altura": altura, "sha256": sha}


@router.get("/iot/midias", summary="Lista a fila do dispositivo (estado de cada envio)")
def listar_fila(dispositivo: str, u=Depends(usuario_atual), db=Depends(get_db), rtdb=Depends(get_rtdb)):
    mac = _mac_ou_422(dispositivo)
    _dispositivo_do_usuario(db, u["uid"], mac)
    nos = rtdb.get(_no(mac)) or {}
    itens = [{"id": k, **n} for k, n in nos.items() if isinstance(n, dict)]
    return sorted(itens, key=lambda i: i.get("criado_em", 0))


@router.get("/iot/midias/{mid}", summary="Estado de um envio (pendente → baixando → concluido | erro)")
def estado_envio(mid: str, dispositivo: str, u=Depends(usuario_atual), db=Depends(get_db), rtdb=Depends(get_rtdb)):
    mac = _mac_ou_422(dispositivo)
    _dispositivo_do_usuario(db, u["uid"], mac)
    no = rtdb.get(_no(mac, mid))
    if not isinstance(no, dict):
        raise erro(404, "nao_encontrado", "Envio não encontrado.")
    return {"id": mid, **no}


@router.delete("/iot/midias/{mid}", status_code=204, summary="Cancela um envio (apaga o conteúdo e o sinal)")
def cancelar(mid: str, dispositivo: str, u=Depends(usuario_atual), db=Depends(get_db), rtdb=Depends(get_rtdb)):
    mac = _mac_ou_422(dispositivo)
    _dispositivo_do_usuario(db, u["uid"], mac)
    _fila(db, mac).document(mid).delete()
    rtdb.delete(_no(mac, mid))


# ═══════════════════════ DISPOSITIVO (X-Device-Token) ═══════════════════════
@router.get("/device/iot/pendentes", tags=["API do aparelho (ESP32)"],
            summary="Itens que o aparelho ainda precisa buscar (alternativa a escutar o Realtime Database)")
def device_pendentes(d=Depends(dispositivo_atual), rtdb=Depends(get_rtdb)):
    mac = d[1]["mac"]
    nos = rtdb.get(_no(mac)) or {}
    itens = [{"id": k, **n} for k, n in nos.items() if isinstance(n, dict) and
             (n.get("estado") == "pendente" or (n.get("estado") == "erro" and n.get("tentativas", 0) < settings.iot_max_tentativas))]
    return sorted(itens, key=lambda i: i.get("criado_em", 0))


@router.get("/device/iot/midias/{mid}", tags=["API do aparelho (ESP32)"],
            summary="Conteúdo em base64 + sha256 (o aparelho decodifica, confere o hash e grava no SD)")
def device_buscar(mid: str, d=Depends(dispositivo_atual), db=Depends(get_db), rtdb=Depends(get_rtdb)):
    mac = d[1]["mac"]
    snap = _fila(db, mac).document(mid).get()
    if not snap.exists:
        raise erro(404, "nao_encontrado", "Item não encontrado (já concluído, cancelado ou expirado).")
    doc = snap.to_dict()
    if doc.get("estado") in ("pendente", "erro"):          # também em nova tentativa após um erro
        rtdb.update(_no(mac, mid), {"estado": "baixando"})
    return {"id": mid, **{k: doc.get(k) for k in ("tipo", "mime", "base64", "sha256", "tamanho", "largura", "altura",
                                                  "botao_id", "rotulo", "categoria_ordem", "botao_ordem")}}


@router.post("/device/iot/midias/{mid}/concluido", tags=["API do aparelho (ESP32)"],
             summary="O aparelho gravou no SD: marca concluído e apaga o base64 do Firestore")
def device_concluir(mid: str, dados: ConclusaoIn, d=Depends(dispositivo_atual), db=Depends(get_db), rtdb=Depends(get_rtdb)):
    mac = d[1]["mac"]
    ref = _fila(db, mac).document(mid)
    snap = ref.get()
    if not snap.exists:
        no = rtdb.get(_no(mac, mid))
        if isinstance(no, dict) and no.get("estado") == "concluido":
            return {"id": mid, "estado": "concluido"}          # confirmação repetida (resposta anterior se perdeu): ok
        raise erro(404, "nao_encontrado", "Item não encontrado (cancelado ou expirado).")
    if dados.sha256 and dados.sha256.lower() != snap.to_dict().get("sha256"):
        raise erro(422, "hash_diferente", "O hash informado não confere com o conteúdo enviado. O arquivo chegou corrompido?")
    rtdb.update(_no(mac, mid), {"estado": "concluido", "concluido_em": agora_ms()})   # 1º o sinal...
    ref.delete()                                                                     # 2º a limpeza
    return {"id": mid, "estado": "concluido"}


@router.post("/device/iot/midias/{mid}/erro", tags=["API do aparelho (ESP32)"],
             summary="O aparelho não conseguiu usar o item (hash errado, SD cheio...): mantém para nova tentativa")
def device_erro(mid: str, dados: ErroIn, d=Depends(dispositivo_atual), db=Depends(get_db), rtdb=Depends(get_rtdb)):
    mac = d[1]["mac"]
    ref = _fila(db, mac).document(mid)
    snap = ref.get()
    if not snap.exists:
        raise erro(404, "nao_encontrado", "Item não encontrado (concluído, cancelado ou expirado).")
    tentativas = snap.to_dict().get("tentativas", 0) + 1
    ref.update({"estado": "erro", "erro": dados.mensagem, "tentativas": tentativas})
    rtdb.update(_no(mac, mid), {"estado": "erro", "erro": dados.mensagem, "tentativas": tentativas})
    return {"id": mid, "estado": "erro", "tentativas": tentativas, "pode_tentar_novamente": tentativas < settings.iot_max_tentativas}

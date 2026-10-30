import re
import unicodedata
from datetime import datetime, timezone

from google.cloud.firestore_v1.base_query import FieldFilter


def agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(t: str) -> str:
    s = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "categoria"


def filtro(campo: str, valor):
    return FieldFilter(campo, "==", valor)


def bump_dispositivos(db, uid: str) -> None:
    """Avisa os aparelhos do usuário que há conteúdo novo (o ESP32 compara config_versao)."""
    for d in db.collection("dispositivos").where(filter=filtro("owner_uid", uid)).stream():
        d.reference.update({"config_versao": d.to_dict().get("config_versao", 1) + 1})


def notificar(db, uid: str, tipo: str, titulo: str, mensagem: str) -> None:
    """Cria uma notificação (respeitando a preferência 'notificacoes_ativas' do usuário)."""
    import uuid
    user = db.collection("usuarios").document(uid)
    snap = user.get()
    if snap.exists and not snap.to_dict().get("notificacoes_ativas", True):
        return
    user.collection("notificacoes").document(uuid.uuid4().hex[:12]).set(
        {"tipo": tipo, "titulo": titulo, "mensagem": mensagem, "lida": False, "criada_em": agora_iso()})


def liberar_midias(db, uid: str, candidatas: set[str]) -> None:
    """Apaga (documento + arquivo em disco) as mídias candidatas que nenhum botão usa mais."""
    if not candidatas:
        return
    from . import storage
    usadas = set()
    for c in db.collection("usuarios").document(uid).collection("categorias").stream():
        for b in c.to_dict().get("botoes", []):
            usadas.update(x for x in (b.get("imagem_id"), b.get("audio_id")) if x)
    col = db.collection("usuarios").document(uid).collection("midias")
    for mid in candidatas - usadas:
        snap = col.document(mid).get()
        if snap.exists:
            storage.remover(snap.to_dict()["arquivo"])
            col.document(mid).delete()


def apagar_dispositivo(db, rtdb, mac: str) -> None:
    """Apaga o dispositivo E tudo que pende dele: a fila do IoT (imagens em base64 no Firestore) e os sinais
    no Realtime Database. No Firestore, apagar um documento NÃO apaga as suas subcoleções (por isso recursive_delete)."""
    import logging
    db.recursive_delete(db.collection("dispositivos").document(mac))   # 1º: o token do aparelho deixa de valer
    if rtdb is not None:
        try:
            rtdb.delete(f"dispositivos/{mac}")
        except Exception as e:  # os sinais não têm conteúdo (só estados), mas registra para limpeza manual
            logging.getLogger("uvicorn.error").error("Não foi possível limpar o Realtime Database de %s: %s: %s", mac, type(e).__name__, e)

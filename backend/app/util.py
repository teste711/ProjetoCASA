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

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.cloud.firestore_v1.base_query import FieldFilter

from . import firebase
from .config import settings
from .security import hash_token

_bearer = HTTPBearer(auto_error=False)
_auth = firebase.FirebaseAuth()


def get_db():
    return firebase.firestore_client()


def get_auth():
    return _auth


def erro(status: int, codigo: str, mensagem: str):
    return HTTPException(status, {"codigo": codigo, "mensagem": mensagem})


def usuario_atual(cred: HTTPAuthorizationCredentials | None = Depends(_bearer), fb=Depends(get_auth)) -> dict:
    """Retorna {uid, email, email_verified} a partir do ID token do Firebase."""
    if not cred:
        raise erro(401, "nao_autenticado", "Faça login para continuar.")
    try:
        c = fb.verify(cred.credentials)
    except Exception as e:
        import logging
        logging.getLogger("uvicorn.error").exception("Falha ao validar token: %s", e)
        raise erro(401, "token_invalido", "Sessão inválida ou expirada. Faça login novamente.")
    if settings.require_email_verified and not c.get("email_verified"):
        raise erro(403, "email_nao_verificado", "Confirme seu e-mail (link enviado pelo Firebase) para continuar.")
    return {"uid": c["uid"], "email": c.get("email"), "email_verified": c.get("email_verified", False)}


def dispositivo_atual(x_device_token: str | None = Header(default=None), db=Depends(get_db)):
    """Autentica o ESP32 pelo token guardado (hash) em dispositivos/{mac}."""
    if not x_device_token:
        raise erro(401, "dispositivo_nao_autenticado", "Cabeçalho X-Device-Token ausente.")
    docs = list(db.collection("dispositivos").where(filter=FieldFilter("token_hash", "==", hash_token(x_device_token))).stream())
    if not docs:
        raise erro(401, "dispositivo_nao_autenticado", "Token de dispositivo inválido.")
    return docs[0].reference, docs[0].to_dict()

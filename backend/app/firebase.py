"""Única parte que fala com o Firebase (Auth + Firestore)."""
import firebase_admin
from firebase_admin import auth, credentials, firestore

from .config import settings


def _init() -> None:
    if firebase_admin._apps:
        return
    cred = credentials.Certificate(settings.firebase_credentials) if settings.firebase_credentials \
        else credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)


class FirebaseAuth:
    """Valida o ID token enviado pelo frontend (gerado por signInWithEmailAndPassword)."""

    def verify(self, token: str) -> dict:
        _init()
        return auth.verify_id_token(token)

    def delete_user(self, uid: str) -> None:
        _init()
        auth.delete_user(uid)


def firestore_client():
    _init()
    return firestore.client()

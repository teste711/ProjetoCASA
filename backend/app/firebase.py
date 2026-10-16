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


class EmailJaExiste(Exception):
    pass


class FirebaseAuth:
    """Valida o ID token enviado pelo frontend (gerado por signInWithEmailAndPassword)."""

    def verify(self, token: str) -> dict:
        _init()
        return auth.verify_id_token(token)

    def email_existe(self, email: str) -> bool:
        _init()
        try:
            auth.get_user_by_email(email)
            return True
        except auth.UserNotFoundError:
            return False

    def create_user(self, email: str, senha: str, nome: str) -> str:
        """Cria a conta JÁ com e-mail verificado (a verificação foi feita pelo código)."""
        _init()
        try:
            return auth.create_user(email=email, password=senha, display_name=nome, email_verified=True).uid
        except auth.EmailAlreadyExistsError:
            raise EmailJaExiste()

    def delete_user(self, uid: str) -> None:
        _init()
        auth.delete_user(uid)


def firestore_client():
    _init()
    return firestore.client()

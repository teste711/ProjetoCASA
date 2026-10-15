import hashlib
import secrets


def novo_token_dispositivo() -> tuple[str, str]:
    t = "casa_" + secrets.token_urlsafe(32)
    return t, hash_token(t)


def hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()

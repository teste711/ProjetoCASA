import hashlib
import secrets


def novo_token_dispositivo() -> tuple[str, str]:
    t = "casa_" + secrets.token_urlsafe(32)
    return t, hash_token(t)


def hash_token(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()


def gerar_codigo() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_codigo(email: str, codigo: str) -> str:
    """HMAC com segredo do servidor: o código nunca fica gravado em texto puro."""
    import hmac
    from .config import settings
    return hmac.new(settings.secret_key.encode(), f"{email}:{codigo}".encode(), hashlib.sha256).hexdigest()


def codigo_confere(email: str, codigo: str, codigo_hash: str) -> bool:
    import hmac
    return hmac.compare_digest(hash_codigo(email, codigo), codigo_hash)

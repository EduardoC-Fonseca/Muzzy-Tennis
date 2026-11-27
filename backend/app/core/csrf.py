import hashlib
import hmac

from app.core.config import settings


def gerar_token_csrf(token_jwt: str) -> str:
    """Gera um token CSRF associado ao JWT da sessão."""

    return hmac.new(
        key=settings.jwt_secret_key.encode("utf-8"),
        msg=f"muzzi-csrf:{token_jwt}".encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()


def validar_token_csrf(token_jwt: str, token_csrf: str | None) -> bool:
    """Verifica se o token CSRF corresponde ao JWT informado."""

    if not token_csrf:
        return False

    token_esperado = gerar_token_csrf(token_jwt)

    return hmac.compare_digest(
        token_esperado,
        token_csrf,
    )

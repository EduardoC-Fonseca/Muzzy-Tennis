from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

_password_hash = PasswordHash.recommended()  # Argon2


def hash_senha(senha: str) -> str:
    return _password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str | None) -> bool:
    if not senha_hash:
        return False
    return _password_hash.verify(senha, senha_hash)


def criar_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    agora = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.access_token_expire_minutes),
        **(extra or {}),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decodificar_token(token: str) -> dict[str, Any]:
    """Decodifica e valida o JWT. Lança ``jwt.InvalidTokenError`` se inválido/expirado."""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

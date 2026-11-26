"""Dependências compartilhadas pelas rotas: sessão do banco e autenticação/autorização."""

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Request
from sqlalchemy.orm import Session

from app.core.exceptions import AcessoNegadoError, NaoAutenticadoError
from app.core.security import decodificar_token
from app.core.csrf import validar_token_csrf
from app.db.session import get_db
from app.models import PapelUsuario, Usuario

DbSession = Annotated[Session, Depends(get_db)]

def get_usuario_atual(db: DbSession, request: Request, token: Annotated[str | None, Cookie(alias="muzzi_session")] = None) -> Usuario:
    if not token:
        raise NaoAutenticadoError("Usuário não autenticado.")


oauth2_opcional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_prefix}/auth/login", auto_error=False
)


def _usuario_do_token(db: Session, token: str) -> Usuario:
    try:
        payload = decodificar_token(token)
        usuario_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise NaoAutenticadoError("Token inválido ou expirado.") from exc

    usuario = db.get(Usuario, usuario_id)

    if usuario is None:
        raise NaoAutenticadoError("Usuário não encontrado.")
    if not usuario.ativo:
        raise AcessoNegadoError("Conta desativada.", code="USUARIO_INATIVO")

    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        token_csrf = request.headers.get("X-CSRF-Token")

        if not validar_token_csrf(token, token_csrf):
            raise AcessoNegadoError("Token CSRF ausente ou inválido.", code="CSRF_INVALIDO")

    return usuario


def get_usuario_atual(db: DbSession, token: Annotated[str, Depends(oauth2_scheme)]) -> Usuario:
    return _usuario_do_token(db, token)


def get_usuario_opcional(
    db: DbSession, token: Annotated[str | None, Depends(oauth2_opcional)]
) -> Usuario | None:
    """Rotas públicas que mostram mais dados a quem está logado. Sem token: ``None``.
    Um token enviado, mas inválido, continua dando 401 (não é ignorado em silêncio)."""
    return _usuario_do_token(db, token) if token else None


UsuarioAtual = Annotated[Usuario, Depends(get_usuario_atual)]
UsuarioOpcional = Annotated[Usuario | None, Depends(get_usuario_opcional)]


def exigir_papel(*papeis: PapelUsuario) -> Callable[[Usuario], Usuario]:
    """Uso: ``Depends(exigir_papel(PapelUsuario.ADMINISTRADOR))``."""

    def _verificar(usuario: UsuarioAtual) -> Usuario:
        if usuario.papel not in papeis:
            raise AcessoNegadoError("Você não tem permissão para acessar este recurso.")
        return usuario

    return _verificar


AdminAtual = Annotated[Usuario, Depends(exigir_papel(PapelUsuario.ADMINISTRADOR))]
DonoQuadraAtual = Annotated[
    Usuario, Depends(exigir_papel(PapelUsuario.DONO_QUADRA, PapelUsuario.ADMINISTRADOR))
]

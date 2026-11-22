"""Dependências compartilhadas pelas rotas: sessão do banco e autenticação/autorização."""

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AcessoNegadoError, NaoAutenticadoError
from app.core.security import decodificar_token
from app.db.session import get_db
from app.models import PapelUsuario, Usuario

DbSession = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def get_usuario_atual(db: DbSession, token: Annotated[str, Depends(oauth2_scheme)]) -> Usuario:
    try:
        payload = decodificar_token(token)
        usuario_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise NaoAutenticadoError("Token inválido ou expirado.") from exc

    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise NaoAutenticadoError("Usuário não encontrado.")
    # CT17: usuário desativado perde acesso imediatamente, mesmo com token ainda válido.
    if not usuario.ativo:
        raise AcessoNegadoError("Conta desativada.", code="USUARIO_INATIVO")
    return usuario


UsuarioAtual = Annotated[Usuario, Depends(get_usuario_atual)]


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

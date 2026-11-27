"""Dependências compartilhadas pelas rotas: sessão do banco e autenticação/autorização.

O token JWT chega por um de dois caminhos:

- **Cookie HttpOnly** ``muzzi_session``, usado pelo front web. Como o navegador envia o
  cookie sozinho, as escritas (POST, PUT, PATCH, DELETE) exigem o cabeçalho ``X-CSRF-Token``.
- **Cabeçalho** ``Authorization: Bearer <token>``, usado pelo Swagger (botão *Authorize*),
  pelos testes e por clientes que não são navegador. Não há cookie envolvido, então não há
  risco de CSRF e o cabeçalho ``X-CSRF-Token`` não é exigido.

Se os dois vierem, vale o cabeçalho ``Authorization``.
"""

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.csrf import validar_token_csrf
from app.core.exceptions import AcessoNegadoError, NaoAutenticadoError
from app.core.security import decodificar_token
from app.db.session import get_db
from app.models import PapelUsuario, Usuario

DbSession = Annotated[Session, Depends(get_db)]

COOKIE_SESSAO = "muzzi_session"
_METODOS_DE_ESCRITA = frozenset({"POST", "PUT", "PATCH", "DELETE"})

# auto_error=False: a falta de token é tratada aqui, para responder no formato padrão
# ({"detail", "code": "NAO_AUTENTICADO"}) em vez do "Not authenticated" do FastAPI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login", auto_error=False)


def get_token_sessao(
    request: Request,
    bearer: Annotated[str | None, Depends(oauth2_scheme)],
    cookie: Annotated[str | None, Cookie(alias=COOKIE_SESSAO, include_in_schema=False)] = None,
) -> str | None:
    """Token da requisição (Bearer ou cookie). Pelo cookie, as escritas exigem CSRF."""
    if bearer:
        return bearer
    if not cookie:
        return None
    if request.method in _METODOS_DE_ESCRITA and not validar_token_csrf(
        cookie, request.headers.get("X-CSRF-Token")
    ):
        raise AcessoNegadoError("Token CSRF ausente ou inválido.", code="CSRF_INVALIDO")
    return cookie


TokenSessao = Annotated[str | None, Depends(get_token_sessao)]


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
    return usuario


def get_usuario_atual(db: DbSession, token: TokenSessao) -> Usuario:
    if not token:
        raise NaoAutenticadoError("Faça login para acessar este recurso.")
    return _usuario_do_token(db, token)


def get_usuario_opcional(db: DbSession, token: TokenSessao) -> Usuario | None:
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

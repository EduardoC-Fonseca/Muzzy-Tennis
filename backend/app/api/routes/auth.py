from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings
from app.core.csrf import gerar_token_csrf
from app.core.exceptions import AcessoNegadoError

from app.api.deps import DbSession, UsuarioAtual
from app.schemas.usuario import DonoRegistrar, UsuarioPublico
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post(
    "/registro",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastro público de dono de quadra",
)
def registrar(db: DbSession, dados: DonoRegistrar) -> UsuarioPublico:
    """Cria a conta do dono já ativa. Depois, o front faz login em ``/auth/login``.

    Erros: ``422 VALIDACAO`` (campos) e ``409 EMAIL_JA_CADASTRADO``.
    """
    return UsuarioPublico.model_validate(auth_service.registrar_dono(db, dados))

@router.post("/login", status_code=status.HTTP_204_NO_CONTENT, summary="Login de dono de quadra ou administrador")
def login(response: Response, request: Request, db: DbSession, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> None:
    """Autentica o usuário e define o JWT em cookie HttpOnly."""
    origem = request.headers.get("Origin")

    if origem not in settings.cors_origins:
        raise AcessoNegadoError(
            "Origem da requisição não permitida.",
            code="ORIGEM_NAO_PERMITIDA",
        )

    token = auth_service.autenticar(db, form.username, form.password)

    response.set_cookie(
        key="muzzi_session",
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/api/v1",
    )

    response.headers["X-CSRF-Token"] = gerar_token_csrf(token)
    response.headers["Cache-Control"] = "no-store"

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Encerrar sessão do usuário")
def logout(response: Response, usuario: UsuarioAtual) -> None:
    """Encerra a sessão removendo o cookie de autenticação."""

    response.delete_cookie(
        key="muzzi_session",
        path="/api/v1",
        secure=settings.environment == "production",
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"


@router.get("/me", response_model=UsuarioPublico, summary="Usuário autenticado")
def me(usuario: UsuarioAtual) -> UsuarioPublico:
    return UsuarioPublico.model_validate(usuario)


@router.get("/csrf", summary="Recuperar token CSRF da sessão autenticada")
def obter_csrf(
    usuario: UsuarioAtual,
    request: Request,
    response: Response,
) -> dict[str, str]:
    """Retorna o token CSRF associado à sessão autenticada."""

    token_jwt = request.cookies["muzzi_session"]
    response.headers["Cache-Control"] = "no-store"
    return {
        "csrf_token": gerar_token_csrf(token_jwt),
    }


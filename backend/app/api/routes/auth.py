from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import COOKIE_SESSAO, DbSession, TokenSessao, UsuarioAtual
from app.core.config import settings
from app.core.csrf import gerar_token_csrf
from app.core.exceptions import AcessoNegadoError
from app.schemas.auth import Token
from app.schemas.usuario import DonoRegistrar, UsuarioPublico
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _origem_permitida(request: Request) -> bool:
    """Sem ``Origin`` (Swagger em alguns navegadores, testes, apps) ou mesma origem da API:
    permitido. Navegador em outra origem: só as liberadas em ``CORS_ORIGINS``."""
    origem = request.headers.get("Origin")
    if origem is None:
        return True
    mesma_origem = f"{request.url.scheme}://{request.headers.get('host', '')}"
    return origem == mesma_origem or origem in settings.cors_origins


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


@router.post("/login", response_model=Token, summary="Login de dono de quadra ou administrador")
def login(
    response: Response,
    request: Request,
    db: DbSession,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Recebe ``username`` (e-mail) e ``password`` como form-data (padrão OAuth2).

    Define o JWT no cookie HttpOnly ``muzzi_session`` (front web) e devolve o token CSRF
    no cabeçalho ``X-CSRF-Token``. O mesmo JWT vem no corpo, para uso como
    ``Authorization: Bearer`` (Swagger, testes e clientes que não são navegador).
    """
    if not _origem_permitida(request):
        raise AcessoNegadoError("Origem da requisição não permitida.", code="ORIGEM_NAO_PERMITIDA")

    token = auth_service.autenticar(db, form.username, form.password)

    response.set_cookie(
        key=COOKIE_SESSAO,
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path=settings.api_prefix,
    )
    response.headers["X-CSRF-Token"] = gerar_token_csrf(token)
    response.headers["Cache-Control"] = "no-store"
    return Token(access_token=token)


@router.post(
    "/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Encerrar sessão do usuário"
)
def logout(response: Response, usuario: UsuarioAtual) -> None:
    """Encerra a sessão removendo o cookie de autenticação."""
    response.delete_cookie(
        key=COOKIE_SESSAO,
        path=settings.api_prefix,
        secure=settings.environment == "production",
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"


@router.get("/me", response_model=UsuarioPublico, summary="Usuário autenticado")
def me(usuario: UsuarioAtual) -> UsuarioPublico:
    return UsuarioPublico.model_validate(usuario)


@router.get("/csrf", summary="Recuperar token CSRF da sessão autenticada")
def obter_csrf(usuario: UsuarioAtual, token: TokenSessao, response: Response) -> dict[str, str]:
    """Retorna o token CSRF associado à sessão autenticada (exigido nas escritas via cookie)."""
    response.headers["Cache-Control"] = "no-store"
    return {"csrf_token": gerar_token_csrf(token or "")}

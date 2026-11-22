from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession, UsuarioAtual
from app.schemas.auth import Token
from app.schemas.usuario import UsuarioPublico
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token, summary="Login de dono de quadra ou administrador")
def login(db: DbSession, form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Recebe ``username`` (e-mail) e ``password`` como form-data (padrão OAuth2)."""
    return Token(access_token=auth_service.autenticar(db, form.username, form.password))


@router.get("/me", response_model=UsuarioPublico, summary="Usuário autenticado")
def me(usuario: UsuarioAtual) -> UsuarioPublico:
    return UsuarioPublico.model_validate(usuario)

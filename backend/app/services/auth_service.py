from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AcessoNegadoError, ConflitoError, NaoAutenticadoError
from app.core.security import criar_access_token, hash_senha, verificar_senha
from app.models import PapelUsuario, Usuario
from app.schemas.usuario import DonoRegistrar

EMAIL_JA_CADASTRADO = "E-mail já cadastrado."


def autenticar(db: Session, email: str, senha: str) -> str:
    """Valida credenciais e devolve um JWT. Usado por donos de quadra e administradores."""
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        raise NaoAutenticadoError("E-mail ou senha inválidos.", code="CREDENCIAIS_INVALIDAS")
    if not usuario.ativo:
        raise AcessoNegadoError("Conta desativada.", code="USUARIO_INATIVO")
    return criar_access_token(usuario.id, {"papel": usuario.papel.value})


def registrar_dono(db: Session, dados: DonoRegistrar) -> Usuario:
    """Cadastro público de dono de quadra (P03): conta ativa na hora, sem aprovação.

    O papel é sempre ``dono_quadra``; administradores só são criados por script. Um e-mail já
    usado (inclusive por um cliente que reservou sem login) devolve 409 EMAIL_JA_CADASTRADO.
    """
    if db.scalar(select(Usuario.id).where(Usuario.email == dados.email)) is not None:
        raise ConflitoError(EMAIL_JA_CADASTRADO, code="EMAIL_JA_CADASTRADO")

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        telefone=dados.telefone,
        senha_hash=hash_senha(dados.senha),
        papel=PapelUsuario.DONO_QUADRA,
        status=True,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError:  # dois cadastros simultâneos com o mesmo e-mail
        db.rollback()
        raise ConflitoError(EMAIL_JA_CADASTRADO, code="EMAIL_JA_CADASTRADO") from None
    db.refresh(usuario)
    return usuario

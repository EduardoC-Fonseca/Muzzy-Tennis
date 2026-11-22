from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AcessoNegadoError, NaoAutenticadoError
from app.core.security import criar_access_token, verificar_senha
from app.models import Usuario


def autenticar(db: Session, email: str, senha: str) -> str:
    """Valida credenciais e devolve um JWT. Usado por donos de quadra e administradores."""
    usuario = db.scalar(select(Usuario).where(Usuario.email == email.strip().lower()))
    if usuario is None or not verificar_senha(senha, usuario.senha_hash):
        raise NaoAutenticadoError("E-mail ou senha inválidos.", code="CREDENCIAIS_INVALIDAS")
    if not usuario.ativo:
        raise AcessoNegadoError("Conta desativada.", code="USUARIO_INATIVO")
    return criar_access_token(usuario.id, {"papel": usuario.papel.value})

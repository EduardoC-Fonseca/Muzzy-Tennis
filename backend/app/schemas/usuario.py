import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import PapelUsuario
from app.schemas.common import DataHoraUTC


class UsuarioPublico(BaseModel):
    """Dados do usuário expostos pela API (nunca inclui senha_hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str  # já validado na entrada; saída não revalida
    telefone: str | None
    papel: PapelUsuario
    status: bool  # True = ativo
    criado_em: DataHoraUTC


SENHA_MIN = 8
SENHA_MAX = 128
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class DonoRegistrar(BaseModel):
    """Corpo de POST /auth/registro: cadastro público de dono de quadra (P03).

    A confirmação de senha é responsabilidade da tela; a API recebe a senha uma vez.
    """

    model_config = ConfigDict(extra="forbid")

    nome: str = Field(min_length=1, max_length=150)
    email: str = Field(max_length=150)
    telefone: str | None = Field(default=None, max_length=20)
    senha: str = Field(min_length=SENHA_MIN, max_length=SENHA_MAX)

    @field_validator("nome")
    @classmethod
    def _nome(cls, v: str) -> str:
        v = " ".join(v.split())
        if not v:
            raise ValueError("Informe o nome.")
        return v

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL.match(v):
            raise ValueError("E-mail inválido.")
        return v

    @field_validator("telefone")
    @classmethod
    def _telefone(cls, v: str | None) -> str | None:
        v = (v or "").strip()
        if not v:
            return None
        digitos = re.sub(r"\D", "", v)
        if not re.fullmatch(r"[\d\s()+\-]+", v) or not 10 <= len(digitos) <= 13:
            raise ValueError("Telefone inválido. Informe DDD e número, ex.: (31) 99999-9999.")
        return v

    @field_validator("senha")
    @classmethod
    def _senha(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("A senha não pode conter apenas espaços.")
        return v

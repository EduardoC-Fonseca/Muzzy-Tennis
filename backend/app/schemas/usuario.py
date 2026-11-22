from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import PapelUsuario


class UsuarioPublico(BaseModel):
    """Dados do usuário expostos pela API (nunca inclui senha_hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str  # já validado na entrada; saída não revalida
    telefone: str | None
    papel: PapelUsuario
    status: bool  # True = ativo
    criado_em: datetime

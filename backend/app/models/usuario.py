from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import PapelUsuario, db_enum

if TYPE_CHECKING:
    from app.models.avaliacao import Avaliacao
    from app.models.quadra import Quadra
    from app.models.reserva import Reserva


class Usuario(TimestampMixin, Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    # Anulável: clientes reservam sem cadastro/login (decisão D1 em docs/db/modelo_dados.md).
    senha_hash: Mapped[str | None] = mapped_column(String(255))
    telefone: Mapped[str | None] = mapped_column(String(20))
    papel: Mapped[PapelUsuario] = mapped_column(
        db_enum(PapelUsuario, "papel_usuario"), nullable=False
    )
    # True = conta ativa; False = desativada pelo administrador (CT17/CT18).
    status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
    data_desativacao: Mapped[datetime | None] = mapped_column(DateTime)

    quadras: Mapped[list[Quadra]] = relationship(back_populates="dono")
    reservas: Mapped[list[Reserva]] = relationship(back_populates="cliente")
    avaliacoes: Mapped[list[Avaliacao]] = relationship(back_populates="cliente")

    @property
    def ativo(self) -> bool:
        return self.status

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email!r} papel={self.papel}>"

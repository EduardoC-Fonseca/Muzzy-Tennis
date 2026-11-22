from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CriadoEmMixin

if TYPE_CHECKING:
    from app.models.quadra import Quadra


class FotoQuadra(CriadoEmMixin, Base):
    __tablename__ = "fotos_quadra"

    id: Mapped[int] = mapped_column(primary_key=True)
    quadra_id: Mapped[int] = mapped_column(
        ForeignKey("quadras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    nome_arquivo: Mapped[str | None] = mapped_column(String(255))
    tipo_arquivo: Mapped[str | None] = mapped_column(String(50))
    tamanho_bytes: Mapped[int | None] = mapped_column(Integer)
    principal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    quadra: Mapped[Quadra] = relationship(back_populates="fotos")

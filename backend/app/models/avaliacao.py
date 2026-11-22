from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CriadoEmMixin

if TYPE_CHECKING:
    from app.models.quadra import Quadra
    from app.models.reserva import Reserva
    from app.models.usuario import Usuario

NOTA_MIN, NOTA_MAX = 1, 5
COMENTARIO_MAX = 300


class Avaliacao(CriadoEmMixin, Base):
    __tablename__ = "avaliacoes"
    __table_args__ = (
        CheckConstraint(f"nota BETWEEN {NOTA_MIN} AND {NOTA_MAX}", name="nota_entre_1_e_5"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Uma avaliação por reserva.
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.id"), nullable=False, unique=True)
    quadra_id: Mapped[int] = mapped_column(ForeignKey("quadras.id"), nullable=False, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    nota: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comentario: Mapped[str | None] = mapped_column(String(COMENTARIO_MAX))

    reserva: Mapped[Reserva] = relationship(back_populates="avaliacao")
    quadra: Mapped[Quadra] = relationship(back_populates="avaliacoes")
    cliente: Mapped[Usuario] = relationship(back_populates="avaliacoes")

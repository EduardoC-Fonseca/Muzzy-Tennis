from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import StatusHorario, db_enum

if TYPE_CHECKING:
    from app.models.quadra import Quadra
    from app.models.reserva import Reserva


class HorarioQuadra(TimestampMixin, Base):
    """Slot de horário que o dono disponibiliza para reserva."""

    __tablename__ = "horarios_quadra"
    __table_args__ = (
        # Impede dois slots iguais na mesma quadra (decisão D3 / RNF01).
        UniqueConstraint("quadra_id", "data", "hora_inicio"),
        CheckConstraint("hora_fim > hora_inicio", name="intervalo_valido"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quadra_id: Mapped[int] = mapped_column(
        ForeignKey("quadras.id", ondelete="CASCADE"), nullable=False
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fim: Mapped[time] = mapped_column(Time, nullable=False)
    # Opcional: quando nulo, vale quadras.preco_hora.
    preco: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    status: Mapped[StatusHorario] = mapped_column(
        db_enum(StatusHorario, "status_horario"),
        nullable=False,
        default=StatusHorario.DISPONIVEL,
    )

    quadra: Mapped[Quadra] = relationship(back_populates="horarios")
    reservas: Mapped[list[Reserva]] = relationship(back_populates="horario")

    @property
    def preco_efetivo(self) -> Decimal:
        """Preço cobrado do cliente: o do horário ou, se nulo, o da quadra."""
        return self.preco if self.preco is not None else self.quadra.preco_hora

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import StatusReserva, db_enum

if TYPE_CHECKING:
    from app.models.avaliacao import Avaliacao
    from app.models.cancelamento import Cancelamento
    from app.models.horario_quadra import HorarioQuadra
    from app.models.pagamento import Pagamento
    from app.models.quadra import Quadra
    from app.models.usuario import Usuario


class Reserva(TimestampMixin, Base):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("quantidade_jogadores > 0", name="quantidade_jogadores_positiva"),
        # Suporta a busca de reservas pendentes vencidas (expiração após 1 hora, CT03).
        Index("ix_reservas_status_expira_em", "status", "expira_em"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    quadra_id: Mapped[int] = mapped_column(ForeignKey("quadras.id"), nullable=False, index=True)
    horario_id: Mapped[int] = mapped_column(
        ForeignKey("horarios_quadra.id"), nullable=False, index=True
    )
    quantidade_jogadores: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[StatusReserva] = mapped_column(
        db_enum(StatusReserva, "status_reserva"),
        nullable=False,
        default=StatusReserva.AGUARDANDO_PAGAMENTO,
    )
    expira_em: Mapped[datetime | None] = mapped_column(DateTime)
    confirmada_em: Mapped[datetime | None] = mapped_column(DateTime)
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime)
    observacoes: Mapped[str | None] = mapped_column(String(300))

    cliente: Mapped[Usuario] = relationship(back_populates="reservas")
    quadra: Mapped[Quadra] = relationship(back_populates="reservas")
    horario: Mapped[HorarioQuadra] = relationship(back_populates="reservas")
    pagamentos: Mapped[list[Pagamento]] = relationship(back_populates="reserva")
    cancelamento: Mapped[Cancelamento | None] = relationship(back_populates="reserva")
    avaliacao: Mapped[Avaliacao | None] = relationship(back_populates="reserva")

    def __repr__(self) -> str:
        return f"<Reserva id={self.id} codigo={self.codigo!r} status={self.status}>"

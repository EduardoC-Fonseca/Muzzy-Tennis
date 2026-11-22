from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import MetodoPagamento, StatusPagamento, db_enum

if TYPE_CHECKING:
    from app.models.estorno import Estorno
    from app.models.reserva import Reserva


class Pagamento(TimestampMixin, Base):
    """Pagamento da garantia da reserva, processado por serviço externo."""

    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.id"), nullable=False, index=True)
    metodo: Mapped[MetodoPagamento] = mapped_column(
        db_enum(MetodoPagamento, "metodo_pagamento"), nullable=False
    )
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[StatusPagamento] = mapped_column(
        db_enum(StatusPagamento, "status_pagamento"),
        nullable=False,
        default=StatusPagamento.PENDENTE,
    )
    codigo_transacao: Mapped[str | None] = mapped_column(String(100), unique=True)
    pago_em: Mapped[datetime | None] = mapped_column(DateTime)

    reserva: Mapped[Reserva] = relationship(back_populates="pagamentos")
    estornos: Mapped[list[Estorno]] = relationship(back_populates="pagamento")

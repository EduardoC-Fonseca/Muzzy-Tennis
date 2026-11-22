from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utcnow

if TYPE_CHECKING:
    from app.models.estorno import Estorno
    from app.models.reserva import Reserva
    from app.models.usuario import Usuario


class Cancelamento(Base):
    __tablename__ = "cancelamentos"
    __table_args__ = (
        CheckConstraint(
            "percentual_estorno >= 0 AND percentual_estorno <= 100",
            name="percentual_estorno_valido",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[int] = mapped_column(ForeignKey("reservas.id"), nullable=False, unique=True)
    # Quem cancelou: o papel do usuário indica se foi cliente, dono ou administrador.
    # Nulo = cancelamento automático pelo sistema (expiração após 1 hora, CT03). Decisão D2.
    cancelado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), index=True)
    motivo: Mapped[str | None] = mapped_column(String(300))
    dentro_regra_24h: Mapped[bool] = mapped_column(Boolean, nullable=False)
    percentual_estorno: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    cancelado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    reserva: Mapped[Reserva] = relationship(back_populates="cancelamento")
    cancelado_por: Mapped[Usuario | None] = relationship()
    estornos: Mapped[list[Estorno]] = relationship(back_populates="cancelamento")

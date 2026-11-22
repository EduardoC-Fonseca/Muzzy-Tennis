from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, utcnow
from app.models.enums import StatusEstorno, db_enum

if TYPE_CHECKING:
    from app.models.cancelamento import Cancelamento
    from app.models.pagamento import Pagamento


class Estorno(Base):
    __tablename__ = "estornos"

    id: Mapped[int] = mapped_column(primary_key=True)
    pagamento_id: Mapped[int] = mapped_column(
        ForeignKey("pagamentos.id"), nullable=False, index=True
    )
    cancelamento_id: Mapped[int] = mapped_column(
        ForeignKey("cancelamentos.id"), nullable=False, index=True
    )
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[StatusEstorno] = mapped_column(
        db_enum(StatusEstorno, "status_estorno"),
        nullable=False,
        default=StatusEstorno.PENDENTE,
    )
    codigo_transacao: Mapped[str | None] = mapped_column(String(100))
    solicitado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    processado_em: Mapped[datetime | None] = mapped_column(DateTime)

    pagamento: Mapped[Pagamento] = relationship(back_populates="estornos")
    cancelamento: Mapped[Cancelamento] = relationship(back_populates="estornos")

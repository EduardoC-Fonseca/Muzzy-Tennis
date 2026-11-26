from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CHAR, Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import TipoPiso, db_enum

if TYPE_CHECKING:
    from app.models.avaliacao import Avaliacao
    from app.models.foto_quadra import FotoQuadra
    from app.models.horario_quadra import HorarioQuadra
    from app.models.reserva import Reserva
    from app.models.usuario import Usuario

DESCRICAO_MAX = 500


class Quadra(TimestampMixin, Base):
    __tablename__ = "quadras"
    __table_args__ = (
        CheckConstraint("limite_jogadores > 0", name="limite_jogadores_positivo"),
        CheckConstraint("preco_hora >= 0", name="preco_hora_nao_negativo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    dono_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(String(DESCRICAO_MAX), nullable=False)
    tipo_piso: Mapped[TipoPiso] = mapped_column(db_enum(TipoPiso, "tipo_piso"), nullable=False)
    coberta: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    limite_jogadores: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_hora: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)
    numero: Mapped[str | None] = mapped_column(String(20))
    bairro: Mapped[str] = mapped_column(String(100), nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    estado: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    cep: Mapped[str] = mapped_column(String(9), nullable=False)
    ativa: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    dono: Mapped[Usuario] = relationship(back_populates="quadras")
    fotos: Mapped[list[FotoQuadra]] = relationship(
        back_populates="quadra", cascade="all, delete-orphan", order_by="FotoQuadra.ordem"
    )
    horarios: Mapped[list[HorarioQuadra]] = relationship(
        back_populates="quadra", cascade="all, delete-orphan"
    )
    reservas: Mapped[list[Reserva]] = relationship(back_populates="quadra")
    avaliacoes: Mapped[list[Avaliacao]] = relationship(back_populates="quadra")

    @property
    def foto_principal_url(self) -> str | None:
        """URL da foto principal (ou da primeira, por segurança). Exige ``fotos`` carregado."""
        principal = next((f for f in self.fotos if f.principal), None)
        foto = principal or (self.fotos[0] if self.fotos else None)
        return foto.url if foto else None

    def __repr__(self) -> str:
        return f"<Quadra id={self.id} nome={self.nome!r}>"

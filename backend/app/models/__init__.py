"""Modelos ORM. Importar este pacote registra todas as tabelas em ``Base.metadata``
(necessário para o autogenerate do Alembic)."""

from app.db.base import Base
from app.models.avaliacao import Avaliacao
from app.models.cancelamento import Cancelamento
from app.models.enums import (
    MetodoPagamento,
    PapelUsuario,
    StatusEstorno,
    StatusHorario,
    StatusPagamento,
    StatusReserva,
    TipoPiso,
)
from app.models.estorno import Estorno
from app.models.foto_quadra import FotoQuadra
from app.models.horario_quadra import HorarioQuadra
from app.models.pagamento import Pagamento
from app.models.quadra import Quadra
from app.models.reserva import Reserva
from app.models.usuario import Usuario

__all__ = [
    "Avaliacao",
    "Base",
    "Cancelamento",
    "Estorno",
    "FotoQuadra",
    "HorarioQuadra",
    "MetodoPagamento",
    "Pagamento",
    "PapelUsuario",
    "Quadra",
    "Reserva",
    "StatusEstorno",
    "StatusHorario",
    "StatusPagamento",
    "StatusReserva",
    "TipoPiso",
    "Usuario",
]

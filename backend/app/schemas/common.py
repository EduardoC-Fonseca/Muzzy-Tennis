from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, PlainSerializer

T = TypeVar("T")

# Valores monetários: entrada aceita número ou texto ("80" / "80.00"); a saída JSON é sempre
# número (ex.: 95.5). Facilita o consumo no Flutter (double).
Dinheiro = Annotated[
    Decimal,
    PlainSerializer(lambda v: float(v), return_type=float, when_used="json"),
]


def _iso_utc(valor: datetime) -> str:
    if valor.tzinfo is None:  # o banco guarda UTC sem fuso (app.db.base.utcnow)
        valor = valor.replace(tzinfo=UTC)
    return valor.astimezone(UTC).isoformat().replace("+00:00", "Z")


# Datas/horas: saída JSON em ISO 8601 UTC com sufixo "Z" (ex.: 2026-11-23T23:03:57.621568Z).
DataHoraUTC = Annotated[datetime, PlainSerializer(_iso_utc, return_type=str, when_used="json")]


class Pagina(BaseModel, Generic[T]):  # noqa: UP046 (Pydantic genérico)
    """Envelope das listagens paginadas."""

    itens: list[T]
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int

    @classmethod
    def montar(cls, itens: list[T], total: int, pagina: int, por_pagina: int) -> "Pagina[T]":
        return cls(
            itens=itens,
            total=total,
            pagina=pagina,
            por_pagina=por_pagina,
            total_paginas=(total + por_pagina - 1) // por_pagina,
        )

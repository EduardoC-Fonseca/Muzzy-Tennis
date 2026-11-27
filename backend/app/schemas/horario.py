"""Contratos dos horários das quadras (tarefa 20 — HU04, CT12)."""

import enum
from datetime import date, time
from decimal import Decimal
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    ValidationInfo,
    field_validator,
    model_validator,
)

from app.core.config import settings
from app.core.tempo import hoje_local
from app.models.enums import StatusHorario
from app.schemas.common import Dinheiro

# Horas trafegam como "HH:MM" (entrada aceita "HH:MM" ou "HH:MM:SS"; os segundos são ignorados).
Hora = Annotated[time, PlainSerializer(lambda t: t.strftime("%H:%M"), return_type=str)]

PrecoOpcional = Annotated[
    Decimal | None, Field(default=None, gt=0, max_digits=10, decimal_places=2)
]


def _sem_segundos(valor: time) -> time:
    return valor.replace(second=0, microsecond=0, tzinfo=None)


class HorariosGerar(BaseModel):
    """Corpo de POST /quadras/{id}/horarios: gera horários de 1 hora em lote.

    Para cada data entre ``data_inicio`` e ``data_fim`` cujo dia da semana esteja em
    ``dias_semana``, cria horários consecutivos de ``hora_abertura`` até ``hora_fechamento``.
    """

    model_config = ConfigDict(extra="forbid")

    data_inicio: date
    data_fim: date
    # ISO 8601, igual ao DateTime.weekday do Dart: 1 = segunda ... 7 = domingo.
    dias_semana: list[Annotated[int, Field(ge=1, le=7)]] | None = Field(
        default=None, min_length=1, description="1 = segunda ... 7 = domingo; omitir = todos"
    )
    hora_abertura: Hora
    hora_fechamento: Hora
    preco: PrecoOpcional = None

    @field_validator("hora_abertura", "hora_fechamento", mode="after")
    @classmethod
    def _truncar(cls, v: time) -> time:
        return _sem_segundos(v)

    @field_validator("data_inicio")
    @classmethod
    def _nao_no_passado(cls, v: date) -> date:
        if v < hoje_local():
            raise ValueError("A data inicial não pode estar no passado.")
        return v

    @field_validator("data_fim")
    @classmethod
    def _periodo(cls, v: date, info: ValidationInfo) -> date:
        inicio = info.data.get("data_inicio")
        if inicio is None:
            return v
        if v < inicio:
            raise ValueError("A data final deve ser igual ou posterior à inicial.")
        maximo = settings.horarios_max_dias_por_operacao
        if (v - inicio).days + 1 > maximo:
            raise ValueError(f"O período pode ter no máximo {maximo} dias.")
        return v

    @field_validator("dias_semana")
    @classmethod
    def _dias_unicos(cls, v: list[int] | None) -> list[int] | None:
        return sorted(set(v)) if v else v

    @field_validator("hora_fechamento")
    @classmethod
    def _cabe_um_horario(cls, v: time, info: ValidationInfo) -> time:
        abertura = info.data.get("hora_abertura")
        if abertura is None:
            return v
        minutos = (v.hour * 60 + v.minute) - (abertura.hour * 60 + abertura.minute)
        if minutos < settings.duracao_slot_minutos:
            raise ValueError(
                f"Deve ser pelo menos {settings.duracao_slot_minutos} minutos depois da abertura."
            )
        return v


class StatusHorarioAlteravel(enum.StrEnum):
    """Status que o dono pode definir. ``reservado`` só é aplicado pelas reservas."""

    DISPONIVEL = StatusHorario.DISPONIVEL.value
    BLOQUEADO = StatusHorario.BLOQUEADO.value


class HorarioAtualizar(BaseModel):
    """Corpo de PATCH /quadras/{id}/horarios/{horario_id}. Envie só o que muda.

    ``preco: null`` volta a usar o preço da quadra.
    """

    model_config = ConfigDict(extra="forbid")

    # Sem "| None": omitir mantém o status; enviar null é rejeitado como valor inválido.
    status: StatusHorarioAlteravel = None  # type: ignore[assignment]
    preco: PrecoOpcional = None

    @model_validator(mode="after")
    def _algum_campo(self) -> "HorarioAtualizar":
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo: status ou preco.")
        return self


class HorarioPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quadra_id: int
    data: date
    hora_inicio: Hora
    hora_fim: Hora
    preco: Dinheiro | None  # preço próprio do horário (null = usa o da quadra)
    preco_efetivo: Dinheiro  # o que o cliente paga: preco ou quadras.preco_hora
    status: StatusHorario


class HorarioIgnorado(BaseModel):
    data: date
    hora_inicio: Hora
    hora_fim: Hora
    code: str
    motivo: str


class HorariosGerados(BaseModel):
    criados: list[HorarioPublico]
    ignorados: list[HorarioIgnorado]

"""Enums do modelo de dados (docs/db/modelo_dados.md)."""

import enum

from sqlalchemy import Enum as SAEnum


class PapelUsuario(enum.StrEnum):
    CLIENTE = "cliente"
    DONO_QUADRA = "dono_quadra"
    ADMINISTRADOR = "administrador"


class StatusHorario(enum.StrEnum):
    DISPONIVEL = "disponivel"
    RESERVADO = "reservado"
    BLOQUEADO = "bloqueado"


class StatusReserva(enum.StrEnum):
    AGUARDANDO_PAGAMENTO = "aguardando_pagamento"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    EXPIRADA = "expirada"
    CONCLUIDA = "concluida"


class StatusPagamento(enum.StrEnum):
    PENDENTE = "pendente"
    PAGO = "pago"
    FALHOU = "falhou"
    ESTORNADO = "estornado"
    ESTORNADO_PARCIALMENTE = "estornado_parcialmente"


class MetodoPagamento(enum.StrEnum):
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"


class StatusEstorno(enum.StrEnum):
    PENDENTE = "pendente"
    PROCESSADO = "processado"
    RECUSADO = "recusado"


class TipoPiso(enum.StrEnum):
    SAIBRO = "saibro"
    RAPIDA = "rapida"
    GRAMA = "grama"
    SINTETICO = "sintetico"


def db_enum(enum_cls: type[enum.Enum], name: str) -> SAEnum:
    """Coluna ENUM que grava o *valor* (ex.: 'dono_quadra'), e não o nome do membro."""
    return SAEnum(
        enum_cls,
        name=name,
        values_callable=lambda cls: [member.value for member in cls],
        validate_strings=True,
    )

from datetime import UTC, datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Convenção de nomes para constraints: deixa as migrações do Alembic determinísticas e
# legíveis (ex.: fk_reservas_quadra_id_quadras, uq_usuarios_email).
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def utcnow() -> datetime:
    """Momento atual em UTC, sem tzinfo (o MySQL DATETIME não guarda fuso).

    Convenção do projeto: todos os timestamps no banco estão em UTC.
    """
    return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class CriadoEmMixin:
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, server_default=func.now(), sort_order=100
    )


class TimestampMixin(CriadoEmMixin):
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        sort_order=101,
    )

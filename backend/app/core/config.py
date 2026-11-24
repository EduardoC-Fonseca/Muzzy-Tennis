from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy.engine import URL

DEFAULT_JWT_SECRET = "dev-inseguro-troque-esta-chave-em-producao"


class Settings(BaseSettings):
    """Configurações lidas de variáveis de ambiente / arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Muzzi Tennis API"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # DATABASE_URL completa, se definida, tem prioridade sobre as variáveis DB_*.
    database_url_override: str | None = Field(default=None, validation_alias="DATABASE_URL")
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "muzzi"
    db_password: str = "muzzi"
    db_name: str = "muzzi_tennis"

    jwt_secret_key: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: Annotated[list[str], NoDecode] = []

    reserva_prazo_pagamento_minutos: int = 60
    cancelamento_antecedencia_horas: int = 24
    estorno_percentual_dentro_prazo: int = 100  # P04
    duracao_slot_minutos: int = 60  # P07: horários de 1 hora
    limite_reservas_dia_cliente: int = 2  # P07: máx. 2 reservas por dia por cliente

    upload_dir: str = "uploads"
    upload_max_bytes: int = 5 * 1024 * 1024
    fotos_max_por_quadra: int = 10

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def _exigir_segredo_em_producao(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret_key == DEFAULT_JWT_SECRET:
            raise ValueError("Defina JWT_SECRET_KEY antes de rodar em produção.")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return URL.create(
            "mysql+pymysql",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

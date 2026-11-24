import re
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import TipoPiso
from app.models.quadra import DESCRICAO_MAX
from app.schemas.common import DataHoraUTC, Dinheiro

# fmt: off
UFS = frozenset({
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
})
# fmt: on
_CEP = re.compile(r"^\d{5}-?\d{3}$")


class QuadraCriar(BaseModel):
    """Corpo de POST /quadras (tarefa 12 / HU03 / CT07, CT08, CT10)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    nome: str = Field(min_length=1, max_length=150)
    descricao: str = Field(min_length=1, max_length=DESCRICAO_MAX)
    tipo_piso: TipoPiso
    coberta: bool = False
    limite_jogadores: int = Field(gt=0)
    preco_hora: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    endereco: str = Field(min_length=1, max_length=255)
    numero: str | None = Field(default=None, max_length=20)
    bairro: str = Field(min_length=1, max_length=100)
    cidade: str = Field(min_length=1, max_length=100)
    estado: str = Field(min_length=2, max_length=2)
    cep: str

    @field_validator("numero")
    @classmethod
    def _numero_vazio_vira_nulo(cls, v: str | None) -> str | None:
        return v or None

    @field_validator("estado")
    @classmethod
    def _validar_uf(cls, v: str) -> str:
        uf = v.upper()
        if uf not in UFS:
            raise ValueError("UF inválida. Use a sigla do estado, ex.: MG.")
        return uf

    @field_validator("cep")
    @classmethod
    def _normalizar_cep(cls, v: str) -> str:
        if not _CEP.match(v):
            raise ValueError("CEP inválido. Use o formato 00000-000.")
        digitos = v.replace("-", "")
        return f"{digitos[:5]}-{digitos[5:]}"


class FotoQuadraPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    nome_arquivo: str | None
    tipo_arquivo: str | None
    tamanho_bytes: int | None
    principal: bool
    ordem: int


class QuadraPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dono_id: int
    nome: str
    descricao: str
    tipo_piso: TipoPiso
    coberta: bool
    limite_jogadores: int
    preco_hora: Dinheiro
    endereco: str
    numero: str | None
    bairro: str
    cidade: str
    estado: str
    cep: str
    ativa: bool
    fotos: list[FotoQuadraPublica]
    criado_em: DataHoraUTC
    atualizado_em: DataHoraUTC


class FotoRejeitada(BaseModel):
    nome_arquivo: str
    code: str
    motivo: str


class UploadFotosResposta(BaseModel):
    fotos: list[FotoQuadraPublica]
    rejeitadas: list[FotoRejeitada]

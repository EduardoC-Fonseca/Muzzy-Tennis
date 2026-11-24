"""Erros de domínio e o formato padrão de erro da API.

Os serviços lançam subclasses de ``AppError`` (sem conhecer HTTP); os handlers registrados em
``app.main`` convertem para JSON no formato:

    {"detail": "mensagem legível", "code": "CODIGO_ESTAVEL", ...campos extras}

Erros de validação de entrada (CT08) seguem o mesmo formato, com a lista de campos:

    {"detail": "Dados inválidos.", "code": "VALIDACAO",
     "erros": [{"campo": "descricao", "mensagem": "Máximo de 500 caracteres."}]}

O campo ``code`` é estável e deve ser usado pelo front-end para decidir o que exibir
(mitigação do risco R4). Contrato completo: docs/integracao_frontend.md.
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "ERRO"

    def __init__(
        self, detail: str, *, code: str | None = None, extra: dict[str, Any] | None = None
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.extra = extra or {}
        if code:
            self.code = code


class NaoEncontradoError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NAO_ENCONTRADO"


class ConflitoError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "CONFLITO"


class RegraNegocioError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "REGRA_NEGOCIO"


class NaoAutenticadoError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "NAO_AUTENTICADO"


class AcessoNegadoError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "ACESSO_NEGADO"


# --- Tradução dos erros do Pydantic para mensagens em português -------------------------------

_MENSAGENS: dict[str, str] = {
    "missing": "Campo obrigatório.",
    "string_too_short": "Deve ter pelo menos {min_length} caractere(s).",
    "string_too_long": "Máximo de {max_length} caracteres.",
    "string_type": "Deve ser um texto.",
    "string_pattern_mismatch": "Formato inválido.",
    "int_parsing": "Deve ser um número inteiro.",
    "int_type": "Deve ser um número inteiro.",
    "int_from_float": "Deve ser um número inteiro.",
    "decimal_parsing": "Deve ser um número.",
    "decimal_type": "Deve ser um número.",
    "decimal_max_digits": "Número com dígitos demais.",
    "decimal_max_places": "Use no máximo {decimal_places} casas decimais.",
    "decimal_whole_digits": "Número com dígitos demais.",
    "greater_than": "Deve ser maior que {gt}.",
    "greater_than_equal": "Deve ser maior ou igual a {ge}.",
    "less_than": "Deve ser menor que {lt}.",
    "less_than_equal": "Deve ser menor ou igual a {le}.",
    "bool_parsing": "Deve ser verdadeiro ou falso.",
    "bool_type": "Deve ser verdadeiro ou falso.",
    "enum": "Valor inválido. Opções: {expected}.",
    "literal_error": "Valor inválido. Opções: {expected}.",
    "json_invalid": "JSON inválido.",
    "model_attributes_type": "Formato do corpo da requisição inválido.",
    "dict_type": "Formato do corpo da requisição inválido.",
    "extra_forbidden": "Campo não permitido.",
}


def _mensagem(erro: dict[str, Any]) -> str:
    tipo = erro.get("type", "")
    if tipo == "value_error":  # validadores próprios: a mensagem já está em português
        return str(erro.get("ctx", {}).get("error", erro.get("msg", "")))
    modelo = _MENSAGENS.get(tipo)
    if modelo is None:
        return erro.get("msg", "Valor inválido.")
    ctx = dict(erro.get("ctx", {}))
    if "expected" in ctx:  # "'a', 'b' or 'c'" -> "'a', 'b' ou 'c'"
        ctx["expected"] = str(ctx["expected"]).replace(" or ", " ou ")
    try:
        return modelo.format(**ctx)
    except (KeyError, IndexError):
        return erro.get("msg", "Valor inválido.")


def _campo(loc: tuple[Any, ...]) -> str:
    # Remove a origem ("body", "query", "path", "form") e junta o caminho: "fotos.0"
    partes = (
        [str(p) for p in loc[1:]]
        if loc and loc[0] in {"body", "query", "path", "form"}
        else [str(p) for p in loc]
    )
    return ".".join(partes) or "corpo"


def formatar_erros_validacao(erros: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [{"campo": _campo(tuple(e.get("loc", ()))), "mensagem": _mensagem(e)} for e in erros]


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, NaoAutenticadoError) else None
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({"detail": exc.detail, "code": exc.code, **exc.extra}),
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Dados inválidos.",
                "code": "VALIDACAO",
                "erros": formatar_erros_validacao(list(exc.errors())),
            },
        )

"""Erros de domínio e o formato padrão de erro da API.

Os serviços lançam subclasses de ``AppError`` (sem conhecer HTTP); o handler registrado em
``app.main`` converte para JSON no formato:

    {"detail": "mensagem legível", "code": "CODIGO_ESTAVEL"}

O campo ``code`` é estável e deve ser usado pelo front-end para decidir o que exibir
(mitigação do risco R4 — contrato de erros entre front e back).
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "ERRO"

    def __init__(self, detail: str, *, code: str | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        if code:
            self.code = code


class NaoEncontradoError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NAO_ENCONTRADO"


class ConflitoError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "CONFLITO"


class RegraNegocioError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "REGRA_NEGOCIO"


class NaoAutenticadoError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "NAO_AUTENTICADO"


class AcessoNegadoError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "ACESSO_NEGADO"


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, NaoAutenticadoError) else None
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
            headers=headers,
        )

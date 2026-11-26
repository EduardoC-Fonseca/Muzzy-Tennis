from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import registrar_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="API do Muzzi Tennis — reserva de quadras de tênis em João Monlevade.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_handlers(app)
    app.include_router(api_router, prefix=settings.api_prefix)

    # Fotos das quadras enviadas pelos donos (tarefa 12).
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

    app.openapi = lambda: _openapi_com_upload_de_arquivos(app)
    return app


def _marcar_binarios(no: object) -> None:
    """OpenAPI 3.1 descreve arquivos como ``contentMediaType: application/octet-stream``, mas o
    Swagger UI só mostra o seletor de arquivo para ``format: binary``. Sem isto, listas de
    arquivos (``list[UploadFile]``) aparecem como campos de texto."""
    if isinstance(no, dict):
        if no.get("type") == "string" and no.get("contentMediaType") == "application/octet-stream":
            no["format"] = "binary"
        for valor in no.values():
            _marcar_binarios(valor)
    elif isinstance(no, list):
        for valor in no:
            _marcar_binarios(valor)


def _openapi_com_upload_de_arquivos(app: FastAPI) -> dict:
    if app.openapi_schema is None:
        esquema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        _marcar_binarios(esquema)
        app.openapi_schema = esquema
    return app.openapi_schema


app = create_app()

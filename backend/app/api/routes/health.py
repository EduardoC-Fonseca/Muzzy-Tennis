from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DbSession

router = APIRouter(tags=["Saúde"])


@router.get("/health", summary="Verifica se a API e o banco estão respondendo")
def health(db: DbSession) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        banco = "ok"
    except SQLAlchemyError:
        banco = "indisponivel"
    return {"status": "ok", "banco": banco}

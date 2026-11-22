from fastapi import APIRouter

from app.api.routes import auth, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)

# Próximos módulos da EAP (docs/gerenciamento/cronograma.md):
#   quadras (12, 13) · horarios (20, 52) · reservas (14, 15, 16, 18, 49, 53)
#   estornos (54) · usuarios/admin (19, 21, 55) · avaliacoes (24, 25)

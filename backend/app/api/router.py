from fastapi import APIRouter

from app.api.routes import auth, health, horarios, quadras

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(quadras.router)
api_router.include_router(horarios.router)

# Próximos módulos da EAP (docs/gerenciamento/cronograma.md):
#   horarios: disponibilidade pública (52) · reservas (14, 15, 16, 18, 49, 53)
#   estornos (54) · usuarios/admin (19, 21, 55) · avaliacoes (24, 25)

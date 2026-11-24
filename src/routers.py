from fastapi import APIRouter

from src.atleta.controller import router as atleta_router
from src.categorias.controller import router as categorias_router
from src.centro_treinamento.controller import router as centro_treinamento_router

api_router = APIRouter()

api_router.include_router(
    atleta_router,
    prefix="/atletas",
    tags=["Atletas"],
)
api_router.include_router(
    categorias_router,
    prefix="/categorias",
    tags=["Categorias"],
)
api_router.include_router(
    centro_treinamento_router,
    prefix="/centros_treinamento",
    tags=["Centros de Treinamento"],
)

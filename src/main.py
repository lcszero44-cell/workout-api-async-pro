from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, status
from fastapi_pagination import add_pagination
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from src.configs.database import async_session, engine, init_db
from src.configs.seed import seed_database
from src.configs.settings import settings
from src.contrib.dependencies import DatabaseDependency
from src.contrib.exceptions import global_integrity_error_handler
from src.contrib.middleware import ObservabilityMiddleware
from src.routers import api_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Gerencia ciclo de vida da aplicação: inicialização do banco, auto-seed e shutdown."""
    await init_db()
    if settings.AUTO_SEED:
        async with async_session() as session:
            await seed_database(session)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API Assíncrona de Alta Concorrência para Competições de CrossFit — "
        "construída com FastAPI, SQLAlchemy 2.0 Async, Pydantic v2, Alembic e fastapi-pagination "
        "(Bootcamp Santander 2025 Python Back-End — DIO)."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middlewares de Observabilidade (X-Request-ID & X-Process-Time-Ms)
app.add_middleware(ObservabilityMiddleware)

# Tratamento global de fallback para violações de integridade
app.add_exception_handler(IntegrityError, global_integrity_error_handler)

# Registro das rotas de domínio
app.include_router(api_router)


@app.get(
    "/",
    tags=["Observabilidade"],
    summary="Informações da API e links rápidos",
    status_code=status.HTTP_200_OK,
)
async def root() -> dict[str, object]:
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database_backend": settings.database_backend,
        "links": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "atletas": "/atletas/",
            "categorias": "/categorias/",
            "centros_treinamento": "/centros_treinamento/",
        },
    }


@app.get(
    "/health",
    tags=["Observabilidade"],
    summary="Verificação de saúde da API e conectividade com o banco de dados",
    status_code=status.HTTP_200_OK,
)
async def health_check(db_session: DatabaseDependency) -> dict[str, str]:
    await db_session.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": settings.database_backend,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


# Paginação oficial (LimitOffsetPage -> limit & offset)
add_pagination(app)

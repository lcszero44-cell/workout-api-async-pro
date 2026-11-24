from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.configs.settings import settings
from src.contrib.models import BaseModel


def _build_engine():
    """Creates an AsyncEngine tuned for either SQLite (zero-config) or PostgreSQL (prod)."""
    if settings.is_sqlite:
        async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(async_engine.sync_engine, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return async_engine

    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


engine = _build_engine()

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Ensures all ORM tables exist (ideal for Zero-Config SQLite startup)."""
    # Import models so SQLAlchemy metadata registers every table before create_all
    import src.atleta.models  # noqa: F401
    import src.categorias.models  # noqa: F401
    import src.centro_treinamento.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI async dependency providing an isolated AsyncSession per request."""
    async with async_session() as session:
        yield session

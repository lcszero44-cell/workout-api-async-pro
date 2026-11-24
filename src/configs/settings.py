from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings powered by Pydantic v2 Settings."""

    APP_NAME: str = Field(default="Workout API Async Pro")
    APP_VERSION: str = Field(default="2.0.0")
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # Dual-Database Zero-Config: SQLite Async por padrão, PostgreSQL Async via env var
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./workout.db")
    AUTO_SEED: bool = Field(default=True)

    HOST: str = Field(default="127.0.0.1")
    PORT: int = Field(default=8000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def database_backend(self) -> str:
        return "SQLite Async (aiosqlite)" if self.is_sqlite else "PostgreSQL Async (asyncpg)"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

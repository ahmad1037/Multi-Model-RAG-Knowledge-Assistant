from functools import lru_cache
from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_env: str = "development"

    database_url: str = (
        "postgresql+psycopg://"
        "rag_user:rag_password@localhost:5432/rag_db"
    )

    frontend_origin: str = "http://localhost:5173"

    storage_root: Path = Path("../storage")

    max_upload_size_mb: int = 25

    model_config = SettingsConfigDict(
        env_file=(
            "../.env",
            ".env",
        ),
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
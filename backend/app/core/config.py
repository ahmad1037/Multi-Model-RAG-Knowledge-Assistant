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

    frontend_origin: str = (
        "http://localhost:5173"
    )

    storage_root: Path = Path(
        "../storage"
    )

    max_upload_size_mb: int = 25

    text_embedding_model: str = (
        "BAAI/bge-small-en-v1.5"
    )

    text_embedding_dimension: int = 384

    text_embedding_batch_size: int = 32

    text_embedding_device: str = "cuda"

    text_query_instruction: str = (
        "Represent this sentence for "
        "searching relevant passages: "
    )
    clip_model_name: str = "ViT-B-32"

    clip_pretrained: str = "openai"

    clip_embedding_dimension: int = 512

    clip_batch_size: int = 32

    clip_device: str = "auto"

    clip_hnsw_ef_search: int = 100

    hnsw_ef_search: int = 100

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
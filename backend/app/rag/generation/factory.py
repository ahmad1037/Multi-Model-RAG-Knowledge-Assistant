from functools import lru_cache

from app.core.config import settings

from app.rag.generation.ollama_provider import (
    OllamaGenerationProvider,
)


@lru_cache
def get_generation_provider():

    if (
        settings.llm_provider
        == "ollama"
    ):

        return (
            OllamaGenerationProvider()
        )

    raise ValueError(
        "Unsupported generation provider: "
        f"{settings.llm_provider}"
    )
from fastapi import (
    HTTPException,
    status,
)

from app.core.config import settings


def require_local_inference() -> None:

    if (
        settings.deployment_mode
        != "local_full"
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),

            detail=(
                "Full AI inference is disabled "
                "in the free Azure cloud preview. "
                "Run the project locally to use "
                "Ollama, VLM analysis and grounded "
                "generation."
            ),
        )
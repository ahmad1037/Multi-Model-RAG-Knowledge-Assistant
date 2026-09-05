import uuid

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

from app.rag.retrieval.visual import (
    KnowledgeBaseHasNoVisualEmbeddingsError,
    text_to_image_search,
)

from app.schemas.visual_retrieval import (
    TextToImageSearchRequest,
    TextToImageSearchResponse,
)

from pathlib import Path

from fastapi import (
    File,
    Form,
    UploadFile,
)

from app.rag.retrieval.visual import (
    image_vector_search,
)

from app.rag.vision.clip_embedder import (
    get_clip_embedder,
)

from app.schemas.visual_retrieval import (
    ImageToImageSearchResponse,
)

from app.services.query_image import (
    UnsupportedQueryImageError,
    save_query_image,
)

router = APIRouter(
    tags=["visual-retrieval"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    (
        "/knowledge-bases/"
        "{knowledge_base_id}/visual-search"
    ),
    response_model=(
        TextToImageSearchResponse
    ),
)
def visual_search(
    knowledge_base_id: uuid.UUID,
    payload: TextToImageSearchRequest,
    db: DatabaseSession,
):

    try:

        results = text_to_image_search(
            db=db,
            knowledge_base_id=(
                knowledge_base_id
            ),
            query=payload.query,
            top_k=payload.top_k,
            mode=payload.mode,
            asset_type=(
                payload.asset_type
            ),
        )

        return {
            "query":
                payload.query,

            "mode":
                payload.mode,

            "model":
                settings.clip_model_name,

            "results":
                results,
        }

    except (
        KnowledgeBaseHasNoVisualEmbeddingsError
    ) as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Visual search failed."
            ),
        )

@router.post(
    (
        "/knowledge-bases/"
        "{knowledge_base_id}/image-search"
    ),
    response_model=(
        ImageToImageSearchResponse
    ),
)
async def image_search(
    knowledge_base_id: uuid.UUID,

    file: Annotated[
        UploadFile,
        File(),
    ],

    db: DatabaseSession,

    top_k: int = Form(5),

    mode: str = Form("exact"),

    asset_type: str = Form("all"),
):

    temp_path: Path | None = None

    try:

        temp_path = (
            await save_query_image(
                file
            )
        )

        embedder = (
            get_clip_embedder()
        )

        query_vector = (
            embedder.encode_images(
                [temp_path]
            )[0]
        )

        results = image_vector_search(
            db=db,

            knowledge_base_id=(
                knowledge_base_id
            ),

            query_vector=(
                query_vector
            ),

            top_k=min(
                max(top_k, 1),
                50,
            ),

            mode=mode,

            asset_type=asset_type,
        )

        return {
            "mode":
                mode,

            "model":
                settings.clip_model_name,

            "results":
                results,
        }

    except (
        UnsupportedQueryImageError
    ) as exc:

        raise HTTPException(
            status_code=415,
            detail=str(exc),
        )

    finally:

        if (
            temp_path is not None
            and temp_path.exists()
        ):

            temp_path.unlink(
                missing_ok=True
            )
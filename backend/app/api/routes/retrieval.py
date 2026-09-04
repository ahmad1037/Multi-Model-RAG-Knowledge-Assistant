import uuid

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.core.config import settings

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.rag.retrieval.semantic import (
    KnowledgeBaseHasNoEmbeddingsError,
    semantic_search,
)

from app.schemas.retrieval import (
    SemanticSearchRequest,
    SemanticSearchResponse,
)


router = APIRouter(
    tags=["retrieval"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    (
        "/knowledge-bases/"
        "{knowledge_base_id}/search"
    ),
    response_model=SemanticSearchResponse,
)
def search_knowledge_base(
    knowledge_base_id: uuid.UUID,
    payload: SemanticSearchRequest,
    db: DatabaseSession,
):

    try:

        results = semantic_search(
            db=db,
            knowledge_base_id=(
                knowledge_base_id
            ),
            query=payload.query,
            top_k=payload.top_k,
            mode=payload.mode,
        )

        return {
            "query":
                payload.query,

            "mode":
                payload.mode,

            "embedding_model":
                settings.text_embedding_model,

            "results":
                results,
        }

    except (
        KnowledgeBaseHasNoEmbeddingsError
    ) as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Semantic search failed."
            ),
        )
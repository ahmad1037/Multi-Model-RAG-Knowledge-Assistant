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

from app.rag.retrieval.lexical import (
    lexical_search,
)

from app.schemas.retrieval import (
    LexicalSearchHit,
    LexicalSearchRequest,
)   

from app.schemas.hybrid_retrieval import (
    HybridSearchRequest,
    HybridSearchResponse,
)

from app.services.hybrid_retrieval import (
    NoHybridResultsError,
    hybrid_search,
)

from app.schemas.reranking import (
    RerankSearchRequest,
    RerankSearchResponse,
)

from app.services.rerank_search import (
    retrieve_and_rerank,
)

from app.services.context_pipeline import (
    retrieve_rerank_and_select,
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

@router.post(
    (
        "/knowledge-bases/"
        "{knowledge_base_id}/"
        "lexical-search"
    ),
    response_model=list[
        LexicalSearchHit
    ],
)
def lexical_search_endpoint(
    knowledge_base_id: uuid.UUID,
    payload: LexicalSearchRequest,
    db: DatabaseSession,
):

    return lexical_search(
        db=db,
        knowledge_base_id=(
            knowledge_base_id
        ),
        query=payload.query,
        top_k=payload.top_k,
    )

@router.post(
    (
        "/knowledge-bases/"
        "{knowledge_base_id}/"
        "hybrid-search"
    ),
    response_model=(
        HybridSearchResponse
    ),
)
def hybrid_search_endpoint(
    knowledge_base_id: uuid.UUID,
    payload: HybridSearchRequest,
    db: DatabaseSession,
):

    try:

        return hybrid_search(
            db=db,

            knowledge_base_id=(
                knowledge_base_id
            ),

            payload=payload,
        )

    except NoHybridResultsError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Hybrid retrieval failed."
            ),
        )


@router.post(
    (
        "/knowledge-bases/"
        "{knowledge_base_id}/"
        "rerank-search"
    ),
    response_model=(
        RerankSearchResponse
    ),
)
def rerank_search_endpoint(
    knowledge_base_id: uuid.UUID,
    payload: RerankSearchRequest,
    db: DatabaseSession,
):

    return retrieve_and_rerank(
        db=db,

        knowledge_base_id=(
            knowledge_base_id
        ),

        payload=payload,
    )

@router.post(
    (
        "/knowledge-bases/"
        "{knowledge_base_id}/"
        "context"
    )
)
def context_endpoint(
    knowledge_base_id: uuid.UUID,
    payload: LexicalSearchRequest,
    db: DatabaseSession,
):

    return (
        retrieve_rerank_and_select(
            db=db,

            knowledge_base_id=(
                knowledge_base_id
            ),

            query=payload.query,
        )
    )


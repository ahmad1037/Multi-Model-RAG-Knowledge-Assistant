import uuid

from sqlalchemy.orm import Session

from app.rag.context.selector import (
    select_context,
)

from app.schemas.reranking import (
    RerankSearchRequest,
)

from app.services.rerank_search import (
    retrieve_and_rerank,
)


def retrieve_rerank_and_select(
    db: Session,
    knowledge_base_id: uuid.UUID,
    query: str,
) -> dict:

    request = (
        RerankSearchRequest(
            query=query,

            candidate_k=20,

            rerank_top_k=10,

            include_semantic=True,

            include_lexical=True,

            include_visual=True,

            semantic_mode="hnsw",

            visual_mode="hnsw",
        )
    )

    reranked = (
        retrieve_and_rerank(
            db=db,

            knowledge_base_id=(
                knowledge_base_id
            ),

            payload=request,
        )
    )

    context = select_context(
        query=query,
        reranked=(
            reranked["results"]
        ),
    )

    return {
        "query":
            query,

        "candidate_count":
            reranked[
                "candidate_count"
            ],

        "reranked_count":
            len(
                reranked["results"]
            ),

        "context":
            context,
    }
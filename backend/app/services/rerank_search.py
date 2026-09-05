import uuid

from sqlalchemy.orm import Session

from app.schemas.hybrid_retrieval import (
    HybridSearchRequest,
)

from app.schemas.reranking import (
    RerankSearchRequest,
)

from app.services.hybrid_retrieval import (
    hybrid_search,
)

from app.services.reranking import (
    rerank_evidence,
)


def retrieve_and_rerank(
    db: Session,
    knowledge_base_id: uuid.UUID,
    payload: RerankSearchRequest,
) -> dict:

    hybrid_payload = (
        HybridSearchRequest(
            query=payload.query,

            top_k=(
                payload.candidate_k
            ),

            candidate_k=max(
                payload.candidate_k,
                20,
            ),

            rrf_k=60,

            include_semantic=(
                payload.include_semantic
            ),

            include_lexical=(
                payload.include_lexical
            ),

            include_visual=(
                payload.include_visual
            ),

            semantic_mode=(
                payload.semantic_mode
            ),

            visual_mode=(
                payload.visual_mode
            ),
        )
    )

    retrieval = hybrid_search(
        db=db,

        knowledge_base_id=(
            knowledge_base_id
        ),

        payload=hybrid_payload,
    )

    candidates = retrieval[
        "results"
    ]

    results = rerank_evidence(
        db=db,
        query=payload.query,
        evidence=candidates,
        top_k=payload.rerank_top_k,
    )

    return {
        "query":
            payload.query,

        "candidate_count":
            len(candidates),

        "results":
            results,
    }
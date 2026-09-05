from sqlalchemy.orm import Session

from app.rag.reranking.bge_reranker import (
    get_reranker,
)

from app.rag.reranking.evidence import (
    evidence_to_rerank_text,
)


def rerank_evidence(
    db: Session,
    query: str,
    evidence: list[dict],
    top_k: int,
) -> list[dict]:

    if not evidence:
        return []

    passages = [
        evidence_to_rerank_text(
            db,
            item,
        )
        for item in evidence
    ]

    reranker = (
        get_reranker()
    )

    scores = (
        reranker.score_pairs(
            query=query,
            passages=passages,
        )
    )

    reranked = []

    for (
        original_rank,
        item,
        score,
        rerank_text,
    ) in zip(
        range(
            1,
            len(evidence) + 1,
        ),
        evidence,
        scores,
        passages,
        strict=True,
    ):

        enriched = dict(
            item
        )

        enriched[
            "original_rank"
        ] = original_rank

        enriched[
            "reranker_score"
        ] = float(score)

        enriched[
            "rerank_text"
        ] = rerank_text

        reranked.append(
            enriched
        )

    reranked.sort(
        key=lambda item:
            item[
                "reranker_score"
            ],
        reverse=True,
    )

    for rank, item in enumerate(
        reranked,
        start=1,
    ):

        item[
            "reranked_rank"
        ] = rank

    return reranked[:top_k]
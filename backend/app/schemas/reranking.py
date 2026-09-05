from pydantic import (
    BaseModel,
    Field,
)

from app.schemas.hybrid_retrieval import (
    HybridEvidence,
)


class RerankSearchRequest(
    BaseModel
):

    query: str = Field(
        min_length=2,
        max_length=2000,
    )

    candidate_k: int = Field(
        default=20,
        ge=5,
        le=100,
    )

    rerank_top_k: int = Field(
        default=10,
        ge=1,
        le=50,
    )

    include_semantic: bool = True

    include_lexical: bool = True

    include_visual: bool = True

    semantic_mode: str = "hnsw"

    visual_mode: str = "hnsw"


class RerankedEvidence(
    HybridEvidence
):

    original_rank: int

    reranked_rank: int

    reranker_score: float


class RerankSearchResponse(
    BaseModel
):

    query: str

    candidate_count: int

    results: list[
        RerankedEvidence
    ]
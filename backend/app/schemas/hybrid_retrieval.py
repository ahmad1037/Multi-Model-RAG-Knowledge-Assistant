import uuid

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


EvidenceType = Literal[
    "text_chunk",
    "visual_asset",
]


RetrievalMode = Literal[
    "exact",
    "hnsw",
]


class HybridSearchRequest(
    BaseModel
):

    query: str = Field(
        min_length=2,
        max_length=2000,
    )

    top_k: int = Field(
        default=10,
        ge=1,
        le=50,
    )

    candidate_k: int = Field(
        default=20,
        ge=5,
        le=100,
    )

    rrf_k: int = Field(
        default=60,
        ge=1,
        le=200,
    )

    include_semantic: bool = True

    include_lexical: bool = True

    include_visual: bool = True

    semantic_mode: RetrievalMode = (
        "hnsw"
    )

    visual_mode: RetrievalMode = (
        "hnsw"
    )

    visual_asset_type: Literal[
        "all",
        "page",
        "embedded_image",
    ] = "all"

    @model_validator(
        mode="after"
    )
    def validate_configuration(self):

        if not any(
            [
                self.include_semantic,
                self.include_lexical,
                self.include_visual,
            ]
        ):

            raise ValueError(
                "At least one retrieval "
                "channel must be enabled."
            )

        if (
            self.candidate_k
            < self.top_k
        ):

            raise ValueError(
                "candidate_k must be "
                "greater than or equal "
                "to top_k."
            )

        return self

class HybridEvidence(
    BaseModel
):

    evidence_id: uuid.UUID

    evidence_type: EvidenceType

    document_id: uuid.UUID

    document_name: str

    heading: str | None = None

    text: str | None = None

    page_start: int | None = None

    page_end: int | None = None

    asset_type: str | None = None

    storage_path: str | None = None

    channels: list[str]

    channel_ranks: dict[str, int]

    channel_scores: dict[str, float]

    rrf_score: float


class HybridSearchResponse(
    BaseModel
):

    query: str

    channels_used: list[str]

    channel_counts: dict[str, int]

    warnings: list[str]

    results: list[
        HybridEvidence
    ]
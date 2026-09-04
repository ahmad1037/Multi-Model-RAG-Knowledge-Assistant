import uuid

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


SearchMode = Literal[
    "exact",
    "hnsw",
]


class SemanticSearchRequest(
    BaseModel
):

    query: str = Field(
        min_length=2,
        max_length=2000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    mode: SearchMode = "exact"


class SemanticSearchHit(
    BaseModel
):

    chunk_id: uuid.UUID

    document_id: uuid.UUID

    document_name: str

    chunk_index: int

    heading: str | None

    page_start: int | None

    page_end: int | None

    text: str

    cosine_distance: float

    similarity: float


class SemanticSearchResponse(
    BaseModel
):

    query: str

    mode: SearchMode

    embedding_model: str

    results: list[
        SemanticSearchHit
    ]
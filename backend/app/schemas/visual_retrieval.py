import uuid

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


VisualSearchMode = Literal[
    "exact",
    "hnsw",
]


VisualAssetType = Literal[
    "all",
    "page",
    "embedded_image",
]


class TextToImageSearchRequest(
    BaseModel
):

    query: str = Field(
        min_length=2,
        max_length=1000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    mode: VisualSearchMode = (
        "exact"
    )

    asset_type: VisualAssetType = (
        "all"
    )


class VisualSearchHit(
    BaseModel
):

    visual_asset_id: uuid.UUID

    document_id: uuid.UUID

    document_name: str

    page_number: int | None

    asset_index: int

    asset_type: str

    storage_path: str

    width_px: int | None

    height_px: int | None

    cosine_distance: float

    similarity: float


class TextToImageSearchResponse(
    BaseModel
):

    query: str

    mode: VisualSearchMode

    model: str

    results: list[
        VisualSearchHit
    ]

class ImageToImageSearchResponse(
    BaseModel
):

    mode: VisualSearchMode

    model: str

    results: list[
        VisualSearchHit
    ]
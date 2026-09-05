import uuid

from pydantic import (
    BaseModel,
)


class ContextItem(
    BaseModel
):

    citation_id: str

    evidence_id: uuid.UUID

    evidence_type: str

    document_id: uuid.UUID

    document_name: str

    page_start: int | None

    page_end: int | None

    heading: str | None

    text: str | None

    visual_asset_id: uuid.UUID | None

    asset_type: str | None

    storage_path: str | None

    reranker_score: float

    estimated_tokens: int


class ContextSelection(
    BaseModel
):

    items: list[
        ContextItem
    ]

    total_text_tokens: int

    text_items: int

    visual_items: int
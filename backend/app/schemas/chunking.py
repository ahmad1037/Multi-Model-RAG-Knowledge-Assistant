import uuid

from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


ChunkingStrategy = Literal[
    "page_v1",
    "structure_recursive_v1",
]


class ChunkingRequest(BaseModel):

    strategy: ChunkingStrategy = (
        "structure_recursive_v1"
    )

    chunk_size_tokens: int = Field(
        default=450,
        ge=100,
        le=2000,
    )

    chunk_overlap_tokens: int = Field(
        default=80,
        ge=0,
        le=500,
    )

    tokenizer_name: str = (
        "cl100k_base"
    )

    @model_validator(
        mode="after"
    )
    def validate_overlap(self):

        if (
            self.chunk_overlap_tokens
            >= self.chunk_size_tokens
        ):

            raise ValueError(
                "chunk_overlap_tokens must "
                "be smaller than "
                "chunk_size_tokens."
            )

        return self


class ChunkingRunRead(BaseModel):

    id: uuid.UUID

    document_id: uuid.UUID

    strategy: str

    tokenizer_name: str

    chunk_size_tokens: int

    chunk_overlap_tokens: int

    status: str

    is_active: bool

    chunk_count: int | None

    average_tokens: float | None

    max_tokens: int | None

    error_message: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ChunkRead(BaseModel):

    id: uuid.UUID

    chunking_run_id: uuid.UUID

    chunk_index: int

    text: str

    heading: str | None

    page_start: int | None

    page_end: int | None

    token_count: int

    model_config = ConfigDict(
        from_attributes=True
    )


class ChunkingResponse(BaseModel):

    run: ChunkingRunRead

    preview: list[ChunkRead]
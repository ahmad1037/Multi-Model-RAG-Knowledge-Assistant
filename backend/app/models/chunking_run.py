from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.document_chunk import DocumentChunk

import uuid
from uuid import UUID as PyUUID
from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID as PGUUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base
from app.models.mixins import TimestampMixin


class ChunkingRun(
    TimestampMixin,
    Base,
):
    __tablename__ = "chunking_runs"

    id: Mapped[PyUUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[PyUUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    strategy: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    tokenizer_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    chunk_size_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_overlap_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="running",
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    chunk_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    average_tokens: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    max_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    run_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunking_runs",
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="chunking_run",
        cascade="all, delete-orphan",
        order_by="DocumentChunk.chunk_index",
    )
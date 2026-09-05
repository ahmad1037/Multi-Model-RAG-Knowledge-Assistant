from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.chunking_run import ChunkingRun


import uuid

from pgvector.sqlalchemy import VECTOR

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Computed,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    TSVECTOR,
    UUID,
)
from app.db.base import Base
from app.models.mixins import TimestampMixin


class DocumentChunk(
    TimestampMixin,
    Base,
):
    __tablename__ = "document_chunks"

    __table_args__ = (
        UniqueConstraint(
            "chunking_run_id",
            "chunk_index",
            name="uq_chunking_run_chunk_index",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    chunking_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chunking_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "knowledge_bases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    search_vector: Mapped[object] = mapped_column(
        TSVECTOR,
        Computed(
            """
            setweight(
                to_tsvector(
                    'english',
                    coalesce(heading, '')
                ),
                'A'
            )
            ||
            setweight(
                to_tsvector(
                    'english',
                    coalesce(text, '')
                ),
                'B'
            )
            """,
            persisted=True,
        ),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    heading: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    page_start: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    page_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    embedding = mapped_column(
        VECTOR(384),
        nullable=True,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    embedding_dimension: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    chunk_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="chunks",
    )

    chunking_run: Mapped["ChunkingRun"] = relationship(
        "ChunkingRun",
        back_populates="chunks",
    )
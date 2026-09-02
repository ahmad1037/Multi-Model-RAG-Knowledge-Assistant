from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.document_chunk import DocumentChunk
from uuid import UUID as PyUUID
import uuid


from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class VisualAsset(
    TimestampMixin,
    Base,
):
    __tablename__ = "visual_assets"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "page_number",
            "asset_index",
            name="uq_visual_asset_location",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    document_chunk_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    document_chunk: Mapped["DocumentChunk"] = relationship(
        "DocumentChunk",
        back_populates="visual_assets",
    )

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "knowledge_bases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    asset_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    asset_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    caption: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ocr_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    visual_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    clip_embedding = mapped_column(
        VECTOR(),
        nullable=True,
    )

    clip_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    clip_dimension: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    colpali_index_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    visual_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    document = relationship(
        "Document",
        back_populates="visual_assets",
    )
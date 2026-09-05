from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.knowledge_base import KnowledgeBase

import uuid

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

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
            "asset_index",
            name="uq_visual_asset_index",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
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

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    asset_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    asset_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    checksum_sha256: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    width_px: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    height_px: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
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
        VECTOR(512),
        nullable=True,
    )

    clip_model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    clip_pretrained: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    clip_dimension: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    clip_embedding_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
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

    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="visual_assets",
    )

    knowledge_base: Mapped["KnowledgeBase"] = relationship(
        "KnowledgeBase",
        back_populates="visual_assets",
    )
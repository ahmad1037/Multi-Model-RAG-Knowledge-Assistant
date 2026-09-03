from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.visual_asset import VisualAsset

import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class KnowledgeBase(
    TimestampMixin,
    Base,
):
    __tablename__ = "knowledge_bases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
    )

    slug: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    documents = relationship(
        "Document",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )

    conversations = relationship(
        "Conversation",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
    visual_assets: Mapped[list["VisualAsset"]] = relationship(
        "VisualAsset",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )
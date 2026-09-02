import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )

    slug: str = Field(
        min_length=2,
        max_length=200,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    description: str | None = None


class KnowledgeBaseRead(BaseModel):
    id: uuid.UUID

    name: str

    slug: str

    description: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
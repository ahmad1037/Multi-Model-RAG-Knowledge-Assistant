import uuid

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class DocumentRead(BaseModel):

    id: uuid.UUID

    knowledge_base_id: uuid.UUID

    original_filename: str

    media_type: str

    file_size_bytes: int | None

    page_count: int | None

    status: str

    error_message: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DocumentUploadResponse(BaseModel):

    document: DocumentRead

    text_characters: int

    page_count: int | None

    visual_assets: int

    extraction_path: str
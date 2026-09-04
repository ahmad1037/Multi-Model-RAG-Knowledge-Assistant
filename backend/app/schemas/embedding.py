import uuid

from pydantic import (
    BaseModel,
)


class EmbedDocumentRequest(BaseModel):

    force: bool = False


class EmbedDocumentResponse(BaseModel):

    document_id: uuid.UUID

    chunking_run_id: uuid.UUID

    model: str

    dimension: int

    chunks_total: int

    chunks_embedded: int

    chunks_skipped: int

    status: str
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.chunking_run import (
    ChunkingRun,
)

from app.models.document_chunk import (
    DocumentChunk,
)

def visual_page_text(
    db: Session,
    document_id: uuid.UUID,
    page_number: int | None,
) -> str:

    if page_number is None:

        return ""

    statement = (
        select(DocumentChunk)
        .join(
            ChunkingRun,
            ChunkingRun.id
            == DocumentChunk.chunking_run_id,
        )
        .where(
            DocumentChunk.document_id
            == document_id,

            ChunkingRun.is_active.is_(
                True
            ),

            ChunkingRun.status
            == "succeeded",

            DocumentChunk.page_start
            <= page_number,

            DocumentChunk.page_end
            >= page_number,
        )
        .order_by(
            DocumentChunk.chunk_index
        )
    )

    chunks = list(
        db.scalars(
            statement
        ).all()
    )

    text = "\n\n".join(
        chunk.text
        for chunk in chunks
    )

    return text[
        :settings
        .visual_context_max_chars
    ]

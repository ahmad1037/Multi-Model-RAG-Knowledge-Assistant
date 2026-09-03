import hashlib
import json
import logging
import uuid

from pathlib import Path

from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.chunking_run import (
    ChunkingRun,
)
from app.models.document import (
    Document,
)
from app.models.document_chunk import (
    DocumentChunk,
)

from app.rag.chunking.strategies import (
    chunk_pages,
)
from app.rag.chunking.types import (
    ChunkingConfig,
)

from app.schemas.chunking import (
    ChunkingRequest,
)


logger = logging.getLogger(
    __name__
)

class DocumentNotFoundError(
    Exception
):
    pass


class DocumentNotReadyError(
    Exception
):
    pass


def extraction_path_for(
    document: Document,
) -> Path:

    relative_path = (
        document.document_metadata.get(
            "extraction_path"
        )
    )

    if not relative_path:

        raise DocumentNotReadyError(
            "Document has no extraction output."
        )

    return (
        settings.storage_root.resolve()
        / relative_path
    )


def load_pages(
    document: Document,
) -> list[dict]:

    path = extraction_path_for(
        document
    )

    if not path.exists():

        raise DocumentNotReadyError(
            "Extraction file does not exist."
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    return payload.get(
        "pages",
        [],
    )

def chunk_hash(
    text: str,
) -> str:

    return hashlib.sha256(
        text.encode(
            "utf-8"
        )
    ).hexdigest()

def run_chunking(
    db: Session,
    document_id: uuid.UUID,
    payload: ChunkingRequest,
) -> tuple[
    ChunkingRun,
    list[DocumentChunk],
]:

    document = db.get(
        Document,
        document_id,
    )

    if document is None:

        raise DocumentNotFoundError

    allowed_statuses = {
        "ready_for_chunking",
        "ready_for_embedding",
        "ready",
    }

    if (
        document.status
        not in allowed_statuses
    ):

        raise DocumentNotReadyError(
            f"Cannot chunk document in "
            f"status '{document.status}'."
        )

    config = ChunkingConfig(
        strategy=payload.strategy,

        chunk_size_tokens=(
            payload.chunk_size_tokens
        ),

        chunk_overlap_tokens=(
            payload.chunk_overlap_tokens
        ),

        tokenizer_name=(
            payload.tokenizer_name
        ),
    )

    run = ChunkingRun(
        document_id=document.id,

        strategy=config.strategy,

        tokenizer_name=(
            config.tokenizer_name
        ),

        chunk_size_tokens=(
            config.chunk_size_tokens
        ),

        chunk_overlap_tokens=(
            config.chunk_overlap_tokens
        ),

        status="running",

        is_active=False,

        run_metadata={},
    )

    db.add(run)

    document.status = "chunking"

    db.commit()

    db.refresh(run)

    try:

        pages = load_pages(
            document
        )

        drafts = chunk_pages(
            pages=pages,
            config=config,
        )

        if not drafts:

            raise ValueError(
                "Chunking produced no text chunks."
            )

        persisted: list[
            DocumentChunk
        ] = []

        for index, draft in enumerate(
            drafts
        ):

            chunk = DocumentChunk(
                chunking_run_id=run.id,

                document_id=document.id,

                knowledge_base_id=(
                    document.knowledge_base_id
                ),

                chunk_index=index,

                text=draft.text,

                heading=draft.heading,

                page_start=(
                    draft.page_start
                ),

                page_end=(
                    draft.page_end
                ),

                token_count=(
                    draft.token_count
                ),

                content_hash=chunk_hash(
                    draft.text
                ),

                chunk_metadata=(
                    draft.metadata
                ),
            )

            db.add(chunk)

            persisted.append(
                chunk
            )

        token_counts = [
            chunk.token_count
            for chunk in persisted
        ]

        # Only one chunking run is considered
        # active for a document at a time.
        db.execute(
            update(ChunkingRun)
            .where(
                ChunkingRun.document_id
                == document.id,

                ChunkingRun.id
                != run.id,
            )
            .values(
                is_active=False
            )
        )

        run.status = "succeeded"

        run.is_active = True

        run.chunk_count = len(
            persisted
        )

        run.average_tokens = (
            sum(token_counts)
            / len(token_counts)
        )

        run.max_tokens = max(
            token_counts
        )

        run.run_metadata = {
            "pages_processed":
                len(pages),
        }

        document.status = (
            "ready_for_embedding"
        )

        document.error_message = None

        db.commit()

        db.refresh(run)

        for chunk in persisted:
            db.refresh(chunk)

        return (
            run,
            persisted,
        )

    except Exception as exc:

        logger.exception(
            "Document chunking failed",
            extra={
                "document_id":
                    str(document.id),

                "chunking_run_id":
                    str(run.id),
            },
        )

        db.rollback()

        failed_run = db.get(
            ChunkingRun,
            run.id,
        )

        failed_document = db.get(
            Document,
            document.id,
        )

        if failed_run:

            failed_run.status = (
                "failed"
            )

            failed_run.error_message = (
                str(exc)[:2000]
            )

        if failed_document:

            failed_document.status = (
                "chunking_failed"
            )

            failed_document.error_message = (
                str(exc)[:2000]
            )

        db.commit()

        raise

def list_chunking_runs(
    db: Session,
    document_id: uuid.UUID,
) -> list[ChunkingRun]:

    statement = (
        select(ChunkingRun)
        .where(
            ChunkingRun.document_id
            == document_id
        )
        .order_by(
            ChunkingRun.created_at.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


def list_chunks(
    db: Session,
    run_id: uuid.UUID,
    limit: int = 100,
) -> list[DocumentChunk]:

    statement = (
        select(DocumentChunk)
        .where(
            DocumentChunk.chunking_run_id
            == run_id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .limit(limit)
    )

    return list(
        db.scalars(
            statement
        ).all()
    )
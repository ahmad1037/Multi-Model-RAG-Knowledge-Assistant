import logging
import uuid

from sqlalchemy import select
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

from app.rag.embeddings.text_embedder import (
    get_text_embedder,
)


logger = logging.getLogger(
    __name__
)


class ActiveChunkingRunNotFoundError(
    Exception
):
    pass


class DocumentEmbeddingNotReadyError(
    Exception
):
    pass


def get_active_chunking_run(
    db: Session,
    document_id: uuid.UUID,
) -> ChunkingRun | None:

    statement = (
        select(ChunkingRun)
        .where(
            ChunkingRun.document_id
            == document_id,

            ChunkingRun.is_active.is_(
                True
            ),

            ChunkingRun.status
            == "succeeded",
        )
    )

    return db.scalar(
        statement
    )


def embed_document(
    db: Session,
    document_id: uuid.UUID,
    force: bool = False,
) -> dict:

    document = db.get(
        Document,
        document_id,
    )

    if document is None:

        raise DocumentEmbeddingNotReadyError(
            "Document not found."
        )

    if document.status not in {
        "ready_for_embedding",
        "ready",
        "embedding_failed",
    }:

        raise DocumentEmbeddingNotReadyError(
            f"Document status "
            f"'{document.status}' "
            f"cannot be embedded."
        )

    active_run = (
        get_active_chunking_run(
            db,
            document_id,
        )
    )

    if active_run is None:

        raise ActiveChunkingRunNotFoundError(
            "No active successful "
            "chunking run exists."
        )

    statement = (
        select(DocumentChunk)
        .where(
            DocumentChunk.chunking_run_id
            == active_run.id
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

    if not chunks:

        raise DocumentEmbeddingNotReadyError(
            "The active chunking run "
            "contains no chunks."
        )

    to_embed: list[
        DocumentChunk
    ] = []

    skipped = 0

    for chunk in chunks:

        already_current = (
            chunk.embedding is not None
            and chunk.embedding_model
            == settings.text_embedding_model
            and chunk.embedding_dimension
            == settings.text_embedding_dimension
        )

        if (
            already_current
            and not force
        ):

            skipped += 1

        else:

            to_embed.append(
                chunk
            )

    embedder = (
        get_text_embedder()
    )

    document.status = "embedding"

    document.error_message = None

    db.commit()

    embedded_count = 0

    try:

        batch_size = (
            settings.text_embedding_batch_size
        )

        for start in range(
            0,
            len(to_embed),
            batch_size,
        ):

            batch = to_embed[
                start:
                start + batch_size
            ]

            texts = [
                chunk.text
                for chunk in batch
            ]

            vectors = (
                embedder.encode_passages(
                    texts
                )
            )

            for chunk, vector in zip(
                batch,
                vectors,
                strict=True,
            ):

                chunk.embedding = (
                    vector
                )

                chunk.embedding_model = (
                    settings
                    .text_embedding_model
                )

                chunk.embedding_dimension = (
                    settings
                    .text_embedding_dimension
                )

                embedded_count += 1

            db.commit()

        document.status = "ready"

        metadata = dict(
            document.document_metadata
            or {}
        )

        metadata[
            "text_embedding"
        ] = {
            "model":
                settings
                .text_embedding_model,

            "dimension":
                settings
                .text_embedding_dimension,

            "chunking_run_id":
                str(active_run.id),

            "normalized":
                True,
        }

        document.document_metadata = (
            metadata
        )

        db.commit()

        return {
            "document_id":
                document.id,

            "chunking_run_id":
                active_run.id,

            "model":
                settings
                .text_embedding_model,

            "dimension":
                settings
                .text_embedding_dimension,

            "chunks_total":
                len(chunks),

            "chunks_embedded":
                embedded_count,

            "chunks_skipped":
                skipped,

            "status":
                "ready",
        }

    except Exception as exc:

        logger.exception(
            "Embedding failed",
            extra={
                "document_id":
                    str(document.id),

                "chunking_run_id":
                    str(active_run.id),
            },
        )

        db.rollback()

        failed_document = db.get(
            Document,
            document.id,
        )

        if failed_document:

            failed_document.status = (
                "embedding_failed"
            )

            failed_document.error_message = (
                str(exc)[:2000]
            )

            db.commit()

        raise
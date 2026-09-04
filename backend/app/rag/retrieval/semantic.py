import uuid

from sqlalchemy import (
    select,
    text,
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

from app.rag.embeddings.text_embedder import (
    get_text_embedder,
)


class KnowledgeBaseHasNoEmbeddingsError(
    Exception
):
    pass


def semantic_search(
    db: Session,
    knowledge_base_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    mode: str = "exact",
) -> list[dict]:

    embedder = (
        get_text_embedder()
    )

    query_vector = (
        embedder.encode_query(
            query
        )
    )

    if mode == "exact":

        # pgvector documentation recommends
        # disabling index scans when comparing
        # approximate retrieval against exact
        # retrieval.
        db.execute(
            text(
                "SET LOCAL "
                "enable_indexscan = off"
            )
        )

    elif mode == "hnsw":

        ef_search = int(
            settings.hnsw_ef_search
        )

        db.execute(
            text(
                f"SET LOCAL "
                f"hnsw.ef_search = "
                f"{ef_search}"
            )
        )

        db.execute(
            text(
                "SET LOCAL "
                "hnsw.iterative_scan = "
                "strict_order"
            )
        )

    else:

        raise ValueError(
            f"Unknown search mode: "
            f"{mode}"
        )

    distance = (
        DocumentChunk.embedding
        .cosine_distance(
            query_vector
        )
        .label(
            "cosine_distance"
        )
    )

    statement = (
        select(
            DocumentChunk,
            Document.original_filename,
            distance,
        )
        .join(
            Document,
            Document.id
            == DocumentChunk.document_id,
        )
        .join(
            ChunkingRun,
            ChunkingRun.id
            == DocumentChunk.chunking_run_id,
        )
        .where(
            DocumentChunk.knowledge_base_id
            == knowledge_base_id,

            ChunkingRun.is_active.is_(
                True
            ),

            ChunkingRun.status
            == "succeeded",

            DocumentChunk.embedding
            .is_not(None),

            DocumentChunk.embedding_model
            == settings.text_embedding_model,

            DocumentChunk.embedding_dimension
            == settings.text_embedding_dimension,
        )
        .order_by(
            distance
        )
        .limit(
            top_k
        )
    )

    rows = db.execute(
        statement
    ).all()

    if not rows:

        raise (
            KnowledgeBaseHasNoEmbeddingsError(
                "No embedded active chunks "
                "were found for this "
                "knowledge base."
            )
        )

    results: list[dict] = []

    for (
        chunk,
        document_name,
        cosine_distance,
    ) in rows:

        distance_value = float(
            cosine_distance
        )

        results.append(
            {
                "chunk_id":
                    chunk.id,

                "document_id":
                    chunk.document_id,

                "document_name":
                    document_name,

                "chunk_index":
                    chunk.chunk_index,

                "heading":
                    chunk.heading,

                "page_start":
                    chunk.page_start,

                "page_end":
                    chunk.page_end,

                "text":
                    chunk.text,

                "cosine_distance":
                    distance_value,

                "similarity":
                    1.0
                    - distance_value,
            }
        )

    return results
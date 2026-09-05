import uuid

from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.models.chunking_run import (
    ChunkingRun,
)

from app.models.document import (
    Document,
)

from app.models.document_chunk import (
    DocumentChunk,
)
def lexical_search(
    db: Session,
    knowledge_base_id: uuid.UUID,
    query: str,
    top_k: int = 20,
) -> list[dict]:

    ts_query = (
        func.websearch_to_tsquery(
            "english",
            query,
        )
    )

    rank = (
        func.ts_rank_cd(
            DocumentChunk.search_vector,
            ts_query,
        )
        .label(
            "lexical_score"
        )
    )

    statement = (
        select(
            DocumentChunk,
            Document.original_filename,
            rank,
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

            DocumentChunk.search_vector.op(
                "@@"
            )(
                ts_query
            ),
        )
        .order_by(
            rank.desc()
        )
        .limit(
            top_k
        )
    )

    rows = db.execute(
        statement
    ).all()

    results: list[dict] = []

    for (
        chunk,
        document_name,
        lexical_score,
    ) in rows:

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

                "lexical_score":
                    float(
                        lexical_score
                    ),
            }
        )

    return results
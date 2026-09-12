import uuid

from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.models.document import (
    Document,
)

from app.models.processing_job import (
    ProcessingJob,
)

from app.models.visual_asset import (
    VisualAsset,
)

from app.schemas.chunking import (
    ChunkingRequest,
)

from app.services.document_chunking import (
    run_chunking,
)

from app.services.document_ingestion import (
    extract_stored_document,
)

from app.services.processing_jobs import (
    update_job,
)

from app.services.text_embeddings import (
    embed_document,
)

from app.services.visual_analysis import (
    analyze_document_visuals,
)

from app.services.visual_embeddings import (
    embed_visual_assets,
)

def document_has_visuals(
    db: Session,
    document_id: uuid.UUID,
) -> bool:

    statement = (
        select(
            func.count(
                VisualAsset.id
            )
        )

        .where(
            VisualAsset.document_id
            == document_id
        )
    )

    count = db.scalar(
        statement
    )

    return bool(
        count
    )


def process_document_job(
    db: Session,
    job: ProcessingJob,
) -> None:

    document_id = (
        job.document_id
    )


    update_job(
        db,
        job,

        status="running",

        stage="extracting",

        progress=10,
    )


    extract_stored_document(
        db,
        document_id,
    )


    update_job(
        db,
        job,

        stage="chunking",

        progress=30,
    )


    chunk_request = (
        ChunkingRequest(

            strategy=(
                "structure_recursive_v1"
            ),

            chunk_size_tokens=450,

            chunk_overlap_tokens=80,

            tokenizer_name=(
                "cl100k_base"
            ),
        )
    )


    run_chunking(
        db=db,

        document_id=(
            document_id
        ),

        payload=(
            chunk_request
        ),
    )
    update_job(
        db,
        job,

        stage="text_embedding",

        progress=50,
    )


    embed_document(
        db=db,

        document_id=document_id,

        force=False,
    )

    if document_has_visuals(
        db,
        document_id,
    ):

        update_job(
            db,
            job,

            stage="visual_embedding",

            progress=70,
        )


        embed_visual_assets(
            db=db,

            document_id=(
                document_id
            ),

            force=False,

            include_page_images=True,

            include_embedded_images=True,
        )
        update_job(
            db,
            job,

            stage="visual_analysis",

            progress=85,
        )


        analyze_document_visuals(
            db=db,

            document_id=(
                document_id
            ),

            force=False,

            asset_types=[
                "page",
                "embedded_image",
            ],
        )
    document = db.get(
        Document,
        document_id,
    )


    if document:

        document.status = "ready"

        document.error_message = None


    update_job(
        db,
        job,

        status="succeeded",

        stage="complete",

        progress=100,
    )


    db.commit()
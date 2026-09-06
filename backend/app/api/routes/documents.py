import uuid
import logging

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.document import (
    DocumentRead,
    DocumentUploadResponse,
)

from app.services.document_ingestion import (
    DuplicateDocumentError,
    FileTooLargeError,
    KnowledgeBaseNotFoundError,
    UnsupportedFileTypeError,
    get_document,
    ingest_document,
    list_documents,
)

from app.schemas.chunking import (
    ChunkingRequest,
    ChunkingResponse,
    ChunkingRunRead,
    ChunkRead,
)

from app.services.document_chunking import (
    DocumentNotFoundError,
    DocumentNotReadyError,
    list_chunking_runs,
    list_chunks,
    run_chunking,
)

from app.schemas.embedding import (
    EmbedDocumentRequest,
    EmbedDocumentResponse,
)

from app.services.text_embeddings import (
    ActiveChunkingRunNotFoundError,
    DocumentEmbeddingNotReadyError,
    embed_document,
)

from app.schemas.visual_embedding import (
    EmbedVisualAssetsRequest,
    EmbedVisualAssetsResponse,
)

from app.services.visual_embeddings import (
    VisualEmbeddingNotReadyError,
    embed_visual_assets,
)

from app.schemas.visual_analysis import (
    AnalyzeVisualsRequest,
)

from app.services.visual_analysis import (
    analyze_document_visuals,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["documents"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    knowledge_base_id: uuid.UUID,
    file: Annotated[
        UploadFile,
        File(
            description=(
                "PDF, DOCX, TXT, or Markdown document"
            )
        ),
    ],
    db: DatabaseSession,
):

    try:

        return await ingest_document(
            db=db,
            knowledge_base_id=(
                knowledge_base_id
            ),
            upload=file,
        )

    except KnowledgeBaseNotFoundError:

        raise HTTPException(
            status_code=404,
            detail=(
                "Knowledge base not found."
            ),
        )

    except UnsupportedFileTypeError as exc:

        raise HTTPException(
            status_code=415,
            detail=str(exc),
        )

    except FileTooLargeError as exc:

        raise HTTPException(
            status_code=413,
            detail=str(exc),
        )

    except DuplicateDocumentError as exc:

        raise HTTPException(
            status_code=409,
            detail={
                "message":
                    "This document already exists "
                    "in the knowledge base.",

                "document_id":
                    str(exc.document_id),
            },
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Document ingestion failed."
            ),
        )


@router.post(
    "/documents/{document_id}/chunk",
    response_model=ChunkingResponse,
)
def chunk_document(
    document_id: uuid.UUID,
    payload: ChunkingRequest,
    db: DatabaseSession,
):

    try:

        run, chunks = run_chunking(
            db=db,
            document_id=document_id,
            payload=payload,
        )

        return {
            "run": run,
            "preview": chunks[:5],
        }

    except DocumentNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    except DocumentNotReadyError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Document chunking failed."
            ),
        )

@router.get(
    "/documents/{document_id}/chunking-runs",
    response_model=list[ChunkingRunRead],
)
def chunking_runs(
    document_id: uuid.UUID,
    db: DatabaseSession,
):

    return list_chunking_runs(
        db,
        document_id,
    )

@router.get(
    "/chunking-runs/{run_id}/chunks",
    response_model=list[ChunkRead],
)
def chunks_for_run(
    run_id: uuid.UUID,
    db: DatabaseSession,
    limit: int = 100,
):

    limit = min(
        max(limit, 1),
        500,
    )

    return list_chunks(
        db,
        run_id,
        limit,
    )

@router.post(
    "/documents/{document_id}/embed",
    response_model=EmbedDocumentResponse,
)
def embed_document_chunks(
    document_id: uuid.UUID,
    payload: EmbedDocumentRequest,
    db: DatabaseSession,
):

    try:

        return embed_document(
            db=db,
            document_id=document_id,
            force=payload.force,
        )

    except (
        ActiveChunkingRunNotFoundError,
        DocumentEmbeddingNotReadyError,
    ) as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except Exception as exce:
        logger.exception(
            "Document embedding failed for document_id=%s",
            document_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Document embedding failed.",
        ) from exce

@router.get(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=list[DocumentRead],
)

@router.post(
    "/documents/{document_id}/embed-visuals",
    response_model=EmbedVisualAssetsResponse,
)
def embed_document_visuals(
    document_id: uuid.UUID,
    payload: EmbedVisualAssetsRequest,
    db: DatabaseSession,
):

    try:

        return embed_visual_assets(
            db=db,
            document_id=document_id,
            force=payload.force,
            include_page_images=(
                payload.include_page_images
            ),
            include_embedded_images=(
                payload.include_embedded_images
            ),
        )

    except (
        VisualEmbeddingNotReadyError
    ) as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Visual embedding failed."
            ),
        )

def documents_for_knowledge_base(
    knowledge_base_id: uuid.UUID,
    db: DatabaseSession,
):

    return list_documents(
        db,
        knowledge_base_id,
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentRead,
)
def document_details(
    document_id: uuid.UUID,
    db: DatabaseSession,
):

    document = get_document(
        db,
        document_id,
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return document

@router.post(
    "/documents/{document_id}/analyze-visuals"
)
def analyze_visuals(
    document_id: uuid.UUID,
    payload: AnalyzeVisualsRequest,
    db: DatabaseSession,
):

    return analyze_document_visuals(
        db=db,

        document_id=document_id,

        force=payload.force,

        asset_types=(
            payload.asset_types
        ),
    )
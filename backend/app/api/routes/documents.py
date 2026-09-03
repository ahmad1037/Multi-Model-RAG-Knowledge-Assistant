import uuid

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


@router.get(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=list[DocumentRead],
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
import logging
import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.document import Document
from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.models.visual_asset import (
    VisualAsset,
)

from app.rag.ingestion.parsers import (
    parse_document,
)

from app.services.file_storage import (
    FileTooLargeError,
    StagedUpload,
    StorageManager,
    UnsupportedFileTypeError,
)


logger = logging.getLogger(
    __name__
)


storage = StorageManager(
    root=settings.storage_root,
    max_upload_size_mb=(
        settings.max_upload_size_mb
    ),
)

def list_documents(
    db: Session,
    knowledge_base_id: uuid.UUID,
) -> list[Document]:

    statement = (
        select(Document)
        .where(
            Document.knowledge_base_id
            == knowledge_base_id
        )
        .order_by(
            Document.created_at.desc()
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


def get_document(
    db: Session,
    document_id: uuid.UUID,
) -> Document | None:

    return db.get(
        Document,
        document_id,
    )

class KnowledgeBaseNotFoundError(
    Exception
):
    pass


class DuplicateDocumentError(
    Exception
):

    def __init__(
        self,
        document_id: uuid.UUID,
    ):
        self.document_id = (
            document_id
        )


async def ingest_document(
    db: Session,
    knowledge_base_id: uuid.UUID,
    upload: UploadFile,
):

    knowledge_base = db.get(
        KnowledgeBase,
        knowledge_base_id,
    )

    if knowledge_base is None:
        raise KnowledgeBaseNotFoundError

    staged: StagedUpload | None = None

    try:

        staged = (
            await storage.stage_upload(
                upload
            )
        )

        duplicate_statement = (
            select(Document)
            .where(
                Document.knowledge_base_id
                == knowledge_base_id,

                Document.checksum_sha256
                == staged.checksum_sha256,
            )
        )

        duplicate = db.scalar(
            duplicate_statement
        )

        if duplicate:

            storage.remove_staged(
                staged
            )

            raise DuplicateDocumentError(
                duplicate.id
            )

        document_id = uuid.uuid4()

        (
            stored_filename,
            relative_path,
        ) = storage.finalize_upload(
            staged,
            document_id,
        )

        document = Document(
            id=document_id,
            knowledge_base_id=(
                knowledge_base_id
            ),
            original_filename=(
                staged.original_filename
            ),
            stored_filename=(
                stored_filename
            ),
            storage_path=(
                relative_path
            ),
            media_type=(
                staged.media_type
            ),
            file_size_bytes=(
                staged.size_bytes
            ),
            checksum_sha256=(
                staged.checksum_sha256
            ),
            status="extracting",
            document_metadata={},
        )

        db.add(document)

        db.commit()

        db.refresh(document)

        try:

            absolute_path = (
                storage.resolve(
                    document.storage_path
                )
            )

            result = parse_document(
                file_path=absolute_path,
                document_id=document.id,
                storage_root=storage.root,
            )

            for visual in result.visuals:

                db.add(
                    VisualAsset(
                        document_id=document.id,
                        knowledge_base_id=(
                            knowledge_base_id
                        ),
                        page_number=(
                            visual.page_number
                        ),
                        asset_index=(
                            visual.asset_index
                        ),
                        asset_type=(
                            visual.asset_type
                        ),
                        storage_path=(
                            visual.storage_path
                        ),
                        mime_type=(
                            visual.mime_type
                        ),
                        checksum_sha256=(
                            visual.checksum_sha256
                        ),
                        width_px=(
                            visual.width_px
                        ),
                        height_px=(
                            visual.height_px
                        ),
                        visual_metadata={},
                    )
                )

            extraction_path = (
                storage.save_extraction(
                    document.id,
                    result,
                )
            )

            text_characters = sum(
                len(page.text)
                for page in result.pages
            )

            document.page_count = (
                result.page_count
            )

            document.status = (
                "ready_for_chunking"
            )

            document.error_message = None

            document.document_metadata = {
                "extraction_path":
                    extraction_path,

                "text_characters":
                    text_characters,

                "visual_assets_count":
                    len(result.visuals),
            }

            db.commit()

            db.refresh(document)

            return {
                "document": document,

                "text_characters":
                    text_characters,

                "page_count":
                    result.page_count,

                "visual_assets":
                    len(result.visuals),

                "extraction_path":
                    extraction_path,
            }

        except Exception as exc:

            logger.exception(
                "Document parsing failed",
                extra={
                    "document_id":
                        str(document.id),
                },
            )

            document.status = "failed"

            document.error_message = (
                str(exc)[:2000]
            )

            db.commit()

            raise

    except (
        UnsupportedFileTypeError,
        FileTooLargeError,
        DuplicateDocumentError,
        KnowledgeBaseNotFoundError,
    ):
        raise
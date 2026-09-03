import hashlib
import json
import shutil
import uuid

from dataclasses import asdict, dataclass
from pathlib import Path

from fastapi import UploadFile

from app.rag.ingestion.types import ParseResult


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


class UnsupportedFileTypeError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


@dataclass
class StagedUpload:
    path: Path

    original_filename: str
    extension: str

    media_type: str

    size_bytes: int

    checksum_sha256: str


class StorageManager:

    def __init__(
        self,
        root: Path,
        max_upload_size_mb: int,
    ):
        self.root = root.resolve()

        self.max_upload_bytes = (
            max_upload_size_mb
            * 1024
            * 1024
        )

        self.staging_dir = (
            self.root / "staging"
        )

        self.upload_dir = (
            self.root / "uploads"
        )

        self.processed_dir = (
            self.root / "processed"
        )

        self.page_images_dir = (
            self.root / "page_images"
        )

        self.extracted_images_dir = (
            self.root / "extracted_images"
        )

        for directory in (
            self.staging_dir,
            self.upload_dir,
            self.processed_dir,
            self.page_images_dir,
            self.extracted_images_dir,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    async def stage_upload(
        self,
        upload: UploadFile,
    ) -> StagedUpload:

        if not upload.filename:
            raise UnsupportedFileTypeError(
                "The uploaded file has no filename."
            )

        extension = (
            Path(upload.filename)
            .suffix
            .lower()
        )

        if extension not in ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"Unsupported file type: {extension}"
            )

        staging_path = (
            self.staging_dir
            / f"{uuid.uuid4().hex}{extension}"
        )

        hasher = hashlib.sha256()

        size_bytes = 0

        try:
            with staging_path.open("wb") as destination:

                while True:
                    chunk = await upload.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    size_bytes += len(chunk)

                    if (
                        size_bytes
                        > self.max_upload_bytes
                    ):
                        raise FileTooLargeError(
                            "Uploaded file exceeds "
                            "the configured size limit."
                        )

                    hasher.update(chunk)

                    destination.write(chunk)

        except Exception:
            staging_path.unlink(
                missing_ok=True
            )

            raise

        finally:
            await upload.close()

        return StagedUpload(
            path=staging_path,
            original_filename=upload.filename,
            extension=extension,
            media_type=(
                upload.content_type
                or "application/octet-stream"
            ),
            size_bytes=size_bytes,
            checksum_sha256=hasher.hexdigest(),
        )

    def finalize_upload(
        self,
        staged: StagedUpload,
        document_id: uuid.UUID,
    ) -> tuple[str, str]:

        directory = (
            self.upload_dir
            / str(document_id)
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        stored_filename = (
            f"{document_id}"
            f"{staged.extension}"
        )

        final_path = (
            directory
            / stored_filename
        )

        shutil.move(
            str(staged.path),
            str(final_path),
        )

        relative_path = (
            final_path
            .relative_to(self.root)
            .as_posix()
        )

        return (
            stored_filename,
            relative_path,
        )

    def resolve(
        self,
        relative_path: str,
    ) -> Path:

        return (
            self.root
            / relative_path
        )

    def remove_staged(
        self,
        staged: StagedUpload,
    ) -> None:

        staged.path.unlink(
            missing_ok=True
        )

    def save_extraction(
        self,
        document_id: uuid.UUID,
        result: ParseResult,
    ) -> str:

        directory = (
            self.processed_dir
            / str(document_id)
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = (
            directory
            / "extraction.json"
        )

        payload = {
            "pages": [
                asdict(page)
                for page in result.pages
            ],
            "visuals": [
                asdict(visual)
                for visual in result.visuals
            ],
            "page_count": result.page_count,
        }

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return (
            path
            .relative_to(self.root)
            .as_posix()
        )
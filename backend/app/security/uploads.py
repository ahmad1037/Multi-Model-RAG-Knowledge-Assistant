from pathlib import Path

from fastapi import HTTPException

from app.core.config import settings


def allowed_extensions() -> set[str]:

    return {

        extension
        .strip()
        .lower()

        for extension
        in settings
        .allowed_upload_extensions
        .split(",")

        if extension.strip()
    }


def validate_filename(
    filename: str | None,
) -> None:

    if not filename:

        raise HTTPException(
            status_code=400,
            detail=(
                "Uploaded file "
                "has no filename."
            ),
        )


    extension = (
        Path(filename)
        .suffix
        .lower()
    )


    if (
        extension
        not in allowed_extensions()
    ):

        raise HTTPException(
            status_code=415,

            detail=(
                "Unsupported file type: "
                f"{extension}"
            ),
        )


def validate_file_size(
    size_bytes: int,
) -> None:

    if (
        size_bytes
        > settings.max_upload_bytes
    ):

        raise HTTPException(
            status_code=413,

            detail=(
                "Uploaded file exceeds "
                "the maximum allowed size."
            ),
        )
import tempfile

from pathlib import Path

from fastapi import UploadFile



ALLOWED_IMAGE_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


class UnsupportedQueryImageError(
    Exception
):
    pass


async def save_query_image(
    upload: UploadFile,
) -> Path:

    content_type = (
        upload.content_type
        or ""
    )

    extension = (
        ALLOWED_IMAGE_TYPES.get(
            content_type
        )
    )

    if extension is None:

        raise (
            UnsupportedQueryImageError(
                "Query image must be "
                "PNG, JPEG, or WebP."
            )
        )

    temp = tempfile.NamedTemporaryFile(
        suffix=extension,
        delete=False,
    )

    path = Path(
        temp.name
    )

    try:

        while True:

            chunk = await upload.read(
                1024 * 1024
            )

            if not chunk:
                break

            temp.write(
                chunk
            )

    finally:

        temp.close()

        await upload.close()

    return path
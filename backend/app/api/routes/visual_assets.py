import uuid

from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
)

from fastapi.responses import (
    FileResponse,
)

from app.core.config import settings
from app.db.session import SessionLocal

from app.models.visual_asset import (
    VisualAsset,
)


router = APIRouter(
    prefix="/visual-assets",
    tags=["visual-assets"],
)


@router.get(
    "/{visual_asset_id}/content"
)
def visual_asset_content(
    visual_asset_id: uuid.UUID,
):

    with SessionLocal() as db:

        asset = db.get(
            VisualAsset,
            visual_asset_id,
        )

        if asset is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Visual asset not found."
                ),
            )

        path = (
            settings
            .storage_root
            .resolve()
            / asset.storage_path
        )

        if not path.exists():

            raise HTTPException(
                status_code=404,
                detail=(
                    "Visual asset file "
                    "does not exist."
                ),
            )

        return FileResponse(
            path=path,
            media_type=(
                asset.mime_type
            ),
        )
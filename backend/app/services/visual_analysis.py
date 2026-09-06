import logging
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.document import Document
from app.models.visual_asset import VisualAsset

from app.rag.vision.prompts import (
    VISUAL_ANALYSIS_PROMPT,
)

from app.rag.vision.parsing import (
    validate_visual_analysis,
)

from app.rag.vision.vlm import (
    get_visual_analyzer,
)


logger = logging.getLogger(
    __name__
)

def analyze_document_visuals(
    db: Session,
    document_id: uuid.UUID,
    force: bool = False,
    asset_types: list[str] | None = None,
) -> dict:

    document = db.get(
        Document,
        document_id,
    )

    if document is None:

        raise ValueError(
            "Document not found."
        )

    asset_types = asset_types or [
        "page",
        "embedded_image",
    ]

    statement = (
        select(VisualAsset)
        .where(
            VisualAsset.document_id
            == document_id,

            VisualAsset.asset_type.in_(
                asset_types
            ),
        )
        .order_by(
            VisualAsset.asset_index
        )
        .limit(
            settings
            .vlm_max_assets_per_request
        )
    )

    assets = list(
        db.scalars(
            statement
        ).all()
    )

    analyzer = (
        get_visual_analyzer()
    )

    analyzed = 0
    skipped = 0
    failed = 0

    for asset in assets:

        current = (
            asset.vlm_status
            == "ready"

            and asset.vlm_model
            == settings.vlm_model

            and asset.vlm_prompt_version
            == settings.vlm_prompt_version
        )

        if current and not force:

            skipped += 1

            continue

        path = (
            settings.storage_root.resolve()
            / asset.storage_path
        )

        if not path.exists():

            asset.vlm_status = "failed"

            asset.vlm_error_message = (
                "Visual file does not exist."
            )

            failed += 1

            db.commit()

            continue

        try:

            asset.vlm_status = (
                "processing"
            )

            asset.vlm_error_message = None

            db.commit()

            raw_output = (
                analyzer.analyze(
                    path,
                    VISUAL_ANALYSIS_PROMPT,
                )
            )

            analysis = (
                validate_visual_analysis(
                    raw_output
                )
            )

            metadata = dict(
                asset.visual_metadata
                or {}
            )

            metadata[
                "vlm_analysis"
            ] = analysis.model_dump()

            asset.visual_metadata = (
                metadata
            )

            asset.visual_description = (
                analysis.summary
            )

            asset.vlm_model = (
                settings.vlm_model
            )

            asset.vlm_prompt_version = (
                settings
                .vlm_prompt_version
            )

            asset.vlm_status = "ready"

            analyzed += 1

            db.commit()

        except Exception as exc:

            logger.exception(
                "VLM analysis failed",
                extra={
                    "visual_asset_id":
                        str(asset.id)
                },
            )

            db.rollback()

            failed_asset = db.get(
                VisualAsset,
                asset.id,
            )

            if failed_asset:

                failed_asset.vlm_status = (
                    "failed"
                )

                failed_asset.vlm_error_message = (
                    str(exc)[:2000]
                )

                db.commit()

            failed += 1

    return {
        "document_id":
            document_id,

        "model":
            settings.vlm_model,

        "analyzed":
            analyzed,

        "skipped":
            skipped,

        "failed":
            failed,
    }


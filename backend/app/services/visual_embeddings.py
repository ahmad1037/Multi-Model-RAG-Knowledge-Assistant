import logging
import uuid

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.document import (
    Document,
)

from app.models.visual_asset import (
    VisualAsset,
)

from app.rag.vision.clip_embedder import (
    get_clip_embedder,
)


logger = logging.getLogger(
    __name__
)


class VisualEmbeddingNotReadyError(
    Exception
):
    pass


def _resolve_asset_path(
    asset: VisualAsset,
) -> Path:

    return (
        settings.storage_root.resolve()
        / asset.storage_path
    )


def embed_visual_assets(
    db: Session,
    document_id: uuid.UUID,
    force: bool = False,
    include_page_images: bool = True,
    include_embedded_images: bool = True,
) -> dict:

    document = db.get(
        Document,
        document_id,
    )

    if document is None:

        raise (
            VisualEmbeddingNotReadyError(
                "Document not found."
            )
        )

    allowed_asset_types = set()

    if include_page_images:

        allowed_asset_types.add(
            "page"
        )

    if include_embedded_images:

        allowed_asset_types.add(
            "embedded_image"
        )

    if not allowed_asset_types:

        raise ValueError(
            "At least one visual asset type "
            "must be enabled."
        )

    statement = (
        select(VisualAsset)
        .where(
            VisualAsset.document_id
            == document_id,

            VisualAsset.asset_type.in_(
                allowed_asset_types
            ),
        )
        .order_by(
            VisualAsset.asset_index
        )
    )

    assets = list(
        db.scalars(
            statement
        ).all()
    )

    if not assets:

        raise (
            VisualEmbeddingNotReadyError(
                "Document contains no "
                "eligible visual assets."
            )
        )

    to_embed: list[
        VisualAsset
    ] = []

    skipped = 0

    for asset in assets:

        current = (
            asset.clip_embedding
            is not None
            and asset.clip_model
            == settings.clip_model_name
            and asset.clip_pretrained
            == settings.clip_pretrained
            and asset.clip_dimension
            == settings.clip_embedding_dimension
        )

        if current and not force:

            skipped += 1

        else:

            to_embed.append(
                asset
            )

    embedder = (
        get_clip_embedder()
    )

    embedded_count = 0

    failed_count = 0

    batch_size = (
        settings.clip_batch_size
    )

    for start in range(
        0,
        len(to_embed),
        batch_size,
    ):

        batch_assets = to_embed[
            start:
            start + batch_size
        ]

        valid_assets = []

        valid_paths = []

        for asset in batch_assets:

            path = _resolve_asset_path(
                asset
            )

            if not path.exists():

                asset.clip_embedding_status = (
                    "failed"
                )

                failed_count += 1

                logger.warning(
                    "Visual asset file missing",
                    extra={
                        "visual_asset_id":
                            str(asset.id),

                        "storage_path":
                            asset.storage_path,
                    },
                )

                continue

            valid_assets.append(
                asset
            )

            valid_paths.append(
                path
            )

        if not valid_assets:
            continue

        try:

            vectors = (
                embedder.encode_images(
                    valid_paths
                )
            )

            for asset, vector in zip(
                valid_assets,
                vectors,
                strict=True,
            ):

                asset.clip_embedding = (
                    vector
                )

                asset.clip_model = (
                    settings.clip_model_name
                )

                asset.clip_pretrained = (
                    settings.clip_pretrained
                )

                asset.clip_dimension = (
                    settings
                    .clip_embedding_dimension
                )

                asset.clip_embedding_status = (
                    "ready"
                )

                embedded_count += 1

            db.commit()

        except Exception:

            logger.exception(
                "CLIP visual embedding "
                "batch failed",
                extra={
                    "document_id":
                        str(document_id),
                },
            )

            db.rollback()

            for asset in batch_assets:

                refreshed = db.get(
                    VisualAsset,
                    asset.id,
                )

                if refreshed:

                    refreshed.clip_embedding_status = (
                        "failed"
                    )

                    failed_count += 1

            db.commit()

    return {
        "document_id":
            document_id,

        "model":
            settings.clip_model_name,

        "pretrained":
            settings.clip_pretrained,

        "dimension":
            (
                settings
                .clip_embedding_dimension
            ),

        "assets_total":
            len(assets),

        "assets_embedded":
            embedded_count,

        "assets_skipped":
            skipped,

        "assets_failed":
            failed_count,
    }
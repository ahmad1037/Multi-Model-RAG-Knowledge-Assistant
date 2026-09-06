import uuid

from sqlalchemy import (
    select,
    text,
)
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


class KnowledgeBaseHasNoVisualEmbeddingsError(
    Exception
):
    pass


def _configure_search(
    db: Session,
    mode: str,
) -> None:

    if mode == "exact":

        db.execute(
            text(
                "SET LOCAL "
                "enable_indexscan = off"
            )
        )

    elif mode == "hnsw":

        ef_search = int(
            settings.clip_hnsw_ef_search
        )

        db.execute(
            text(
                f"SET LOCAL "
                f"hnsw.ef_search = "
                f"{ef_search}"
            )
        )

        db.execute(
            text(
                "SET LOCAL "
                "hnsw.iterative_scan = "
                "strict_order"
            )
        )

    else:

        raise ValueError(
            f"Unknown visual search mode: "
            f"{mode}"
        )


def text_to_image_search(
    db: Session,
    knowledge_base_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    mode: str = "exact",
    asset_type: str = "all",
) -> list[dict]:

    embedder = (
        get_clip_embedder()
    )

    query_vector = (
        embedder.encode_text(
            query
        )
    )

    _configure_search(
        db,
        mode,
    )

    distance = (
        VisualAsset.clip_embedding
        .cosine_distance(
            query_vector
        )
        .label(
            "cosine_distance"
        )
    )

    statement = (
        select(
            VisualAsset,
            Document.original_filename,
            distance,
        )
        .join(
            Document,
            Document.id
            == VisualAsset.document_id,
        )
        .where(
            VisualAsset.knowledge_base_id
            == knowledge_base_id,

            VisualAsset.clip_embedding
            .is_not(None),

            VisualAsset.clip_model
            == settings.clip_model_name,

            VisualAsset.clip_pretrained
            == settings.clip_pretrained,

            VisualAsset.clip_dimension
            == settings.clip_embedding_dimension,

            VisualAsset.clip_embedding_status
            == "ready",
        )
    )

    if asset_type != "all":

        statement = statement.where(
            VisualAsset.asset_type
            == asset_type
        )

    statement = (
        statement
        .order_by(
            distance
        )
        .limit(
            top_k
        )
    )

    try:

        rows = db.execute(
            statement
        ).all()

    finally:

        if mode == "exact":

            db.execute(
                text(
                    "SET LOCAL "
                    "enable_indexscan = on"
                )
            )

    if not rows:

        raise (
            KnowledgeBaseHasNoVisualEmbeddingsError(
                "No CLIP-embedded visual "
                "assets were found for "
                "this knowledge base."
            )
        )

    results = []

    for (
        asset,
        document_name,
        cosine_distance,
    ) in rows:

        distance_value = float(
            cosine_distance
        )

        results.append(
            {
                "visual_asset_id":
                    asset.id,

                "document_id":
                    asset.document_id,

                "document_name":
                    document_name,

                "page_number":
                    asset.page_number,

                "asset_index":
                    asset.asset_index,

                "asset_type":
                    asset.asset_type,

                "storage_path":
                    asset.storage_path,

                "visual_description":
                    asset.visual_description,

                "width_px":
                    asset.width_px,

                "height_px":
                    asset.height_px,

                "cosine_distance":
                    distance_value,

                "similarity":
                    1.0
                    - distance_value,
            }
        )

    return results

def image_vector_search(
    db: Session,
    knowledge_base_id: uuid.UUID,
    query_vector: list[float],
    top_k: int = 5,
    mode: str = "exact",
    asset_type: str = "all",
) -> list[dict]:

    _configure_search(
        db,
        mode,
    )

    distance = (
        VisualAsset.clip_embedding
        .cosine_distance(
            query_vector
        )
        .label(
            "cosine_distance"
        )
    )

    statement = (
        select(
            VisualAsset,
            Document.original_filename,
            distance,
        )
        .join(
            Document,
            Document.id
            == VisualAsset.document_id,
        )
        .where(
            VisualAsset.knowledge_base_id
            == knowledge_base_id,

            VisualAsset.clip_embedding
            .is_not(None),

            VisualAsset.clip_model
            == settings.clip_model_name,

            VisualAsset.clip_pretrained
            == settings.clip_pretrained,

            VisualAsset.clip_dimension
            == settings.clip_embedding_dimension,

            VisualAsset.clip_embedding_status
            == "ready",
        )
    )

    if asset_type != "all":

        statement = statement.where(
            VisualAsset.asset_type
            == asset_type
        )

    rows = db.execute(
        statement
        .order_by(
            distance
        )
        .limit(top_k)
    ).all()

    if not rows:

        raise (
            KnowledgeBaseHasNoVisualEmbeddingsError(
                "No visual embeddings found."
            )
        )

    results = []

    for (
        asset,
        document_name,
        cosine_distance,
    ) in rows:

        distance_value = float(
            cosine_distance
        )

        results.append(
            {
                "visual_asset_id":
                    asset.id,

                "document_id":
                    asset.document_id,

                "document_name":
                    document_name,

                "page_number":
                    asset.page_number,

                "asset_index":
                    asset.asset_index,

                "asset_type":
                    asset.asset_type,

                "storage_path":
                    asset.storage_path,

                "visual_description":
                    asset.visual_description,

                "width_px":
                    asset.width_px,

                "height_px":
                    asset.height_px,

                "cosine_distance":
                    distance_value,

                "similarity":
                    1.0
                    - distance_value,
            }
        )

    return results
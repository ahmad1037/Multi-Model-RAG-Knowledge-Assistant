import uuid

from pydantic import BaseModel


class EmbedVisualAssetsRequest(
    BaseModel
):

    force: bool = False

    include_page_images: bool = True

    include_embedded_images: bool = True


class EmbedVisualAssetsResponse(
    BaseModel
):

    document_id: uuid.UUID

    model: str

    pretrained: str

    dimension: int

    assets_total: int

    assets_embedded: int

    assets_skipped: int

    assets_failed: int
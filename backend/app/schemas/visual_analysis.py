from pydantic import (
    BaseModel,
    Field,
)


class VisualKeyValue(BaseModel):

    label: str

    value: str | None = None

    unit: str | None = None


class VisualAnalysis(BaseModel):

    visual_type: str

    title: str | None = None

    summary: str

    visible_text: list[str] = Field(
        default_factory=list
    )

    key_values: list[
        VisualKeyValue
    ] = Field(
        default_factory=list
    )

    relationships: list[str] = Field(
        default_factory=list
    )

    uncertainties: list[str] = Field(
        default_factory=list
    )

class AnalyzeVisualsRequest(
    BaseModel
):

    force: bool = False

    asset_types: list[str] = [
        "page",
        "embedded_image",
    ]


class AnalyzeVisualsResponse(
    BaseModel
):

    document_id: str

    model: str

    analyzed: int

    skipped: int

    failed: int


import uuid
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    StringConstraints,
)
CitationId = Annotated[
    str,
    StringConstraints(
        pattern=r"^S\d+$"
    ),
]


class GroundedModelOutput(
    BaseModel
):

    answerable: bool

    answer: str

    citations: list[
        CitationId
    ]
    refusal_reason: str


class VerificationOutput(
    BaseModel
):

    all_claims_supported: bool

    unsupported_claims: list[str]

    supporting_source_ids: list[str]

    explanation: str

class SourceCitation(
    BaseModel
):

    source_id: str

    evidence_type: str

    document_id: uuid.UUID

    document_name: str

    page_start: int | None

    page_end: int | None

    heading: str | None = None

    visual_asset_id: (
        uuid.UUID | None
    ) = None


class GroundedQuestionRequest(
    BaseModel
):

    question: str = Field(
        min_length=2,
        max_length=4000,
    )

    verify_grounding: bool = True


class GroundedAnswerResponse(
    BaseModel
):

    answerable: bool

    answer: str

    citations: list[str]

    sources: list[
        SourceCitation
    ]

    refusal_reason: str | None

    generation_model: str

    grounding_verified: bool

    unsupported_claims: list[str]
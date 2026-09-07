import uuid

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
class ConversationSummaryOutput(
    BaseModel
):

    summary: str

class ConversationCreate(
    BaseModel
):

    title: str | None = Field(
        default=None,
        max_length=300,
    )


class ConversationRead(
    BaseModel
):

    id: uuid.UUID

    knowledge_base_id: uuid.UUID

    title: str | None

    summary: str | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class MessageRead(
    BaseModel
):

    id: uuid.UUID

    role: str

    content: str

    citations: list

    model_name: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
    
class ConversationTurnRequest(
    BaseModel
):

    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    verify_grounding: bool = True


class ConversationTurnResponse(
    BaseModel
):

    conversation_id: uuid.UUID

    user_message_id: uuid.UUID

    assistant_message_id: (
        uuid.UUID | None
    )

    standalone_question: str

    depends_on_history: bool

    answerable: bool

    answer: str

    citations: list[str]

    sources: list[dict]

    grounding_verified: bool

    clarification_needed: bool

    clarification_question: str
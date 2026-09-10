from sqlalchemy import select

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.conversation import (
    Conversation,
)

from app.models.message import (
    Message,
)

from app.rag.generation.factory import (
    get_generation_provider,
)

from app.rag.memory.prompts import (
    CONVERSATION_SUMMARY_PROMPT,
)

from app.schemas.conversation import (
    ConversationSummaryOutput,
)
def maybe_update_summary(
    db: Session,
    conversation: Conversation,
) -> None:

    statement = (
        select(Message)
        .where(
            Message.conversation_id
            == conversation.id
        )
        .order_by(
            Message.created_at
        )
    )

    messages = list(
        db.scalars(
            statement
        ).all()
    )

    total = len(
        messages
    )

    if (
        total
        < settings
        .conversation_summary_trigger
    ):

        return

    new_messages = (
        total
        - conversation
        .summarized_message_count
    )

    if (
        conversation.summary
        and new_messages
        < settings
        .conversation_summary_refresh_every
    ):

        return
    transcript = "\n\n".join(
        (
            f"{message.role.upper()}: "
            f"{message.content}"
        )
        for message in messages
    )

    provider = (
        get_generation_provider()
    )

    result = provider.generate(
        operation="conversation_summary",
        model=(
            settings
            .conversation_summary_model
        ),

        system_prompt=(
            CONVERSATION_SUMMARY_PROMPT
        ),

        user_prompt=f"""
EXISTING SUMMARY

{conversation.summary or "(none)"}


CONVERSATION

{transcript}
""",

        response_model=(
            ConversationSummaryOutput
        ),
    )

    conversation.summary = (
        result.summary[
            :settings
            .conversation_summary_max_chars
        ]
    )

    conversation.summarized_message_count = (
        total
    )

    db.commit()
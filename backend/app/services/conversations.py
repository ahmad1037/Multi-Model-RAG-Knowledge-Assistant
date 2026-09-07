import uuid

from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.conversation import (
    Conversation,
)

from app.models.knowledge_base import (
    KnowledgeBase,
)

from app.models.message import (
    Message,
)


class ConversationNotFoundError(
    Exception
):
    pass


def create_conversation(
    db: Session,
    knowledge_base_id: uuid.UUID,
    title: str | None = None,
) -> Conversation:

    knowledge_base = db.get(
        KnowledgeBase,
        knowledge_base_id,
    )

    if knowledge_base is None:

        raise ValueError(
            "Knowledge base not found."
        )

    conversation = Conversation(
        knowledge_base_id=(
            knowledge_base_id
        ),

        title=title,

        summary=None,

        summarized_message_count=0,
    )

    db.add(
        conversation
    )

    db.commit()

    db.refresh(
        conversation
    )

    return conversation

def get_conversation(
    db: Session,
    conversation_id: uuid.UUID,
) -> Conversation:

    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is None:

        raise (
            ConversationNotFoundError
        )

    return conversation


def list_messages(
    db: Session,
    conversation_id: uuid.UUID,
) -> list[Message]:

    statement = (
        select(Message)
        .where(
            Message.conversation_id
            == conversation_id
        )
        .order_by(
            Message.created_at
        )
    )

    return list(
        db.scalars(
            statement
        ).all()
    )


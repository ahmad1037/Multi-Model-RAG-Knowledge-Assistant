import uuid

from sqlalchemy import (
    func,
    select,
)

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.message import Message


def recent_messages(
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
            Message.created_at.desc()
        )
        .limit(
            settings
            .conversation_recent_messages
        )
    )

    messages = list(
        db.scalars(
            statement
        ).all()
    )

    messages.reverse()

    return messages


def message_count(
    db: Session,
    conversation_id: uuid.UUID,
) -> int:

    statement = (
        select(
            func.count(
                Message.id
            )
        )
        .where(
            Message.conversation_id
            == conversation_id
        )
    )

    return int(
        db.scalar(statement)
        or 0
    )

def format_messages(
    messages: list[Message],
) -> str:

    lines = []

    for message in messages:

        role = (
            "USER"
            if message.role == "user"
            else "ASSISTANT"
        )

        lines.append(
            f"{role}: "
            f"{message.content}"
        )

    return "\n\n".join(
        lines
    )


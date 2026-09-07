import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from typing import Annotated
from sqlalchemy.orm import Session
from app.db.session import get_db

DatabaseSession = Annotated[
    Session,
    Depends(get_db)
]

from app.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    ConversationTurnRequest,
    ConversationTurnResponse,
    MessageRead,
)
from app.services.conversations import (
    ConversationNotFoundError,
    create_conversation,
    get_conversation,
    list_messages,
)
from app.schemas.conversation_turn import (
    run_conversation_turn,
)

router = APIRouter(
    tags=["conversations"],
)


@router.post(
    "/knowledge-bases/{kb_id}/conversations",
    response_model=ConversationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation_endpoint(
    kb_id: uuid.UUID,
    payload: ConversationCreate,
    db: DatabaseSession,
):
    try:
        return create_conversation(
            db=db,
            knowledge_base_id=kb_id,
            title=payload.title,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationRead,
)
def get_conversation_endpoint(
    conversation_id: uuid.UUID,
    db: DatabaseSession,
):
    try:
        return get_conversation(
            db=db,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Conversation not found.",
        ) from exc


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageRead],
)
def get_messages_endpoint(
    conversation_id: uuid.UUID,
    db: DatabaseSession,
):
    try:
        get_conversation(
            db=db,
            conversation_id=conversation_id,
        )

        return list_messages(
            db=db,
            conversation_id=conversation_id,
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Conversation not found.",
        ) from exc


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=(
        ConversationTurnResponse
    ),
)
def send_message(
    conversation_id: uuid.UUID,
    payload: ConversationTurnRequest,
    db: DatabaseSession,
):
    try:
        return run_conversation_turn(
            db=db,
            conversation_id=(
                conversation_id
            ),
            message_text=(
                payload.message
            ),
            verify_grounding=(
                payload.verify_grounding
            ),
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Conversation not found.",
        ) from exc
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.message import Message

from app.rag.memory.history import (
    format_messages,
    recent_messages,
)

from app.rag.memory.query_rewriter import (
    rewrite_question,
)

from app.rag.memory.summarizer import (
    maybe_update_summary,
)

from app.services.conversations import (
    get_conversation,
)

from app.services.grounded_generation import (
    answer_question,
)

def run_conversation_turn(
    db: Session,
    conversation_id: uuid.UUID,
    message_text: str,
    verify_grounding: bool = True,
) -> dict:

    conversation = (
        get_conversation(
            db,
            conversation_id,
        )
    )

    history_before = (
        recent_messages(
            db,
            conversation.id,
        )
    )

    history_text = (
        format_messages(
            history_before
        )
    )

    user_message = Message(
        conversation_id=(
            conversation.id
        ),

        role="user",

        content=message_text,

        citations=[],

        message_metadata={},
    )

    db.add(
        user_message
    )

    db.commit()

    db.refresh(
        user_message
    )

    rewrite = rewrite_question(
        current_question=(
            message_text
        ),

        conversation_summary=(
            conversation.summary
        ),

        recent_history=(
            history_text
        ),
    )
    if (
        rewrite.clarification_needed
    ):

        assistant_message = Message(
            conversation_id=(
                conversation.id
            ),

            role="assistant",

            content=(
                rewrite
                .clarification_question
            ),

            citations=[],

            model_name=(
                settings
                .conversation_rewrite_model
            ),

            message_metadata={
                "clarification": True,
            },
        )

        db.add(
            assistant_message
        )

        db.commit()

        db.refresh(
            assistant_message
        )

        return {
            "conversation_id":
                conversation.id,

            "user_message_id":
                user_message.id,

            "assistant_message_id":
                assistant_message.id,

            "standalone_question":
                rewrite
                .standalone_question,

            "depends_on_history":
                rewrite
                .depends_on_history,

            "answerable":
                False,

            "answer":
                rewrite
                .clarification_question,

            "citations":
                [],

            "sources":
                [],

            "grounding_verified":
                True,

            "clarification_needed":
                True,

            "clarification_question":
                rewrite
                .clarification_question,
        }
    conversation_context = f"""
SUMMARY

{conversation.summary or "(none)"}


RECENT CONVERSATION

{history_text or "(none)"}
"""
    answer = answer_question(
        db=db,

        knowledge_base_id=(
            conversation
            .knowledge_base_id
        ),

        question=message_text,

        retrieval_query=(
            rewrite
            .standalone_question
        ),

        conversation_context=(
            conversation_context
        ),

        verify_grounding=(
            verify_grounding
        ),
    )
    assistant_message = Message(
        conversation_id=(
            conversation.id
        ),

        role="assistant",

        content=(
            answer["answer"]
        ),

        citations=(
            answer["citations"]
        ),

        model_name=(
            settings
            .generation_model
        ),

        message_metadata={

            "standalone_question":
                rewrite
                .standalone_question,

            "depends_on_history":
                rewrite
                .depends_on_history,

            "resolved_references":
                rewrite
                .resolved_references,

            "sources":
                answer["sources"],

            "grounding_verified":
                answer[
                    "grounding_verified"
                ],

            "answerable":
                answer[
                    "answerable"
                ],
        },
    )

    db.add(
        assistant_message
    )

    db.commit()

    db.refresh(
        assistant_message
    )
    if (
        conversation.title
        is None
    ):

        conversation.title = (
            message_text[:80]
        )

        db.commit()
    maybe_update_summary(
        db,
        conversation,
    )
    return {
        "conversation_id":
            conversation.id,

        "user_message_id":
            user_message.id,

        "assistant_message_id":
            assistant_message.id,

        "standalone_question":
            rewrite
            .standalone_question,

        "depends_on_history":
            rewrite
            .depends_on_history,

        "answerable":
            answer[
                "answerable"
            ],

        "answer":
            answer[
                "answer"
            ],

        "citations":
            answer[
                "citations"
            ],

        "sources":
            answer[
                "sources"
            ],

        "grounding_verified":
            answer[
                "grounding_verified"
            ],

        "clarification_needed":
            False,

        "clarification_question":
            "",
    }
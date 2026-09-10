from app.core.config import settings

from app.rag.generation.factory import (
    get_generation_provider,
)

from app.rag.memory.prompts import (
    QUERY_REWRITE_PROMPT,
)

from app.schemas.query_rewrite import (
    QueryRewriteOutput,
)


def rewrite_question(
    *,
    current_question: str,
    conversation_summary: str | None,
    recent_history: str,
) -> QueryRewriteOutput:

    provider = (
        get_generation_provider()
    )

    user_prompt = f"""
CONVERSATION SUMMARY

{conversation_summary or "(none)"}


RECENT CONVERSATION

{recent_history or "(none)"}


CURRENT USER QUESTION

{current_question}


Rewrite the current question into a
standalone retrieval query.
"""

    return provider.generate(
        operation="query_rewrite",
        model=(
            settings
            .conversation_rewrite_model
        ),

        system_prompt=(
            QUERY_REWRITE_PROMPT
        ),

        user_prompt=user_prompt,

        response_model=(
            QueryRewriteOutput
        ),
    )
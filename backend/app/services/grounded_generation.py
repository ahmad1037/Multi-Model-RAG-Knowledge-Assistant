import uuid

from sqlalchemy.orm import Session

from app.core.config import settings

from app.rag.generation.citations import (
    build_source_records,
    validate_citations,
)

from app.rag.generation.citations import (
    CitationValidationError,
    build_source_records,
    validate_citations,
)

from app.rag.generation.context_formatter import (
    format_context,
)

from app.rag.generation.factory import (
    get_generation_provider,
)

from app.rag.generation.output_schemas import (
    GROUNDED_ANSWER_SCHEMA,
)

from app.rag.generation.prompts import (
    GROUNDED_SYSTEM_PROMPT,
)

from app.rag.generation.verifier import (
    verify_grounded_answer,
)

from app.schemas.generation import (
    GroundedModelOutput,
)

from app.services.context_pipeline import (
    retrieve_rerank_and_select,
)

def generate_with_valid_citations(
    *,
    question: str,
    context_items: list[dict],
) -> tuple[
    GroundedModelOutput,
    list[str],
]:

    generated = generate_once(
        question=question,
        context_items=context_items,
    )

    try:

        citations = validate_citations(
            answerable=(
                generated.answerable
            ),
            answer=generated.answer,
            declared_citations=(
                generated.citations
            ),
            context_items=(
                context_items
            ),
        )

        return (
            generated,
            citations,
        )

    except CitationValidationError as exc:

        correction = f"""
Your previous answer failed citation
validation.

Validation error:

{exc}

Rewrite the answer.

Citation requirements:

- Put citations inline exactly as [S1], [S2], etc.
- The citations array must contain IDs without
  brackets, for example ["S1", "S2"].
- Every inline citation must appear in the array.
- Every citation in the array must appear inline.
- Use ONLY source IDs supplied in the evidence.
- Do not invent citations.
"""

        generated = generate_once(
            question=question,
            context_items=context_items,
            corrective_instruction=(
                correction
            ),
        )

        citations = validate_citations(
            answerable=(
                generated.answerable
            ),
            answer=generated.answer,
            declared_citations=(
                generated.citations
            ),
            context_items=(
                context_items
            ),
        )

        return (
            generated,
            citations,
        )


def safe_refusal(
    question: str,
) -> dict:

    return {
        "answerable":
            False,

        "answer":
            (
                "I couldn't find enough "
                "supported evidence in the "
                "selected knowledge base "
                "to answer that question."
            ),

        "citations":
            [],

        "sources":
            [],

        "refusal_reason":
            (
                "Insufficient grounded "
                "evidence."
            ),

        "generation_model":
            settings
            .generation_model,

        "grounding_verified":
            True,

        "unsupported_claims":
            [],
    }

def generate_once(
    *,
    question: str,
    context_items: list[dict],
    corrective_instruction: str = "",
    conversation_context: str | None = None,
) -> GroundedModelOutput:

    provider = (
        get_generation_provider()
    )

    evidence = format_context(
        context_items
    )

    user_prompt = f"""
CONVERSATION CONTEXT

{conversation_context or "(none)"}

IMPORTANT:
Conversation context is provided only for
continuity and reference resolution.

It is NOT evidence and must never be cited.


USER QUESTION

{question}


RETRIEVED EVIDENCE

<evidence>

{evidence}

</evidence>
"""

    return provider.generate(
        model=(
            settings
            .generation_model
        ),

        system_prompt=(
            GROUNDED_SYSTEM_PROMPT
        ),

        user_prompt=user_prompt,

        response_model=(
            GroundedModelOutput
        ),
    )

def answer_question(
    db: Session,
    knowledge_base_id: uuid.UUID,
    question: str,
    verify_grounding: bool = True,
    retrieval_query: str | None = None,
    conversation_context: str | None = None,
) -> dict:

    retrieval = (
        retrieve_rerank_and_select(
        db=db,

        knowledge_base_id=(
            knowledge_base_id
        ),

        query=(
            retrieval_query
            or question
        ),
        )
    )

    context_items = (
        retrieval[
            "context"
        ][
            "items"
        ]
    )

    if not context_items:

        return safe_refusal(
            question
        )

    evidence_text = (
        format_context(
            context_items
        )
    )

    try:

        (
            generated,
            citations,
        ) = generate_with_valid_citations(
            question=question,
            context_items=context_items,
        )

    except CitationValidationError:

        return {
            "answerable":
                False,

            "answer":
                (
                    "I found relevant evidence, "
                    "but I couldn't produce an "
                    "answer with valid source "
                    "citations."
                ),

            "citations":
                [],

            "sources":
                [],

            "refusal_reason":
                (
                    "Citation validation "
                    "failed after retry."
                ),

            "generation_model":
                settings.generation_model,

            "grounding_verified":
                False,

            "unsupported_claims":
                [],
        }

    if not generated.answerable:

        return {
            "answerable":
                False,

            "answer":
                generated.answer,

            "citations":
                [],

            "sources":
                [],

            "refusal_reason":
                generated
                .refusal_reason,

            "generation_model":
                settings
                .generation_model,

            "grounding_verified":
                True,

            "unsupported_claims":
                [],
        }


    if not verify_grounding:

        sources = (
            build_source_records(
                context_items,
                citations,
            )
        )

        return {
            "answerable":
                True,

            "answer":
                generated.answer,

            "citations":
                citations,

            "sources":
                sources,

            "refusal_reason":
                None,

            "generation_model":
                settings
                .generation_model,

            "grounding_verified":
                False,

            "unsupported_claims":
                [],
        }


    verification = (
        verify_grounded_answer(
            question=question,

            answer=generated.answer,

            evidence_text=(
                evidence_text
            ),
        )
    )
    attempts = 0

    while (
        not verification
        .all_claims_supported

        and attempts
        < settings
        .max_grounding_retries
    ):

        attempts += 1

        unsupported = "\n".join(
            (
                f"- {claim}"
                for claim
                in verification
                .unsupported_claims
            )
        )

        correction = f"""
The previous answer contained these
unsupported claims:

{unsupported}

Generate a new answer that removes
those claims and uses only statements
directly supported by the evidence.
"""

        generated = generate_once(
            question=question,

            context_items=(
                context_items
            ),

            corrective_instruction=(
                correction
            ),
        )

        citations = (
            validate_citations(
                answerable=(
                    generated
                    .answerable
                ),

                answer=(
                    generated.answer
                ),

                declared_citations=(
                    generated.citations
                ),

                context_items=(
                    context_items
                ),
            )
        )

        if not generated.answerable:

            return safe_refusal(
                question
            )

        verification = (
            verify_grounded_answer(
                question=question,

                answer=(
                    generated.answer
                ),

                evidence_text=(
                    evidence_text
                ),
            )
        )
    if not (
        verification
        .all_claims_supported
    ):

        return {
            "answerable":
                False,

            "answer":
                (
                    "I found potentially "
                    "relevant evidence, but "
                    "I couldn't produce an "
                    "answer that passed the "
                    "grounding check."
                ),

            "citations":
                [],

            "sources":
                [],

            "refusal_reason":
                (
                    "Generated claims could "
                    "not be fully verified "
                    "against the evidence."
                ),

            "generation_model":
                settings
                .generation_model,

            "grounding_verified":
                False,

            "unsupported_claims":
                verification
                .unsupported_claims,
        }
    sources = build_source_records(
        context_items,
        citations,
    )

    return {
        "answerable":
            True,

        "answer":
            generated.answer,

        "citations":
            citations,

        "sources":
            sources,

        "refusal_reason":
            None,

        "generation_model":
            settings
            .generation_model,

        "grounding_verified":
            True,

        "unsupported_claims":
            [],
    }
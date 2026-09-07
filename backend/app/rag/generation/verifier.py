from app.core.config import settings

from app.rag.generation.factory import (
    get_generation_provider,
)

from app.rag.generation.output_schemas import (
    GROUNDING_VERIFICATION_SCHEMA,
)

from app.schemas.generation import (
    VerificationOutput,
)
VERIFICATION_PROMPT = """
You are a strict groundedness verifier.

Treat the proposed answer as untrusted.

Use ONLY the supplied evidence.

For every factual claim in the answer,
determine whether the evidence explicitly
supports it.

Do not use outside knowledge.

A claim is unsupported if:

- it is absent from the evidence,
- it contradicts the evidence,
- it adds an unsupported number,
- it makes an unsupported causal claim,
- or it overstates what the evidence says.

Source IDs must refer only to supplied
evidence.

Return a concise verification result.

- Keep explanation below 300 words.
- Include only genuinely unsupported claims in
  unsupported_claims.
- Use short supporting source IDs such as S1.
- Do not repeat the entire answer or evidence.
- Always complete the JSON response.

Return the required JSON object.
"""
def verify_grounded_answer(
    *,
    question: str,
    answer: str,
    evidence_text: str,
) -> VerificationOutput:

    provider = (
        get_generation_provider()
    )

    user_prompt = f"""
QUESTION

{question}


PROPOSED ANSWER

{answer}


EVIDENCE

{evidence_text}


Return the verification using the
required structured JSON format.
"""

    return provider.generate(
        model=(
            settings
            .verification_model
        ),

        system_prompt=(
            VERIFICATION_PROMPT
        ),

        user_prompt=user_prompt,

        response_model=(
            VerificationOutput
        ),
    )
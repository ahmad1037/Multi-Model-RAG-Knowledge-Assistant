from app.rag.generation.factory import (
    get_generation_provider,
)

from app.schemas.generation import (
    GroundedModelOutput,
)


provider = (
    get_generation_provider()
)


result = provider.generate(
    model="qwen3:8b",

    system_prompt="""
You answer only from supplied evidence.
""",

    user_prompt="""
Evidence:
Gradient Boosting RMSE = 214.09.

Question:
What was the RMSE?

Use citation S1.
""",

    response_model=(
        GroundedModelOutput
    ),
)


print(result)
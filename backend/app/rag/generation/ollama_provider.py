from typing import TypeVar

from ollama import Client

from pydantic import BaseModel

from app.core.config import settings

from app.observability.logging import (
    get_logger,
)

from app.observability.metrics import (
    OLLAMA_LATENCY,
    OLLAMA_LOAD_LATENCY,
    OLLAMA_OUTPUT_TOKENS,
    OLLAMA_PROMPT_TOKENS,
    OLLAMA_TOKENS_PER_SECOND,
)

logger = get_logger()

T = TypeVar(
    "T",
    bound=BaseModel,
)


class OllamaGenerationProvider:

    def __init__(self):

        self.client = Client(
            host=(
                settings
                .ollama_base_url
            )
        )


    def generate(
        self,
        *,
        operation: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:

        response = (
            self.client.chat(
                model=model,

                messages=[
                    {
                        "role": "system",
                        "content":
                            system_prompt,
                    },

                    {
                        "role": "user",
                        "content":
                            user_prompt,
                    },
                ],

                format=(
                    response_model
                    .model_json_schema()
                ),

                options={
                    "temperature":
                        settings
                        .generation_temperature,
                },

                think=False,

                stream=False,
            )
        )
        total_seconds = (
            (response.total_duration or 0)
            / 1_000_000_000
        )


        load_seconds = (
            (response.load_duration or 0)
            / 1_000_000_000
        )


        prompt_tokens = (
            response.prompt_eval_count
            or 0
        )


        output_tokens = (
            response.eval_count
            or 0
        )


        eval_seconds = (
            (response.eval_duration or 0)
            / 1_000_000_000
        )
        OLLAMA_LATENCY.labels(
            operation=operation,
            model=model,
        ).observe(
            total_seconds
        )


        OLLAMA_LOAD_LATENCY.labels(
            model=model,
        ).observe(
            load_seconds
        )


        OLLAMA_PROMPT_TOKENS.labels(
            operation=operation,
            model=model,
        ).observe(
            prompt_tokens
        )


        OLLAMA_OUTPUT_TOKENS.labels(
            operation=operation,
            model=model,
        ).observe(
            output_tokens
        )
        if (
            output_tokens > 0
            and eval_seconds > 0
        ):

            tokens_per_second = (
                output_tokens
                / eval_seconds
            )

            OLLAMA_TOKENS_PER_SECOND.labels(
                operation=operation,
                model=model,
            ).observe(
                tokens_per_second
            )
        logger.info(
            "ollama_request_complete",

            operation=operation,

            model=model,

            total_duration_ms=round(
                total_seconds * 1000,
                2,
            ),

            load_duration_ms=round(
                load_seconds * 1000,
                2,
            ),

            prompt_tokens=prompt_tokens,

            output_tokens=output_tokens,
        )


        return (
            response_model
            .model_validate_json(
                response
                .message
                .content
            )
        )
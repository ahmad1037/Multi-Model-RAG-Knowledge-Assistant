from typing import TypeVar

from ollama import Client

from pydantic import BaseModel

from app.core.config import settings


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

        return (
            response_model
            .model_validate_json(
                response
                .message
                .content
            )
        )
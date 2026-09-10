from typing import Protocol

from pydantic import BaseModel


class StructuredGenerationProvider(
    Protocol
):

    def generate(
        self,
        *,
        operation: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ):

        ...
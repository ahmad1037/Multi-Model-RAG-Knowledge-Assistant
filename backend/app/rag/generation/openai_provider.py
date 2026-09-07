import json
import os

from openai import OpenAI

from app.core.config import settings
from app.rag.generation.provider import (
    ProviderResult,
)


class OpenAIGenerationProvider:
    def __init__(self):
        if settings.openai_api_key is None:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        base_url = os.getenv(
            "OPENAI_BASE_URL"
        )

        client_kwargs = {
            "api_key": (
                settings
                .openai_api_key
                .get_secret_value()
            ),
        }

        if base_url:
            client_kwargs["base_url"] = (
                base_url
            )

        self.client = OpenAI(
            **client_kwargs
        )

        self.use_ollama = bool(
            base_url
            and "11434" in base_url
        )

    def generate(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        schema_name: str,
        schema: dict,
        max_output_tokens: int,
    ) -> ProviderResult:
        if self.use_ollama:
            return self._generate_with_ollama(
                model=model,
                instructions=instructions,
                input_text=input_text,
                schema_name=schema_name,
                schema=schema,
                max_output_tokens=(
                    max_output_tokens
                ),
            )

        return self._generate_with_openai(
            model=model,
            instructions=instructions,
            input_text=input_text,
            schema_name=schema_name,
            schema=schema,
            max_output_tokens=(
                max_output_tokens
            ),
        )

    def _generate_with_openai(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        schema_name: str,
        schema: dict,
        max_output_tokens: int,
    ) -> ProviderResult:
        response = (
            self.client
            .responses
            .create(
                model=model,
                instructions=instructions,
                input=input_text,
                max_output_tokens=(
                    max_output_tokens
                ),
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "strict": True,
                        "schema": schema,
                    }
                },
            )
        )

        payload = self._parse_json(
            response.output_text
        )

        return ProviderResult(
            payload=payload,
            response_id=response.id,
            model=model,
        )

    def _generate_with_ollama(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        schema_name: str,
        schema: dict,
        max_output_tokens: int,
    ) -> ProviderResult:
        schema_text = json.dumps(
            schema,
            ensure_ascii=False,
        )

        system_message = (
            f"{instructions}\n\n"
            "Citation requirements:\n"
            "- If answerable is true, citations cannot be empty.\n"
            "- Every factual sentence must end with an inline "
            "citation such as [S1].\n"
            "- citations contains the same IDs without brackets, "
            "for example [\"S1\"].\n"
            "- Never return an answerable answer without [S#] "
            "markers.\n"
            "- If no supplied source supports the answer, set "
            "answerable to false.\n"
            f"{schema_text}"
        )

        response = (
            self.client
            .chat
            .completions
            .create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {
                        "role": "user",
                        "content": input_text,
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema_name,
                        "strict": True,
                        "schema": schema,
                    },
                },
                reasoning_effort="none",
                temperature=0,
                max_tokens=max_output_tokens,
            )
        )

        raw_output = (
            response
            .choices[0]
            .message
            .content
            or ""
        )

        payload = self._parse_json(
            raw_output
        )

        return ProviderResult(
            payload=payload,
            response_id=response.id,
            model=model,
        )

    @staticmethod
    def _parse_json(
        raw_output: str,
    ) -> dict:
        cleaned = raw_output.strip()

        if not cleaned:
            raise ValueError(
                "The generation model returned "
                "an empty response."
            )

        try:
            payload = json.loads(
                cleaned
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                "The generation model returned "
                "invalid JSON: "
                f"{cleaned[:500]!r}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "The generation model response "
                "must be a JSON object."
            )

        return payload
import json

from app.schemas.visual_analysis import (
    VisualAnalysis,
)


class InvalidVisualAnalysisError(
    ValueError
):
    pass


def extract_json_object(
    text: str,
) -> dict:

    value = text.strip()

    if value.startswith("```"):

        lines = value.splitlines()

        lines = [
            line
            for line in lines
            if not line.strip().startswith(
                "```"
            )
        ]

        value = "\n".join(lines)

    start = value.find("{")

    end = value.rfind("}")

    if (
        start == -1
        or end == -1
        or end <= start
    ):

        raise InvalidVisualAnalysisError(
            "VLM output contained no "
            "valid JSON object."
        )

    try:

        return json.loads(
            value[start:end + 1]
        )

    except json.JSONDecodeError as exc:

        raise InvalidVisualAnalysisError(
            "VLM returned invalid JSON."
        ) from exc


def validate_visual_analysis(
    text: str,
) -> VisualAnalysis:

    payload = extract_json_object(
        text
    )

    return VisualAnalysis.model_validate(
        payload
    )
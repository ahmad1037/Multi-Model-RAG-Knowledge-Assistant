import json
import uuid

from datetime import (
    datetime,
    timezone,
)

from pathlib import Path


def save_evaluation_report(
    *,
    evaluation_type: str,
    metrics: dict,
    configuration: dict,
    output_directory: Path,
) -> Path:

    run_id = str(
        uuid.uuid4()
    )

    payload = {

        "run_id":
            run_id,

        "evaluation_type":
            evaluation_type,

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "configuration":
            configuration,

        "metrics":
            metrics,
    }

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = (
        output_directory
        / (
            f"{evaluation_type}_"
            f"{run_id}.json"
        )
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
        ),

        encoding="utf-8",
    )

    return path
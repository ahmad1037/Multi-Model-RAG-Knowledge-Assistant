import uuid

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ProcessingJobRead(
    BaseModel
):

    id: uuid.UUID

    document_id: uuid.UUID

    job_type: str

    status: str

    current_stage: str

    progress_percent: int

    celery_task_id: str | None

    attempt_count: int

    error_message: str | None

    started_at: datetime | None

    finished_at: datetime | None

    created_at: datetime

    updated_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )
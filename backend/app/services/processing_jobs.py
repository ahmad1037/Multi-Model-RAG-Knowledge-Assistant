import uuid

from datetime import (
    datetime,
    timezone,
)

from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.processing_job import (
    ProcessingJob,
)

ACTIVE_JOB_STATUSES = {
    "queued",
    "running",
    "retrying",
}

def get_processing_job(
    db: Session,
    job_id: uuid.UUID,
) -> ProcessingJob | None:

    return db.get(
        ProcessingJob,
        job_id,
    )

def get_active_processing_job(
    db: Session,
    document_id: uuid.UUID,
) -> ProcessingJob | None:

    statement = (
        select(ProcessingJob)

        .where(
            ProcessingJob.document_id
            == document_id,

            ProcessingJob.status.in_(
                ACTIVE_JOB_STATUSES
            ),
        )

        .order_by(
            ProcessingJob.created_at.desc()
        )
    )

    return db.scalar(
        statement
    )

def create_processing_job(
    db: Session,
    document_id: uuid.UUID,
) -> ProcessingJob:

    existing = (
        get_active_processing_job(
            db,
            document_id,
        )
    )

    if existing is not None:

        return existing


    job = ProcessingJob(
        document_id=document_id,

        status="queued",

        current_stage="queued",

        progress_percent=0,

        job_metadata={
            "completed_stages": [],
        },
    )


    db.add(job)

    db.commit()

    db.refresh(job)

    return job

def update_job(
    db: Session,
    job: ProcessingJob,
    *,
    status: str | None = None,
    stage: str | None = None,
    progress: int | None = None,
    error_message: str | None = None,
) -> None:

    if status is not None:

        job.status = status


    if stage is not None:

        job.current_stage = stage


    if progress is not None:

        job.progress_percent = (
            progress
        )


    job.error_message = (
        error_message
    )


    db.commit()

    db.refresh(job)

    
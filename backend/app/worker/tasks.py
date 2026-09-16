import uuid
import logging

from datetime import (
    datetime,
    timezone,
)

from celery.signals import worker_ready
from sqlalchemy import select

from app.core.config import settings

from app.db.session import (
    SessionLocal,
)

from app.models.document import (
    Document,
)

from app.models.processing_job import (
    ProcessingJob,
)

from app.services.background_pipeline import (
    process_document_job,
)

from app.worker.celery_app import (
    celery_app,
)

logger = logging.getLogger(__name__)


@worker_ready.connect
def recover_interrupted_jobs(**_kwargs):
    """Requeue jobs abandoned by the project's single worker on restart."""
    from app.services.background_jobs import enqueue_document_processing

    with SessionLocal() as db:
        interrupted = db.scalars(
            select(ProcessingJob).where(ProcessingJob.status == "running")
        ).all()

        for job in interrupted:
            try:
                document_id = job.document_id
                job.status = "failed"
                job.current_stage = "failed"
                job.error_message = "Worker stopped before this job completed."
                job.finished_at = datetime.now(timezone.utc)
                db.commit()
                enqueue_document_processing(db, document_id)
                logger.info("Requeued interrupted document job %s", job.id)
            except Exception:
                db.rollback()
                logger.exception("Could not recover interrupted job %s", job.id)

@celery_app.task(
    bind=True,

    name=(
        "process_document_pipeline"
    ),

    max_retries=(
        settings
        .processing_max_retries
    ),
)
def process_document_pipeline(
    self,
    job_id: str,
):

    parsed_job_id = uuid.UUID(
        job_id
    )


    with SessionLocal() as db:

        job = db.get(
            ProcessingJob,
            parsed_job_id,
        )


        if job is None:

            raise ValueError(
                "Processing job not found."
            )

        # A late Redis redelivery must not rerun a job that was
        # already completed or explicitly abandoned after worker loss.
        if job.status in {"succeeded", "failed"}:
            return {
                "job_id": str(job.id),
                "status": job.status,
            }


        try:

            job.status = "running"

            job.attempt_count = (
                self.request.retries
                + 1
            )


            if job.started_at is None:

                job.started_at = (
                    datetime.now(
                        timezone.utc
                    )
                )


            job.error_message = None

            db.commit()


            process_document_job(
                db,
                job,
            )


            job.finished_at = (
                datetime.now(
                    timezone.utc
                )
            )

            db.commit()


            return {
                "job_id":
                    str(job.id),

                "status":
                    "succeeded",
            }
        except Exception as exc:

            db.rollback()


            job = db.get(
                ProcessingJob,
                parsed_job_id,
            )


            if (
                self.request.retries
                < self.max_retries
            ):

                if job:

                    job.status = (
                        "retrying"
                    )

                    job.error_message = (
                        str(exc)[:2000]
                    )

                    db.commit()


                countdown = (
                    settings
                    .processing_retry_delay_seconds
                    * (
                        2
                        ** self.request.retries
                    )
                )


                raise self.retry(
                    exc=exc,

                    countdown=(
                        countdown
                    ),
                )


            if job:

                job.status = "failed"

                job.current_stage = (
                    "failed"
                )

                job.error_message = (
                    str(exc)[:2000]
                )

                job.finished_at = (
                    datetime.now(
                        timezone.utc
                    )
                )


                document = db.get(
                    Document,
                    job.document_id,
                )


                if document:

                    document.status = (
                        "processing_failed"
                    )

                    document.error_message = (
                        str(exc)[:2000]
                    )


                db.commit()


            raise

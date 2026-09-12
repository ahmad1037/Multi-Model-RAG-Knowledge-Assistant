import uuid

from datetime import (
    datetime,
    timezone,
)

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
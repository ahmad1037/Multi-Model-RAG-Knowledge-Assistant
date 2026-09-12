import uuid

from sqlalchemy.orm import Session

from app.services.processing_jobs import (
    create_processing_job,
)

from app.worker.tasks import (
    process_document_pipeline,
)


def enqueue_document_processing(
    db: Session,
    document_id: uuid.UUID,
):

    job = create_processing_job(
        db,
        document_id,
    )


    if job.celery_task_id:

        return job


    try:

        task = (
            process_document_pipeline
            .delay(
                str(job.id)
            )
        )


        job.celery_task_id = (
            task.id
        )

        db.commit()

        db.refresh(job)

        return job


    except Exception as exc:

        job.status = "failed"

        job.error_message = (
            f"Could not queue task: "
            f"{exc}"
        )

        db.commit()

        raise
import uuid

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.processing_job import (
    ProcessingJobRead,
)

from app.services.background_jobs import (
    enqueue_document_processing,
)

from app.services.processing_jobs import (
    get_processing_job,
)


router = APIRouter(
    tags=[
        "processing-jobs"
    ]
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

@router.get(
    "/processing-jobs/{job_id}",

    response_model=(
        ProcessingJobRead
    ),
)
def processing_job_status(
    job_id: uuid.UUID,
    db: DatabaseSession,
):

    job = get_processing_job(
        db,
        job_id,
    )


    if job is None:

        raise HTTPException(
            status_code=404,

            detail=(
                "Processing job "
                "not found."
            ),
        )


    return job


@router.post(
    "/documents/{document_id}/process-async",

    response_model=(
        ProcessingJobRead
    ),

    status_code=(
        status.HTTP_202_ACCEPTED
    ),
)
def start_document_processing(
    document_id: uuid.UUID,
    db: DatabaseSession,
):

    return (
        enqueue_document_processing(
            db,
            document_id,
        )
    )


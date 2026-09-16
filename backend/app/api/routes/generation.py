import uuid
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.knowledge_base import KnowledgeBase

from app.schemas.generation import (
    GroundedAnswerResponse,
    GroundedQuestionRequest,
)

from app.services.grounded_generation import (
    answer_question,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["generation"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    (
        "/knowledge-bases/"
        "{knowledge_base_id}/answer"
    ),
    response_model=(
        GroundedAnswerResponse
    ),
)
def grounded_answer(
    knowledge_base_id: uuid.UUID,
    payload: GroundedQuestionRequest,
    db: DatabaseSession,
):
    if db.get(KnowledgeBase, knowledge_base_id) is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found.")

    try:

        return answer_question(
            db=db,

            knowledge_base_id=(
                knowledge_base_id
            ),

            question=(
                payload.question
            ),

            verify_grounding=(
                payload
                .verify_grounding
            ),
        )

    except Exception as exc:
        logger.exception(
            "Grounded generation failed"
        )
        raise HTTPException(
            status_code=500,
            detail="Grounded generation failed.",
        ) from exc

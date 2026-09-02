from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseRead,
)
from app.services.knowledge_bases import (
    create_knowledge_base,
    get_knowledge_base_by_slug,
    list_knowledge_bases,
)


router = APIRouter(
    prefix="/knowledge-bases",
    tags=["knowledge-bases"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "",
    response_model=KnowledgeBaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create(
    payload: KnowledgeBaseCreate,
    db: DatabaseSession,
):
    existing = get_knowledge_base_by_slug(
        db,
        payload.slug,
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A knowledge base with this "
                "slug already exists."
            ),
        )

    return create_knowledge_base(
        db,
        payload,
    )


@router.get(
    "",
    response_model=list[KnowledgeBaseRead],
)
def list_all(
    db: DatabaseSession,
):
    return list_knowledge_bases(db)
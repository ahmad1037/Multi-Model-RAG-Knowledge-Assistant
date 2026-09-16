from typing import Annotated
import uuid
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from app.models.knowledge_base import KnowledgeBase

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
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

    try:
        return create_knowledge_base(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="A knowledge base with this name or slug already exists.") from exc


@router.get(
    "",
    response_model=list[KnowledgeBaseRead],
)
def list_all(
    db: DatabaseSession,
):
    return list_knowledge_bases(db)

@router.delete("/{knowledge_base_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(knowledge_base_id: uuid.UUID, db: DatabaseSession):
    # Database foreign keys cascade deletion to related records.
    deleted_id = db.scalar(delete(KnowledgeBase).where(
        KnowledgeBase.id == knowledge_base_id,
    ).returning(KnowledgeBase.id))
    if deleted_id is None:
        raise HTTPException(status_code=404, detail="Knowledge base not found.")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

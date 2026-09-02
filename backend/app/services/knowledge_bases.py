from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_base import (
    KnowledgeBase,
)
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
)


def create_knowledge_base(
    db: Session,
    payload: KnowledgeBaseCreate,
) -> KnowledgeBase:

    knowledge_base = KnowledgeBase(
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
    )

    db.add(knowledge_base)

    db.commit()

    db.refresh(knowledge_base)

    return knowledge_base


def list_knowledge_bases(
    db: Session,
) -> list[KnowledgeBase]:

    statement = (
        select(KnowledgeBase)
        .order_by(
            KnowledgeBase.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_knowledge_base_by_slug(
    db: Session,
    slug: str,
) -> KnowledgeBase | None:

    statement = (
        select(KnowledgeBase)
        .where(
            KnowledgeBase.slug == slug
        )
    )

    return db.scalar(statement)
import json

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_base import (
    KnowledgeBase,
)

from app.rag.evaluation.retrieval_metrics import (
    recall_at_k,
    reciprocal_rank,
)

from app.rag.retrieval.semantic import (
    semantic_search,
)


def load_cases(
    path: Path,
) -> list[dict]:

    cases: list[dict] = []

    with path.open(
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            cases.append(
                json.loads(line)
            )

    return cases


def find_knowledge_base(
    db: Session,
    slug: str,
) -> KnowledgeBase:

    statement = (
        select(KnowledgeBase)
        .where(
            KnowledgeBase.slug
            == slug
        )
    )

    knowledge_base = db.scalar(
        statement
    )

    if knowledge_base is None:

        raise ValueError(
            f"Unknown knowledge base: "
            f"{slug}"
        )

    return knowledge_base


def evaluate_retrieval(
    db: Session,
    cases: list[dict],
    mode: str = "exact",
    max_k: int = 10,
) -> dict:

    recall_1 = []
    recall_3 = []
    recall_5 = []
    recall_10 = []

    reciprocal_ranks = []

    for case in cases:

        knowledge_base = (
            find_knowledge_base(
                db,
                case[
                    "knowledge_base_slug"
                ],
            )
        )

        results = semantic_search(
            db=db,
            knowledge_base_id=(
                knowledge_base.id
            ),
            query=case["question"],
            top_k=max_k,
            mode=mode,
        )

        expected_document = (
            case["expected_document"]
        )

        expected_pages = (
            case.get(
                "expected_pages",
                [],
            )
        )

        recall_1.append(
            recall_at_k(
                results,
                expected_document,
                expected_pages,
                1,
            )
        )

        recall_3.append(
            recall_at_k(
                results,
                expected_document,
                expected_pages,
                3,
            )
        )

        recall_5.append(
            recall_at_k(
                results,
                expected_document,
                expected_pages,
                5,
            )
        )

        recall_10.append(
            recall_at_k(
                results,
                expected_document,
                expected_pages,
                10,
            )
        )

        reciprocal_ranks.append(
            reciprocal_rank(
                results,
                expected_document,
                expected_pages,
            )
        )

    count = len(cases)

    if count == 0:

        raise ValueError(
            "Evaluation dataset is empty."
        )

    return {
        "queries": count,

        "mode": mode,

        "recall_at_1":
            sum(recall_1)
            / count,

        "recall_at_3":
            sum(recall_3)
            / count,

        "recall_at_5":
            sum(recall_5)
            / count,

        "recall_at_10":
            sum(recall_10)
            / count,

        "mrr":
            sum(reciprocal_ranks)
            / count,
    }
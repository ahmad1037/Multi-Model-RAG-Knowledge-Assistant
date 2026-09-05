import math


def dcg_at_k(
    relevance: list[int],
    k: int,
) -> float:

    score = 0.0

    for rank, rel in enumerate(
        relevance[:k],
        start=1,
    ):

        score += (
            rel
            / math.log2(
                rank + 1
            )
        )

    return score

def ndcg_at_k(
    relevance: list[int],
    k: int,
) -> float:

    actual = dcg_at_k(
        relevance,
        k,
    )

    ideal = sorted(
        relevance,
        reverse=True,
    )

    ideal_score = dcg_at_k(
        ideal,
        k,
    )

    if ideal_score == 0:

        return 0.0

    return (
        actual
        / ideal_score
    )

def context_contains_relevant(
    selected: list[dict],
    expected_document: str,
    expected_pages: list[int],
) -> float:

    for item in selected:

        if (
            item["document_name"]
            != expected_document
        ):
            continue

        if not expected_pages:
            return 1.0

        start = item.get(
            "page_start"
        )

        end = item.get(
            "page_end"
        )

        if (
            start is None
            or end is None
        ):
            continue

        if any(
            start <= page <= end
            for page in expected_pages
        ):

            return 1.0

    return 0.0



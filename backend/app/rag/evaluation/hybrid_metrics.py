def page_matches(
    result: dict,
    expected_pages: list[int],
) -> bool:

    if not expected_pages:

        return True

    start = result.get(
        "page_start"
    )

    end = result.get(
        "page_end"
    )

    if (
        start is None
        or end is None
    ):

        return False

    return any(
        start <= page <= end
        for page
        in expected_pages
    )

def hybrid_result_is_relevant(
    result: dict,
    expected_document: str,
    expected_pages: list[int],
    expected_evidence_types: list[
        str
    ] | None = None,
) -> bool:

    if (
        result["document_name"]
        != expected_document
    ):

        return False

    if expected_evidence_types:

        if (
            result["evidence_type"]
            not in expected_evidence_types
        ):

            return False

    return page_matches(
        result,
        expected_pages,
    )

def hybrid_recall_at_k(
    results: list[dict],
    expected_document: str,
    expected_pages: list[int],
    k: int,
    expected_evidence_types: list[
        str
    ] | None = None,
) -> float:

    found = any(
        hybrid_result_is_relevant(
            result=result,

            expected_document=(
                expected_document
            ),

            expected_pages=(
                expected_pages
            ),

            expected_evidence_types=(
                expected_evidence_types
            ),
        )
        for result in results[:k]
    )

    return (
        1.0
        if found
        else 0.0
    )

def hybrid_reciprocal_rank(
    results: list[dict],
    expected_document: str,
    expected_pages: list[int],
    expected_evidence_types: list[
        str
    ] | None = None,
) -> float:

    for rank, result in enumerate(
        results,
        start=1,
    ):

        if hybrid_result_is_relevant(
            result=result,

            expected_document=(
                expected_document
            ),

            expected_pages=(
                expected_pages
            ),

            expected_evidence_types=(
                expected_evidence_types
            ),
        ):

            return 1.0 / rank

    return 0.0


def page_matches(
    page_start: int | None,
    page_end: int | None,
    expected_pages: list[int],
) -> bool:

    if not expected_pages:

        return True

    if (
        page_start is None
        or page_end is None
    ):

        return False

    return any(
        page_start
        <= page
        <= page_end
        for page in expected_pages
    )


def result_is_relevant(
    result: dict,
    expected_document: str,
    expected_pages: list[int],
) -> bool:

    if (
        result["document_name"]
        != expected_document
    ):

        return False

    return page_matches(
        page_start=(
            result["page_start"]
        ),
        page_end=(
            result["page_end"]
        ),
        expected_pages=(
            expected_pages
        ),
    )


def reciprocal_rank(
    results: list[dict],
    expected_document: str,
    expected_pages: list[int],
) -> float:

    for rank, result in enumerate(
        results,
        start=1,
    ):

        if result_is_relevant(
            result,
            expected_document,
            expected_pages,
        ):

            return 1.0 / rank

    return 0.0

def recall_at_k(
    results: list[dict],
    expected_document: str,
    expected_pages: list[int],
    k: int,
) -> float:

    top_results = results[:k]

    found = any(
        result_is_relevant(
            result,
            expected_document,
            expected_pages,
        )
        for result in top_results
    )

    return (
        1.0
        if found
        else 0.0
    )
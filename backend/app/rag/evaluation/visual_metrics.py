def visual_result_is_relevant(
    result: dict,
    expected_document: str,
    expected_pages: list[int],
    expected_asset_type: str | None = None,
) -> bool:

    if (
        result["document_name"]
        != expected_document
    ):

        return False

    if (
        expected_asset_type
        is not None
        and result["asset_type"]
        != expected_asset_type
    ):

        return False

    if not expected_pages:

        return True

    return (
        result["page_number"]
        in expected_pages
    )


def visual_recall_at_k(
    results: list[dict],
    expected_document: str,
    expected_pages: list[int],
    k: int,
    expected_asset_type: str | None = None,
) -> float:

    found = any(
        visual_result_is_relevant(
            result,
            expected_document,
            expected_pages,
            expected_asset_type,
        )
        for result in results[:k]
    )

    return (
        1.0
        if found
        else 0.0
    )


def visual_reciprocal_rank(
    results: list[dict],
    expected_document: str,
    expected_pages: list[int],
    expected_asset_type: str | None = None,
) -> float:

    for rank, result in enumerate(
        results,
        start=1,
    ):

        if visual_result_is_relevant(
            result,
            expected_document,
            expected_pages,
            expected_asset_type,
        ):

            return 1.0 / rank

    return 0.0
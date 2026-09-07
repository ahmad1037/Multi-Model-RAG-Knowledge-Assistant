import re


CITATION_PATTERN = re.compile(
    r"\[\s*(S\d+)\s*\]",
    re.IGNORECASE,
)


class CitationValidationError(
    ValueError
):
    pass


def normalize_source_id(
    value: str,
) -> str:

    value = (
        value
        .strip()
        .upper()
    )

    # Accept both:
    # S1
    # [S1]
    if (
        value.startswith("[")
        and value.endswith("]")
    ):
        value = value[1:-1].strip()

    if not re.fullmatch(
        r"S\d+",
        value,
    ):
        raise CitationValidationError(
            f"Invalid citation ID: {value}"
        )

    return value


def inline_citations(
    answer: str,
) -> set[str]:

    return {
        match.upper()
        for match
        in CITATION_PATTERN.findall(
            answer
        )
    }


def validate_citations(
    *,
    answerable: bool,
    answer: str,
    declared_citations: list[str],
    context_items: list[dict],
) -> list[str]:

    allowed = {
        normalize_source_id(
            item["citation_id"]
        )
        for item in context_items
    }

    declared = {
        normalize_source_id(
            citation
        )
        for citation
        in declared_citations
    }

    inline = inline_citations(
        answer
    )

    unknown_declared = (
        declared
        - allowed
    )

    if unknown_declared:
        raise CitationValidationError(
            "Answer declares unknown "
            "citations: "
            f"{sorted(unknown_declared)}"
        )

    unknown_inline = (
        inline
        - allowed
    )

    if unknown_inline:
        raise CitationValidationError(
            "Answer contains unknown "
            "inline citations: "
            f"{sorted(unknown_inline)}"
        )

    if declared != inline:
        raise CitationValidationError(
            "Declared citations do not "
            "match inline citations. "
            f"Declared={sorted(declared)}, "
            f"Inline={sorted(inline)}"
        )

    if (
        answerable
        and not declared
    ):
        raise CitationValidationError(
            "Grounded answer contains "
            "no citations."
        )

    return sorted(
        declared,
        key=lambda value:
            int(value[1:]),
    )


def build_source_records(
    context_items: list[dict],
    citations: list[str],
) -> list[dict]:

    by_id = {
        normalize_source_id(
            item["citation_id"]
        ): item
        for item in context_items
    }

    records = []

    for citation in citations:

        normalized = (
            normalize_source_id(
                citation
            )
        )

        item = by_id.get(
            normalized
        )

        if item is None:
            raise CitationValidationError(
                "Citation source not found "
                "in selected context: "
                f"{normalized}"
            )

        records.append(
            {
                "source_id":
                    normalized,

                "evidence_type":
                    item[
                        "evidence_type"
                    ],

                "document_id":
                    item[
                        "document_id"
                    ],

                "document_name":
                    item[
                        "document_name"
                    ],

                "page_start":
                    item.get(
                        "page_start"
                    ),

                "page_end":
                    item.get(
                        "page_end"
                    ),

                "heading":
                    item.get(
                        "heading"
                    ),

                "visual_asset_id":
                    (
                        item[
                            "evidence_id"
                        ]
                        if (
                            item[
                                "evidence_type"
                            ]
                            == "visual_asset"
                        )
                        else None
                    ),
            }
        )

    return records
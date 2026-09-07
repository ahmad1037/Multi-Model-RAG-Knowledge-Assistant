def format_evidence_item(
    item: dict,
) -> str:

    source_id = item[
        "citation_id"
    ]

    lines = [
        f"[{source_id}]",

        (
            "Evidence type: "
            f"{item['evidence_type']}"
        ),

        (
            "Document: "
            f"{item['document_name']}"
        ),
    ]

    start = item.get(
        "page_start"
    )

    end = item.get(
        "page_end"
    )

    if start is not None:

        if (
            end is None
            or end == start
        ):

            lines.append(
                f"Page: {start}"
            )

        else:

            lines.append(
                f"Pages: {start}-{end}"
            )

    heading = item.get(
        "heading"
    )

    if heading:

        lines.append(
            f"Section: {heading}"
        )

    if (
        item["evidence_type"]
        == "text_chunk"
    ):

        lines.append(
            "Content:"
        )

        lines.append(
            item.get(
                "text",
                "",
            )
        )

    else:

        lines.append(
            (
                "Visual type: "
                f"{item.get('asset_type')}"
            )
        )

        description = (
            item.get(
                "visual_description"
            )
        )

        if description:

            lines.append(
                "Visual description:"
            )

            lines.append(
                description
            )

    return "\n".join(
        lines
    )


def format_context(
    items: list[dict],
) -> str:

    return "\n\n---\n\n".join(
        format_evidence_item(
            item
        )
        for item in items
    )
from sqlalchemy.orm import Session

from app.rag.reranking.visual_context import (
    visual_page_text,
)


def text_candidate_for_reranking(
    evidence: dict,
) -> str:

    parts = []

    heading = evidence.get(
        "heading"
    )

    if heading:

        parts.append(
            f"Section: {heading}"
        )

    parts.append(
        f"Document: "
        f"{evidence['document_name']}"
    )

    if (
        evidence.get("page_start")
        is not None
    ):

        start = evidence[
            "page_start"
        ]

        end = evidence.get(
            "page_end",
            start,
        )

        if start == end:

            parts.append(
                f"Page: {start}"
            )

        else:

            parts.append(
                f"Pages: {start}-{end}"
            )

    text = evidence.get(
        "text"
    )

    if text:

        parts.append(text)

    return "\n".join(parts)

def visual_candidate_for_reranking(
    db: Session,
    evidence: dict,
) -> str:
    

    visual_description = (
        evidence.get(
            "visual_description"
        )
    )


    if visual_description:

        parts.append(
            "Visual interpretation:"
        )

        parts.append(
            visual_description
        )
    page = evidence.get(
        "page_start"
    )

    nearby_text = (
        visual_page_text(
            db=db,

            document_id=(
                evidence[
                    "document_id"
                ]
            ),

            page_number=page,
        )
    )

    parts = [
        (
            "Visual evidence from "
            f"{evidence['document_name']}"
        ),
        (
            "Visual type: "
            f"{evidence.get('asset_type')}"
        ),
    ]

    if page is not None:

        parts.append(
            f"Page: {page}"
        )

    if nearby_text:

        parts.append(
            "Nearby page text:"
        )

        parts.append(
            nearby_text
        )

    return "\n".join(parts)

def evidence_to_rerank_text(
    db: Session,
    evidence: dict,
) -> str:

    if (
        evidence["evidence_type"]
        == "text_chunk"
    ):

        return (
            text_candidate_for_reranking(
                evidence
            )
        )

    if (
        evidence["evidence_type"]
        == "visual_asset"
    ):

        return (
            visual_candidate_for_reranking(
                db,
                evidence,
            )
        )

    raise ValueError(
        "Unsupported evidence type: "
        f"{evidence['evidence_type']}"
    )
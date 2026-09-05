from collections import defaultdict

from app.core.config import settings

from app.rag.chunking.tokenizer import (
    TokenCounter,
)

from app.rag.context.query_intent import (
    has_visual_intent,
)
def evidence_token_cost(
    evidence: dict,
    tokenizer: TokenCounter,
) -> int:

    if (
        evidence["evidence_type"]
        == "visual_asset"
    ):

        # Actual image-token cost depends on
        # the future VLM provider.
        #
        # Text budget only counts the textual
        # metadata attached to the image.
        text = evidence.get(
            "rerank_text",
            "",
        )

        return tokenizer.count(
            text
        )

    return tokenizer.count(
        evidence.get(
            "text",
            "",
        )
    )

def select_context(
    query: str,
    reranked: list[dict],
) -> dict:

    tokenizer = TokenCounter(
        "cl100k_base"
    )

    selected = []

    total_tokens = 0

    visual_count = 0

    page_counts = defaultdict(
        int
    )

    wants_visual = (
        has_visual_intent(
            query
        )
    )

    #
    # If the query explicitly asks for a
    # chart/figure/etc., reserve one visual
    # candidate when available.
    #
    if wants_visual:

        best_visual = next(
            (
                item
                for item in reranked
                if (
                    item[
                        "evidence_type"
                    ]
                    == "visual_asset"
                )
            ),
            None,
        )

        if best_visual:

            selected.append(
                best_visual
            )
            total_tokens += (
                evidence_token_cost(
                    best_visual,
                    tokenizer,
                )
            )

            visual_count += 1

            page_key = (
                best_visual[
                    "document_id"
                ],
                best_visual.get(
                    "page_start"
                ),
            )

            page_counts[
                page_key
            ] += 1

    for item in reranked:

        if item in selected:
            continue

        if (
            len(selected)
            >= settings
            .context_max_items
        ):
            break

        if (
            item["evidence_type"]
            == "visual_asset"
        ):

            if (
                visual_count
                >= settings
                .context_max_visual_items
            ):
                continue

        page_key = (
            item["document_id"],
            item.get(
                "page_start"
            ),
        )

        if (
            page_counts[page_key]
            >= settings
            .context_max_items_per_page
        ):

            continue

        token_cost = (
            evidence_token_cost(
                item,
                tokenizer,
            )
        )

        if (
            total_tokens
            + token_cost
            > settings
            .context_max_tokens
        ):

            continue

        selected.append(
            item
        )

        total_tokens += (
            token_cost
        )

        page_counts[
            page_key
        ] += 1

        if (
            item["evidence_type"]
            == "visual_asset"
        ):

            visual_count += 1
        for index, item in enumerate(
            selected,
            start=1,
        ):

            item[
                "citation_id"
            ] = f"S{index}"

    return {
        "items":
            selected,

        "total_text_tokens":
            total_tokens,

        "text_items":
            sum(
                item["evidence_type"]
                == "text_chunk"
                for item in selected
            ),

        "visual_items":
            sum(
                item["evidence_type"]
                == "visual_asset"
                for item in selected
            ),
    }


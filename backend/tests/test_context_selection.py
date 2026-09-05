from app.rag.context.selector import (
    select_context,
)


def test_context_selector_respects_limit(
    monkeypatch,
):

    items = []

    for index in range(10):

        items.append(
            {
                "evidence_id":
                    f"id-{index}",

                "evidence_type":
                    "text_chunk",

                "document_id":
                    "doc-1",

                "document_name":
                    "report.pdf",

                "page_start":
                    index + 1,

                "page_end":
                    index + 1,

                "heading":
                    None,

                "text":
                    "Relevant text. " * 10,

                "rerank_text":
                    "Relevant text. " * 10,

                "reranker_score":
                    10 - index,
            }
        )

    result = select_context(
        query="Explain the results",
        reranked=items,
    )

    assert (
        len(result["items"])
        <= 8
    )
from app.rag.evaluation.retrieval_metrics import (
    recall_at_k,
    reciprocal_rank,
)


def test_retrieval_metrics():

    results = [
        {
            "document_name":
                "wrong.pdf",

            "page_start":
                1,

            "page_end":
                1,
        },
        {
            "document_name":
                "report.pdf",

            "page_start":
                4,

            "page_end":
                5,
        },
    ]

    assert recall_at_k(
        results=results,
        expected_document=(
            "report.pdf"
        ),
        expected_pages=[4],
        k=1,
    ) == 0.0

    assert recall_at_k(
        results=results,
        expected_document=(
            "report.pdf"
        ),
        expected_pages=[4],
        k=2,
    ) == 1.0

    assert reciprocal_rank(
        results=results,
        expected_document=(
            "report.pdf"
        ),
        expected_pages=[4],
    ) == 0.5
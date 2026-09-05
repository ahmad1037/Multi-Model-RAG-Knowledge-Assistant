from app.rag.retrieval.fusion import (
    reciprocal_rank_fusion,
)


def test_rrf_rewards_cross_channel_hits():

    semantic = [
        {
            "chunk_id": "a",
            "document_id": "doc",
            "document_name": "test.md",
            "chunk_index": 0,
            "heading": None,
            "page_start": None,
            "page_end": None,
            "text": "A",
            "similarity": 0.9,
        },
        {
            "chunk_id": "b",
            "document_id": "doc",
            "document_name": "test.md",
            "chunk_index": 1,
            "heading": None,
            "page_start": None,
            "page_end": None,
            "text": "B",
            "similarity": 0.8,
        },
    ]

    lexical = [
        {
            "chunk_id": "b",
            "document_id": "doc",
            "document_name": "test.md",
            "chunk_index": 1,
            "heading": None,
            "page_start": None,
            "page_end": None,
            "text": "B",
            "lexical_score": 1.0,
        }
    ]

    results = (
        reciprocal_rank_fusion(
            {
                "semantic":
                    semantic,

                "lexical":
                    lexical,
            },
            rrf_k=60,
            top_k=10,
        )
    )

    assert (
        results[0]["evidence_id"]
        == "b"
    )

    assert set(
        results[0]["channels"]
    ) == {
        "semantic",
        "lexical",
    }
from app.rag.reranking.bge_reranker import (
    get_reranker,
)


reranker = get_reranker()


query = (
    "Why was Gradient Boosting selected?"
)


passages = [
    (
        "Gradient Boosting achieved the "
        "lowest held-out RMSE and the "
        "highest R2."
    ),

    (
        "The project was developed "
        "using FastAPI."
    ),

    (
        "The dataset includes retail "
        "sales observations."
    ),
]


scores = reranker.score_pairs(
    query,
    passages,
)


for passage, score in zip(
    passages,
    scores,
    strict=True,
):

    print(
        score,
        passage,
    )
import uuid

from sqlalchemy.orm import Session

from app.rag.retrieval.fusion import (
    reciprocal_rank_fusion,
)

from app.rag.retrieval.lexical import (
    lexical_search,
)

from app.rag.retrieval.semantic import (
    KnowledgeBaseHasNoEmbeddingsError,
    semantic_search,
)

from app.rag.retrieval.visual import (
    KnowledgeBaseHasNoVisualEmbeddingsError,
    text_to_image_search,
)

from app.schemas.hybrid_retrieval import (
    HybridSearchRequest,
)

from app.observability.metrics import (
    RETRIEVAL_RESULTS,
)
from app.observability.timing import (
    observe_stage,
)

class NoHybridResultsError(
    Exception
):
    pass


def hybrid_search(
    db: Session,
    knowledge_base_id: uuid.UUID,
    payload: HybridSearchRequest,
) -> dict:

    channel_results: dict[
        str,
        list[dict],
    ] = {}

    warnings: list[str] = []

    #
    # Lexical first.
    #
    if payload.include_lexical:
        with observe_stage(
            "lexical_retrieval"
        ):

            lexical_results = (
                lexical_search(
                    db=db,

                    knowledge_base_id=(
                        knowledge_base_id
                    ),

                    query=payload.query,

                    top_k=(
                        payload.candidate_k
                    ),
                )
            )


        RETRIEVAL_RESULTS.labels(
            channel="lexical"
        ).observe(
            len(lexical_results)
        )

        channel_results[
            "lexical"
        ] = lexical_results

    #
    # Semantic
    #
    if payload.include_semantic:

        try:
            with observe_stage(
                "semantic_retrieval"
            ):

                semantic_results = (
                    semantic_search(
                        db=db,

                        knowledge_base_id=(
                            knowledge_base_id
                        ),

                        query=payload.query,

                        top_k=(
                            payload.candidate_k
                        ),

                        mode=(
                            payload.semantic_mode
                        ),
                    )
                )


            RETRIEVAL_RESULTS.labels(
                channel="semantic"
            ).observe(
                len(semantic_results)
            )

            channel_results[
                "semantic"
            ] = semantic_results

        except (
            KnowledgeBaseHasNoEmbeddingsError
        ) as exc:

            warnings.append(
                f"Semantic channel: {exc}"
            )

    #
    # Visual
    #
    if payload.include_visual:

        try:
            with observe_stage(
                "visual_retrieval"
            ):

                visual_results = (
                    text_to_image_search(
                        db=db,

                        knowledge_base_id=(
                            knowledge_base_id
                        ),

                        query=payload.query,

                        top_k=(
                            payload.candidate_k
                        ),

                        mode=(
                            payload.visual_mode
                        ),

                        asset_type=(
                            payload.visual_asset_type
                        ),
                    )
                )


            RETRIEVAL_RESULTS.labels(
                channel="visual"
            ).observe(
                len(visual_results)
            )

            channel_results[
                "visual"
            ] = visual_results

        except (
            KnowledgeBaseHasNoVisualEmbeddingsError
        ) as exc:

            warnings.append(
                f"Visual channel: {exc}"
            )

    if not any(
        channel_results.values()
    ):

        raise NoHybridResultsError(
            "No retrieval channel "
            "returned evidence."
        )
    with observe_stage(
        "rank_fusion"
    ):

        results = (
            reciprocal_rank_fusion(
                channel_results=(
                    channel_results
                ),

                rrf_k=payload.rrf_k,

                top_k=payload.top_k,
            )
        )

    return {
        "query":
            payload.query,

        "channels_used":
            [
                channel
                for channel, values
                in channel_results.items()
                if values
            ],

        "channel_counts":
            {
                channel: len(values)
                for channel, values
                in channel_results.items()
            },

        "warnings":
            warnings,

        "results":
            results,
    }
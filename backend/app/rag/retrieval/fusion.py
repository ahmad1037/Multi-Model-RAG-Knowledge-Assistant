def evidence_key(
    channel: str,
    result: dict,
) -> str:

    if channel in {
        "semantic",
        "lexical",
    }:

        return (
            "text:"
            + str(
                result["chunk_id"]
            )
        )

    if channel == "visual":

        return (
            "visual:"
            + str(
                result[
                    "visual_asset_id"
                ]
            )
        )

    raise ValueError(
        f"Unknown channel: {channel}"
    )

def initial_evidence(
    channel: str,
    result: dict,
) -> dict:

    if channel in {
        "semantic",
        "lexical",
    }:

        return {
            "evidence_id":
                result["chunk_id"],

            "evidence_type":
                "text_chunk",

            "document_id":
                result["document_id"],

            "document_name":
                result["document_name"],

            "heading":
                result["heading"],

            "text":
                result["text"],

            "page_start":
                result["page_start"],

            "page_end":
                result["page_end"],

            "asset_type":
                None,

            "storage_path":
                None,

            "channels":
                [],

            "channel_ranks":
                {},

            "channel_scores":
                {},

            "rrf_score":
                0.0,
        }

    return {
        "evidence_id":
            result[
                "visual_asset_id"
            ],

        "evidence_type":
            "visual_asset",

        "document_id":
            result["document_id"],

        "document_name":
            result["document_name"],

        "heading":
            None,

        "text":
            None,

        "page_start":
            result["page_number"],

        "page_end":
            result["page_number"],

        "asset_type":
            result["asset_type"],

        "storage_path":
            result["storage_path"],

        "channels":
            [],

        "channel_ranks":
            {},

        "channel_scores":
            {},

        "rrf_score":
            0.0,
    }

def raw_channel_score(
    channel: str,
    result: dict,
) -> float:

    if channel == "semantic":

        return float(
            result["similarity"]
        )

    if channel == "lexical":

        return float(
            result["lexical_score"]
        )

    if channel == "visual":

        return float(
            result["similarity"]
        )

    raise ValueError(
        f"Unknown channel: {channel}"
    )

def reciprocal_rank_fusion(
    channel_results: dict[
        str,
        list[dict],
    ],
    rrf_k: int = 60,
    top_k: int = 10,
) -> list[dict]:

    fused: dict[
        str,
        dict,
    ] = {}

    for (
        channel,
        results,
    ) in channel_results.items():

        for rank, result in enumerate(
            results,
            start=1,
        ):

            key = evidence_key(
                channel,
                result,
            )

            if key not in fused:

                fused[key] = (
                    initial_evidence(
                        channel,
                        result,
                    )
                )

            evidence = fused[key]

            evidence[
                "rrf_score"
            ] += (
                1.0
                / (
                    rrf_k
                    + rank
                )
            )

            evidence[
                "channels"
            ].append(
                channel
            )

            evidence[
                "channel_ranks"
            ][channel] = rank

            evidence[
                "channel_scores"
            ][channel] = (
                raw_channel_score(
                    channel,
                    result,
                )
            )

    ranked = sorted(
        fused.values(),
        key=lambda item: (
            -item["rrf_score"],
            str(
                item["evidence_id"]
            ),
        ),
    )

    return ranked[:top_k]


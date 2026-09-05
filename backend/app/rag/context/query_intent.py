VISUAL_TERMS = {
    "chart",
    "graph",
    "figure",
    "diagram",
    "image",
    "plot",
    "visual",
    "screenshot",
    "table",
    "shown",
    "displayed",
}


def has_visual_intent(
    query: str,
) -> bool:

    words = set(
        query
        .lower()
        .replace("?", " ")
        .replace(",", " ")
        .split()
    )

    return bool(
        words
        & VISUAL_TERMS
    )
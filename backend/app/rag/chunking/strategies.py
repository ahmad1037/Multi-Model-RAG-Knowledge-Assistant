from app.rag.chunking.structure import (
    build_structured_blocks,
)
from app.rag.chunking.tokenizer import (
    TokenCounter,
)
from app.rag.chunking.types import (
    ChunkDraft,
    ChunkingConfig,
    StructuredBlock,
    TextSegment,
)
def block_text(
    block: StructuredBlock,
) -> str:

    if block.heading:

        return (
            f"{block.heading}\n"
            f"{block.text}"
        )

    return block.text

def split_block(
    block: StructuredBlock,
    tokenizer: TokenCounter,
    max_tokens: int,
) -> list[TextSegment]:

    text = block_text(block)

    tokens = tokenizer.encode(
        text
    )

    if len(tokens) <= max_tokens:

        return [
            TextSegment(
                text=text,
                page_number=(
                    block.page_number
                ),
                heading=(
                    block.heading
                ),
            )
        ]

    segments: list[TextSegment] = []

    start = 0

    while start < len(tokens):

        end = start + max_tokens

        segment_text = (
            tokenizer.decode(
                tokens[start:end]
            ).strip()
        )

        if segment_text:

            segments.append(
                TextSegment(
                    text=segment_text,
                    page_number=(
                        block.page_number
                    ),
                    heading=(
                        block.heading
                    ),
                )
            )

        start = end

    return segments

def unique_values(
    values,
):

    result = []

    for value in values:

        if (
            value is not None
            and value not in result
        ):
            result.append(value)

    return result


def segments_text(
    segments: list[TextSegment],
) -> str:

    return "\n\n".join(
        segment.text.strip()
        for segment in segments
        if segment.text.strip()
    )


def create_chunk(
    segments: list[TextSegment],
    tokenizer: TokenCounter,
    strategy: str,
) -> ChunkDraft:

    text = segments_text(
        segments
    )

    pages = unique_values(
        [
            segment.page_number
            for segment in segments
        ]
    )

    headings = unique_values(
        [
            segment.heading
            for segment in segments
        ]
    )

    numeric_pages = [
        page
        for page in pages
        if page is not None
    ]

    return ChunkDraft(
        text=text,

        heading=(
            headings[0]
            if headings
            else None
        ),

        page_start=(
            min(numeric_pages)
            if numeric_pages
            else None
        ),

        page_end=(
            max(numeric_pages)
            if numeric_pages
            else None
        ),

        token_count=(
            tokenizer.count(text)
        ),

        metadata={
            "strategy":
                strategy,

            "pages":
                pages,

            "headings":
                headings,
        },
    )

def overlap_tail(
    segments: list[TextSegment],
    tokenizer: TokenCounter,
    token_budget: int,
) -> list[TextSegment]:

    if token_budget <= 0:
        return []

    selected: list[TextSegment] = []

    remaining = token_budget

    for segment in reversed(
        segments
    ):

        tokens = tokenizer.encode(
            segment.text
        )

        if len(tokens) <= remaining:

            selected.append(
                segment
            )

            remaining -= len(tokens)

        else:

            if remaining > 0:

                tail_text = tokenizer.decode(
                    tokens[-remaining:]
                ).strip()

                if tail_text:

                    selected.append(
                        TextSegment(
                            text=tail_text,
                            page_number=(
                                segment.page_number
                            ),
                            heading=(
                                segment.heading
                            ),
                        )
                    )

            break

        if remaining <= 0:
            break

    selected.reverse()

    return selected

def structure_recursive_chunks(
    pages: list[dict],
    config: ChunkingConfig,
) -> list[ChunkDraft]:

    tokenizer = TokenCounter(
        config.tokenizer_name
    )

    blocks = build_structured_blocks(
        pages
    )

    segments: list[TextSegment] = []

    for block in blocks:

        segments.extend(
            split_block(
                block=block,
                tokenizer=tokenizer,
                max_tokens=(
                    config.chunk_size_tokens
                ),
            )
        )

    chunks: list[ChunkDraft] = []

    current: list[TextSegment] = []

    for segment in segments:

        if not current:

            current = [segment]

            continue

        candidate = (
            current
            + [segment]
        )

        candidate_text = (
            segments_text(
                candidate
            )
        )

        if (
            tokenizer.count(
                candidate_text
            )
            <= config.chunk_size_tokens
        ):

            current.append(
                segment
            )

            continue

        chunks.append(
            create_chunk(
                current,
                tokenizer,
                config.strategy,
            )
        )

        segment_tokens = (
            tokenizer.count(
                segment.text
            )
        )

        available_overlap = max(
            0,
            config.chunk_size_tokens
            - segment_tokens,
        )

        overlap_budget = min(
            config.chunk_overlap_tokens,
            available_overlap,
        )

        overlap = overlap_tail(
            current,
            tokenizer,
            overlap_budget,
        )

        current = (
            overlap
            + [segment]
        )

        # Separator tokens can occasionally
        # push the combined text over the
        # configured maximum.
        while (
            len(current) > 1
            and tokenizer.count(
                segments_text(current)
            )
            > config.chunk_size_tokens
        ):

            current.pop(0)

    if current:

        chunks.append(
            create_chunk(
                current,
                tokenizer,
                config.strategy,
            )
        )

    return chunks

def page_chunks(
    pages: list[dict],
    config: ChunkingConfig,
) -> list[ChunkDraft]:

    tokenizer = TokenCounter(
        config.tokenizer_name
    )

    chunks: list[ChunkDraft] = []

    step = (
        config.chunk_size_tokens
        - config.chunk_overlap_tokens
    )

    if step <= 0:

        raise ValueError(
            "Chunk overlap must be smaller "
            "than chunk size."
        )

    for page in pages:

        page_number = page.get(
            "page_number"
        )

        text = page.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        tokens = tokenizer.encode(
            text
        )

        for start in range(
            0,
            len(tokens),
            step,
        ):

            token_slice = tokens[
                start:
                start
                + config.chunk_size_tokens
            ]

            if not token_slice:
                continue

            chunk_text = (
                tokenizer.decode(
                    token_slice
                ).strip()
            )

            chunks.append(
                ChunkDraft(
                    text=chunk_text,

                    heading=None,

                    page_start=(
                        page_number
                    ),

                    page_end=(
                        page_number
                    ),

                    token_count=len(
                        token_slice
                    ),

                    metadata={
                        "strategy":
                            config.strategy,

                        "pages":
                            [page_number],

                        "headings":
                            [],
                    },
                )
            )

            if (
                start
                + config.chunk_size_tokens
                >= len(tokens)
            ):
                break

    return chunks


def chunk_pages(
    pages: list[dict],
    config: ChunkingConfig,
) -> list[ChunkDraft]:

    if config.strategy == "page_v1":

        return page_chunks(
            pages,
            config,
        )

    if (
        config.strategy
        == "structure_recursive_v1"
    ):

        return structure_recursive_chunks(
            pages,
            config,
        )

    raise ValueError(
        f"Unknown chunking strategy: "
        f"{config.strategy}"
    )

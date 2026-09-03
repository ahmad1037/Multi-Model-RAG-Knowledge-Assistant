from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkingConfig:

    strategy: str

    chunk_size_tokens: int

    chunk_overlap_tokens: int

    tokenizer_name: str


@dataclass
class StructuredBlock:

    text: str

    page_number: int | None

    heading: str | None


@dataclass
class TextSegment:

    text: str

    page_number: int | None

    heading: str | None


@dataclass
class ChunkDraft:

    text: str

    heading: str | None

    page_start: int | None

    page_end: int | None

    token_count: int

    metadata: dict
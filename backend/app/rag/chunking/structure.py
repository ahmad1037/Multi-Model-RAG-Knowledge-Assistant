import re

from app.rag.chunking.cleaning import (
    clean_extracted_text,
)
from app.rag.chunking.types import (
    StructuredBlock,
)


MARKDOWN_HEADING = re.compile(
    r"^#{1,6}\s+\S+"
)

NUMBERED_HEADING = re.compile(
    r"^\d+(?:\.\d+)*[\.\)]?\s+\S+"
)


def normalize_heading(
    line: str,
) -> str:

    line = re.sub(
        r"^#{1,6}\s*",
        "",
        line,
    )

    return line.strip()


def is_heading(
    line: str,
) -> bool:

    value = line.strip()

    if not value:
        return False

    if len(value) > 120:
        return False

    if MARKDOWN_HEADING.match(value):
        return True

    if NUMBERED_HEADING.match(value):

        word_count = len(
            value.split()
        )

        return word_count <= 14

    letters = [
        char
        for char in value
        if char.isalpha()
    ]

    if (
        letters
        and value.upper() == value
        and len(value.split()) <= 12
    ):
        return True

    return False

def build_structured_blocks(
    pages: list[dict],
) -> list[StructuredBlock]:

    blocks: list[StructuredBlock] = []

    current_heading: str | None = None

    for page in pages:

        page_number = page.get(
            "page_number"
        )

        text = clean_extracted_text(
            page.get(
                "text",
                "",
            )
        )

        if not text:
            continue

        paragraph_lines: list[str] = []

        def flush_paragraph() -> None:

            nonlocal paragraph_lines

            paragraph = " ".join(
                paragraph_lines
            ).strip()

            if paragraph:

                blocks.append(
                    StructuredBlock(
                        text=paragraph,
                        page_number=(
                            page_number
                        ),
                        heading=(
                            current_heading
                        ),
                    )
                )

            paragraph_lines = []

        for line in text.split("\n"):

            value = line.strip()

            if not value:

                flush_paragraph()

                continue

            if is_heading(value):

                flush_paragraph()

                current_heading = (
                    normalize_heading(
                        value
                    )
                )

                continue

            paragraph_lines.append(
                value
            )

        flush_paragraph()

    return blocks


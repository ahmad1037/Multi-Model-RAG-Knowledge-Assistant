import pytest

from app.rag.generation.citations import (
    CitationValidationError,
    validate_citations,
)


CONTEXT = [
    {
        "citation_id": "S1",
    },
    {
        "citation_id": "S2",
    },
]


def test_valid_citations():

    result = validate_citations(
        answerable=True,

        answer=(
            "The model performed "
            "better. [S1]"
        ),

        declared_citations=[
            "S1"
        ],

        context_items=CONTEXT,
    )

    assert result == [
        "S1"
    ]


def test_unknown_citation_rejected():

    with pytest.raises(
        CitationValidationError
    ):

        validate_citations(
            answerable=True,

            answer=(
                "The model performed "
                "better. [S9]"
            ),

            declared_citations=[
                "S9"
            ],

            context_items=CONTEXT,
        )

def test_declared_and_inline_must_match():

    with pytest.raises(
        CitationValidationError
    ):

        validate_citations(
            answerable=True,

            answer=(
                "Supported claim. "
                "[S1] [S2]"
            ),

            declared_citations=[
                "S1"
            ],

            context_items=CONTEXT,
        )
        
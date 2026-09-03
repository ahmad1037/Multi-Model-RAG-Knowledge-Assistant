import re


def clean_extracted_text(
    text: str,
) -> str:

    if not text:
        return ""

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    text = text.replace(
        "\x00",
        "",
    )

    # Join words split by PDF line-break
    # hyphenation:
    #
    # forecasting-
    # system
    #
    # ->
    #
    # forecastingsystem
    #
    text = re.sub(
        r"(?<=\w)-\n(?=\w)",
        "",
        text,
    )

    # Normalize spaces while preserving
    # paragraph boundaries.
    lines = [
        re.sub(
            r"[ \t]+",
            " ",
            line,
        ).strip()
        for line in text.split("\n")
    ]

    text = "\n".join(lines)

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


"""Exact comparisons for unqualified accuracy questions over retrieved tables."""
import re
from decimal import Decimal


def restore_table_rows(text: str) -> str:
    # Older ingestion joined Markdown rows with spaces. Only repair table lines
    # containing a separator row; ordinary prose remains untouched.
    return "\n".join(
        re.sub(r"\|[ \t]+\|", "|\n|", line)
        if re.search(r"\|\s*:?-{3,}:?\s*\|", line) else line
        for line in text.splitlines()
    )


def accuracy_comparison(question: str, items: list[dict]) -> dict | None:
    query = question.strip().lower().rstrip("?.! ")
    # Scoped comparisons, explanations and multiple metrics require normal RAG.
    if not re.fullmatch(
        r"(?:what(?: is| gives| has)?|which(?: technique| method| model)?(?: gives| has| achieves)?|best|highest)"
        r"(?: the)?(?: best| highest)? accuracy(?: technique| method| model)?", query
    ):
        return None
    tables = {}
    for item in items:
        if item.get("evidence_type") != "text_chunk":
            continue
        lines = restore_table_rows(item.get("text", "")).splitlines()
        for index, line in enumerate(lines[:-1]):
            cells = [cell.strip().strip("* ") for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2 or "accuracy" not in [c.lower() for c in cells]:
                continue
            column = [c.lower() for c in cells].index("accuracy")
            separators = lines[index + 1].strip().strip("|").split("|")
            if len(separators) != len(cells) or not all(re.fullmatch(r"\s*:?-{3,}:?\s*", c) for c in separators):
                continue
            rows = []
            for row in lines[index + 2:]:
                if not row.strip().startswith("|"):
                    break
                values = [c.strip().strip("* ") for c in row.strip().strip("|").split("|")]
                if len(values) != len(cells) or not values[0] or not re.fullmatch(r"(?:0?\.\d+|\d+(?:\.\d+)?)(?:%)?", values[column]):
                    rows = []
                    break
                raw = values[column]
                value = Decimal(raw.rstrip("%")) / (100 if raw.endswith("%") else 1)
                if not 0 <= value <= 1:
                    rows = []
                    break
                rows.append((values[0], value, raw))
            if len(rows) >= 2:
                tables.setdefault(tuple(rows), item["citation_id"])
    # Do not silently combine separate experiments or conflicting tables.
    if len(tables) != 1:
        return None
    rows, source = next(iter(tables.items()))
    maximum = max(row[1] for row in rows)
    winners = [row for row in rows if row[1] == maximum]
    names = " and ".join(row[0] for row in winners)
    verb = "has" if len(winners) == 1 else "tie for"
    return {
        "answer": f"{names} {verb} the highest accuracy among the rows in the retrieved table: {winners[0][2]}. [{source}]",
        "citations": [source],
    }

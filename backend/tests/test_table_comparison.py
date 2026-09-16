from pathlib import Path
import pytest
from app.rag.generation.table_comparison import accuracy_comparison, restore_table_rows

REPORT = (Path(__file__).parent / "fixtures" / "imbalance_report.md").read_text()

def evidence(text):
    return [{"evidence_type": "text_chunk", "text": text, "citation_id": "S1"}]

@pytest.mark.parametrize("question", ["Best accuracy technique ?", "Which technique gives highest accuracy ?", "Which method has the highest accuracy?", "What is the highest accuracy?"])
@pytest.mark.parametrize("flattened", [False, True])
def test_report_accuracy_uses_baseline(question, flattened):
    text = REPORT
    if flattened:
        text = text.replace("|\n|", "| |")
    result = accuracy_comparison(question, evidence(text))
    assert result is not None
    assert "Baseline" in result["answer"]
    assert "0.999220" in result["answer"]
    assert "Random Under Sampling" not in result["answer"]
    assert result["citations"] == ["S1"]

@pytest.mark.parametrize("question", ["Best method?", "Highest PR-AUC?", "Which sampling technique excluding Baseline has highest accuracy?", "Why is accuracy misleading?"])
def test_scoped_or_different_metric_is_not_intercepted(question):
    assert accuracy_comparison(question, evidence(REPORT)) is None

def test_ties_and_percentages():
    result = accuracy_comparison("Best accuracy technique?", evidence("| Method | Accuracy |\n|---|---|\n| A | 99% |\n| B | 0.99 |\n| C | 0.8 |"))
    assert "A and B tie" in result["answer"]

def test_incomplete_numeric_column_falls_back():
    assert accuracy_comparison("Best accuracy technique?", evidence(REPORT.replace("0.999220", "N/A"))) is None

def test_conflicting_tables_are_not_combined():
    items = evidence(REPORT) + evidence(REPORT.replace("0.999220", "0.900000"))
    assert accuracy_comparison("Best accuracy technique?", items) is None

def test_existing_flattened_rows_are_restored():
    assert "|\n|" in restore_table_rows(REPORT.replace("|\n|", "| |"))


def test_ingestion_preserves_markdown_table_rows():
    from app.rag.chunking.structure import build_structured_blocks
    blocks = build_structured_blocks([{"page_number": 1, "text": REPORT}])
    table = next(block.text for block in blocks if "0.999220" in block.text)
    assert "|\n|" in table
    assert accuracy_comparison("Best accuracy technique?", evidence(table)) is not None

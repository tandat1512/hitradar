import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_fact_matrix_has_no_mismatch_and_consistency_is_explicit():
    with (REPORT / "feature_3_8_qa_fact_matrix.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 20
    assert all(row["status"].startswith("VERIFIED") for row in rows)
    consistency = json.loads((REPORT / "feature_3_8_qa_document_consistency.json").read_text(encoding="utf-8"))
    assert consistency["qa_internal_fact_mismatch_count"] == 0
    assert consistency["known_document_conflicts"]
    assert consistency["status"] == "PASS_WITH_WARNINGS"

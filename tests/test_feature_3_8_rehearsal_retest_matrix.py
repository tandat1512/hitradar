import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_retest_and_timing_artifacts_do_not_invent_results():
    with (REPORT / "feature_3_8_rehearsal_retest_matrix.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        assert set(handle.seek(0) or next(csv.reader(handle))) == {"issue_id", "severity", "owner", "proposed_fix", "fix_status", "retest_status", "evidence"}
    assert rows == []
    comparison = json.loads((REPORT / "feature_3_8_rehearsal_timing_comparison.json").read_text(encoding="utf-8"))
    assert comparison["official_duration_known"] is False
    assert comparison["rehearsal_1_total_seconds"] is None
    assert comparison["rehearsal_2_total_seconds"] is None
    assert comparison["comparison_status"] == "HUMAN_REHEARSALS_REQUIRED"

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_protocol_covers_human_rehearsal_and_records_are_pending():
    protocol = (REPORT / "REHEARSAL_PROTOCOL_FEATURE_3_8.md").read_text(encoding="utf-8").lower()
    for phrase in ("full slide flow", "actual presenter handoffs", "live demo flow", "failure drill", "must_know", "section times", "total duration", "issue registry"):
        assert phrase in protocol
    assert "a technical smoke is not a rehearsal" in protocol
    r1 = json.loads((REPORT / "feature_3_8_rehearsal_1.json").read_text(encoding="utf-8"))
    r2 = json.loads((REPORT / "feature_3_8_rehearsal_2.json").read_text(encoding="utf-8"))
    for record in (r1, r2):
        assert record["status"] == "HUMAN_REHEARSAL_REQUIRED"
        assert record["actual_session_recorded"] is False
        assert record["total_duration_seconds"] is None
        assert record["demo_attempted"] is False
    assert r2["prerequisite_rehearsal_1_complete"] is False

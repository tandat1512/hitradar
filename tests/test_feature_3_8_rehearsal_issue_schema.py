import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_issue_registry_schema_exists_without_fabricated_r1_issues():
    registry = json.loads((REPORT / "feature_3_8_rehearsal_issue_registry.json").read_text(encoding="utf-8"))
    required = {
        "issue_id", "source", "category", "severity", "description", "evidence",
        "owner", "proposed_fix", "fix_status", "retest_status",
    }
    assert set(registry["issue_schema"]) == required
    assert registry["rehearsal_1_actual"] is False
    assert registry["issues"] == []
    assert registry["status"] == "AWAITING_REHEARSAL_1"
    assert all(risk["source"] == "PRE_REHEARSAL_READINESS" for risk in registry["pre_rehearsal_known_risks"])
    assert not any(risk["risk_id"].startswith("F38-R1-") for risk in registry["pre_rehearsal_known_risks"])

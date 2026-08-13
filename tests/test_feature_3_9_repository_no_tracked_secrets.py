import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_9" / "validation"


def test_secret_audit_has_no_confirmed_tracked_or_untracked_exposure():
    audit = json.loads((REPORT / "feature_3_9_secret_audit.json").read_text(encoding="utf-8"))
    assert audit["tracked_secret_risk_count"] == 0
    assert audit["untracked_secret_risk_count"] == 0
    assert all(item["secret_exposure"] is False for item in audit["files"])

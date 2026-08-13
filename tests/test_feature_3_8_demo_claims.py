import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_claim_audit_counts_are_zero():
    audit = json.loads((REPORT / "feature_3_8_demo_claim_audit.json").read_text(encoding="utf-8"))
    for key in (
        "guarantee_claim", "causal_shap_claim", "causal_what_if_claim",
        "offline_live_misrepresentation", "unsupported_metric_claim",
    ):
        assert audit[key] == 0
    assert audit["status"] == "PASS"

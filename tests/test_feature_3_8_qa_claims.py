import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_all_qa_claim_audit_counts_are_zero():
    audit = json.loads((REPORT / "feature_3_8_qa_claim_audit.json").read_text(encoding="utf-8"))
    keys = (
        "accuracy_mislabel", "guarantee_claim", "causal_shap_claim",
        "causal_what_if_claim", "unsupported_dataset_claim",
        "unsupported_model_claim", "production_ready_overclaim",
    )
    assert all(audit[key] == 0 for key in keys)
    assert audit["unsupported_policy_present"] is True
    assert audit["status"] == "PASS"

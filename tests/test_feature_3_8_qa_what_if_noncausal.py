import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_what_if_answer_is_model_comparison_not_causation():
    doc = (REPORT / "DEFENSE_QA_SHAP.md").read_text(encoding="utf-8").lower()
    assert "what-if có phải causal inference không" in doc
    assert "chạy lại cùng model" in doc
    assert "không" in doc
    assert "no real-world effect is established" in doc
    audit = json.loads((REPORT / "feature_3_8_qa_claim_audit.json").read_text(encoding="utf-8"))
    assert audit["causal_what_if_claim"] == 0

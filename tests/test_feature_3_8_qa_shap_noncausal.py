import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_shap_bank_is_noncausal_and_evidence_backed():
    doc = (REPORT / "DEFENSE_QA_SHAP.md").read_text(encoding="utf-8").lower()
    assert len(re.findall(r"^### q s\d+", doc, re.MULTILINE)) >= 15
    assert "không chứng minh quan hệ nhân quả" in doc
    assert "treeexplainer" in doc
    assert "5.000/5.000" in doc and "tolerance 0.001" in doc
    audit = json.loads((REPORT / "feature_3_8_qa_claim_audit.json").read_text(encoding="utf-8"))
    assert audit["causal_shap_claim"] == 0

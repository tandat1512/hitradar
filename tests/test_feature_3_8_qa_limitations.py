import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_limitations_bank_and_top_three_are_complete():
    doc = (REPORT / "DEFENSE_QA_LIMITATIONS.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^### Q L\d+", doc, re.MULTILINE)) >= 15
    for topic in ("Dataset limitation", "Target limitation", "SHAP limitation", "What-if limitation", "Dashboard limitation", "Offline demo limitation"):
        assert topic in doc
    top = json.loads((REPORT / "feature_3_8_top_limitations.json").read_text(encoding="utf-8"))["top_limitations"]
    assert len(top) == 3
    assert all({"limitation", "impact", "mitigation_current", "future_improvement", "source"} <= item.keys() for item in top)
    assert "production-ready chưa" in doc.lower() and "Chưa" in doc

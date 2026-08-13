import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_regression_and_r2_wording_are_correct():
    doc = (REPORT / "DEFENSE_QA_MODEL.md").read_text(encoding="utf-8").lower()
    assert len(re.findall(r"^### q m\d+", doc, re.MULTILINE)) >= 15
    assert "continuous regression estimate" in doc
    assert "r² không phải accuracy" in doc
    assert "coefficient of determination; not accuracy" in doc
    assert "accuracy là 6,96%" not in doc
    assert "accuracy 93%" not in doc

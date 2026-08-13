import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_model_qa_matches_official_test_metrics():
    official = json.loads((ROOT / "7.ML/7.8.model_evaluation/metrics/champion_test_metrics.json").read_text(encoding="utf-8"))
    registry = json.loads((REPORT / "feature_3_8_qa_source_registry.json").read_text(encoding="utf-8"))
    facts = registry["categories"]["METRICS"]["facts"]
    assert facts["test_rows"] == official["test_rows"] == 85876
    assert facts["MAE"] == official["official_metrics"]["MAE"]
    assert facts["RMSE"] == official["official_metrics"]["RMSE"]
    assert facts["R2"] == official["official_metrics"]["R2"]
    doc = (REPORT / "DEFENSE_QA_MODEL.md").read_text(encoding="utf-8")
    assert "MAE 17.65" in doc and "RMSE 21.01" in doc and "R² 0.0696" in doc

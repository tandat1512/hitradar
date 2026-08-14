import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_predict_and_what_if_baselines_are_consistent():
    scenario = json.loads((REPORT / "feature_3_8_demo_scenario.json").read_text(encoding="utf-8"))
    source_output = json.loads((ROOT / "7.ML/7.10.model_packaging/package/examples/example_output.json").read_text(encoding="utf-8"))
    consistency = json.loads((REPORT / "feature_3_8_demo_result_consistency.json").read_text(encoding="utf-8"))
    assert abs(scenario["expected_predict"]["prediction_raw"] - source_output["prediction_raw"]) <= scenario["expected_predict"]["tolerance"]
    assert consistency["predict"]["consistent"] is True
    assert consistency["what_if"]["baseline_consistent"] is True
    assert consistency["explain"]["status"] == "VERIFIED_FINAL_SMOKE"
    assert consistency["explain"]["consistent"] is True

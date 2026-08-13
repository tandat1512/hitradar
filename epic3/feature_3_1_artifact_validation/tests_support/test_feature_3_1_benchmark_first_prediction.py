"""Test: Benchmark First Prediction — Phase 4"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
RES_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json"

def test_first_prediction_has_median():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "median_ms" in data["first_prediction"]
    assert data["first_prediction"]["median_ms"] > 0

def test_first_prediction_median_greater_than_warm():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    fp = data["first_prediction"]["median_ms"]
    ws = data["warm_single_prediction"]["median_ms"]
    assert fp > ws  # first prediction is expected to be slower than warm

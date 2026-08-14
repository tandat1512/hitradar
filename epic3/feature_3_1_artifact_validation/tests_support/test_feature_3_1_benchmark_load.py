"""Test: Benchmark Load — Phase 4"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
RES_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json"

def test_cold_load_measured():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_load"] is not None
    assert data["model_load"]["count"] >= 3

def test_cold_load_has_median():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "median_ms" in data["model_load"]
    assert data["model_load"]["median_ms"] > 0

def test_first_prediction_measured():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["first_prediction"] is not None
    assert data["first_prediction"]["count"] >= 3

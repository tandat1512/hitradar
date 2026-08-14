"""Test: Prediction Determinism — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_example_prediction_result.json"

def test_deterministic():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["determinism"]["deterministic"] == True

def test_all_runs_identical():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    det = data["determinism"]
    assert det["run_1"] == det["run_2"] == det["run_3"] == 46.421062

def test_max_abs_difference_zero():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["determinism"]["max_absolute_difference"] == 0.0

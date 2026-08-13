"""Test: Inference No-Refit — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_no_refit_inference_validation.json"

def test_validation_status():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"

def test_fit_count_zero():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["fit_call_count"] == 0

def test_fit_transform_count_zero():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["fit_transform_call_count"] == 0

def test_partial_fit_count_zero():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["partial_fit_call_count"] == 0

def test_no_training():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["training_executed"] == False

def test_hash_unchanged():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["hash_unchanged"] == True

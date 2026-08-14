"""Test: Phase 3 No Source Mutation"""
import json, pathlib, hashlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
PKG_ROOT  = REPO_ROOT / "7.ML/7.10.model_packaging/package"
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_no_refit_inference_validation.json"

CANONICAL_SHA = "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"

def test_model_hash_unchanged():
    sha = hashlib.sha256((PKG_ROOT / "pipeline/full_inference_pipeline.joblib").read_bytes()).hexdigest()
    assert sha == CANONICAL_SHA

def test_no_refit_validation_file():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["training_executed"] == False
    assert data["refit_executed"] == False

def test_prediction_result_file():
    PRES = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_example_prediction_result.json"
    with open(PRES, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["hash_unchanged"] == True
    assert data["fit_call_count_after_predictions"] == 0

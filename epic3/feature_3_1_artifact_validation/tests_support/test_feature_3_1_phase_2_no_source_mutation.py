"""Test: Phase 2 No Source Mutation
Verify no source artifact files were modified during Phase 2.
"""
import json, pathlib, hashlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT  = REPO_ROOT / "7.ML/7.10.model_packaging/package"
NOREFIT_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_no_refit_validation.json"
LOAD_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_load_validation.json"
CHECKPOINT_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/checkpoints/feature_3_1_model_load_validation.json"

CRITICAL_ARTIFACTS = [
    PKG_ROOT / "pipeline/full_inference_pipeline.joblib",
    PKG_ROOT / "schemas/input_schema.json",
    PKG_ROOT / "schemas/output_schema.json",
    PKG_ROOT / "schemas/selected_features.json",
    PKG_ROOT / "schemas/feature_names.json",
    PKG_ROOT / "schemas/feature_mapping.json",
]

def test_model_load_no_modification():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["source_artifacts_modified"] == False
    assert data["hash_unchanged"] == True

def test_checkpoint_no_training():
    # Read from phase 2 checkpoint which has training_executed/refit_executed
    ckpt = REPO_ROOT / "epic3/feature_3_1_artifact_validation/checkpoints/feature_3_1_phase_2_checkpoint.json"
    with open(ckpt, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["training_executed"] == False
    assert data["refit_executed"] == False

def test_checkpoint_prediction_not_executed():
    """Prediction test belongs to Phase 3, not Phase 2."""
    ckpt = REPO_ROOT / "epic3/feature_3_1_artifact_validation/checkpoints/feature_3_1_phase_2_checkpoint.json"
    with open(ckpt, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["prediction_executed"] == False

def test_all_critical_artifacts_exist():
    for f in CRITICAL_ARTIFACTS:
        assert f.exists(), f"Critical artifact missing: {f}"

def test_model_artifact_hash_still_correct():
    """Verify the model artifact hasn't been overwritten."""
    model = PKG_ROOT / "pipeline/full_inference_pipeline.joblib"
    actual = hashlib.sha256(model.read_bytes()).hexdigest()
    expected = "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"
    assert actual == expected

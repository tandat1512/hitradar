"""Test: Model Hash Before/After
Verify artifact hash is unchanged after Phase 2 operations.
"""
import json, pathlib, hashlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
ARTIFACT  = REPO_ROOT / "7.ML/7.10.model_packaging/package/pipeline/full_inference_pipeline.joblib"
LOAD_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_load_validation.json"

def test_artifact_file_exists():
    assert ARTIFACT.exists()

def test_artifact_hash_matches_known():
    actual = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()
    expected = "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"
    assert actual == expected

def test_model_load_validation_hash_matches():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    expected = "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"
    assert data["artifact_sha256"] == expected

def test_before_after_hash_equal():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Hash unchanged during Phase 2 load
    assert data["hash_unchanged"] == True

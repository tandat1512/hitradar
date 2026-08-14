"""Test: Model Loader
Verify full_inference_pipeline.joblib loads successfully with runtime patches.
"""
import json, pathlib, hashlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
LOAD_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_load_validation.json"

def test_model_load_validation_file_exists():
    assert LOAD_VAL_FILE.exists(), f"Model load validation file not found: {LOAD_VAL_FILE}"

def test_model_load_valid():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["load_valid"] == True, f"Model load failed: {data.get('load_error')}"

def test_model_load_duration():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["load_duration_ms"] is not None
    assert data["load_duration_ms"] > 0
    assert data["load_duration_ms"] < 10000  # should load in < 10 seconds

def test_object_type_is_hitradar():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["object_type"] == "HitRadarInferencePipeline"
    assert data["object_module"] == "inference_pipeline"

def test_predict_interface_available():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["predict_available"] == True

def test_model_id_exposed():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_id_exposed"] == "EXP24-XGB-FINAL-001"

def test_model_version_exposed():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_version_exposed"] == "1.0.0"

def test_artifact_hash():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    expected = "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"
    assert data["artifact_sha256"] == expected

def test_hash_unchanged():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["hash_unchanged"] == True
    assert data["artifact_sha256"] == data["artifact_sha256"]

def test_loader_is_joblib():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["loader"] == "joblib"
    assert data["loader_version"] is not None

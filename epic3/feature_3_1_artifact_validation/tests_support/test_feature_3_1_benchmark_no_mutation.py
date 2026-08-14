"""Test: Benchmark No Mutation — Phase 4"""
import json, pathlib, hashlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
PKG_ROOT  = REPO_ROOT / "7.ML/7.10.model_packaging/package"
NM_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_no_mutation_validation.json"

CANONICAL_SHA = "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"

def test_training_executed_false():
    with open(NM_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["training_executed"] == False

def test_refit_executed_false():
    with open(NM_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["refit_executed"] == False

def test_hash_unchanged():
    with open(NM_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["hash_unchanged"] == True

def test_model_hash_matches_canonical():
    sha = hashlib.sha256((PKG_ROOT / "pipeline/full_inference_pipeline.joblib").read_bytes()).hexdigest()
    assert sha == CANONICAL_SHA

"""Test: Benchmark Statistics — Phase 4"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
RES_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_benchmark_results.json"

def test_status_pass():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "PASS"

def test_no_blockers():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["blockers"] == []

def test_training_executed_false():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["training_executed"] == False

def test_refit_executed_false():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["refit_executed"] == False

def test_source_artifacts_modified_false():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["source_artifacts_modified"] == False

def test_prediction_consistency_valid():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["prediction_consistency_valid"] == True

def test_memory_not_measured():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["memory_status"] == "NOT_MEASURED_OPTIONAL"

def test_target_latency_not_defined():
    with open(RES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["target_latency_defined"] == False

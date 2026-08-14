"""Test: Metric Stage Consistency — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
CONS_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_metric_consistency.json"

def test_consistency_status_pass():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"

def test_model_id_consistent():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_id_check"]["status"] == "PASS"

def test_model_version_consistent():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_version_check"]["status"] == "PASS"

def test_evaluation_split_test():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["evaluation_split_check"]["status"] == "PASS"
    assert data["evaluation_split_check"]["champion_test_metrics"] == "test"

def test_sample_rows_match():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["sample_rows_check"]["status"] == "PASS"

def test_mae_matches_residual_stats():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["mae_check"]["status"] == "PASS"

def test_mean_residual_match():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["mean_residual_check"]["status"] == "PASS"
    assert data["mean_residual_check"]["difference"] == 0.0

def test_all_checks_passed():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["all_checks_passed"] == True

def test_no_blockers():
    with open(CONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["blockers"] == []

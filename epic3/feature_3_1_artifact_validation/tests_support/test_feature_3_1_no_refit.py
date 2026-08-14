"""Test: No Refit
Verify no fit/fit_transform/partial_fit calls were made during Phase 2.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
NOREFIT_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_no_refit_validation.json"
LOAD_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_load_validation.json"

def test_fit_call_count_zero():
    with open(NOREFIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["call_counts"]["fit_call_count"] == 0

def test_fit_transform_count_zero():
    with open(NOREFIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["call_counts"]["fit_transform_call_count"] == 0

def test_partial_fit_count_zero():
    with open(NOREFIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["call_counts"]["partial_fit_call_count"] == 0

def test_no_refit_status_pass():
    with open(NOREFIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"

def test_validation_status_pass():
    with open(NOREFIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"

def test_hash_unchanged():
    with open(NOREFIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["artifact_hash"]["unchanged"] == True

def test_no_serialization():
    with open(NOREFIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["checks"]["no_serialization"] == "PASS"

def test_source_not_modified():
    with open(NOREFIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["source_artifacts_modified"] == False

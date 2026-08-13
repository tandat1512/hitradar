"""Test: Example Input Schema — Phase 3"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
VAL_FILE  = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_example_input_validation.json"

def test_validation_status():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"

def test_field_count_18():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["field_count"] == 18

def test_all_fields_present():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_present = all(f["present"] for f in data["field_validation"])
    assert all_present

def test_target_excluded():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["target_exclusion_check"]["target_popularity_present"] == False
    assert data["target_exclusion_check"]["track_id_present"] == False

def test_no_unknown_fields():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["no_unknown_fields"] == True

def test_all_range_checks_pass():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    failed = [c for c in data["range_checks"] if c["status"] != "PASS"]
    assert failed == []

def test_all_category_checks_pass():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    failed = [c for c in data["category_checks"] if c["status"] != "PASS"]
    assert failed == []

def test_no_blockers():
    with open(VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["blockers"] == []

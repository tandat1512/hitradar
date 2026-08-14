"""Test: Feature Count Consistency
Verify all feature counts are consistent across schemas.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
FCC_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_feature_contract_consistency.json"

def _load():
    with open(FCC_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def test_consistency_status_pass():
    data = _load()
    assert data["validation_status"] == "PASS"

def test_raw_input_count_is_18():
    data = _load()
    assert data["consistency_summary"]["raw_input_count"] == 18

def test_selected_count_is_31():
    data = _load()
    assert data["consistency_summary"]["selected_feature_count"] == 31

def test_transformed_count_is_49():
    data = _load()
    assert data["consistency_summary"]["transformed_model_feature_count"] == 49

def test_all_counts_distinct():
    data = _load()
    assert data["consistency_summary"]["all_counts_distinct"] == True

def test_target_excluded():
    data = _load()
    assert data["consistency_summary"]["target_excluded_from_raw"] == True

def test_identifier_excluded():
    data = _load()
    assert data["consistency_summary"]["identifier_excluded_from_raw"] == True

def test_all_consistency_checks_pass():
    data = _load()
    # model_n_features_in_unavailable is PASS_WITH_NOTE, not a failure
    failed = [c["check"] for c in data["consistency_checks"]
              if c["status"] not in ("PASS", "PASS_WITH_NOTE")]
    assert failed == [], f"Failed checks: {failed}"

def test_feature_mapping_49_entries():
    import json
    with open(REPO_ROOT / "7.ML/7.10.model_packaging/package/schemas/feature_mapping.json", "r", encoding="utf-8") as f:
        mapping = json.load(f)
    assert len(mapping) == 49

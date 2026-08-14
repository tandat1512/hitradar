"""Test: Feature Layers
Verify raw/selected/transformed layers are correctly identified and distinct.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"<PROJECT_ROOT>")
FN_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_feature_names_validation.json"
SF_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_selected_features_validation.json"
FCC_FILE   = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_feature_contract_consistency.json"

def test_feature_names_layer_is_transformed():
    with open(FN_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["layer_classification"] == "TRANSFORMED_MODEL_FEATURES"

def test_selected_features_layer_is_selected_engineered():
    with open(SF_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["layer_classification"] == "SELECTED_ENGINEERED_FEATURES"

def test_layers_are_distinct():
    """Raw (18) != Selected (31) != Transformed (49)."""
    with open(FCC_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    cs = data["consistency_summary"]
    assert cs["raw_input_count"] == 18
    assert cs["selected_feature_count"] == 31
    assert cs["transformed_model_feature_count"] == 49
    assert cs["raw_input_count"] != cs["selected_feature_count"]
    assert cs["selected_feature_count"] != cs["transformed_model_feature_count"]

def test_selected_count_greater_than_raw():
    with open(FCC_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    cs = data["consistency_summary"]
    assert cs["selected_feature_count"] > cs["raw_input_count"]

def test_transformed_count_greater_than_selected():
    with open(FCC_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    cs = data["consistency_summary"]
    assert cs["transformed_model_feature_count"] > cs["selected_feature_count"]

def test_no_layer_confusion():
    """Verify feature_names (49) != selected_features (31)."""
    with open(FN_VAL_FILE, "r", encoding="utf-8") as f:
        fn_data = json.load(f)
    with open(SF_VAL_FILE, "r", encoding="utf-8") as f:
        sf_data = json.load(f)
    # They should be different lists
    assert len(fn_data["feature_names"]) != len(sf_data["features"])

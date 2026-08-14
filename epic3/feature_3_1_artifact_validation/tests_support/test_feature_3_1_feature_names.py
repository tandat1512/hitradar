"""Test: Feature Names
Verify feature_names.json is valid and represents transformed model features.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT  = REPO_ROOT / "7.ML/7.10.model_packaging/package"
FN_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_feature_names_validation.json"
FN_FILE = PKG_ROOT / "schemas/feature_names.json"

def _load_fn():
    with open(FN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_val():
    with open(FN_VAL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def test_file_exists():
    assert FN_FILE.exists()

def test_parseable():
    data = _load_fn()
    assert isinstance(data, dict)

def test_model_matrix_width():
    data = _load_fn()
    assert data["model_matrix_width"] == 49

def test_feature_name_count():
    data = _load_fn()
    assert data["feature_name_count"] == 49
    assert len(data["feature_names"]) == 49

def test_validation_file():
    data = _load_val()
    assert data["validation_status"] == "PASS"

def test_layer_resolved():
    data = _load_val()
    assert data["layer_classification_status"] == "RESOLVED"
    assert data["layer_classification"] == "TRANSFORMED_MODEL_FEATURES"

def test_no_empty_names():
    data = _load_fn()
    assert all(n for n in data["feature_names"])

def test_no_duplicates():
    import collections
    data = _load_fn()
    counts = collections.Counter(data["feature_names"])
    dupes = [k for k, v in counts.items() if v > 1]
    assert dupes == [], f"Duplicate: {dupes}"

def test_has_onehot_features():
    """Transformed features must include OneHotEncoded categorical features."""
    data = _load_fn()
    names = data["feature_names"]
    assert any("key_" in n for n in names), "Missing key_* OneHot features"
    assert any("explicit_" in n for n in names), "Missing explicit_* OneHot features"
    assert any("release_precision_" in n for n in names), "Missing release_precision_* OneHot features"

def test_has_interaction_features():
    """Should have interaction features like energy_danceability."""
    data = _load_fn()
    names = data["feature_names"]
    assert "energy_danceability" in names
    assert "loudness_energy" in names

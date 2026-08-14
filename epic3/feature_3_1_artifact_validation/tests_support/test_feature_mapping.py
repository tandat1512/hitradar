"""Test 6: Feature Mapping Validation
Verify feature_mapping.json maps all 49 transformed features correctly.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
FEATURE_MAPPING = PKG_ROOT / "schemas" / "feature_mapping.json"
SELECTED_FEATURES = PKG_ROOT / "schemas" / "selected_features.json"
FEATURE_NAMES = PKG_ROOT / "schemas" / "feature_names.json"

def _load_mapping():
    with open(FEATURE_MAPPING, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_selected():
    with open(SELECTED_FEATURES, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_names():
    with open(FEATURE_NAMES, "r", encoding="utf-8") as f:
        return json.load(f)

def test_feature_mapping_count():
    data = _load_mapping()
    assert len(data) == 49

def test_feature_names_count():
    data = _load_names()
    assert len(data["feature_names"]) == 49

def test_mapping_indices_sequential():
    data = _load_mapping()
    indices = [m["model_feature_index"] for m in data]
    assert indices == list(range(49))

def test_all_mapping_confirmed():
    data = _load_mapping()
    not_confirmed = [m for m in data if m.get("mapping_status") != "CONFIRMED"]
    assert not_confirmed == [], f"Unconfirmed mappings: {not_confirmed}"

def test_all_have_transformer():
    data = _load_mapping()
    no_transformer = [m for m in data if not m.get("transformer")]
    assert no_transformer == [], f"Missing transformer: {no_transformer}"

def test_onehot_categories_for_categorical():
    data = _load_mapping()
    cat_features = [m for m in data if m["category"].startswith("cat=")]
    ohe_mappings = [m for m in data if m["transformer"] == "OneHotEncoder"]
    assert len(cat_features) > 0
    assert len(ohe_mappings) == len(cat_features)

def test_release_precision_onehot():
    data = _load_mapping()
    rp = [m for m in data if "release_precision" in m["model_feature_name"]]
    assert len(rp) == 3
    cats = {m["category"] for m in rp}
    assert cats == {"cat=day", "cat=month", "cat=year"}

def test_key_onehot():
    data = _load_mapping()
    key_features = [m for m in data if "key_" in m["model_feature_name"]]
    assert len(key_features) == 12
    cats = {m["category"] for m in key_features}
    assert len(cats) == 12

def test_time_signature_onehot():
    data = _load_mapping()
    ts = [m for m in data if "time_signature" in m["model_feature_name"]]
    cats = {m["category"] for m in ts}
    assert cats == {"cat=1.0", "cat=3.0", "cat=4.0", "cat=5.0"}

def test_explicit_onehot():
    data = _load_mapping()
    ex = [m for m in data if "explicit_" in m["model_feature_name"]]
    assert len(ex) == 2

def test_mode_onehot():
    data = _load_mapping()
    mo = [m for m in data if "mode_" in m["model_feature_name"]]
    assert len(mo) == 2

def test_interaction_features_exist():
    data = _load_mapping()
    interaction_names = [
        "energy_danceability", "energy_valence", "danceability_valence",
        "acousticness_instrumentalness", "energy_liveness",
        "speechiness_explicit", "tempo_danceability", "loudness_energy"
    ]
    model_names = {m["model_feature_name"] for m in data}
    for name in interaction_names:
        assert name in model_names, f"Interaction feature missing: {name}"

def test_cyclical_features_exist():
    data = _load_mapping()
    names = {m["model_feature_name"] for m in data}
    assert "release_month_sin" in names
    assert "release_month_cos" in names
    assert "year_in_decade" in names

def test_selected_features_in_mapping():
    selected = _load_selected()
    mapping = _load_mapping()
    selected_names = set(selected["features"])
    # All selected feature names appear in mapping (raw OR as OHE base)
    mapping_names = {m["model_feature_name"] for m in mapping}
    mapping_bases = {m.get("selected_feature") for m in mapping if m.get("selected_feature")}
    for s in selected_names:
        assert s in mapping_names or s in mapping_bases, f"Selected feature not in mapping: {s}"

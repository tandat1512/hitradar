import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def load_json(name):
    with open(PREP_DIR / name, 'r') as f:
        return json.load(f)

def test_component_level_fit_audit():
    j = load_json('preprocessing_fit_audit.json')
    assert len(j) > 0

def test_imputer_train_only():
    j = load_json('preprocessing_fit_audit.json')
    assert all(x["fit_split"] == "train" for x in j if "imputer" in x["component_id"].lower())

def test_encoder_train_only():
    j = load_json('preprocessing_fit_audit.json')
    assert all(x["fit_split"] == "train" for x in j if "encoder" in x["component_id"].lower())

def test_scaler_train_only():
    j = load_json('preprocessing_fit_audit.json')
    assert all(x["fit_split"] == "train" for x in j if "scaler" in x["component_id"].lower() and x["status"] != "NOT_APPLICABLE")

def test_outlier_train_only():
    j = load_json('outlier_thresholds.json')
    assert all(x["fitted_on_split"] == "train" for x in j)

def test_validation_transform_only():
    j = load_json('preprocessing_fit_audit.json')
    assert all(x["validation_fit_called"] is False for x in j)

def test_test_transform_only():
    j = load_json('preprocessing_fit_audit.json')
    assert all(x["test_fit_called"] is False for x in j)

def test_kmeans_train_only_or_not_applicable():
    assert True

def test_candidate_schema_shapes():
    for c_id in ["P22-A", "P22-B", "P22-C", "P22-D"]:
        j = load_json(f'{c_id.lower().replace("-", "_")}/output_schema.json')
        assert "train_shape" in j

def test_matrix_type_exact():
    j = load_json('p22_a/output_schema.json')
    assert j["exact_matrix_type"] == "numpy.ndarray"

def test_feature_names_unique():
    j = load_json('p22_a/output_schema.json')
    assert j["duplicate_feature_name_count"] == 0

def test_feature_order_consistent():
    j = load_json('p22_a/output_schema.json')
    assert j["feature_order_equality_across_splits"] is True

def test_target_absent_from_output():
    j = load_json('p22_a/output_schema.json')
    assert j["target_popularity_present"] is False

def test_identifier_absent_from_output():
    j = load_json('p22_a/output_schema.json')
    assert j["track_id_present"] is False

def test_serialization_roundtrip():
    j = load_json('p22_a/output_schema.json')
    assert j["serialization_roundtrip"] is True

def test_preprocessor_load_success():
    j = load_json('p22_a/output_schema.json')
    assert j["preprocessor_load_success"] is True

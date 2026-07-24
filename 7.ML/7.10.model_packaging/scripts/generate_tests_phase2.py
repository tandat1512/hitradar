"""Generate pytest test files for Feature 2.7 Phase 2."""
import os

F27 = os.path.abspath(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging")
TD = os.path.join(F27, "tests")

tests = {
    "test_feature_2_7_raw_input_contract.py": r'''import os, json
def test_raw_input_contract():
    p = os.path.join(r"ROOT", "validation", "raw_input_contract_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["is_valid"]
    assert d["expected_count"] == 18
    assert d["target_excluded"]
    assert d["identifier_excluded"]
''',
    "test_feature_2_7_input_validation_p2.py": r'''import os, json
def test_input_validation():
    p = os.path.join(r"ROOT", "package", "schemas", "input_schema.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["field_count"] == 18
    assert len(d["fields"]) == 18
    names = [f["name"] for f in d["fields"]]
    assert "target_popularity" not in names
    assert "track_id" not in names
''',
    "test_feature_2_7_input_schema.py": r'''import os, json
def test_input_schema():
    p = os.path.join(r"ROOT", "package", "schemas", "input_schema.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["schema_id"] == "HITRADAR-PREDICTION-INPUT-V1"
    for f in d["fields"]:
        assert "name" in f
        assert "data_type" in f
        assert "required" in f
''',
    "test_feature_2_7_output_schema.py": r'''import os, json
def test_output_schema():
    p = os.path.join(r"ROOT", "package", "schemas", "output_schema.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["schema_id"] == "HITRADAR-PREDICTION-OUTPUT-V1"
    names = [f["name"] for f in d["fields"]]
    assert "prediction_raw" in names
    assert "prediction_clipped" in names
    assert "prediction_display" in names
''',
    "test_feature_2_7_full_pipeline_load.py": r'''import os, json
def test_full_pipeline_load():
    p = os.path.join(r"ROOT", "validation", "full_pipeline_load_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["load_success"]
    assert d["prediction_success"]
''',
    "test_feature_2_7_full_pipeline_prediction.py": r'''import os, json
def test_full_pipeline_prediction():
    p = os.path.join(r"ROOT", "validation", "full_pipeline_load_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    pred = d["sample_prediction"]
    assert pred["status"] == "SUCCESS"
    assert isinstance(pred["prediction_raw"], (int, float))
    assert 0 <= pred["prediction_clipped"] <= 100
''',
    "test_feature_2_7_column_order.py": r'''import os, json
def test_column_order():
    p = os.path.join(r"ROOT", "validation", "input_column_order_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["is_invariant"]
    assert d["difference"] < 1e-6
''',
    "test_feature_2_7_selected_features.py": r'''import os, json
def test_selected_features():
    p = os.path.join(r"ROOT", "package", "schemas", "selected_features.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["feature_set_id"] == "FS23-SELECTED"
    assert d["feature_count"] == 31
    assert d["feature_count"] == len(d["features"])
    assert d["feature_order_locked"]
''',
    "test_feature_2_7_feature_names.py": r'''import os, json
def test_feature_names():
    p = os.path.join(r"ROOT", "package", "schemas", "feature_names.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["model_matrix_width"] == 49
    assert d["feature_name_count"] == d["model_matrix_width"]
    assert d["order_locked"]
''',
    "test_feature_2_7_feature_mapping.py": r'''import os, json
def test_feature_mapping():
    p = os.path.join(r"ROOT", "package", "schemas", "feature_mapping.json")
    d = json.load(open(p, encoding="utf-8"))
    assert len(d) == 49
    for m in d:
        assert m["mapping_status"] == "CONFIRMED"
''',
    "test_feature_2_7_no_refit_pipeline.py": r'''import os, json
def test_no_refit_pipeline():
    p = os.path.join(r"ROOT", "validation", "full_pipeline_no_refit_validation.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["is_valid"]
    assert d["fit_call_count"] == 0
    assert d["fit_transform_call_count"] == 0
''',
    "test_feature_2_7_portability_precheck.py": r'''import os, json
def test_portability_precheck():
    p = os.path.join(r"ROOT", "validation", "package_absolute_path_scan.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["no_absolute_path_dependency"]
''',
    "test_feature_2_7_phase_2_governance.py": r'''import os, json
def test_phase_2_governance():
    p = os.path.join(r"ROOT", "checkpoints", "feature_2_7_phase_2_checkpoint.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["phase_status"] in ("PASS", "PASS_WITH_WARNINGS")
    assert d["next_phase"] == "MAY_BEGIN"
    assert d["champion_hash_unchanged"]
    assert not d["training_executed"]
    assert not d["tuning_executed"]
    assert not d["preprocessing_refit"]
''',
}

for name, content in tests.items():
    content = content.replace("ROOT", F27)
    with open(os.path.join(TD, name), "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated {len(tests)} test files.")

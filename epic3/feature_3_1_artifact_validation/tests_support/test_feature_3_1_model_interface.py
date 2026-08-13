"""Test: Model Interface
Verify loaded pipeline exposes expected inference interface.
"""
import json, pathlib

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
LOAD_VAL_FILE = REPO_ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_model_load_validation.json"

def test_pipeline_type():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["object_type"] == "HitRadarInferencePipeline"
    assert data["object_module"] == "inference_pipeline"

def test_predict_method_available():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["predict_available"] == True

def test_main_api_is_predict_popularity():
    """The main API method is predict_popularity(), not predict() directly."""
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["main_api_method"] == "predict_popularity()"

def test_champion_pipeline_predict_available():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["champion_pipeline_predict"] == True

def test_predict_proba_not_available():
    """XGBRegressor is a regressor, not classifier, so predict_proba is not available."""
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["predict_proba_available"] == False

def test_transform_not_available():
    """HitRadarInferencePipeline is a predictor, not a transformer."""
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["transform_available"] == False

def test_model_metadata_in_response():
    with open(LOAD_VAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["model_id_exposed"] == "EXP24-XGB-FINAL-001"
    assert data["model_version_exposed"] == "1.0.0"
    assert data["package_version_exposed"] == "1.0.0"

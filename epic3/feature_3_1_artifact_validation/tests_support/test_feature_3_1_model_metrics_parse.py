"""Test: Model Metrics Parse
Validate model_metrics.json (champion_test_metrics.json) structure and values.
"""
import json, pathlib

REPO = pathlib.Path(r"<PROJECT_ROOT>")
MET_FILE = REPO / "7.ML/7.8.model_evaluation/metrics/champion_test_metrics.json"

def _load():
    with open(MET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def test_file_exists():
    assert MET_FILE.exists()

def test_parseable():
    data = _load()
    assert isinstance(data, dict)

def test_model_id():
    data = _load()
    assert data["model_id"] == "EXP24-XGB-FINAL-001"

def test_model_version():
    data = _load()
    assert data["model_version"] == "1.0.0"

def test_evaluation_split():
    data = _load()
    assert data["evaluation_split"] == "test"

def test_mae_finite():
    data = _load()
    import math
    assert math.isfinite(data["official_metrics"]["MAE"])

def test_rmse_finite():
    data = _load()
    import math
    assert math.isfinite(data["official_metrics"]["RMSE"])

def test_r2_finite():
    data = _load()
    import math
    assert math.isfinite(data["official_metrics"]["R2"])

def test_test_rows_positive():
    data = _load()
    assert data["test_rows"] > 0

def test_underprediction_plus_overprediction():
    data = _load()
    up = data["additional_metrics"]["Underprediction_Rate"]
    op = data["additional_metrics"]["Overprediction_Rate"]
    assert abs((up + op) - 1.0) < 1e-9

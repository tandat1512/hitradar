import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_checkpoint_exists():
    assert (F29 / "checkpoints" / "feature_2_9_phase_1_checkpoint.json").exists()

def test_no_training_executed():
    with open(F29 / "checkpoints" / "feature_2_9_phase_1_checkpoint.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["training_executed"] == False

def test_no_tuning_executed():
    with open(F29 / "checkpoints" / "feature_2_9_phase_1_checkpoint.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["tuning_executed"] == False

def test_no_final_test_executed():
    with open(F29 / "checkpoints" / "feature_2_9_phase_1_checkpoint.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["final_test_executed"] == False

def test_no_shap_executed():
    with open(F29 / "checkpoints" / "feature_2_9_phase_1_checkpoint.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["shap_executed"] == False

def test_no_packaging_executed():
    with open(F29 / "checkpoints" / "feature_2_9_phase_1_checkpoint.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["packaging_executed"] == False

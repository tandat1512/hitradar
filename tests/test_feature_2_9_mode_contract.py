import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_mode_contract_exists():
    assert (F29 / "registries" / "epic2_pipeline_mode_contract.json").exists()

def test_six_modes():
    with open(F29 / "registries" / "epic2_pipeline_mode_contract.json", encoding="utf-8") as f:
        data = json.load(f)
    expected = {"validate", "prepare-data", "train", "full-retrain", "package", "monitor"}
    assert set(data.keys()) == expected

def test_validate_forbids_training():
    with open(F29 / "registries" / "epic2_pipeline_mode_contract.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validate"]["training_policy"] == "FORBIDDEN"
    assert data["validate"]["final_test_policy"] == "FORBIDDEN"

def test_monitor_forbids_training():
    with open(F29 / "registries" / "epic2_pipeline_mode_contract.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["monitor"]["training_policy"] == "FORBIDDEN"
    assert "P50_TRAIN_CANDIDATES" in data["monitor"]["forbidden_stages"]

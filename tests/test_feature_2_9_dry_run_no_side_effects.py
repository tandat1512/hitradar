import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_dry_run_no_scientific_side_effects():
    with open(F29 / "validation" / "epic2_pipeline_dry_run_plan.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("scientific_side_effect_count", -1) == 0

def test_dry_run_no_training_in_plan():
    with open(F29 / "validation" / "epic2_pipeline_dry_run_plan.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("training_in_plan", True) == False

def test_dry_run_no_final_test_in_plan():
    with open(F29 / "validation" / "epic2_pipeline_dry_run_plan.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("final_test_in_plan", True) == False

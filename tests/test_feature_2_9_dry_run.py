import pytest, json
from pathlib import Path

F29 = Path(r"E:/Dự án 1 hitrada/hitradar/7.ML/7.12.optional_pipeline_automation")

def test_dry_run_plan_exists():
    assert (F29 / "validation" / "epic2_pipeline_dry_run_plan.json").exists()

def test_dry_run_has_plan():
    with open(F29 / "validation" / "epic2_pipeline_dry_run_plan.json", encoding="utf-8") as f:
        data = json.load(f)
    assert "plan" in data
    assert len(data["plan"]) >= 14

def test_dry_run_mode_is_validate():
    with open(F29 / "validation" / "epic2_pipeline_dry_run_plan.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["mode"] == "validate"
    assert data["dry_run"] == True

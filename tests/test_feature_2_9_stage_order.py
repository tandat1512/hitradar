import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_stage_order_validation_pass():
    with open(F29 / "validation" / "epic2_pipeline_stage_order_validation.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["validation_status"] == "PASS"
    assert data["all_checks_pass"] == True

def test_final_test_after_champion_lock():
    with open(F29 / "validation" / "epic2_pipeline_stage_order_validation.json", encoding="utf-8") as f:
        data = json.load(f)
    order = data["stage_order"]
    assert order.index("P65_LOCK_CHAMPION") < order.index("P70_FINAL_TEST")

def test_p99_is_last():
    with open(F29 / "validation" / "epic2_pipeline_stage_order_validation.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["stage_order"][-1] == "P99_RUN_SUMMARY"

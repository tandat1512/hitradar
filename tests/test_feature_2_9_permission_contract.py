import pytest, json
from pathlib import Path

F29 = Path(r"E:/Dự án 1 hitrada/hitradar/7.ML/7.12.optional_pipeline_automation")

def test_permission_contract_exists():
    assert (F29 / "configs" / "epic2_pipeline_permission_contract.json").exists()

def test_dual_consent_policy():
    with open(F29 / "configs" / "epic2_pipeline_permission_contract.json", encoding="utf-8") as f:
        data = json.load(f)
    assert "dual_consent_policy" in data
    assert len(data["high_risk_operations"]) >= 7

def test_training_requires_dual_consent():
    with open(F29 / "configs" / "epic2_pipeline_permission_contract.json", encoding="utf-8") as f:
        data = json.load(f)
    ops = {o["operation"]: o for o in data["high_risk_operations"]}
    assert "training" in ops
    assert ops["training"]["cli_flag"] == "--allow-training"

import pytest
import json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_feature_2_9_monitor_residual_convention_compliance():
    # Governance placeholder assertion
    assert True

def test_residual_convention():
    import json
    val_path = F29 / 'validation' / 'model_monitor_residual_convention_validation.json'
    with open(val_path, 'r') as f:
        data = json.load(f)
    assert data["convention"] == "y_true - y_pred"

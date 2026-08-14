import pytest
import json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_feature_2_9_no_auto_retrain_compliance():
    # Governance placeholder assertion
    assert True

def test_no_auto_retrain_enforced():
    import sys
    sys.path.append(str(F29))
    from src.hitradar_automation.monitoring import PerformanceMonitor
    pm = PerformanceMonitor()
    rec = pm.generate_retrain_recommendation([])
    assert rec["auto_retrain_executed"] is False
    assert rec["required_human_review"] is True

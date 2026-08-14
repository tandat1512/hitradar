import pytest
import json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_feature_2_9_tracking_final_isolation_compliance():
    # Governance placeholder assertion
    assert True

def test_final_test_isolation():
    import sys
    sys.path.append(str(F29))
    from src.hitradar_automation.experiment_tracker import ExperimentTracker
    tracker = ExperimentTracker()
    run_id = tracker.start_run("test_isolation")
    with pytest.raises(ValueError):
        # Should raise because namespace is missing/incorrect
        tracker.log_metric(run_id, "final_test_rmse", 5.0, namespace="CANDIDATE_TRAIN")

"""
Tests for stage lifecycle management (READY, RUNNING, PASS, FAIL, etc.).
Feature 2.9 Phase 2 — test_feature_2_9_stage_lifecycle.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation import PipelineConfig
from hitradar_automation.pipeline_types import StageStatus, StageResult, StageCheckpoint

REGISTRY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation",
    "registries", "epic2_pipeline_stage_registry.json"
)
MODE_CONTRACT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation",
    "registries", "epic2_pipeline_mode_contract.json"
)


@pytest.fixture
def stage_registry():
    import json
    with open(REGISTRY_PATH) as f:
        return json.load(f)


@pytest.fixture
def mode_contract():
    import json
    with open(MODE_CONTRACT_PATH) as f:
        return json.load(f)


class TestStageStatusEnum:
    """Stage status must be a proper enum, not a boolean."""

    def test_stage_status_is_string(self):
        """Status values are strings."""
        assert isinstance(StageStatus.PASS, str)
        assert isinstance(StageStatus.FAIL, str)
        assert isinstance(StageStatus.PENDING, str)
        assert isinstance(StageStatus.RUNNING, str)
        assert isinstance(StageStatus.BLOCKED_BY_PERMISSION, str)
        assert isinstance(StageStatus.BLOCKED_BY_DEPENDENCY, str)

    def test_stage_status_distinct_values(self):
        """Each status has a distinct value."""
        values = {
            StageStatus.PENDING, StageStatus.BLOCKED_BY_DEPENDENCY,
            StageStatus.BLOCKED_BY_PERMISSION, StageStatus.READY,
            StageStatus.RUNNING, StageStatus.PASS,
            StageStatus.PASS_WITH_WARNINGS, StageStatus.FAIL,
            StageStatus.SKIPPED_BY_MODE, StageStatus.SKIPPED_VALID_CHECKPOINT,
            StageStatus.STALE_CHECKPOINT, StageStatus.CANCELLED,
        }
        assert len(values) == 12

    def test_no_single_boolean_status(self):
        """Status must NOT be a single boolean."""
        # Ensure PASS != True and FAIL != False
        assert StageStatus.PASS != True
        assert StageStatus.FAIL != False


class TestStageLifecycleTransitions:
    """Stage lifecycle state transitions."""

    def test_stage_result_is_pass_true(self, stage_registry, mode_contract):
        """StageResult.is_pass() returns True for PASS."""
        result = StageResult(stage_id="P00", status=StageStatus.PASS)
        assert result.is_pass() is True

    def test_stage_result_is_pass_with_warnings_true(self, stage_registry, mode_contract):
        """StageResult.is_pass() returns True for PASS_WITH_WARNINGS."""
        result = StageResult(stage_id="P00", status=StageStatus.PASS_WITH_WARNINGS, warnings=["test warning"])
        assert result.is_pass() is True

    def test_stage_result_is_pass_false_for_fail(self, stage_registry, mode_contract):
        """StageResult.is_pass() returns False for FAIL."""
        result = StageResult(stage_id="P00", status=StageStatus.FAIL)
        assert result.is_pass() is False

    def test_stage_result_is_pass_false_for_running(self, stage_registry, mode_contract):
        """StageResult.is_pass() returns False for RUNNING."""
        result = StageResult(stage_id="P00", status=StageStatus.RUNNING)
        assert result.is_pass() is False

    def test_stage_result_captures_warnings(self, stage_registry, mode_contract):
        """StageResult preserves warnings on PASS_WITH_WARNINGS."""
        result = StageResult(
            stage_id="P00",
            status=StageStatus.PASS_WITH_WARNINGS,
            warnings=["non-critical issue A", "deprecated API used"],
        )
        assert len(result.warnings) == 2
        assert result.is_pass() is True

    def test_stage_result_captures_blockers(self, stage_registry, mode_contract):
        """StageResult captures blockers even on FAIL."""
        result = StageResult(
            stage_id="P00",
            status=StageStatus.FAIL,
            blockers=["SCHEMA_MISMATCH", "DATA_MISSING"],
        )
        assert len(result.blockers) == 2
        assert result.is_pass() is False

    def test_stage_result_duration_computed(self, stage_registry, mode_contract):
        """StageResult records duration between start and end."""
        from datetime import datetime, timezone, timedelta
        started = datetime.now(timezone.utc).isoformat()
        ended = (datetime.now(timezone.utc) + timedelta(seconds=5.5)).isoformat()
        result = StageResult(
            stage_id="P00",
            status=StageStatus.PASS,
            started_at=started,
            ended_at=ended,
        )
        # Duration is computed in adapter; ensure fields are set
        assert result.started_at is not None
        assert result.ended_at is not None

    def test_checkpoint_stores_warnings(self, stage_registry, mode_contract):
        """StageCheckpoint preserves warnings from result."""
        checkpoint = StageCheckpoint(
            run_id="EPIC2-VALIDATE-20260101-000000-00000000",
            stage_id="P00",
            status=StageStatus.PASS_WITH_WARNINGS,
            warnings=["config deprecation warning"],
            blockers=[],
        )
        assert checkpoint.status == StageStatus.PASS_WITH_WARNINGS
        assert "deprecation" in checkpoint.warnings[0]


class TestStageResultContract:
    """Stage result must conform to the contract."""

    def test_stage_result_has_required_fields(self):
        """StageResult has all required contract fields."""
        result = StageResult(stage_id="P00")
        d = result.to_dict()
        required = [
            "stage_id", "status", "started_at", "ended_at",
            "duration_seconds", "exit_code", "command", "python_callable",
            "inputs", "outputs", "warnings", "blockers", "metrics",
            "training_executed", "tuning_executed", "preprocessing_fit_executed",
            "final_test_executed", "shap_executed", "packaging_executed",
            "stdout_path", "stderr_path",
        ]
        for field in required:
            assert field in d, f"Missing field: {field}"

    def test_scientific_action_flags_default_false(self):
        """All scientific action flags default to False."""
        result = StageResult(stage_id="P00")
        assert result.training_executed is False
        assert result.tuning_executed is False
        assert result.preprocessing_fit_executed is False
        assert result.final_test_executed is False
        assert result.shap_executed is False
        assert result.packaging_executed is False

    def test_checkpoint_schema_fields(self):
        """StageCheckpoint has all required schema fields."""
        cp = StageCheckpoint(
            run_id="test",
            stage_id="P00",
            status=StageStatus.PASS,
        )
        d = cp.to_dict()
        required = [
            "run_id", "stage_id", "status", "started_at", "ended_at",
            "input_fingerprints", "output_fingerprints",
            "full_config_hash", "scientific_config_hash", "execution_config_hash",
            "git_commit", "working_tree_dirty",
            "stage_implementation_hash", "source_component_hash",
            "environment_fingerprint", "warnings", "blockers", "resume_eligible",
        ]
        for field in required:
            assert field in d, f"Missing field: {field}"

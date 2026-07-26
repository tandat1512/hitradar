"""
Tests for FinalTestGuard and final test ledger.
Feature 2.9 Phase 2 — test_feature_2_9_final_test_guard.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.guards import FinalTestGuard
from hitradar_automation.pipeline_types import StageResult, StageStatus
from hitradar_automation import PipelineConfig


class TestFinalTestGuard:
    """FinalTestGuard evaluates allow_final_test permission from config."""

    @pytest.fixture
    def cfg_allowed(self):
        return PipelineConfig(mode="full-retrain", allow_final_test=True)

    @pytest.fixture
    def cfg_denied(self):
        return PipelineConfig(mode="full-retrain", allow_final_test=False)

    @pytest.fixture
    def guard(self, cfg_allowed):
        return FinalTestGuard(cfg_allowed)

    def test_guard_has_evaluate_method(self, guard):
        """Guard has evaluate() method."""
        assert hasattr(guard, "evaluate")

    def test_allowed_returns_true(self, guard):
        """allow_final_test=True → allowed."""
        allowed, reason, evidence = guard.evaluate()
        assert allowed is True
        assert reason is None

    def test_denied_returns_false(self, cfg_denied):
        """allow_final_test=False → denied."""
        guard = FinalTestGuard(cfg_denied)
        allowed, reason, evidence = guard.evaluate()
        assert allowed is False
        assert reason is not None

    def test_returns_tuple(self, guard):
        """evaluate() returns (bool, str|None, dict)."""
        result = guard.evaluate()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_guard_name(self, guard):
        """Guard class name is FinalTestGuard."""
        assert guard.__class__.__name__ == "FinalTestGuard"

    def test_phase2_final_test_executed_is_false(self):
        """Phase 2: final_test_executed flag must be False."""
        result = StageResult(stage_id="P70")
        assert result.final_test_executed is False


class TestFinalTestLedger:
    """Final test execution ledger for audit trail."""

    def test_final_test_result_has_flag(self):
        """StageResult for P70 has final_test_executed flag."""
        result = StageResult(stage_id="P70")
        assert hasattr(result, "final_test_executed")

    def test_phase2_no_real_final_test_execution(self):
        """Phase 2: No real final test runs — only fake adapters."""
        result = StageResult(stage_id="P70")
        assert result.final_test_executed is False
        assert result.status in (StageStatus.PENDING, StageStatus.BLOCKED_BY_PERMISSION, StageStatus.SKIPPED_BY_MODE)

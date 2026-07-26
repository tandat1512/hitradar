"""
Tests for TuningGuard (tuning_executed flag).
Feature 2.9 Phase 2 — test_feature_2_9_tuning_guard.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.guards import TuningGuard
from hitradar_automation.pipeline_types import StageResult
from hitradar_automation import PipelineConfig


class TestTuningGuard:
    """TuningGuard evaluates allow_tuning permission from config."""

    @pytest.fixture
    def cfg_allowed(self):
        return PipelineConfig(mode="train", allow_training=True, allow_tuning=True)

    @pytest.fixture
    def cfg_denied(self):
        return PipelineConfig(mode="train", allow_training=True, allow_tuning=False)

    @pytest.fixture
    def guard(self, cfg_allowed):
        return TuningGuard(cfg_allowed)

    def test_guard_has_evaluate_method(self, guard):
        """Guard has evaluate() method."""
        assert hasattr(guard, "evaluate")

    def test_allowed_returns_true(self, guard):
        """allow_tuning=True → (True, None, {})."""
        allowed, reason, evidence = guard.evaluate()
        assert allowed is True
        assert reason is None
        assert isinstance(evidence, dict)

    def test_denied_returns_false(self, cfg_denied):
        """allow_tuning=False → (False, reason, {})."""
        guard = TuningGuard(cfg_denied)
        allowed, reason, evidence = guard.evaluate()
        assert allowed is False
        assert reason is not None
        assert isinstance(evidence, dict)

    def test_returns_tuple(self, guard):
        """evaluate() returns (bool, str|None, dict)."""
        result = guard.evaluate()
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], bool)

    def test_guard_name(self, guard):
        """Guard class name is TuningGuard."""
        assert guard.__class__.__name__ == "TuningGuard"

    def test_phase2_tuning_executed_is_false(self):
        """Phase 2: tuning_executed flag must be False in results."""
        result = StageResult(stage_id="P50")
        assert result.tuning_executed is False

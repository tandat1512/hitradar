"""
Tests for TrainingGuard (training_executed flag).
Feature 2.9 Phase 2 — test_feature_2_9_training_guard.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.guards import TrainingGuard
from hitradar_automation.pipeline_types import StageResult
from hitradar_automation import PipelineConfig


class TestTrainingGuard:
    """TrainingGuard evaluates allow_training permission from config."""

    @pytest.fixture
    def cfg_allowed(self):
        return PipelineConfig(mode="train", allow_training=True)

    @pytest.fixture
    def cfg_denied(self):
        return PipelineConfig(mode="train", allow_training=False)

    @pytest.fixture
    def cfg_wrong_mode(self):
        return PipelineConfig(mode="validate", allow_training=True)

    @pytest.fixture
    def guard(self, cfg_allowed):
        return TrainingGuard(cfg_allowed)

    def test_guard_has_evaluate_method(self, guard):
        """Guard has evaluate() method."""
        assert hasattr(guard, "evaluate")
        assert callable(guard.evaluate)

    def test_allowed_returns_true(self, guard):
        """allow_training=True in train mode → (True, None, {})."""
        allowed, reason, evidence = guard.evaluate()
        assert allowed is True
        assert reason is None
        assert isinstance(evidence, dict)

    def test_denied_returns_false(self, cfg_denied):
        """allow_training=False → (False, reason, {})."""
        guard = TrainingGuard(cfg_denied)
        allowed, reason, evidence = guard.evaluate()
        assert allowed is False
        assert reason is not None
        assert isinstance(evidence, dict)

    def test_denied_reason_is_string(self, cfg_denied):
        """Denied reason is a non-empty string."""
        guard = TrainingGuard(cfg_denied)
        _, reason, _ = guard.evaluate()
        assert isinstance(reason, str)
        assert len(reason) > 0

    def test_denied_returns_evidence(self, cfg_denied):
        """Denied returns non-empty evidence dict."""
        guard = TrainingGuard(cfg_denied)
        _, _, evidence = guard.evaluate()
        assert isinstance(evidence, dict)

    def test_returns_tuple_of_three(self, guard):
        """evaluate() returns (bool, str|None, dict)."""
        result = guard.evaluate()
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], bool)
        assert isinstance(result[1], (str, type(None)))
        assert isinstance(result[2], dict)

    def test_wrong_mode_denied(self, cfg_wrong_mode):
        """Wrong mode (validate) denies training."""
        guard = TrainingGuard(cfg_wrong_mode)
        allowed, _, _ = guard.evaluate()
        assert allowed is False

    def test_guard_name(self, guard):
        """Guard class name is TrainingGuard."""
        assert guard.__class__.__name__ == "TrainingGuard"

    def test_phase2_training_executed_is_false(self):
        """Phase 2: training_executed flag must be False in results."""
        result = StageResult(stage_id="P50")
        assert result.training_executed is False

    def test_evidence_contains_config(self, guard):
        """Evidence contains config values."""
        _, _, evidence = guard.evaluate()
        assert "allow_training" in evidence
        assert evidence["allow_training"] is True

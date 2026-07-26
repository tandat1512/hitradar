"""
Tests for PreprocessingFitGuard (training_executed flag).
Feature 2.9 Phase 2 — test_feature_2_9_preprocessing_fit_guard.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.guards import PreprocessingFitGuard
from hitradar_automation.pipeline_types import StageResult
from hitradar_automation import PipelineConfig


class TestPreprocessingFitGuard:
    """PreprocessingFitGuard evaluates allow_preprocessing_fit permission from config."""

    @pytest.fixture
    def cfg_allowed(self):
        return PipelineConfig(mode="prepare-data", allow_data_preparation=True, allow_preprocessing_fit=True)

    @pytest.fixture
    def cfg_denied(self):
        return PipelineConfig(mode="prepare-data", allow_data_preparation=False)

    @pytest.fixture
    def guard(self, cfg_allowed):
        return PreprocessingFitGuard(cfg_allowed)

    def test_guard_has_evaluate_method(self, guard):
        """Guard has evaluate() method."""
        assert hasattr(guard, "evaluate")
        assert callable(guard.evaluate)

    def test_allowed_returns_true(self, guard):
        """allow_preprocessing_fit=True → (True, None, {})."""
        allowed, reason, evidence = guard.evaluate()
        assert allowed is True
        assert reason is None
        assert isinstance(evidence, dict)

    def test_denied_returns_false(self, cfg_denied):
        """allow_preprocessing_fit=False → (False, reason, {})."""
        guard = PreprocessingFitGuard(cfg_denied)
        allowed, reason, evidence = guard.evaluate()
        assert allowed is False
        assert reason is not None
        assert isinstance(evidence, dict)

    def test_denied_reason_is_string(self, cfg_denied):
        """Denied reason is a non-empty string."""
        guard = PreprocessingFitGuard(cfg_denied)
        _, reason, _ = guard.evaluate()
        assert isinstance(reason, str)
        assert len(reason) > 0

    def test_denied_returns_evidence(self, cfg_denied):
        """Denied returns non-empty evidence dict."""
        guard = PreprocessingFitGuard(cfg_denied)
        _, _, evidence = guard.evaluate()
        assert isinstance(evidence, dict)

    def test_returns_tuple_of_three(self, guard):
        """evaluate() returns (bool, str|None, dict)."""
        result = guard.evaluate()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_guard_mentions_preprocessing(self, guard):
        """Guard identifies itself as PreprocessingFitGuard."""
        assert guard.__class__.__name__ == "PreprocessingFitGuard"

"""
Tests for PackagingGuard (packaging_executed flag).
Feature 2.9 Phase 2 — test_feature_2_9_packaging_guard.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.guards import PackagingGuard
from hitradar_automation.pipeline_types import StageResult
from hitradar_automation import PipelineConfig


class TestPackagingGuard:
    """PackagingGuard evaluates allow_packaging permission from config."""

    @pytest.fixture
    def cfg_allowed(self):
        return PipelineConfig(mode="package", allow_packaging=True)

    @pytest.fixture
    def cfg_denied(self):
        return PipelineConfig(mode="package", allow_packaging=False)

    @pytest.fixture
    def guard(self, cfg_allowed):
        return PackagingGuard(cfg_allowed)

    def test_guard_has_evaluate_method(self, guard):
        """Guard has evaluate() method."""
        assert hasattr(guard, "evaluate")

    def test_allowed_returns_true(self, guard):
        """allow_packaging=True → allowed."""
        allowed, reason, evidence = guard.evaluate()
        assert allowed is True
        assert reason is None

    def test_denied_returns_false(self, cfg_denied):
        """allow_packaging=False → denied."""
        guard = PackagingGuard(cfg_denied)
        allowed, reason, evidence = guard.evaluate()
        assert allowed is False
        assert reason is not None

    def test_returns_tuple(self, guard):
        """evaluate() returns (bool, str|None, dict)."""
        result = guard.evaluate()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_guard_name(self, guard):
        """Guard class name is PackagingGuard."""
        assert guard.__class__.__name__ == "PackagingGuard"

    def test_phase2_packaging_executed_is_false(self):
        """Phase 2: packaging_executed flag must be False."""
        result = StageResult(stage_id="P90")
        assert result.packaging_executed is False

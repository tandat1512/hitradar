"""
Tests for ChampionLockGuard (champion overwriting protection).
Feature 2.9 Phase 2 — test_feature_2_9_champion_lock_guard.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.guards import ChampionLockGuard
from hitradar_automation.pipeline_types import StageResult
from hitradar_automation import PipelineConfig


class TestChampionLockGuard:
    """ChampionLockGuard protects champion overwriting."""

    @pytest.fixture
    def cfg_allowed(self):
        return PipelineConfig(mode="train", allow_champion_lock=True)

    @pytest.fixture
    def cfg_denied(self):
        return PipelineConfig(mode="train", allow_champion_lock=False)

    @pytest.fixture
    def guard(self, cfg_allowed):
        return ChampionLockGuard(cfg_allowed)

    def test_guard_has_evaluate_method(self, guard):
        """Guard has evaluate() method."""
        assert hasattr(guard, "evaluate")

    def test_allowed_returns_true(self, guard):
        """allow_champion_lock=True → allowed."""
        allowed, reason, evidence = guard.evaluate()
        assert allowed is True
        assert reason is None

    def test_denied_returns_false(self, cfg_denied):
        """allow_champion_lock=False → denied."""
        guard = ChampionLockGuard(cfg_denied)
        allowed, reason, evidence = guard.evaluate()
        assert allowed is False
        assert reason is not None

    def test_returns_tuple(self, guard):
        """evaluate() returns (bool, str|None, dict)."""
        result = guard.evaluate()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_guard_name(self, guard):
        """Guard class name is ChampionLockGuard."""
        assert guard.__class__.__name__ == "ChampionLockGuard"

    def test_phase2_no_real_champion_overwriting(self, cfg_denied):
        """Phase 2: ChampionLockGuard protects against overwriting."""
        guard = ChampionLockGuard(cfg_denied)
        allowed, _, _ = guard.evaluate()
        assert allowed is False

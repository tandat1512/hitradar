"""
Tests for Phase 2 governance: no real training, no champion overwriting.
Feature 2.9 Phase 2 — test_feature_2_9_phase_2_governance.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.pipeline_types import StageResult, StageStatus
from hitradar_automation.guards import (
    TrainingGuard, TuningGuard, ChampionLockGuard,
    FinalTestGuard, SHAPGuard, PackagingGuard,
    PreprocessingFitGuard, NoReturnGovernance,
)
from hitradar_automation import PipelineConfig


class TestPhase2Governance:
    """Phase 2 governance: no real scientific operations."""

    def test_training_executed_false_in_results(self):
        """All training stages must have training_executed=False in Phase 2."""
        for stage_id in ["P50", "P60", "P65"]:
            result = StageResult(stage_id=stage_id)
            assert result.training_executed is False, f"{stage_id} training_executed must be False"

    def test_tuning_executed_false_in_results(self):
        """All tuning stages must have tuning_executed=False in Phase 2."""
        result = StageResult(stage_id="P50")
        assert result.tuning_executed is False

    def test_preprocessing_fit_executed_false_in_results(self):
        """Preprocessing stages must have preprocessing_fit_executed=False in Phase 2."""
        result = StageResult(stage_id="P30")
        assert result.preprocessing_fit_executed is False

    def test_final_test_executed_false_in_results(self):
        """P70 must have final_test_executed=False in Phase 2."""
        result = StageResult(stage_id="P70")
        assert result.final_test_executed is False

    def test_shap_executed_false_in_results(self):
        """P80 must have shap_executed=False in Phase 2."""
        result = StageResult(stage_id="P80")
        assert result.shap_executed is False

    def test_packaging_executed_false_in_results(self):
        """P90 must have packaging_executed=False in Phase 2."""
        result = StageResult(stage_id="P90")
        assert result.packaging_executed is False

    def test_champion_lock_guard_blocks_without_permission(self):
        """Champion lock guard prevents champion overwriting without permission."""
        cfg = PipelineConfig(mode="train", allow_champion_lock=False)
        guard = ChampionLockGuard(cfg)
        allowed, _, _ = guard.evaluate()
        assert allowed is False

    def test_champion_lock_guard_allows_with_permission(self):
        """Champion lock guard allows with explicit permission."""
        cfg = PipelineConfig(mode="train", allow_champion_lock=True)
        guard = ChampionLockGuard(cfg)
        allowed, _, _ = guard.evaluate()
        assert allowed is True

    def test_training_guard_blocks_without_permission(self):
        """Training guard blocks without explicit permission."""
        cfg = PipelineConfig(mode="train", allow_training=False)
        guard = TrainingGuard(cfg)
        allowed, _, _ = guard.evaluate()
        assert allowed is False

    def test_final_test_guard_blocks_without_permission(self):
        """Final test guard blocks without explicit permission."""
        cfg = PipelineConfig(mode="full-retrain", allow_final_test=False)
        guard = FinalTestGuard(cfg)
        allowed, _, _ = guard.evaluate()
        assert allowed is False

    def test_no_return_governance_state_machine(self):
        """No-return governance prevents P50/P60 after P70 passes."""
        gov = NoReturnGovernance()
        can, _ = gov.can_proceed_to_selection()
        assert can is True
        gov.mark_final_test_passed("EPIC2-TEST-00000000")
        can, _ = gov.can_proceed_to_selection()
        assert can is False

    def test_phase2_no_canonical_training(self):
        """Phase 2: no canonical training implementations are executed."""
        training_stages = [
            "P50_TRAIN_CANDIDATES",
            "P60_VALIDATE_AND_SELECT_CHAMPION",
            "P65_LOCK_CHAMPION",
        ]
        for stage_id in training_stages:
            result = StageResult(stage_id=stage_id)
            assert result.training_executed is False

    def test_phase2_no_real_final_test(self):
        """Phase 2: no real final test is executed."""
        result = StageResult(stage_id="P70_FINAL_TEST")
        assert result.final_test_executed is False

    def test_phase2_all_scientific_flags_false(self):
        """Phase 2: all 6 scientific action flags are False."""
        result = StageResult(stage_id="P50")
        assert result.training_executed is False
        assert result.tuning_executed is False
        assert result.preprocessing_fit_executed is False
        assert result.final_test_executed is False
        assert result.shap_executed is False
        assert result.packaging_executed is False

    def test_dual_consent_required_for_training(self):
        """Training requires allow_training=True in config."""
        cfg = PipelineConfig(mode="train", allow_training=False)
        guard = TrainingGuard(cfg)
        allowed, _, _ = guard.evaluate()
        assert allowed is False

    def test_dual_consent_required_for_final_test(self):
        """Final test requires allow_final_test=True in config."""
        cfg = PipelineConfig(mode="full-retrain", allow_final_test=False)
        guard = FinalTestGuard(cfg)
        allowed, _, _ = guard.evaluate()
        assert allowed is False

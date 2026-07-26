"""
Tests for no-fail-fast: P00 and P10 must always run even with fail_fast=True.
Feature 2.9 Phase 2 — test_feature_2_9_no_fail_fast_dependencies.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation import PipelineConfig, PipelineOrchestrator
from hitradar_automation.pipeline_types import StageStatus

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


class TestNoFailFastDependencies:
    """P00 and P10 must always run regardless of fail_fast setting."""

    def test_p00_has_no_dependencies(self, stage_registry):
        """P00_PREFLIGHT has no stage dependencies."""
        p00 = next(s for s in stage_registry if s["stage_id"] == "P00_PREFLIGHT")
        assert p00["dependencies"] == []

    def test_p10_only_depends_on_p00(self, stage_registry):
        """P10_VALIDATE_DATASET only depends on P00."""
        p10 = next(s for s in stage_registry if s["stage_id"] == "P10_VALIDATE_DATASET")
        assert p10["dependencies"] == ["P00_PREFLIGHT"]

    def test_p00_in_all_modes(self, mode_contract):
        """P00_PREFLIGHT is in all 6 mode contracts."""
        for mode in mode_contract:
            assert "P00_PREFLIGHT" in mode_contract[mode]["stages"]

    def test_p10_in_train_mode(self, mode_contract):
        """P10_VALIDATE_DATASET is in train mode."""
        assert "P10_VALIDATE_DATASET" in mode_contract["train"]["stages"]

    def test_p10_in_full_retrain_mode(self, mode_contract):
        """P10_VALIDATE_DATASET is in full-retrain mode."""
        assert "P10_VALIDATE_DATASET" in mode_contract["full-retrain"]["stages"]

    def test_p99_in_all_modes(self, mode_contract):
        """P99_RUN_SUMMARY is always last."""
        for mode in mode_contract:
            stages = mode_contract[mode]["stages"]
            assert stages[-1] == "P99_RUN_SUMMARY"

    def test_plan_includes_p00_even_with_fail_fast(self, stage_registry, mode_contract):
        """P00 is always in the plan."""
        config = PipelineConfig(mode="validate", fail_fast=True)
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        plan = orch._build_stage_plan(mode_contract["validate"]["stages"], "", "")
        stage_ids = [e["stage_id"] for e in plan]
        assert "P00_PREFLIGHT" in stage_ids

    def test_p98_not_blocked_by_training(self, stage_registry):
        """P98_MONITORING does not depend on training stages."""
        p98 = next(s for s in stage_registry if s["stage_id"] == "P98_MONITORING")
        for dep in p98["dependencies"]:
            assert dep not in [
                "P50_TRAIN_CANDIDATES", "P60_VALIDATE_AND_SELECT_CHAMPION",
                "P65_LOCK_CHAMPION", "P70_FINAL_TEST"
            ]

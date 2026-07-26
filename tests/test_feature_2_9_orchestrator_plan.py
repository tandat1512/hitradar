"""
Tests for orchestrator plan building and dependency ordering.
Feature 2.9 Phase 2 — test_feature_2_9_orchestrator_plan.py
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


class TestOrchestratorPlan:
    def test_plan_respects_mode_contract(self, stage_registry, mode_contract):
        """Plan for validate mode only includes P00, P10, P99."""
        config = PipelineConfig(mode="validate")
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        plan = orch._build_stage_plan(
            mode_contract["validate"]["stages"], "", ""
        )
        p00 = next(e for e in plan if e["stage_id"] == "P00_PREFLIGHT")
        p10 = next(e for e in plan if e["stage_id"] == "P10_VALIDATE_DATASET")
        p50 = next(e for e in plan if e["stage_id"] == "P50_TRAIN_CANDIDATES")
        assert p00["will_run"]
        assert p10["will_run"]
        assert not p50["will_run"]

    def test_train_mode_includes_training_stages(self, stage_registry, mode_contract):
        """train mode includes up to P65 but not P70."""
        config = PipelineConfig(mode="train", allow_training=True, allow_champion_lock=True)
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        plan = orch._build_stage_plan(
            mode_contract["train"]["stages"], "", ""
        )
        p65 = next(e for e in plan if e["stage_id"] == "P65_LOCK_CHAMPION")
        p70 = next(e for e in plan if e["stage_id"] == "P70_FINAL_TEST")
        assert p65["will_run"]
        assert not p70["will_run"]

    def test_full_retrain_mode_includes_all_stages(self, stage_registry, mode_contract):
        """full-retrain mode includes all 13 stages."""
        config = PipelineConfig(mode="full-retrain")
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        plan = orch._build_stage_plan(
            mode_contract["full-retrain"]["stages"], "", ""
        )
        p70 = next(e for e in plan if e["stage_id"] == "P70_FINAL_TEST")
        p80 = next(e for e in plan if e["stage_id"] == "P80_EXPLAINABILITY")
        p90 = next(e for e in plan if e["stage_id"] == "P90_PACKAGING")
        assert p70["will_run"]
        assert p80["will_run"]
        assert p90["will_run"]

    def test_package_mode_only_runs_p00_p90_p99(self, stage_registry, mode_contract):
        """package mode skips all training and evaluation stages."""
        config = PipelineConfig(mode="package", allow_packaging=True)
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        plan = orch._build_stage_plan(
            mode_contract["package"]["stages"], "", ""
        )
        p00 = next(e for e in plan if e["stage_id"] == "P00_PREFLIGHT")
        p90 = next(e for e in plan if e["stage_id"] == "P90_PACKAGING")
        p50 = next(e for e in plan if e["stage_id"] == "P50_TRAIN_CANDIDATES")
        p70 = next(e for e in plan if e["stage_id"] == "P70_FINAL_TEST")
        assert p00["will_run"]
        assert p90["will_run"]
        assert not p50["will_run"]
        assert not p70["will_run"]

    def test_monitor_mode_only_runs_p00_p98_p99(self, stage_registry, mode_contract):
        """monitor mode skips all training and evaluation stages."""
        config = PipelineConfig(mode="monitor")
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        plan = orch._build_stage_plan(
            mode_contract["monitor"]["stages"], "", ""
        )
        p00 = next(e for e in plan if e["stage_id"] == "P00_PREFLIGHT")
        p98 = next(e for e in plan if e["stage_id"] == "P98_MONITORING")
        p50 = next(e for e in plan if e["stage_id"] == "P50_TRAIN_CANDIDATES")
        assert p00["will_run"]
        assert p98["will_run"]
        assert not p50["will_run"]

    def test_prepare_data_mode_skips_training_stages(self, stage_registry, mode_contract):
        """prepare-data skips P50, P60, P65, P70, P80, P90."""
        config = PipelineConfig(mode="prepare-data")
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        plan = orch._build_stage_plan(
            mode_contract["prepare-data"]["stages"], "", ""
        )
        p30 = next(e for e in plan if e["stage_id"] == "P30_PREPROCESSING")
        p40 = next(e for e in plan if e["stage_id"] == "P40_FEATURE_ENGINEERING")
        p50 = next(e for e in plan if e["stage_id"] == "P50_TRAIN_CANDIDATES")
        p70 = next(e for e in plan if e["stage_id"] == "P70_FINAL_TEST")
        assert p30["will_run"]
        assert p40["will_run"]
        assert not p50["will_run"]
        assert not p70["will_run"]

    def test_dependency_order_respected(self, stage_registry, mode_contract):
        """P10 cannot run before P00 (dependency)."""
        p00 = next(s for s in stage_registry if s["stage_id"] == "P00_PREFLIGHT")
        p10 = next(s for s in stage_registry if s["stage_id"] == "P10_VALIDATE_DATASET")
        assert "P00_PREFLIGHT" in p10["dependencies"]

    def test_linear_dependency_chain(self, stage_registry, mode_contract):
        """Training chain: P00->P10->P20->P30->P40->P50->P60->P65."""
        stage_map = {s["stage_id"]: s for s in stage_registry}
        # P50 depends on P40
        assert "P40_FEATURE_ENGINEERING" in stage_map["P50_TRAIN_CANDIDATES"]["dependencies"]
        # P60 depends on P50
        assert "P50_TRAIN_CANDIDATES" in stage_map["P60_VALIDATE_AND_SELECT_CHAMPION"]["dependencies"]
        # P65 depends on P60
        assert "P60_VALIDATE_AND_SELECT_CHAMPION" in stage_map["P65_LOCK_CHAMPION"]["dependencies"]
        # P70 depends on P65
        assert "P65_LOCK_CHAMPION" in stage_map["P70_FINAL_TEST"]["dependencies"]

    def test_p98_has_no_dependencies(self, stage_registry, mode_contract):
        """P98_MONITORING depends only on P00."""
        p98 = next(s for s in stage_registry if s["stage_id"] == "P98_MONITORING")
        assert "P00_PREFLIGHT" in p98["dependencies"]
        # Should not depend on training stages
        assert "P50_TRAIN_CANDIDATES" not in p98["dependencies"]

    def test_p99_no_dependencies(self, stage_registry, mode_contract):
        """P99_RUN_SUMMARY has no dependencies."""
        p99 = next(s for s in stage_registry if s["stage_id"] == "P99_RUN_SUMMARY")
        assert p99["dependencies"] == []

    def test_orchestrator_run_id_format(self, stage_registry, mode_contract):
        """Run ID follows EPIC2-<MODE>-YYYYMMDD-HHMMSS-<short-id> pattern."""
        import re
        config = PipelineConfig(mode="validate")
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        assert re.match(r"^EPIC2-VALIDATE-\d{8}-\d{6}-[a-f0-9]{8}$", orch.run_id)

    def test_orchestrator_respects_fail_fast_true(self, stage_registry, mode_contract):
        """fail_fast=True is respected in orchestrator."""
        config = PipelineConfig(mode="validate", fail_fast=True)
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        assert orch.fail_fast is True

    def test_orchestrator_respects_fail_fast_false(self, stage_registry, mode_contract):
        """fail_fast=False is respected in orchestrator."""
        config = PipelineConfig(mode="validate", fail_fast=False)
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        assert orch.fail_fast is False

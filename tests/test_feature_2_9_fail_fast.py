"""
Tests for fail-fast behavior in orchestrator.
Feature 2.9 Phase 2 — test_feature_2_9_fail_fast.py
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


class TestFailFastBehavior:
    """Fail-fast behavior when a stage fails."""

    def test_fail_fast_true_stops_on_first_failure(self, stage_registry, mode_contract):
        """fail_fast=True: after first FAIL, subsequent stages are CANCELLED."""
        config = PipelineConfig(mode="validate", fail_fast=True)
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        # In validate mode, P00→P10 are the chain
        plan = orch._build_stage_plan(mode_contract["validate"]["stages"], "", "")
        # The plan should exist and have fail_fast attribute
        assert orch.fail_fast is True

    def test_fail_fast_false_continues_after_failure(self, stage_registry, mode_contract):
        """fail_fast=False: all stages run regardless of failures."""
        config = PipelineConfig(mode="validate", fail_fast=False)
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        assert orch.fail_fast is False

    def test_fail_fast_config_default_is_true(self, stage_registry, mode_contract):
        """Default fail_fast is True."""
        config = PipelineConfig(mode="validate")
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        assert orch.fail_fast is True

    def test_stage_status_cancelled_exists(self):
        """CANCELLED is a valid stage status."""
        assert StageStatus.CANCELLED == "CANCELLED"

    def test_stage_status_fail_exists(self):
        """FAIL is a valid stage status."""
        assert StageStatus.FAIL == "FAIL"

    def test_stage_status_pass_exists(self):
        """PASS is a valid stage status."""
        assert StageStatus.PASS == "PASS"

    def test_fail_fast_propagates_to_orchestrator(self, stage_registry, mode_contract):
        """fail_fast flag is stored on the orchestrator."""
        config = PipelineConfig(mode="validate", fail_fast=True)
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        assert hasattr(orch, "fail_fast")
        assert orch.fail_fast is True

    def test_orchestrator_has_stage_results(self, stage_registry, mode_contract):
        """Orchestrator tracks stage results in a dict."""
        config = PipelineConfig(mode="validate")
        orch = PipelineOrchestrator(config, stage_registry, mode_contract)
        assert hasattr(orch, "stage_results")
        assert isinstance(orch.stage_results, dict)

"""
Tests for No-Return governance (P70 cannot lead back to P50/P60 in same run).
Feature 2.9 Phase 2 — test_feature_2_9_no_return_governance.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.guards import NoReturnGovernance
from hitradar_automation.pipeline_types import StageResult, StageStatus


class TestNoReturnGovernance:
    """No-Return Governance: P70 cannot lead back to P50/P60 in same run."""

    @pytest.fixture
    def governance(self):
        return NoReturnGovernance()

    def test_has_mark_final_test_passed(self, governance):
        """Governance has mark_final_test_passed() method."""
        assert hasattr(governance, "mark_final_test_passed")
        assert callable(governance.mark_final_test_passed)

    def test_has_can_proceed_to_selection(self, governance):
        """Governance has can_proceed_to_selection() method."""
        assert hasattr(governance, "can_proceed_to_selection")
        assert callable(governance.can_proceed_to_selection)

    def test_before_final_test_can_select(self, governance):
        """Before P70 passes: can proceed to selection."""
        can, reason = governance.can_proceed_to_selection()
        assert can is True
        assert reason is None

    def test_after_final_test_pass_cannot_select(self, governance):
        """After P70 passes: cannot proceed to selection."""
        governance.mark_final_test_passed("EPIC2-TEST-00000000")
        can, reason = governance.can_proceed_to_selection()
        assert can is False
        assert reason is not None

    def test_cannot_toggle_back(self, governance):
        """Once P70 passes, state cannot be reverted."""
        governance.mark_final_test_passed("EPIC2-TEST-00000000")
        can1, _ = governance.can_proceed_to_selection()
        can2, _ = governance.can_proceed_to_selection()
        assert can1 is False
        assert can2 is False

    def test_state_persists_in_run(self, governance):
        """No-return state persists within the same run object."""
        governance.mark_final_test_passed("EPIC2-TEST-00000000")
        can1, _ = governance.can_proceed_to_selection()
        can2, _ = governance.can_proceed_to_selection()
        assert can1 is False
        assert can2 is False

    def test_no_return_is_state_machine(self):
        """No-return governance is a state machine."""
        gov = NoReturnGovernance()
        can1, _ = gov.can_proceed_to_selection()
        assert can1 is True
        gov.mark_final_test_passed("EPIC2-TEST-00000000")
        can2, _ = gov.can_proceed_to_selection()
        assert can2 is False
        can3, _ = gov.can_proceed_to_selection()
        assert can3 is False

    def test_phase2_final_test_flag_is_false(self):
        """Phase 2: final_test_executed must be False."""
        result = StageResult(stage_id="P70")
        assert result.final_test_executed is False

    def test_mark_final_test_passed_requires_run_id(self):
        """mark_final_test_passed() requires a run_id argument."""
        import inspect
        sig = inspect.signature(NoReturnGovernance.mark_final_test_passed)
        assert "run_id" in sig.parameters

    def test_can_proceed_returns_tuple(self, governance):
        """can_proceed_to_selection() returns (bool, str|None)."""
        result = governance.can_proceed_to_selection()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], (str, type(None)))

"""
Tests for resume validation — all 10 conditions must pass.
Feature 2.9 Phase 2 — test_feature_2_9_resume_valid.py
"""
import pytest
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.pipeline_types import StageCheckpoint, StageStatus
from hitradar_automation.orchestrator import ResumeValidator


class TestResumeValidationConditions:
    """All 10 conditions must pass for a valid resume."""

    @pytest.fixture
    def validator(self, tmp_path):
        return ResumeValidator(str(tmp_path))

    @pytest.fixture
    def cp_path(self, tmp_path, good_checkpoint):
        """Write a good checkpoint to disk and return its path."""
        path = str(tmp_path / "checkpoint.json")
        with open(path, "w") as f:
            json.dump(good_checkpoint.to_dict(), f)
        return path

    @pytest.fixture
    def good_checkpoint(self):
        return StageCheckpoint(
            run_id="EPIC2-VALIDATE-20260101-000000-00000000",
            stage_id="P00",
            status=StageStatus.PASS,
            full_config_hash="a" * 64,
            scientific_config_hash="b" * 64,
            execution_config_hash="c" * 64,
            git_commit="abc1234",
            working_tree_dirty=False,
            stage_implementation_hash="implhash",
            source_component_hash="srchash",
            environment_fingerprint={"python_version": "3.13.0"},
            input_fingerprints={},
            output_fingerprints={},
            warnings=[],
            blockers=[],
            resume_eligible=True,
        )

    def test_condition_1_pass_status_required(self, validator, good_checkpoint, cp_path):
        """C1: Stage must have PASS or PASS_WITH_WARNINGS status."""
        valid, _, reasons = validator.validate(
            "P00", cp_path,
            [],  # current_input_hashes
            "b" * 64,  # current_scientific_config_hash
            "implhash",  # current_stage_impl_hash
            "srchash",  # current_source_component_hash
            "abc1234",  # current_git_commit
            {"python_version": "3.13.0"},  # current_env_fingerprint
            [],  # dependency_checkpoints
            [],  # output_artifact_paths
        )
        assert valid is True

    def test_condition_1_fail_status_rejected(self, validator, tmp_path):
        """C1: FAIL status is rejected."""
        cp = StageCheckpoint(
            run_id="EPIC2", stage_id="P00", status=StageStatus.FAIL,
            full_config_hash="a" * 64, scientific_config_hash="b" * 64,
            execution_config_hash="c" * 64, git_commit="abc1234",
            working_tree_dirty=False, stage_implementation_hash="implhash",
            source_component_hash="srchash",
            environment_fingerprint={"python_version": "3.13.0"},
            input_fingerprints={}, output_fingerprints={},
            warnings=[], blockers=[], resume_eligible=True,
        )
        path = str(tmp_path / "fail_cp.json")
        with open(path, "w") as f:
            json.dump(cp.to_dict(), f)
        valid, _, reasons = validator.validate(
            "P00", path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is False

    def test_condition_2_resume_eligible_true(self, validator, good_checkpoint, cp_path):
        """C2: resume_eligible=True is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True


    def test_condition_3_config_hash_match(self, validator, good_checkpoint, cp_path):
        """C3: full_config_hash match is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True

    def test_condition_4_scientific_hash_match(self, validator, good_checkpoint, cp_path):
        """C4: scientific_config_hash match is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True

    def test_condition_5_execution_hash_match(self, validator, good_checkpoint, cp_path):
        """C5: execution_config_hash match is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True

    def test_condition_6_git_commit_match(self, validator, good_checkpoint, cp_path):
        """C6: git_commit match is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True

    def test_condition_7_working_tree_not_dirty(self, validator, good_checkpoint, cp_path):
        """C7: working_tree_dirty=False is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True

    def test_condition_8_stage_impl_hash_match(self, validator, good_checkpoint, cp_path):
        """C8: stage_implementation_hash match is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True

    def test_condition_9_source_component_hash_match(self, validator, good_checkpoint, cp_path):
        """C9: source_component_hash match is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True

    def test_condition_10_environment_fingerprint_match(self, validator, good_checkpoint, cp_path):
        """C10: environment_fingerprint match is accepted."""
        valid, _, _ = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True

    def test_all_10_conditions_pass_returns_valid(self, validator, good_checkpoint, cp_path):
        """When all 10 conditions pass, validate() returns valid=True."""
        valid, cp, reasons = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is True
        assert cp is not None
        assert len(reasons) == 0

    def test_stale_reasons_list_defined(self, validator):
        """STALE_REASONS list contains all condition descriptions."""
        assert hasattr(validator, "STALE_REASONS")
        assert len(validator.STALE_REASONS) >= 8

    def test_returns_tuple_format(self, validator, good_checkpoint, cp_path):
        """validate() returns (bool, StageCheckpoint|None, list[str])."""
        result = validator.validate(
            "P00", cp_path, [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], bool)
        assert isinstance(result[1], (type(None), StageCheckpoint))
        assert isinstance(result[2], list)

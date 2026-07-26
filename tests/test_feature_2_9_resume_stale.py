"""
Tests for stale checkpoint detection and rejection.
Feature 2.9 Phase 2 — test_feature_2_9_resume_stale.py
"""
import pytest
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.pipeline_types import StageCheckpoint, StageStatus
from hitradar_automation.orchestrator import ResumeValidator


class TestStaleCheckpointRejection:
    """Stale checkpoints must be detected and rejected by ResumeValidator."""

    @pytest.fixture
    def validator(self, tmp_path):
        return ResumeValidator(str(tmp_path))

    def _write_cp(self, tmp_path, **overrides):
        defaults = dict(
            run_id="EPIC2-VALIDATE-20260101-000000-00000000",
            stage_id="P50",
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
        defaults.update(overrides)
        cp = StageCheckpoint(**defaults)
        path = str(tmp_path / "cp.json")
        with open(path, "w") as f:
            json.dump(cp.to_dict(), f)
        return path

    def _validate(self, validator, cp_path, **overrides):
        defaults = dict(
            current_input_hashes=[],
            current_scientific_config_hash="b" * 64,
            current_stage_impl_hash="implhash",
            current_source_component_hash="srchash",
            current_git_commit="abc1234",
            current_env_fingerprint={"python_version": "3.13.0"},
            dependency_checkpoints=[],
            output_artifact_paths=[],
        )
        defaults.update(overrides)
        return validator.validate("P50", cp_path, **defaults)

    def test_changed_config_hash_marks_stale(self, validator, tmp_path):
        """Changed full_config_hash makes checkpoint stale."""
        cp_path = self._write_cp(tmp_path)
        valid, _, reasons = self._validate(
            validator, cp_path,
            current_scientific_config_hash="different" + "b" * 57,
        )
        assert valid is False
        assert len(reasons) > 0

    def test_changed_scientific_hash_marks_stale(self, validator, tmp_path):
        """Changed scientific_config_hash makes checkpoint stale."""
        cp_path = self._write_cp(tmp_path)
        valid, _, reasons = self._validate(
            validator, cp_path,
            current_scientific_config_hash="different" + "b" * 57,
        )
        assert valid is False

    def test_changed_git_commit_marks_stale(self, validator, tmp_path):
        """Changed git_commit makes checkpoint stale."""
        cp_path = self._write_cp(tmp_path)
        valid, _, reasons = self._validate(
            validator, cp_path,
            current_git_commit="newcommit",
        )
        assert valid is False

    def test_changed_impl_hash_marks_stale(self, validator, tmp_path):
        """Changed stage_implementation_hash makes checkpoint stale."""
        cp_path = self._write_cp(tmp_path)
        valid, _, reasons = self._validate(
            validator, cp_path,
            current_stage_impl_hash="different_impl_hash",
        )
        assert valid is False

    def test_changed_env_fingerprint_marks_stale(self, validator, tmp_path):
        """Changed environment_fingerprint makes checkpoint stale."""
        cp_path = self._write_cp(tmp_path)
        valid, _, reasons = self._validate(
            validator, cp_path,
            current_env_fingerprint={"python_version": "3.12.0"},
        )
        assert valid is False

    def test_failed_stage_is_stale(self, validator, tmp_path):
        """A FAIL status checkpoint is stale (incomplete)."""
        cp_path = self._write_cp(tmp_path, status=StageStatus.FAIL)
        valid, _, reasons = self._validate(validator, cp_path)
        assert valid is False

    def test_valid_checkpoint_not_stale(self, validator, tmp_path):
        """A valid checkpoint passes all stale checks."""
        cp_path = self._write_cp(tmp_path)
        valid, _, reasons = self._validate(validator, cp_path)
        assert valid is True
        assert len(reasons) == 0

    def test_stale_reasons_are_strings(self, validator, tmp_path):
        """Stale reasons are non-empty strings."""
        cp_path = self._write_cp(tmp_path, status=StageStatus.FAIL)
        _, _, reasons = self._validate(validator, cp_path)
        for reason in reasons:
            assert isinstance(reason, str)
            assert len(reason) > 0

    def test_missing_checkpoint_file_is_invalid(self, validator):
        """A non-existent checkpoint path is invalid."""
        valid, _, reasons = validator.validate(
            "P50", "/nonexistent/checkpoint.json",
            [], "b" * 64, "implhash", "srchash",
            "abc1234", {"python_version": "3.13.0"}, [], [],
        )
        assert valid is False

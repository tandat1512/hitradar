"""
Tests for RunManifest construction and content.
Feature 2.9 Phase 2 — test_feature_2_9_run_manifest.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.pipeline_types import RunManifest
from hitradar_automation.pipeline_types import RunStatus


class TestRunManifest:
    """RunManifest must contain all required fields from Phase 2 spec."""

    def _minimal(self, **kwargs):
        defaults = dict(
            run_id="EPIC2-TEST-00000000",
            mode="validate",
            dry_run=False,
            resume_requested=False,
            repository_root="/tmp",
        )
        defaults.update(kwargs)
        return RunManifest(**defaults)

    def test_has_run_id(self):
        manifest = self._minimal(run_id="EPIC2-VALIDATE-20260101-000000-00000000")
        assert manifest.run_id == "EPIC2-VALIDATE-20260101-000000-00000000"

    def test_has_mode(self):
        manifest = self._minimal(mode="train")
        assert manifest.mode == "train"

    def test_has_repository_root(self):
        manifest = self._minimal(repository_root="/workspace/hitradar")
        assert manifest.repository_root == "/workspace/hitradar"

    def test_has_dry_run(self):
        manifest = self._minimal(dry_run=True)
        assert manifest.dry_run is True

    def test_has_resume_requested(self):
        manifest = self._minimal(resume_requested=True)
        assert manifest.resume_requested is True

    def test_has_started_at(self):
        manifest = self._minimal(started_at="2026-01-01T00:00:00+00:00")
        assert manifest.started_at == "2026-01-01T00:00:00+00:00"

    def test_has_ended_at(self):
        manifest = self._minimal(ended_at="2026-01-01T01:00:00+00:00")
        assert manifest.ended_at == "2026-01-01T01:00:00+00:00"

    def test_has_duration_seconds(self):
        manifest = self._minimal(duration_seconds=3600.5)
        assert manifest.duration_seconds == 3600.5

    def test_has_status(self):
        manifest = self._minimal(status=RunStatus.PASS)
        assert manifest.status == RunStatus.PASS

    def test_has_stage_counts(self):
        manifest = self._minimal(
            stage_total=10, stage_passed=8, stage_warning=1,
            stage_failed=1, stage_skipped=0, stage_stale=0,
        )
        assert manifest.stage_total == 10
        assert manifest.stage_passed == 8
        assert manifest.stage_failed == 1

    def test_has_git_commit(self):
        manifest = self._minimal(git_commit="abc123def456")
        assert manifest.git_commit == "abc123def456"

    def test_has_working_tree_dirty(self):
        manifest = self._minimal(working_tree_dirty=True)
        assert manifest.working_tree_dirty is True

    def test_has_full_config_hash(self):
        manifest = self._minimal(full_config_hash="a" * 64)
        assert len(manifest.full_config_hash) == 64

    def test_has_scientific_config_hash(self):
        manifest = self._minimal(scientific_config_hash="b" * 64)
        assert len(manifest.scientific_config_hash) == 64

    def test_has_warnings_list(self):
        manifest = self._minimal(warnings=["some warning"])
        assert "some warning" in manifest.warnings

    def test_has_blockers_list(self):
        manifest = self._minimal(blockers=["some blocker"])
        assert "some blocker" in manifest.blockers

    def test_has_scientific_flags_defaults_false(self):
        manifest = self._minimal()
        assert manifest.training_executed is False
        assert manifest.tuning_executed is False
        assert manifest.preprocessing_fit_executed is False
        assert manifest.final_test_executed is False
        assert manifest.shap_executed is False
        assert manifest.packaging_executed is False

    def test_to_dict_returns_dict(self):
        manifest = self._minimal()
        d = manifest.to_dict()
        assert isinstance(d, dict)
        assert d["run_id"] == manifest.run_id
        assert d["mode"] == manifest.mode

    def test_from_dict_restores_manifest(self):
        original = self._minimal(
            run_id="EPIC2-TEST",
            mode="train",
            git_commit="abc123",
            full_config_hash="f" * 64,
            scientific_config_hash="s" * 64,
        )
        restored = RunManifest.from_dict(original.to_dict())
        assert restored.run_id == original.run_id
        assert restored.mode == original.mode
        assert restored.git_commit == original.git_commit
        assert restored.full_config_hash == original.full_config_hash

    def test_status_defaults_to_fail(self):
        manifest = self._minimal()
        assert manifest.status == RunStatus.FAIL

    def test_phase2_scientific_flags_consistent(self):
        """Phase 2: all scientific flags must be False in manifest."""
        manifest = self._minimal(
            training_executed=False,
            tuning_executed=False,
            preprocessing_fit_executed=False,
            final_test_executed=False,
            shap_executed=False,
            packaging_executed=False,
        )
        assert manifest.training_executed is False
        assert manifest.tuning_executed is False

"""
Tests for StageContext construction and content.
Feature 2.9 Phase 2 — test_feature_2_9_stage_context.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation import PipelineConfig
from hitradar_automation.pipeline_types import StageContext


class TestStageContextConstruction:
    """StageContext must contain all required information."""

    def test_context_has_run_id(self):
        """StageContext contains run_id."""
        cfg = PipelineConfig(mode="validate")
        ctx = StageContext(
            run_id="EPIC2-VALIDATE-20260101-000000-00000000",
            mode="validate",
            repository_root="/repo",
            output_root="/output",
            run_directory="/run",
            config=cfg,
            permissions={},
        )
        assert ctx.run_id == "EPIC2-VALIDATE-20260101-000000-00000000"

    def test_context_has_mode(self):
        """StageContext contains mode."""
        cfg = PipelineConfig(mode="train")
        ctx = StageContext(
            run_id="test", mode="train",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions={},
        )
        assert ctx.mode == "train"

    def test_context_has_repository_root(self):
        """StageContext contains repository_root."""
        cfg = PipelineConfig()
        ctx = StageContext(
            run_id="test", mode="validate",
            repository_root="/workspace/hitradar",
            output_root="/out", run_directory="/run",
            config=cfg, permissions={},
        )
        assert "/hitradar" in ctx.repository_root

    def test_context_has_output_root(self):
        """StageContext contains output_root."""
        cfg = PipelineConfig()
        ctx = StageContext(
            run_id="test", mode="validate",
            repository_root="/repo",
            output_root="/workspace/hitradar/7.ML/7.12",
            run_directory="/run", config=cfg, permissions={},
        )
        assert "7.12" in ctx.output_root

    def test_context_has_run_directory(self):
        """StageContext contains run_directory."""
        cfg = PipelineConfig()
        ctx = StageContext(
            run_id="EPIC2-validate-123",
            mode="validate",
            repository_root="/repo", output_root="/out",
            run_directory="/output/runs/EPIC2-validate-123",
            config=cfg, permissions={},
        )
        assert "EPIC2-validate-123" in ctx.run_directory

    def test_context_has_config(self):
        """StageContext contains config object."""
        cfg = PipelineConfig(mode="validate", allow_training=True)
        ctx = StageContext(
            run_id="test", mode="validate",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions={},
        )
        assert ctx.config.allow_training is True

    def test_context_has_permissions(self):
        """StageContext contains permissions dict."""
        cfg = PipelineConfig()
        perms = {"allow_training": True, "allow_final_test": False}
        ctx = StageContext(
            run_id="test", mode="train",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions=perms,
        )
        assert ctx.permissions["allow_training"] is True
        assert ctx.permissions["allow_final_test"] is False

    def test_context_has_input_artifact_paths(self):
        """StageContext can carry input artifact paths."""
        cfg = PipelineConfig()
        ctx = StageContext(
            run_id="test", mode="train",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions={},
            input_artifact_paths=["7.6.feature_engineering/features.parquet"],
        )
        assert len(ctx.input_artifact_paths) == 1
        assert "feature_engineering" in ctx.input_artifact_paths[0]

    def test_context_has_dry_run_flag(self):
        """StageContext carries dry_run flag."""
        cfg = PipelineConfig(dry_run=True)
        ctx = StageContext(
            run_id="test", mode="validate",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions={},
            dry_run=True,
        )
        assert ctx.dry_run is True

    def test_context_has_resume_flag(self):
        """StageContext carries resume flag."""
        cfg = PipelineConfig(resume=True)
        ctx = StageContext(
            run_id="test", mode="validate",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions={},
            resume=True,
        )
        assert ctx.resume is True

    def test_context_has_git_info(self):
        """StageContext carries Git commit and dirty flag."""
        cfg = PipelineConfig()
        ctx = StageContext(
            run_id="test", mode="validate",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions={},
            git_commit="abc1234",
            git_dirty=True,
        )
        assert ctx.git_commit == "abc1234"
        assert ctx.git_dirty is True

    def test_context_has_environment_snapshot(self):
        """StageContext carries environment snapshot."""
        cfg = PipelineConfig()
        env = {"python_version": "3.13.0", "platform": "win32"}
        ctx = StageContext(
            run_id="test", mode="validate",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions={},
            environment_snapshot=env,
        )
        assert ctx.environment_snapshot["python_version"] == "3.13.0"

    def test_context_to_dict_serialization(self):
        """StageContext serializes to dict without error."""
        cfg = PipelineConfig()
        ctx = StageContext(
            run_id="test", mode="validate",
            repository_root="/repo", output_root="/out",
            run_directory="/run", config=cfg, permissions={},
        )
        d = ctx.to_dict()
        assert "run_id" in d
        assert "mode" in d
        assert "config" in d

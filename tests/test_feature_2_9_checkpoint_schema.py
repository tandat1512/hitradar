"""
Tests for checkpoint schema and structure.
Feature 2.9 Phase 2 — test_feature_2_9_checkpoint_schema.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.pipeline_types import StageCheckpoint, StageStatus


class TestCheckpointSchema:
    """StageCheckpoint must have all required schema fields."""

    def test_checkpoint_has_run_id(self):
        """Checkpoint contains run_id."""
        cp = StageCheckpoint(
            run_id="EPIC2-VALIDATE-20260101-000000-00000000",
            stage_id="P00",
            status=StageStatus.PASS,
        )
        assert cp.run_id == "EPIC2-VALIDATE-20260101-000000-00000000"

    def test_checkpoint_has_stage_id(self):
        """Checkpoint contains stage_id."""
        cp = StageCheckpoint(
            run_id="test",
            stage_id="P50_TRAIN_CANDIDATES",
            status=StageStatus.PASS,
        )
        assert cp.stage_id == "P50_TRAIN_CANDIDATES"

    def test_checkpoint_has_status(self):
        """Checkpoint contains status."""
        cp = StageCheckpoint(
            run_id="test",
            stage_id="P00",
            status=StageStatus.PASS_WITH_WARNINGS,
        )
        assert cp.status == StageStatus.PASS_WITH_WARNINGS

    def test_checkpoint_has_started_at(self):
        """Checkpoint contains started_at."""
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        cp = StageCheckpoint(
            run_id="test", stage_id="P00", status=StageStatus.PASS,
            started_at=ts,
        )
        assert cp.started_at == ts

    def test_checkpoint_has_ended_at(self):
        """Checkpoint contains ended_at."""
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        cp = StageCheckpoint(
            run_id="test", stage_id="P00", status=StageStatus.PASS,
            ended_at=ts,
        )
        assert cp.ended_at == ts

    def test_checkpoint_has_input_fingerprints(self):
        """Checkpoint contains input_fingerprints."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P50",
            status=StageStatus.PASS,
            input_fingerprints={"features.parquet": {"sha256": "abc123"}},
        )
        assert "features.parquet" in cp.input_fingerprints

    def test_checkpoint_has_output_fingerprints(self):
        """Checkpoint contains output_fingerprints."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P50",
            status=StageStatus.PASS,
            output_fingerprints={"model.joblib": {"sha256": "def456"}},
        )
        assert "model.joblib" in cp.output_fingerprints

    def test_checkpoint_has_full_config_hash(self):
        """Checkpoint contains full_config_hash."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS,
            full_config_hash="a" * 64,
        )
        assert len(cp.full_config_hash) == 64

    def test_checkpoint_has_scientific_config_hash(self):
        """Checkpoint contains scientific_config_hash."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS,
            scientific_config_hash="b" * 64,
        )
        assert len(cp.scientific_config_hash) == 64

    def test_checkpoint_has_execution_config_hash(self):
        """Checkpoint contains execution_config_hash."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS,
            execution_config_hash="c" * 64,
        )
        assert len(cp.execution_config_hash) == 64

    def test_checkpoint_has_git_commit(self):
        """Checkpoint contains git_commit."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS,
            git_commit="a1b2c3d4e5f6",
        )
        assert cp.git_commit == "a1b2c3d4e5f6"

    def test_checkpoint_has_working_tree_dirty(self):
        """Checkpoint contains working_tree_dirty flag."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS,
            working_tree_dirty=True,
        )
        assert cp.working_tree_dirty is True

    def test_checkpoint_has_stage_implementation_hash(self):
        """Checkpoint contains stage_implementation_hash."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS,
            stage_implementation_hash="stagehash123",
        )
        assert cp.stage_implementation_hash is not None

    def test_checkpoint_has_environment_fingerprint(self):
        """Checkpoint contains environment_fingerprint."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS,
            environment_fingerprint={"python_version": "3.13.0"},
        )
        assert cp.environment_fingerprint["python_version"] == "3.13.0"

    def test_checkpoint_has_warnings(self):
        """Checkpoint contains warnings list."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS_WITH_WARNINGS,
            warnings=["config deprecation"],
        )
        assert len(cp.warnings) == 1

    def test_checkpoint_has_blockers(self):
        """Checkpoint contains blockers list."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.FAIL,
            blockers=["SCHEMA_MISMATCH"],
        )
        assert len(cp.blockers) == 1

    def test_checkpoint_has_resume_eligible(self):
        """Checkpoint contains resume_eligible flag."""
        cp = StageCheckpoint(
            run_id="test", stage_id="P00",
            status=StageStatus.PASS,
            resume_eligible=True,
        )
        assert cp.resume_eligible is True

    def test_checkpoint_to_dict_serialization(self):
        """Checkpoint serializes to dict with all required keys."""
        cp = StageCheckpoint(
            run_id="EPIC2-VALIDATE-20260101-000000-00000000",
            stage_id="P00",
            status=StageStatus.PASS,
            full_config_hash="a" * 64,
            scientific_config_hash="b" * 64,
            execution_config_hash="c" * 64,
            git_commit="abc123",
            working_tree_dirty=False,
            stage_implementation_hash="impl123",
            source_component_hash="src123",
        )
        d = cp.to_dict()
        required = [
            "run_id", "stage_id", "status", "started_at", "ended_at",
            "input_fingerprints", "output_fingerprints",
            "full_config_hash", "scientific_config_hash", "execution_config_hash",
            "git_commit", "working_tree_dirty",
            "stage_implementation_hash", "source_component_hash",
            "environment_fingerprint", "warnings", "blockers", "resume_eligible",
        ]
        for field in required:
            assert field in d, f"Missing field: {field}"

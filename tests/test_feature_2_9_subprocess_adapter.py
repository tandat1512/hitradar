"""
Tests for subprocess stage adapter.
Feature 2.9 Phase 2 — test_feature_2_9_subprocess_adapter.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation import PipelineConfig
from hitradar_automation.pipeline_types import StageContext, StageStatus
from hitradar_automation.stage_adapters import SubprocessAdapter


class TestSubprocessAdapter:
    """Tests for SubprocessAdapter."""

    def _make_ctx(self, dry_run=False, repo_root=None):
        cfg = PipelineConfig(mode="validate")
        return StageContext(
            run_id="EPIC2-TEST-00000000-000000-00000000",
            mode="validate",
            repository_root=repo_root or os.getcwd(),
            output_root=os.getcwd(),
            run_directory=os.getcwd(),
            config=cfg,
            permissions={},
            dry_run=dry_run,
        )

    def test_dry_run_returns_pass(self, tmp_path):
        """In dry_run mode, subprocess adapter returns PASS without running."""
        stage_def = {
            "stage_id": "P10_VALIDATE_DATASET",
            "script_path": "/nonexistent/script.py",
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        ctx = self._make_ctx(dry_run=True)
        result = adapter.execute(ctx, stdout_dir=str(tmp_path), stderr_dir=str(tmp_path))
        assert result.status == StageStatus.PASS
        assert result.duration_seconds == 0.0

    def test_missing_script_returns_fail(self, tmp_path):
        """Missing script results in FAIL."""
        stage_def = {
            "stage_id": "P10_VALIDATE_DATASET",
            "script_path": "/nonexistent/script.py",
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        ctx = self._make_ctx()
        result = adapter.execute(ctx, stdout_dir=str(tmp_path), stderr_dir=str(tmp_path))
        assert result.status == StageStatus.FAIL
        assert result.exit_code != 0  # non-zero for missing script
        assert any("SUBPROCESS_ERROR" in b for b in result.blockers)

    def test_successful_command_returns_pass(self, tmp_path):
        """A command that succeeds returns PASS."""
        stage_def = {
            "stage_id": "P10_VALIDATE_DATASET",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        ctx = self._make_ctx(repo_root=os.getcwd())
        # Override build_command to use python -c
        adapter._build_command = lambda ctx: [sys.executable, "-c", "print('ok')"]
        result = adapter.execute(ctx, stdout_dir=str(tmp_path), stderr_dir=str(tmp_path))
        assert result.status == StageStatus.PASS
        assert result.exit_code == 0

    def test_failing_command_returns_fail(self, tmp_path):
        """A command that fails returns FAIL."""
        stage_def = {
            "stage_id": "P10_VALIDATE_DATASET",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        ctx = self._make_ctx()
        adapter._build_command = lambda ctx: [sys.executable, "-c", "import sys; sys.exit(1)"]
        result = adapter.execute(ctx, stdout_dir=str(tmp_path), stderr_dir=str(tmp_path))
        assert result.status == StageStatus.FAIL
        assert result.exit_code == 1

    def test_stdout_captured(self, tmp_path):
        """Stdout is captured to a file."""
        stage_def = {
            "stage_id": "P10",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        ctx = self._make_ctx()
        adapter._build_command = lambda ctx: [sys.executable, "-c", "print('hello from stdout')"]
        stdout_dir = str(tmp_path / "stdout")
        os.makedirs(stdout_dir, exist_ok=True)
        result = adapter.execute(ctx, stdout_dir=stdout_dir, stderr_dir=str(tmp_path / "stderr"))
        assert result.stdout_path is not None
        assert os.path.exists(result.stdout_path)
        with open(result.stdout_path) as f:
            assert "hello from stdout" in f.read()

    def test_stderr_captured_on_failure(self, tmp_path):
        """Stderr is captured to a file on failure."""
        stage_def = {
            "stage_id": "P10",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        ctx = self._make_ctx()
        adapter._build_command = lambda ctx: [sys.executable, "-c", "import sys; sys.stderr.write('error\\n'); sys.exit(1)"]
        stderr_dir = str(tmp_path / "stderr")
        os.makedirs(stderr_dir, exist_ok=True)
        result = adapter.execute(ctx, stdout_dir=str(tmp_path / "stdout"), stderr_dir=stderr_dir)
        assert result.stderr_path is not None
        assert os.path.exists(result.stderr_path)

    def test_command_field_populated(self, tmp_path):
        """Command field is populated in result."""
        stage_def = {
            "stage_id": "P10",
            "script_path": "/fake/script.py",
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        ctx = self._make_ctx()
        adapter._build_command = lambda c: [sys.executable, "-c", "pass"]
        result = adapter.execute(ctx, stdout_dir=str(tmp_path), stderr_dir=str(tmp_path))
        assert result.command is not None
        assert sys.executable in result.command

    def test_no_shell_true_by_default(self, tmp_path):
        """shell=True is not used by default (uses list form)."""
        stage_def = {
            "stage_id": "P10",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        assert adapter.cli_template is None

    def test_subprocess_uses_list_not_string(self, tmp_path):
        """Subprocess is invoked with list args, not shell string."""
        stage_def = {
            "stage_id": "P10",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 60,
        }
        adapter = SubprocessAdapter(stage_def)
        cmd = adapter._build_command(self._make_ctx())
        # Must be a list, not a string
        assert isinstance(cmd, list)
        assert all(isinstance(c, str) for c in cmd)

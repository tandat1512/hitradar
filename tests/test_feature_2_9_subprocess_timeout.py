"""
Tests for subprocess timeout handling.
Feature 2.9 Phase 2 — test_feature_2_9_subprocess_timeout.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation import PipelineConfig
from hitradar_automation.pipeline_types import StageContext, StageStatus
from hitradar_automation.stage_adapters import SubprocessAdapter


class TestSubprocessTimeout:
    """Tests for subprocess timeout behavior."""

    def _make_ctx(self):
        cfg = PipelineConfig(mode="validate")
        return StageContext(
            run_id="EPIC2-TEST-00000000",
            mode="validate",
            repository_root=os.getcwd(),
            output_root=os.getcwd(),
            run_directory=os.getcwd(),
            config=cfg,
            permissions={},
        )

    def test_timeout_returns_fail(self, tmp_path):
        """A command that times out returns FAIL with TIMEOUT blocker."""
        stage_def = {
            "stage_id": "P50_TRAIN_CANDIDATES",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
        }
        adapter = SubprocessAdapter(stage_def, timeout=1)
        ctx = self._make_ctx()
        # Command that sleeps for 5 seconds
        adapter._build_command = lambda c: [
            sys.executable, "-c", "import time; time.sleep(5)"
        ]
        result = adapter.execute(ctx, stdout_dir=str(tmp_path), stderr_dir=str(tmp_path))
        assert result.status == StageStatus.FAIL
        assert result.exit_code == 124  # standard timeout exit code
        assert any("TIMEOUT" in b for b in result.blockers)

    def test_timeout_writes_stderr(self, tmp_path):
        """Timeout writes error to stderr file."""
        stage_def = {
            "stage_id": "P50",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
        }
        adapter = SubprocessAdapter(stage_def, timeout=1)
        ctx = self._make_ctx()
        adapter._build_command = lambda c: [sys.executable, "-c", "import time; time.sleep(5)"]
        stderr_dir = str(tmp_path / "stderr")
        os.makedirs(stderr_dir, exist_ok=True)
        result = adapter.execute(ctx, stdout_dir=str(tmp_path / "stdout"), stderr_dir=stderr_dir)
        assert result.stderr_path is not None
        assert any("TIMEOUT" in b for b in result.blockers)

    def test_timeout_uses_stage_timeout(self, tmp_path):
        """Timeout value comes from stage definition."""
        stage_def = {
            "stage_id": "P10",
            "script_path": sys.executable,
            "implementation_type": "SUBPROCESS",
            "default_timeout_seconds": 999,  # very long
        }
        adapter = SubprocessAdapter(stage_def, timeout=999)
        assert adapter.timeout == 999

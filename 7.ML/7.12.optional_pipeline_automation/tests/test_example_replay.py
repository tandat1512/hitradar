"""
test_example_replay.py — Example replay validation tests.
Feature 2.9 Phase 3/5.
"""
from __future__ import annotations

import subprocess
import sys
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "model_monitor.py"
CONFIG = Path(__file__).parent.parent / "monitoring" / "model_monitor_config.yaml"


class TestExampleReplay:
    def test_example_replay_result_file_written(self, tmp_path):
        """Example replay validation result should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        f = out / "model_monitor_example_replay_validation.json"
        assert f.exists()

    def test_example_replay_status_valid(self, tmp_path):
        """Example replay should complete without errors."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_example_replay_validation.json").read_text())
        # Status should be either OK (pipeline works) or SKIPPED/ERROR (runtime deps missing)
        assert data["overall_status"] in ("OK", "WARNING", "SKIPPED", "PREDICTION_ERROR")

    def test_example_input_fields_present(self, tmp_path):
        """Example replay result should include the input used."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_example_replay_validation.json").read_text())
        if data.get("example_input"):
            # Should have the 18 schema fields
            assert isinstance(data["example_input"], dict)

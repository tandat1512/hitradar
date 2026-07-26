"""
test_sample_size.py — Sample size policy tests.
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


class TestSampleSize:
    def test_sample_size_result_written(self, tmp_path, batch_csv_200):
        """Sample size validation result should always be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True
        )
        f = out / "model_monitor_sample_size_validation.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert "batch_rows" in data
        assert "minimum_batch_rows" in data

    def test_small_batch_not_enough_data(self, tmp_path, batch_csv_20):
        """Batch < 30 rows should fail minimum_batch_rows."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_20),
             "--batch-id", "SMALL",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_sample_size_validation.json").read_text())
        assert data["batch_rows"] == 20
        assert data["rows_above_minimum"] is False

    def test_adequate_batch_passes(self, tmp_path, batch_csv_200):
        """Batch >= 30 rows should pass minimum_batch_rows."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_sample_size_validation.json").read_text())
        assert data["batch_rows"] == 200
        assert data["rows_above_minimum"] is True
        assert data["rows_above_drift_minimum"] is True

    def test_no_batch_sample_size(self, tmp_path):
        """Without batch, sample size should show 0 rows."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_sample_size_validation.json").read_text())
        assert data["batch_rows"] == 0

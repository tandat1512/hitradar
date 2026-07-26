"""
test_prediction_drift.py — Prediction drift monitoring tests.
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


class TestPredictionDrift:
    def test_prediction_drift_result_file_written(self, tmp_path):
        """prediction_drift_results.json should be written even when pipeline unavailable."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        # Run completes even without runtime deps
        assert r.returncode in (0, 2)
        f = out / "model_monitor_prediction_drift_results.json"
        assert f.exists()

    def test_prediction_generation_manifest_written(self, tmp_path, batch_csv_200):
        """Prediction generation manifest should be written with batch input."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        f = out / "model_monitor_prediction_generation_manifest.json"
        assert f.exists()
        data = json.loads(f.read_text())
        # Should indicate runtime dep is missing
        assert "error" in data or "predictions_generated" in data

    def test_no_predictions_when_batch_absent(self, tmp_path):
        """Without batch, prediction drift should NOT_RUN."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 0
        assert "Pred Drift     : NOT_RUN" in r.stdout

    def test_prediction_drift_status_when_not_run(self, tmp_path):
        """Prediction drift status should be NOT_RUN when pipeline unavailable."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_prediction_drift_results.json").read_text())
        # Status reflects that predictions couldn't be generated
        assert data.get("overall_status") in ("NOT_RUN", "NOT_ENOUGH_DATA", "NO_PREDICTIONS")

    def test_prediction_drift_result_in_run_manifest(self, tmp_path, batch_csv_200):
        """Run manifest should reflect prediction drift check execution."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        manifest = json.loads((out / "model_monitor_run_manifest.json").read_text())
        # execution flag depends on whether pipeline was available
        assert "prediction_drift_check_executed" in manifest

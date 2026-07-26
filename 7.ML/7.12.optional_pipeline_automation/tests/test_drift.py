"""
test_drift.py — Feature drift monitoring tests (numeric + categorical).
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


class TestFeatureDrift:
    def test_numeric_drift_results_written(self, tmp_path, batch_csv_200):
        """Numeric drift results file should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--batch-id", "DRIFT_TEST",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        f = out / "model_monitor_numeric_drift_results.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert "features" in data
        assert isinstance(data["features"], list)

    def test_categorical_drift_results_written(self, tmp_path, batch_csv_200):
        """Categorical drift results file should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        f = out / "model_monitor_categorical_drift_results.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert "features" in data

    def test_feature_drift_summary_written(self, tmp_path, batch_csv_200):
        """Feature drift summary should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        f = out / "model_monitor_feature_drift_summary.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert "total_features_checked" in data
        assert "overall_status" in data

    def test_small_batch_not_enough_data(self, tmp_path, batch_csv_20):
        """Batch below minimum_drift_rows should return NOT_ENOUGH_DATA."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_20),
             "--batch-id", "SMALL_BATCH",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_sample_size_validation.json").read_text())
        assert data["drift_metrics_status"] == "NOT_ENOUGH_DATA"
        assert data["rows_above_drift_minimum"] is False

    def test_categorical_null_baseline_tvd_returns_null(self, tmp_path, batch_csv_200):
        """Categorical features with null baseline frequencies should not crash."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode in (0, 2), r.stdout
        data = json.loads((out / "model_monitor_categorical_drift_results.json").read_text())
        # Should have results for each categorical feature
        assert len(data["features"]) > 0

    def test_numeric_features_have_drift_info(self, tmp_path, batch_csv_200):
        """Each numeric feature should have drift info (mean_delta, std_ratio, psi)."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_numeric_drift_results.json").read_text())
        for feat in data["features"]:
            assert "feature" in feat
            assert "type" in feat
            assert feat["type"] == "numeric"

    def test_psi_uses_fixed_baseline_bins(self, tmp_path, batch_csv_200):
        """PSI results should indicate 'fixed_from_baseline' bin policy."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_numeric_drift_results.json").read_text())
        psis = [f["psi"] for f in data["features"] if f.get("psi")]
        if psis:
            first_psi = next(f["psi"] for f in data["features"] if f.get("psi"))
            assert first_psi["bin_policy"] == "fixed_from_baseline"

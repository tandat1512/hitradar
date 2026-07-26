"""
test_output_structure.py — Output file structure and run manifest tests.
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

EXPECTED_OUTPUT_FILES = [
    "model_monitor_results.json",
    "model_monitor_run_manifest.json",
    "model_monitor_alerts.json",
    "model_monitor_open_items.json",
    "model_monitor_sample_size_validation.json",
    "model_monitor_label_availability_validation.json",
    "model_monitor_version_consistency.json",
    "model_monitor_baseline_immutability_validation.json",
    "model_monitor_artifact_integrity_results.json",
    "model_monitor_example_replay_validation.json",
    "model_monitor_schema_results.json",
    "model_monitor_data_quality_results.json",
    "model_monitor_numeric_drift_results.json",
    "model_monitor_categorical_drift_results.json",
    "model_monitor_feature_drift_summary.json",
    "model_monitor_prediction_drift_results.json",
    "model_monitor_prediction_generation_manifest.json",
]


class TestOutputStructure:
    def test_all_result_files_written(self, tmp_path, batch_csv_200):
        """All expected output files should be written after a full monitoring run."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True
        )
        for fname in EXPECTED_OUTPUT_FILES:
            f = out / fname
            assert f.exists(), f"Missing: {fname}"

    def test_run_manifest_required_fields(self, tmp_path):
        """Run manifest should contain all required fields."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_run_manifest.json").read_text())
        for field in ["monitor_run_id", "model_id", "model_version", "package_version",
                       "baseline_id", "input_rows", "status",
                       "training_executed", "refit_executed",
                       "auto_retrain_executed", "auto_update_baseline_executed",
                       "started_at", "ended_at"]:
            assert field in data, f"Missing field: {field}"

    def test_results_has_required_fields(self, tmp_path):
        """Main results JSON should contain required fields."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_results.json").read_text())
        for field in ["monitor_run_id", "model_id", "model_version",
                       "overall_status", "governance"]:
            assert field in data, f"Missing field: {field}"

    def test_results_includes_all_check_flags(self, tmp_path):
        """Results should include all *_check_executed flags."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_results.json").read_text())
        for flag in ["schema_check_executed", "data_quality_check_executed",
                      "feature_drift_check_executed", "prediction_drift_check_executed",
                      "artifact_integrity_check_executed"]:
            assert flag in data, f"Missing flag: {flag}"

    def test_console_output_shows_all_sections(self, tmp_path):
        """Console output should display all required sections."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        for keyword in ["Monitor Run ID", "Model", "Package", "Baseline",
                        "Hash pre", "Hash post", "Schema",
                        "Artifact Int.", "Overall Status"]:
            assert keyword in r.stdout, f"Missing in console output: {keyword}"

    def test_json_summary_flag_prints_json(self, tmp_path):
        """--json-summary should print JSON to stdout."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out),
             "--json-summary"],
            capture_output=True, text=True
        )
        assert r.returncode == 0
        output = json.loads(r.stdout)
        assert "monitor_run_id" in output

    def test_run_id_unique_per_run(self, tmp_path):
        """Each run should produce a unique run ID."""
        out1 = tmp_path / "out1"; out1.mkdir()
        out2 = tmp_path / "out2"; out2.mkdir()
        r1 = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out1)],
            capture_output=True, text=True
        )
        r2 = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out2)],
            capture_output=True, text=True
        )
        id1 = json.loads((out1 / "model_monitor_results.json").read_text())["monitor_run_id"]
        id2 = json.loads((out2 / "model_monitor_results.json").read_text())["monitor_run_id"]
        assert id1 != id2

    def test_mixed_scenario_pass_with_warnings(self, tmp_path, batch_csv_200):
        """Run with batch should produce PASS_WITH_WARNINGS due to feature drift."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--batch-id", "DRIFT_TEST",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 2
        assert "PASS_WITH_WARNINGS" in r.stdout
        assert "Feature Drift  : WARNING" in r.stdout

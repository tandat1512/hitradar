"""
test_exit_codes.py — Verify correct exit codes for all scenarios.
Feature 2.9 Phase 3/5.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "model_monitor.py"
CONFIG = Path(__file__).parent.parent / "monitoring" / "model_monitor_config.yaml"
BATCH_MISSING = Path(__file__).parent.parent / "monitoring" / "synthetic_batch_missing_field.csv"


class TestExitCodes:
    def test_pass_no_batch(self, tmp_path):
        """Artifact-integrity-only run with no batch should exit 0 (PASS)."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--output-dir", str(out),
             "--artifact-integrity"],
            capture_output=True, text=True
        )
        assert r.returncode == 0, f"Expected exit 0, got {r.returncode}\n{r.stderr}"

    def test_input_error_missing_config(self, tmp_path):
        """Non-existent config should exit 10 (INPUT_ERROR)."""
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(tmp_path / "does_not_exist.yaml")],
            capture_output=True, text=True
        )
        assert r.returncode == 10, f"Expected exit 10, got {r.returncode}"

    def test_schema_blocker_missing_required_field(self, tmp_path, batch_csv_missing_field):
        """Batch missing required field should exit 14 (SCHEMA_BLOCKER)."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_missing_field),
             "--batch-id", "TEST_MISSING",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 14, f"Expected exit 14, got {r.returncode}\n{r.stdout}"

    def test_governance_violation_config_flag(self, tmp_path):
        """Config with auto_retrain=true should exit 30 (GOVERNANCE_VIOLATION)."""
        bad_cfg = tmp_path / "bad_config.yaml"
        bad_cfg.write_text("""
governance:
  auto_retrain: true
  auto_update_baseline: false
  fail_on_artifact_hash_mismatch: true
  require_explicit_labels_flag: true
monitoring:
  schema: false
  data_quality: false
  feature_drift: false
  prediction_drift: false
  performance: false
  artifact_integrity: false
sample_requirements:
  minimum_batch_rows: 30
  minimum_drift_rows: 100
paths:
  output_dir: null
monitoring_identifiers:
  model_id: EXP24-XGB-FINAL-001
  model_version: "1.0.0"
  package_version: "2.7.0"
  data_version: "1.0.0"
  schema_id: HITRADAR-PREDICTION-INPUT-V1
  schema_version: "1.0.0"
""", encoding="utf-8")
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(bad_cfg),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 30, f"Expected exit 30, got {r.returncode}"

    def test_warnings_exit_code(self, tmp_path, batch_csv_200):
        """Run with batch that triggers warnings should exit 2 (PASS_WITH_WARNINGS)."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--batch-id", "TEST_200",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 2, f"Expected exit 2, got {r.returncode}\n{r.stdout}"
        assert "PASS_WITH_WARNINGS" in r.stdout

    def test_no_training_indicator(self, tmp_path):
        """Monitor run should never set training_executed=True."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert "Training done  : False" in r.stdout
        assert r.returncode in (0, 2)

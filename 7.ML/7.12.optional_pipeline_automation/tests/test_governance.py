"""
test_governance.py — Governance enforcement tests.
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


class TestGovernance:
    def test_auto_retrain_false_required(self, tmp_path):
        """Config with auto_retrain=true should cause exit 30."""
        cfg = tmp_path / "governance_violation.yaml"
        cfg.write_text("""
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
paths: {}
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
            [sys.executable, str(SCRIPT), "--config", str(cfg), "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 30, f"Expected 30, got {r.returncode}\n{r.stdout}"

    def test_auto_update_baseline_false_required(self, tmp_path):
        """Config with auto_update_baseline=true should cause exit 30."""
        cfg = tmp_path / "governance_violation2.yaml"
        cfg.write_text("""
governance:
  auto_retrain: false
  auto_update_baseline: true
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
paths: {}
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
            [sys.executable, str(SCRIPT), "--config", str(cfg), "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 30, f"Expected 30, got {r.returncode}"

    def test_training_executed_always_false(self, tmp_path):
        """Monitor run should always report training_executed=False."""
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

    def test_refit_executed_always_false(self, tmp_path):
        """Monitor run should always report refit_executed=False."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert "Refit done     : False" in r.stdout

    def test_auto_retrain_executed_always_false(self, tmp_path):
        """Monitor run should always report auto_retrain_executed=False."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert "Auto-retrain   : False" in r.stdout

    def test_champion_changed_always_false(self, tmp_path):
        """Monitor run should always report champion_changed=False."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert "Champion chg   : False" in r.stdout

    def test_labels_authorized_false_without_flag(self, tmp_path):
        """Without --with-labels, labels_authorized should be False."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert "Labels Auth.   : False" in r.stdout

    def test_labels_authorized_true_with_flag(self, tmp_path):
        """With --with-labels, labels_authorized should be True."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--with-labels",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert "Labels Auth.   : True" in r.stdout

    def test_governance_section_in_results(self, tmp_path):
        """Results JSON should include a governance section."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        results = json.loads((out / "model_monitor_results.json").read_text())
        assert "governance" in results
        gov = results["governance"]
        assert gov["auto_retrain"] is False
        assert gov["auto_update_baseline"] is False
        assert gov["training_executed"] is False
        assert gov["refit_executed"] is False
        assert len(gov["governance_violations"]) == 0

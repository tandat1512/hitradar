"""
test_baseline_immutability.py — Baseline immutability validation tests.
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


class TestBaselineImmutability:
    def test_baseline_hash_matches_pre_post(self, tmp_path):
        """Pre- and post-monitoring baseline hashes must match (immutability check)."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        imm = json.loads((out / "model_monitor_baseline_immutability_validation.json").read_text())
        assert imm["hashes_match"] is True
        assert imm["pre_monitoring_hash"] == imm["post_monitoring_hash"]
        assert imm["result"] == "PASS"

    def test_baseline_immutability_result_file_written(self, tmp_path):
        """Baseline immutability result file should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        f = out / "model_monitor_baseline_immutability_validation.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert data["validation_type"] == "BASELINE_IMMUTABILITY_CHECK"
        assert data["baseline_id"] == "BASELINE-001"
        assert data["baseline_version"] == "1.0.0"

    def test_baseline_hash_is_sha256_format(self, tmp_path):
        """Baseline hashes should be valid 64-char SHA256 hex strings."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        imm = json.loads((out / "model_monitor_baseline_immutability_validation.json").read_text())
        h = imm["pre_monitoring_hash"]
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_immutability_file_recorded_in_results(self, tmp_path):
        """Main results should include the post-monitoring baseline hash."""
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
        assert results["baseline_hash_pre"] == results["baseline_hash_post"]
        assert len(results["baseline_hash_pre"]) == 64

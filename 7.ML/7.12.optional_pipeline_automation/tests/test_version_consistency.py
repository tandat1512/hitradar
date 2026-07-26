"""
test_version_consistency.py — Version consistency monitoring tests.
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


class TestVersionConsistency:
    def test_version_consistency_result_file_written(self, tmp_path):
        """Version consistency result should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        f = out / "model_monitor_version_consistency.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert "model_version" in data
        assert "package_version" in data
        assert "schema_id" in data

    def test_model_version_matches_config(self, tmp_path):
        """model_version from artifact should match config monitoring_identifiers."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_version_consistency.json").read_text())
        assert data["model_version"].get("model_version") == "1.0.0"
        assert data["model_version"].get("model_id") == "EXP24-XGB-FINAL-001"

    def test_package_version_matches_config(self, tmp_path):
        """package_version from artifact should match config monitoring_identifiers."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_version_consistency.json").read_text())
        assert data["package_version"].get("package_version") == "2.7.0"

    def test_schema_id_matches_config(self, tmp_path):
        """schema_id from input_schema should match config monitoring_identifiers."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_version_consistency.json").read_text())
        assert data["schema_id"] == "HITRADAR-PREDICTION-INPUT-V1"

    def test_checks_list_populated(self, tmp_path):
        """Version consistency should have a non-empty checks list."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_version_consistency.json").read_text())
        assert len(data["checks"]) >= 3
        assert all("field" in c for c in data["checks"])
        assert all("consistent" in c for c in data["checks"])

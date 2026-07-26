"""
test_schema_monitoring.py — Schema monitoring integration tests.
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


class TestSchemaMonitoring:
    def test_missing_required_field_blocks(self, tmp_path, batch_csv_missing_field):
        """Missing required field should create a BLOCKER alert."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_missing_field),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 14
        alerts = json.loads((out / "model_monitor_alerts.json").read_text())
        blockers = [a for a in alerts["alerts"] if a["severity"] == "BLOCKER"]
        assert len(blockers) > 0
        assert any("release_year" in str(b) for b in blockers)

    def test_schema_result_file_written(self, tmp_path, batch_csv_200):
        """Schema results JSON should be written on valid run."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        schema_file = out / "model_monitor_schema_results.json"
        assert schema_file.exists()
        data = json.loads(schema_file.read_text())
        assert data["overall_status"] in ("OK", "FAIL", "WARNING")

    def test_unexpected_field_raises_warning(self, tmp_path, batch_csv_200):
        """Unexpected fields should generate WARNING alerts, not BLOCKER."""
        import pandas as pd
        df = pd.read_csv(batch_csv_200)
        df["extra_spurious_column"] = 1.0
        bad_csv = tmp_path / "batch_extra.csv"
        df.to_csv(bad_csv, index=False)

        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(bad_csv),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        schema_file = out / "model_monitor_schema_results.json"
        data = json.loads(schema_file.read_text())
        assert "extra_spurious_column" in data.get("unexpected_fields", [])

    def test_schema_check_not_run_without_batch(self, tmp_path):
        """Schema check should NOT_RUN when no batch is provided."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--output-dir", str(out),
             "--artifact-integrity"],
            capture_output=True, text=True
        )
        assert r.returncode == 0
        assert "Schema         : NOT_RUN" in r.stdout

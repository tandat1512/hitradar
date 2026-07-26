"""
test_alerts.py — Alert engine and severity level tests.
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


class TestAlerts:
    def test_alerts_file_written(self, tmp_path):
        """model_monitor_alerts.json should be written after any run."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        f = out / "model_monitor_alerts.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert "alerts" in data
        assert "generated_at" in data

    def test_alert_has_required_fields(self, tmp_path):
        """Each alert must have all required fields."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_alerts.json").read_text())
        for alert in data["alerts"]:
            assert "alert_id" in alert
            assert "category" in alert
            assert "severity" in alert
            assert "message" in alert
            assert "recommended_action" in alert
            assert alert["auto_action_executed"] is False

    def test_blocker_has_BLOCKER_severity(self, tmp_path, batch_csv_missing_field):
        """Blocker-level alerts must have severity BLOCKER."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_missing_field),
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_alerts.json").read_text())
        blockers = [a for a in data["alerts"] if a["severity"] == "BLOCKER"]
        assert len(blockers) > 0

    def test_open_items_file_written(self, tmp_path):
        """model_monitor_open_items.json should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        f = out / "model_monitor_open_items.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert "open_items" in data
        assert "open_item_count" in data

    def test_open_items_deferred_for_phase3(self, tmp_path):
        """Open items should include a deferred entry for Phase 3 labels unavailability."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_open_items.json").read_text())
        phase3_deferred = [
            item for item in data["open_items"]
            if "Phase 3" in item.get("description", "") or "PERFORMANCE" in item.get("category", "")
        ]
        assert len(phase3_deferred) > 0
        assert phase3_deferred[0]["status"] == "DEFERRED"

    def test_no_auto_action_executed(self, tmp_path):
        """No alert should have auto_action_executed=True."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_alerts.json").read_text())
        for alert in data["alerts"]:
            assert alert["auto_action_executed"] is False

    def test_alert_id_unique(self, tmp_path):
        """All alert IDs should be unique."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_alerts.json").read_text())
        ids = [a["alert_id"] for a in data["alerts"]]
        assert len(ids) == len(set(ids))

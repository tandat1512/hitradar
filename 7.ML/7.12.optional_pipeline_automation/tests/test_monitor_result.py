"""
test_monitor_result.py — MonitorResult dataclass and build_alerts unit tests.
Feature 2.9 Phase 3/5.
"""
from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import asdict

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from model_monitor import (
    MonitorResult,
    MonitorAlert,
    build_alerts,
    build_open_items,
    verify_governance,
    sha256_file,
    sha256_str,
    make_uuid,
    utcnow,
)


class TestMonitorResult:
    def test_result_init(self):
        r = MonitorResult(
            monitor_run_id="TEST-001",
            batch_id="BATCH-001",
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
        )
        assert r.monitor_run_id == "TEST-001"
        assert r.training_executed is False
        assert r.refit_executed is False
        assert r.auto_retrain_executed is False
        assert r.auto_update_baseline_executed is False
        assert r.champion_changed is False
        assert r.labels_authorized is False

    def test_result_to_dict(self):
        r = MonitorResult(
            monitor_run_id="TEST-002",
            batch_id=None,
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
            baseline_hash_pre="a" * 64,
            baseline_hash_post="a" * 64,
            output_dir=Path("/tmp"),
        )
        d = r.to_dict()
        assert isinstance(d, dict)
        assert d["monitor_run_id"] == "TEST-002"
        assert d["training_executed"] is False

    def test_blockers_and_warnings_fields(self):
        r = MonitorResult(
            monitor_run_id="TEST-003",
            batch_id=None,
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
            output_dir=Path("/tmp"),
        )
        assert isinstance(r.blockers, list)
        assert isinstance(r.warnings, list)
        assert isinstance(r.alerts, list)
        assert isinstance(r.open_items, list)


class TestBuildAlerts:
    def test_blockers_become_alerts(self):
        r = MonitorResult(
            monitor_run_id="TEST-004",
            batch_id=None,
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
            output_dir=Path("/tmp"),
        )
        r.blockers.append({
            "category": "SCHEMA",
            "field": "release_year",
            "check": "missing_required_field",
            "severity": "BLOCKER",
            "message": "Required field release_year is missing",
        })
        alerts = build_alerts(r)
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "BLOCKER"
        assert alerts[0]["category"] == "SCHEMA"
        assert alerts[0]["auto_action_executed"] is False

    def test_warnings_become_alerts(self):
        r = MonitorResult(
            monitor_run_id="TEST-005",
            batch_id=None,
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
            output_dir=Path("/tmp"),
        )
        r.warnings.append({
            "category": "FEATURE_DRIFT",
            "field": "danceability",
            "check": "mean_delta",
            "severity": "WARNING",
            "message": "Mean shifted by 0.12",
        })
        alerts = build_alerts(r)
        assert len(alerts) == 1
        assert alerts[0]["severity"] == "WARNING"

    def test_alert_id_format(self):
        r = MonitorResult(
            monitor_run_id="TEST-006",
            batch_id=None,
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
            output_dir=Path("/tmp"),
        )
        r.blockers.append({"category": "TEST", "message": "test"})
        alerts = build_alerts(r)
        assert alerts[0]["alert_id"].startswith("ALERT-")
        assert len(alerts[0]["alert_id"]) == 14  # "ALERT-" + 8 hex chars


class TestBuildOpenItems:
    def test_blocker_becomes_open_item(self):
        r = MonitorResult(
            monitor_run_id="TEST-007",
            batch_id=None,
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
            output_dir=Path("/tmp"),
        )
        r.blockers.append({
            "category": "SCHEMA",
            "message": "Missing field",
            "severity": "BLOCKER",
        })
        items = build_open_items(r)
        # Should have the blocker item + the Phase 3 deferred item
        assert len(items) >= 1
        blocking = [i for i in items if i["blocking"]]
        assert len(blocking) > 0

    def test_phase3_deferred_item_present(self):
        r = MonitorResult(
            monitor_run_id="TEST-008",
            batch_id=None,
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
            output_dir=Path("/tmp"),
        )
        items = build_open_items(r)
        deferred = [i for i in items if i["status"] == "DEFERRED"]
        assert len(deferred) > 0
        assert deferred[0]["category"] == "PERFORMANCE"

    def test_open_item_id_format(self):
        r = MonitorResult(
            monitor_run_id="TEST-009",
            batch_id=None,
            model_id="EXP24-XGB-FINAL-001",
            model_version="1.0.0",
            package_version="2.7.0",
            data_version="1.0.0",
            baseline_id="BASELINE-001",
            baseline_version="1.0.0",
            output_dir=Path("/tmp"),
        )
        r.blockers.append({"category": "TEST", "message": "test", "severity": "BLOCKER"})
        items = build_open_items(r)
        for item in items:
            assert item["item_id"].startswith("OI-")
            assert item["retraining_candidate"] is False
            assert item["status"] in ("OPEN", "DEFERRED")


class TestVerifyGovernance:
    def test_no_violations_with_clean_result(self, minimal_result):
        cfg = {
            "governance": {
                "auto_retrain": False,
                "auto_update_baseline": False,
            }
        }
        gov = verify_governance(minimal_result, cfg)
        assert gov["overall_status"] == "PASS"
        assert len(gov["governance_violations"]) == 0
        assert gov["auto_retrain"] is False
        assert gov["auto_update_baseline"] is False

    def test_violation_if_training_executed(self, minimal_result):
        minimal_result.training_executed = True
        cfg = {"governance": {"auto_retrain": False, "auto_update_baseline": False}}
        gov = verify_governance(minimal_result, cfg)
        assert gov["overall_status"] == "FAIL"
        assert len(gov["governance_violations"]) > 0

    def test_violation_if_baseline_mutated(self, minimal_result):
        minimal_result.baseline_hash_pre = "a" * 64
        minimal_result.baseline_hash_post = "b" * 64
        cfg = {"governance": {"auto_retrain": False, "auto_update_baseline": False}}
        gov = verify_governance(minimal_result, cfg)
        assert gov["baseline_mutated"] is True
        assert len(gov["governance_violations"]) > 0


class TestUtilityFunctions:
    def test_sha256_file(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("hello world")
            tmp = f.name
        try:
            h = sha256_file(Path(tmp))
            assert len(h) == 64
            assert h == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        finally:
            os.unlink(tmp)

    def test_sha256_str(self):
        h = sha256_str("hello world")
        assert len(h) == 64
        assert h == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    def test_make_uuid_format(self):
        uid = make_uuid()
        assert len(uid) == 8
        assert all(c in "0123456789abcdef" for c in uid)

    def test_utcnow_format(self):
        ts = utcnow()
        # ISO format: 2026-07-25T...
        assert ts.startswith("2026-")
        assert "T" in ts

"""
test_artifact_integrity.py — Artifact integrity monitoring tests.
Feature 2.9 Phase 3/5.
"""
from __future__ import annotations

import subprocess
import sys
import json
import hashlib
import shutil
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "model_monitor.py"
CONFIG = Path(__file__).parent.parent / "monitoring" / "model_monitor_config.yaml"


class TestArtifactIntegrity:
    def test_artifact_integrity_passes_on_valid_package(self, tmp_path):
        """With a valid package, artifact integrity should PASS."""
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        assert r.returncode == 0, f"Expected 0, got {r.returncode}\n{r.stderr}"
        assert "Artifact Int.  : PASS" in r.stdout

    def test_artifact_integrity_result_file_written(self, tmp_path):
        """artifact_integrity_results.json should exist after run."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        f = out / "model_monitor_artifact_integrity_results.json"
        assert f.exists()
        data = json.loads(f.read_text())
        assert "artifact_checks" in data
        assert "overall_status" in data

    def test_pipeline_hash_checked(self, tmp_path):
        """Pipeline SHA256 should be verified and present in results."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_artifact_integrity_results.json").read_text())
        pipeline_check = next(
            (c for c in data.get("artifact_checks", []) if "full_inference_pipeline_hash" in c.get("artifact", "")),
            None
        )
        assert pipeline_check is not None
        assert "match" in pipeline_check

    def test_pipeline_load_skipped_on_missing_runtime_deps(self, tmp_path):
        """Pipeline load test should SKIP (not block) when runtime deps are unavailable."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_artifact_integrity_results.json").read_text())
        load_check = next(
            (c for c in data.get("artifact_checks", []) if "pipeline_load" in c.get("artifact", "")),
            None
        )
        assert load_check is not None
        assert load_check.get("status") == "SKIPPED"
        assert load_check.get("severity") == "INFO"

    def test_requirements_lock_artifact_checked(self, tmp_path):
        """requirements_lock artifact should be in the checks list."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_artifact_integrity_results.json").read_text())
        lock_check = next(
            (c for c in data.get("artifact_checks", [])
             if c.get("artifact") == "requirements_lock"),
            None
        )
        assert lock_check is not None
        # Status should be PASS (hash matches manifest)
        assert lock_check.get("match") is True

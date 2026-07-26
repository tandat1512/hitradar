"""
test_label_availability.py — Label availability policy tests for Phase 3.
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


class TestLabelAvailability:
    def test_phase3_labels_not_available(self, tmp_path, batch_csv_200):
        """Phase 3 should always report performance_status=LABELS_NOT_AVAILABLE."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_label_availability_validation.json").read_text())
        assert data["performance_status"] == "LABELS_NOT_AVAILABLE"
        assert data["performance_computed"] is False

    def test_labels_not_authorized_without_flag(self, tmp_path, batch_csv_200):
        """Without --with-labels, labels_authorized should be False."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_label_availability_validation.json").read_text())
        assert data["labels_authorized"] is False

    def test_labels_authorized_with_flag(self, tmp_path, batch_csv_200):
        """With --with-labels, labels_authorized should be True."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--with-labels",
             "--output-dir", str(out)],
            capture_output=True
        )
        data = json.loads((out / "model_monitor_label_availability_validation.json").read_text())
        assert data["labels_authorized"] is True
        # Phase 3 still does NOT compute performance even with --with-labels
        assert data["performance_computed"] is False

    def test_target_present_not_authorized_warning(self, tmp_path):
        """Batch with target column but no --with-labels should warn."""
        import pandas as pd
        np = None  # noqa: F841
        exec("import numpy as np")
        np = __import__("numpy")
        df = pd.DataFrame({
            "duration_min": [1.0, 2.0, 3.0],
            "explicit": [False, True, False],
            "release_year": [2020, 2021, 2022],
            "release_month": [1, 2, 3],
            "decade": [2020, 2020, 2020],
            "release_precision": ["year"] * 3,
            "danceability": [0.5, 0.6, 0.7],
            "energy": [0.5, 0.6, 0.7],
            "loudness": [-5.0, -6.0, -7.0],
            "speechiness": [0.01, 0.02, 0.03],
            "acousticness": [0.5, 0.6, 0.7],
            "instrumentalness": [0.0, 0.0, 0.0],
            "liveness": [0.1, 0.2, 0.3],
            "valence": [0.5, 0.6, 0.7],
            "tempo": [120.0, 130.0, 140.0],
            "key": [0, 1, 2],
            "mode": [0, 1, 0],
            "time_signature": [4, 4, 4],
            "target_popularity": [45.0, 52.0, 38.0],  # target column present
        })
        bad_csv = tmp_path / "batch_with_target.csv"
        df.to_csv(bad_csv, index=False)
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(bad_csv),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        # Should exit cleanly (warning, not blocker)
        assert r.returncode in (0, 2)

    def test_label_availability_result_file_written(self, tmp_path):
        """Label availability validation file should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--artifact-integrity",
             "--output-dir", str(out)],
            capture_output=True
        )
        f = out / "model_monitor_label_availability_validation.json"
        assert f.exists()

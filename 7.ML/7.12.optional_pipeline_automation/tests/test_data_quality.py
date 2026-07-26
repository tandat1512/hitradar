"""
test_data_quality.py — Data quality monitoring tests.
Feature 2.9 Phase 3/5.
"""
from __future__ import annotations

import subprocess
import sys
import json
import numpy as np
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "model_monitor.py"
CONFIG = Path(__file__).parent.parent / "monitoring" / "model_monitor_config.yaml"


class TestDataQuality:
    def test_dq_results_file_written(self, tmp_path, batch_csv_200):
        """Data quality results file should be written."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        f = out / "model_monitor_data_quality_results.json"
        assert f.exists()

    def test_empty_batch_is_blocker(self, tmp_path):
        """Empty batch should produce BLOCKER alerts (schema blocks on missing fields)."""
        import pandas as pd
        df = pd.DataFrame({"duration_min": [], "explicit": [], "release_year": []})
        bad_csv = tmp_path / "empty.csv"
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
        # Empty batch → all required fields are absent → schema BLOCKER, exit 14
        assert r.returncode == 14, f"Expected exit 14, got {r.returncode}"
        alerts = json.loads((out / "model_monitor_alerts.json").read_text())
        blockers = [a for a in alerts["alerts"] if a["severity"] == "BLOCKER"]
        assert len(blockers) > 0, "Empty batch should produce BLOCKER alerts"

    def test_inf_values_blocker(self, tmp_path):
        """Inf/-Inf values in numeric columns should be BLOCKER."""
        import pandas as pd
        df = pd.DataFrame({
            "duration_min": [1.0, 2.0, float("inf")],
            "explicit": [False, True, False],
            "release_year": [2020, 2021, 2022],
            "release_month": [1, 2, 3],
            "decade": [2020, 2020, 2020],
            "release_precision": ["year", "year", "year"],
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
        })
        bad_csv = tmp_path / "inf_batch.csv"
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
        assert r.returncode in (2, 14, 15)
        alerts = json.loads((out / "model_monitor_alerts.json").read_text())
        blockers = [a for a in alerts["alerts"] if a["severity"] == "BLOCKER"]
        assert len(blockers) > 0

    def test_dq_rows_count_correct(self, tmp_path, batch_csv_200):
        """Data quality result should report correct row count."""
        out = tmp_path / "out"
        out.mkdir()
        subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(batch_csv_200),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        data = json.loads((out / "model_monitor_data_quality_results.json").read_text())
        assert data["rows_received"] == 200
        assert data["rows_valid"] + data["rows_invalid"] == 200

    def test_duplicate_rows_detected(self, tmp_path):
        """Duplicate rows should generate a WARNING."""
        import pandas as pd
        df = pd.DataFrame({
            "duration_min": [1.0, 2.0, 1.0],
            "explicit": [False, True, False],
            "release_year": [2020, 2021, 2020],
            "release_month": [1, 2, 1],
            "decade": [2020, 2020, 2020],
            "release_precision": ["year", "year", "year"],
            "danceability": [0.5, 0.6, 0.5],
            "energy": [0.5, 0.6, 0.5],
            "loudness": [-5.0, -6.0, -5.0],
            "speechiness": [0.01, 0.02, 0.01],
            "acousticness": [0.5, 0.6, 0.5],
            "instrumentalness": [0.0, 0.0, 0.0],
            "liveness": [0.1, 0.2, 0.1],
            "valence": [0.5, 0.6, 0.5],
            "tempo": [120.0, 130.0, 120.0],
            "key": [0, 1, 0],
            "mode": [0, 1, 0],
            "time_signature": [4, 4, 4],
        })
        dup_csv = tmp_path / "dup.csv"
        df.to_csv(dup_csv, index=False)
        out = tmp_path / "out"
        out.mkdir()
        r = subprocess.run(
            [sys.executable, str(SCRIPT),
             "--config", str(CONFIG),
             "--input", str(dup_csv),
             "--output-dir", str(out)],
            capture_output=True, text=True
        )
        dq = json.loads((out / "model_monitor_data_quality_results.json").read_text())
        assert dq["duplicate_rows_count"] == 1
        assert dq["duplicate_rows_rate"] == pytest.approx(1 / 3, rel=0.1)

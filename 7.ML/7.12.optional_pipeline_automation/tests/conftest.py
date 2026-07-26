"""
conftest.py — pytest fixtures for Feature 2.9 Phase 3 model_monitor tests.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure model_monitor is importable
_MONITOR_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_MONITOR_DIR))

from model_monitor import (
    compute_psi,
    compute_tvd,
    load_json,
    sha256_file,
    sha256_str,
    utcnow,
    make_uuid,
    MonitorResult,
    MonitorAlert,
)

# ── paths ────────────────────────────────────────────────────────────────────

MONITOR_DIR = _MONITOR_DIR / "monitoring"
CONFIG_PATH = MONITOR_DIR / "model_monitor_config.yaml"
BASELINE_PATH = MONITOR_DIR / "model_monitor_baseline.json"
PKG_DIR = _MONITOR_DIR / ".." / "7.10.model_packaging" / "package"


# ── fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def baseline():
    return load_json(BASELINE_PATH)


@pytest.fixture
def config():
    import yaml
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture
def pkg_dir():
    return PKG_DIR


@pytest.fixture
def synthetic_batch_200():
    """200-row DataFrame with realistic feature distributions."""
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "duration_min":     np.random.exponential(3.5, n).clip(0.1, 60),
        "explicit":          np.random.choice([True, False], n, p=[0.1, 0.9]),
        "release_year":      np.random.randint(1920, 2025, n),
        "release_month":     np.random.choice(list(range(1, 13)), n),
        "decade":            (np.random.randint(192, 203, n) * 10),
        "release_precision": np.random.choice(["year", "month", "day"], n, p=[0.5, 0.3, 0.2]),
        "danceability":      np.random.beta(5, 5, n),
        "energy":            np.random.beta(4, 6, n),
        "loudness":          np.random.normal(-10.6, 5, n).clip(-60, 0),
        "speechiness":       np.random.exponential(0.043, n).clip(0, 1),
        "acousticness":      np.random.beta(5, 4, n),
        "instrumentalness":  np.random.exponential(0.0001, n).clip(0, 1),
        "liveness":          np.random.beta(1.5, 8, n).clip(0, 1),
        "valence":           np.random.beta(5, 5, n),
        "tempo":             np.random.normal(115, 20, n).clip(0, 300),
        "key":               np.random.randint(0, 12, n),
        "mode":              np.random.randint(0, 2, n),
        "time_signature":    np.random.choice([3, 4], n, p=[0.05, 0.95]),
    })


@pytest.fixture
def synthetic_batch_20():
    """20-row DataFrame below minimum_drift_rows threshold."""
    np.random.seed(7)
    n = 20
    return pd.DataFrame({
        "duration_min":     np.random.exponential(3.5, n).clip(0.1, 60),
        "explicit":          np.random.choice([True, False], n),
        "release_year":      np.random.randint(1920, 2025, n),
        "release_month":     np.random.choice(list(range(1, 13)), n),
        "decade":            (np.random.randint(192, 203, n) * 10),
        "release_precision": np.random.choice(["year", "month", "day"], n),
        "danceability":      np.random.beta(5, 5, n),
        "energy":            np.random.beta(4, 6, n),
        "loudness":          np.random.normal(-10.6, 5, n).clip(-60, 0),
        "speechiness":       np.random.exponential(0.043, n).clip(0, 1),
        "acousticness":      np.random.beta(5, 4, n),
        "instrumentalness":  np.random.exponential(0.0001, n).clip(0, 1),
        "liveness":          np.random.beta(1.5, 8, n).clip(0, 1),
        "valence":           np.random.beta(5, 5, n),
        "tempo":             np.random.normal(115, 20, n).clip(0, 300),
        "key":               np.random.randint(0, 12, n),
        "mode":              np.random.randint(0, 2, n),
        "time_signature":    np.random.choice([3, 4], n),
    })


@pytest.fixture
def synthetic_batch_missing_field():
    """Batch missing a required schema field (release_year)."""
    np.random.seed(99)
    n = 50
    return pd.DataFrame({
        "duration_min":     np.random.exponential(3.5, n).clip(0.1, 60),
        "explicit":          np.random.choice([True, False], n),
        # release_year intentionally missing
        "release_month":     np.random.choice(list(range(1, 13)), n),
        "decade":            (np.random.randint(192, 203, n) * 10),
        "release_precision": np.random.choice(["year", "month", "day"], n),
        "danceability":      np.random.beta(5, 5, n),
        "energy":            np.random.beta(4, 6, n),
        "loudness":          np.random.normal(-10.6, 5, n).clip(-60, 0),
        "speechiness":       np.random.exponential(0.043, n).clip(0, 1),
        "acousticness":      np.random.beta(5, 4, n),
        "instrumentalness":  np.random.exponential(0.0001, n).clip(0, 1),
        "liveness":          np.random.beta(1.5, 8, n).clip(0, 1),
        "valence":           np.random.beta(5, 5, n),
        "tempo":             np.random.normal(115, 20, n).clip(0, 300),
        "key":               np.random.randint(0, 12, n),
        "mode":              np.random.randint(0, 2, n),
        "time_signature":    np.random.choice([3, 4], n),
    })


@pytest.fixture
def batch_csv_200(tmp_path, synthetic_batch_200):
    p = tmp_path / "batch_200.csv"
    synthetic_batch_200.to_csv(p, index=False)
    return p


@pytest.fixture
def batch_csv_20(tmp_path, synthetic_batch_20):
    p = tmp_path / "batch_20.csv"
    synthetic_batch_20.to_csv(p, index=False)
    return p


@pytest.fixture
def batch_csv_missing_field(tmp_path, synthetic_batch_missing_field):
    p = tmp_path / "batch_missing.csv"
    synthetic_batch_missing_field.to_csv(p, index=False)
    return p


@pytest.fixture
def output_dir(tmp_path):
    d = tmp_path / "monitoring_output"
    d.mkdir()
    return d


@pytest.fixture
def minimal_result():
    return MonitorResult(
        monitor_run_id="TEST-001",
        batch_id="BATCH_TEST",
        model_id="EXP24-XGB-FINAL-001",
        model_version="1.0.0",
        package_version="2.7.0",
        data_version="1.0.0",
        baseline_id="BASELINE-001",
        baseline_version="1.0.0",
        baseline_hash_pre="a" * 64,
        baseline_hash_post="a" * 64,
        input_rows=200,
        output_dir=Path(tempfile.gettempdir()),
    )

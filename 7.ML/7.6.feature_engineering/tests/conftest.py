"""
Shared pytest fixtures for Feature 2.3 test suite.
"""

import json
import os
import pytest
import hashlib


# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
OUTPUT_DIR = os.path.join(REPO_ROOT, "7.ML", "7.6.feature_engineering")


# ---------------------------------------------------------------------------
# Artifact loaders (cached per session)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def output_dir():
    """Absolute path to the feature engineering output directory."""
    assert os.path.isdir(OUTPUT_DIR), f"OUTPUT_DIR not found: {OUTPUT_DIR}"
    return OUTPUT_DIR


@pytest.fixture(scope="session")
def baseline_feature_set(output_dir):
    """Parsed baseline_feature_set.json."""
    path = os.path.join(output_dir, "baseline_feature_set.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def feature_2_3_validation_results(output_dir):
    """Parsed feature_2_3_validation_results.json."""
    path = os.path.join(output_dir, "feature_2_3_validation_results.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def feature_registry(output_dir):
    """Parsed feature_registry.json."""
    path = os.path.join(output_dir, "feature_registry.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def feature_engineering_pipeline_manifest(output_dir):
    """Parsed feature_engineering_pipeline_manifest.json."""
    path = os.path.join(output_dir, "feature_engineering_pipeline_manifest.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def feature_ablation_results(output_dir):
    """Parsed feature_ablation_results.json."""
    path = os.path.join(output_dir, "feature_ablation_results.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def selected_feature_set(output_dir):
    """Parsed selected_feature_set.json."""
    path = os.path.join(output_dir, "selected_feature_set.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def baseline_metrics(output_dir):
    """Parsed baseline_metrics.json."""
    path = os.path.join(output_dir, "baseline_metrics.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def duration_thresholds(output_dir):
    """Parsed duration_thresholds.json."""
    path = os.path.join(output_dir, "duration_thresholds.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def feature_selection_results(output_dir):
    """Parsed feature_selection_results.json."""
    path = os.path.join(output_dir, "feature_selection_results.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def feature_2_4_input_contract(output_dir):
    """Parsed feature_2_4_input_contract.json."""
    path = os.path.join(output_dir, "feature_2_4_input_contract.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def feature_registry_manifest(output_dir):
    """Parsed feature_registry_manifest.json."""
    path = os.path.join(output_dir, "feature_registry_manifest.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Canonical reference lists
# ---------------------------------------------------------------------------

EXPECTED_BASELINE_FEATURES = [
    "duration_min", "release_year", "danceability", "energy", "loudness",
    "speechiness", "acousticness", "instrumentalness", "liveness", "valence",
    "tempo", "release_month", "decade", "release_precision", "key",
    "time_signature", "explicit", "mode",
]

EXPECTED_ENGINEERED_FEATURES = [
    "release_month_sin", "release_month_cos", "year_in_decade",
    "duration_log", "duration_squared",
    "energy_danceability", "energy_valence", "danceability_valence",
    "acousticness_instrumentalness", "energy_liveness",
    "speechiness_explicit", "tempo_danceability", "loudness_energy",
]

BASELINE_SHA256 = "823ced641e09acf862ea3d186a92e35a6a1456aa4f4285f3aefa22e5f7b69e6c"


@pytest.fixture(scope="session")
def expected_baseline_features():
    """Canonical ordered list of 18 baseline features."""
    return EXPECTED_BASELINE_FEATURES


@pytest.fixture(scope="session")
def expected_engineered_features():
    """Canonical ordered list of 13 selected engineered features."""
    return EXPECTED_ENGINEERED_FEATURES


@pytest.fixture(scope="session")
def baseline_sha256():
    """Expected SHA-256 hash of the baseline feature list."""
    return BASELINE_SHA256


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def sha256_of_list(items):
    """Compute deterministic SHA-256 of a sorted feature list."""
    joined = ",".join(sorted(items))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def sha256_of_list_ordered(items):
    """Compute deterministic SHA-256 of a feature list preserving order."""
    joined = ",".join(items)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()

"""
Trend Data Loader — Feature 3.4 Phase 1.

Loads trend data from the canonical processed dataset.
Read-only. Does not modify source.
Does not perform model inference or SHAP computation.

Schema (confirmed from CSV header):
  Canonical source: 5.DATA/processed/ml_ready_dataset.csv
  Rows: 169,681
  Columns: track_id, target_popularity, duration_min, explicit,
           release_year, release_month, decade, release_precision,
           danceability, energy, key, loudness, mode,
           speechiness, acousticness, instrumentalness, liveness,
           valence, tempo, time_signature
  Year range: 1922–2019 (PARTIAL_RANGE — no 1921, no 2020)
  Duration unit: minutes (NOT milliseconds)
  Popularity field: target_popularity (NOT "popularity")
  Artist/genre: NOT available in this dataset
  Decade: pre-computed column (release_year // 10) * 10
"""
from __future__ import annotations

import hashlib
import os
import pathlib
from typing import Any

import pandas as pd


# ── Source Paths ─────────────────────────────────────────────────────────────

_REPO_ROOT = pathlib.Path(os.path.dirname(__file__)).resolve().parent.parent.parent

_CANONICAL_DATASET = _REPO_ROOT / "5.DATA" / "processed" / "ml_ready_dataset.csv"
_CANONICAL_EVAL = (
    _REPO_ROOT
    / "7.ML"
    / "7.8.model_evaluation"
    / "temporal"
    / "yearly_evaluation.csv"
)

# ── Canonical Field Names ─────────────────────────────────────────────────────

FIELD_TEMPORAL = "release_year"
FIELD_POPULARITY = "target_popularity"   # NOT "popularity"
FIELD_DURATION = "duration_min"            # NOT "duration_ms" — unit is MINUTES
FIELD_EXPLICIT = "explicit"
FIELD_DECADE = "decade"                   # pre-computed: (release_year // 10) * 10
FIELD_TRACK_ID = "track_id"

AUDIO_FEATURES = [
    "danceability", "energy", "key", "loudness", "mode",
    "speechiness", "acousticness", "instrumentalness",
    "liveness", "valence", "tempo", "time_signature",
]

YEARLY_EVAL_COLS = [
    "actual_mean", "predicted_mean", "MAE", "RMSE", "R2",
    "actual_median", "predicted_median",
]


# ── Source Info ────────────────────────────────────────────────────────────────

def get_source_paths() -> dict[str, pathlib.Path]:
    return {
        "dataset": _CANONICAL_DATASET,
        "evaluation": _CANONICAL_EVAL,
    }


def get_source_info() -> dict[str, dict]:
    return {
        "dataset": {
            "path": str(_CANONICAL_DATASET),
            "relative": "5.DATA/processed/ml_ready_dataset.csv",
            "source_epic": "EPIC 1 / Feature 1.3",
            "year_min": 1922,
            "year_max": 2019,
            "rows": 169681,
        },
        "evaluation": {
            "path": str(_CANONICAL_EVAL),
            "relative": "7.ML/7.8.model_evaluation/temporal/yearly_evaluation.csv",
            "source_epic": "EPIC 2",
            "year_min": 2014,
            "year_max": 2021,
        },
    }


# ── Hash ──────────────────────────────────────────────────────────────────────

def _hash_file(path: pathlib.Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def get_source_fingerprint() -> dict[str, dict]:
    return {
        "dataset": {
            "path": str(_CANONICAL_DATASET),
            "sha256": _hash_file(_CANONICAL_DATASET),
        },
        "evaluation": {
            "path": str(_CANONICAL_EVAL),
            "sha256": _hash_file(_CANONICAL_EVAL),
        },
    }


# ── Load ──────────────────────────────────────────────────────────────────────

def load_trend_dataset() -> pd.DataFrame:
    """
    Load the canonical processed dataset (read-only).

    Returns:
        DataFrame with all 169,681 rows and 20 columns.
        Caller must not mutate the returned DataFrame in-place.

    Raises:
        FileNotFoundError: if canonical dataset does not exist.
    """
    path = _CANONICAL_DATASET
    if not path.exists():
        raise FileNotFoundError(f"Canonical dataset not found: {path}")

    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    return df.copy()  # immutable semantic copy


def load_yearly_evaluation() -> pd.DataFrame:
    """
    Load yearly model evaluation data (read-only).

    Returns:
        DataFrame with yearly evaluation metrics (2014–2021).
    """
    path = _CANONICAL_EVAL
    if not path.exists():
        raise FileNotFoundError(f"Canonical evaluation not found: {path}")

    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    return df.copy()


# ── Aggregations ───────────────────────────────────────────────────────────────

def aggregate_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate audio features by release_year.

    Returns a DataFrame with one row per year and mean values per audio feature.
    """
    agg_cols = [f for f in AUDIO_FEATURES if f in df.columns]
    numeric_cols = [FIELD_TEMPORAL] + agg_cols
    available = [c for c in numeric_cols if c in df.columns]

    result = (
        df[available]
        .groupby(FIELD_TEMPORAL, as_index=False)
        .mean(numeric_only=True)
    )
    count = df.groupby(FIELD_TEMPORAL, as_index=False).size().rename(columns={"size": "_count"})
    return result.merge(count, on=FIELD_TEMPORAL)


def aggregate_by_decade(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate audio features by decade (using pre-computed 'decade' column).

    Decade label: 1920s, 1930s, ..., 2010s.
    Note: 2020 is a single-year edge case, NOT a full decade.
    """
    if FIELD_DECADE not in df.columns:
        df = df.copy()
        df[FIELD_DECADE] = (df[FIELD_TEMPORAL] // 10) * 10

    agg_cols = [f for f in AUDIO_FEATURES if f in df.columns]
    available = [FIELD_DECADE] + agg_cols
    result = (
        df[available]
        .groupby(FIELD_DECADE, as_index=False)
        .mean(numeric_only=True)
    )
    count = df.groupby(FIELD_DECADE, as_index=False).size().rename(columns={"size": "_count"})
    return result.merge(count, on=FIELD_DECADE)


def aggregate_popularity_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate target_popularity by release_year."""
    if FIELD_POPULARITY not in df.columns:
        return pd.DataFrame()
    return (
        df[[FIELD_TEMPORAL, FIELD_POPULARITY]]
        .groupby(FIELD_TEMPORAL, as_index=False)
        .agg(
            popularity_mean=(FIELD_POPULARITY, "mean"),
            popularity_std=(FIELD_POPULARITY, "std"),
            popularity_count=(FIELD_POPULARITY, "count"),
        )
        .rename(columns={FIELD_TEMPORAL: "year"})
    )


# ── Schema Validation ─────────────────────────────────────────────────────────

REQUIRED_COLUMNS = {FIELD_TEMPORAL, FIELD_POPULARITY, FIELD_DURATION, FIELD_EXPLICIT}
OPTIONAL_AUDIO = set(AUDIO_FEATURES)


def validate_schema(df: pd.DataFrame) -> list[str]:
    """
    Validate that the loaded DataFrame has the required columns.

    Returns:
        List of validation error messages. Empty list means valid.
    """
    errors = []
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {sorted(missing)}")
    unknown = set(df.columns) - REQUIRED_COLUMNS - OPTIONAL_AUDIO - {"track_id", FIELD_DECADE, "release_month", "release_precision"}
    if unknown:
        errors.append(f"Unexpected columns (ignored for visualization): {sorted(unknown)}")
    return errors

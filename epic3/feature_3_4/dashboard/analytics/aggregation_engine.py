"""
Aggregation Engine — Feature 3.4 Phase 2.

Provides aggregation functions for:
- Popularity by year
- Popularity by decade
- Audio features by year
- Audio features by decade

All functions return structured dicts (not chart objects).
The Streamlit page is responsible for rendering.

Strict rules:
- Never mutate the input DataFrame.
- Never fill missing years by interpolation.
- Never impute missing values.
- Always include valid_rows and total_rows coverage.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from dashboard.loaders.trend_data_loader import (
    FIELD_TEMPORAL,
    FIELD_POPULARITY,
    FIELD_DURATION,
    FIELD_EXPLICIT,
    FIELD_DECADE,
    AUDIO_FEATURES,
)
from dashboard.analytics.audio_feature_engine import (
    is_valid_feature,
    get_feature_metadata,
)


# ── Constants ────────────────────────────────────────────────────────────────

YEAR_MIN = 1922
YEAR_MAX = 2019
REQUIRED_START = 1921
REQUIRED_END = 2020


# ── Helper ─────────────────────────────────────────────────────────────────

def _coverage(valid_rows: int, total_rows: int) -> float:
    if total_rows == 0:
        return 0.0
    return round(valid_rows / total_rows, 6)


# ── Year Filter ──────────────────────────────────────────────────────────────

def filter_by_year(df: pd.DataFrame, year_min: int, year_max: int) -> pd.DataFrame:
    """
    Filter DataFrame to a year range (inclusive).

    Returns a COPY — does not mutate the input.
    """
    if FIELD_TEMPORAL not in df.columns:
        return df.copy()
    years = df[FIELD_TEMPORAL]
    mask = years.between(year_min, year_max)
    return df.loc[mask].copy()


# ── Popularity by Year ──────────────────────────────────────────────────────

def aggregate_popularity_by_year(
    df: pd.DataFrame,
    year_min: int = YEAR_MIN,
    year_max: int = YEAR_MAX,
    method: str = "mean",
) -> dict[str, Any]:
    """
    Aggregate target_popularity by release_year.

    Args:
        df: Source DataFrame.
        year_min: Minimum year (default: 1922).
        year_max: Maximum year (default: 2019).
        method: "mean" or "median".

    Returns:
        Structured dict with chart-ready data points.
        Never interpolates missing years.
    """
    if FIELD_POPULARITY not in df.columns or FIELD_TEMPORAL not in df.columns:
        return _empty_trend("popularity_by_year")

    subset = filter_by_year(df, year_min, year_max)
    if subset.empty:
        return _empty_trend("popularity_by_year")

    if method not in ("mean", "median"):
        method = "mean"

    agg_fn = "mean" if method == "mean" else "median"
    total_rows = len(subset)
    valid_rows = subset[FIELD_POPULARITY].notna().sum()

    year_pop = (
        subset[[FIELD_TEMPORAL, FIELD_POPULARITY]]
        .dropna(subset=[FIELD_POPULARITY])
        .groupby(FIELD_TEMPORAL, as_index=False)
        .agg(popularity=(FIELD_POPULARITY, agg_fn))
    )
    year_pop = year_pop.sort_values(FIELD_TEMPORAL)

    points = []
    for _, row in year_pop.iterrows():
        yr = int(row[FIELD_TEMPORAL])
        count_in_year = int(subset[subset[FIELD_TEMPORAL] == yr].shape[0])
        valid_in_year = int(
            subset[subset[FIELD_TEMPORAL] == yr][FIELD_POPULARITY].notna().sum()
        )
        points.append({
            "year": yr,
            "popularity_value": round(float(row["popularity"]), 4),
            "aggregation": method,
            "valid_rows": valid_in_year,
            "total_rows": count_in_year,
            "coverage": _coverage(valid_in_year, count_in_year),
        })

    return {
        "metric": "popularity",
        "aggregation": method,
        "time_granularity": "year",
        "year_min": int(year_min),
        "year_max": int(year_max),
        "data_points": points,
        "total_years": len(points),
        "overall_valid_rows": int(valid_rows),
        "overall_total_rows": int(total_rows),
        "overall_coverage": _coverage(valid_rows, total_rows),
        "missing_years": [
            y for y in range(int(year_min), int(year_max) + 1)
            if y not in [p["year"] for p in points]
        ],
        "status": "OK" if points else "NO_DATA",
    }


# ── Popularity by Decade ────────────────────────────────────────────────────

def aggregate_popularity_by_decade(
    df: pd.DataFrame,
    method: str = "mean",
) -> dict[str, Any]:
    """
    Aggregate target_popularity by decade.

    2020 is treated as a SINGLE-YEAR and labeled as '2020 (single year)'.
    Not included in a full '2020s' decade bar.

    Returns structured dict with chart-ready data points.
    """
    if FIELD_POPULARITY not in df.columns or FIELD_TEMPORAL not in df.columns:
        return _empty_trend("popularity_by_decade")

    if FIELD_DECADE not in df.columns:
        df = df.copy()
        df[FIELD_DECADE] = (df[FIELD_TEMPORAL] // 10) * 10

    total_rows = len(df)
    valid_rows = df[FIELD_POPULARITY].notna().sum()

    decade_pop = (
        df[[FIELD_DECADE, FIELD_POPULARITY]]
        .dropna(subset=[FIELD_POPULARITY])
        .groupby(FIELD_DECADE, as_index=False)
        .agg(popularity=("target_popularity", "mean" if method == "mean" else "median"))
    )
    decade_pop = decade_pop.sort_values(FIELD_DECADE)

    points = []
    for _, row in decade_pop.iterrows():
        dec = int(row[FIELD_DECADE])
        # Check if this decade has only 2020 (single year)
        years_in_decade = df[df[FIELD_DECADE] == dec][FIELD_TEMPORAL].unique()
        is_single_2020 = (dec == 2020 and set(years_in_decade) == {2020})

        label = f"{dec}s" if not is_single_2020 else f"{dec} (single year)"
        count_in_decade = int(df[df[FIELD_DECADE] == dec].shape[0])
        valid_in_decade = int(
            df[df[FIELD_DECADE] == dec][FIELD_POPULARITY].notna().sum()
        )
        points.append({
            "decade": dec,
            "decade_label": label,
            "popularity_value": round(float(row["popularity"]), 4),
            "aggregation": method,
            "is_single_year_2020": is_single_2020,
            "valid_rows": valid_in_decade,
            "total_rows": count_in_decade,
            "coverage": _coverage(valid_in_decade, count_in_decade),
        })

    return {
        "metric": "popularity",
        "aggregation": method,
        "time_granularity": "decade",
        "data_points": points,
        "total_decades": len(points),
        "overall_valid_rows": int(valid_rows),
        "overall_total_rows": int(total_rows),
        "overall_coverage": _coverage(valid_rows, total_rows),
        "status": "OK" if points else "NO_DATA",
    }


# ── Audio Feature by Year ────────────────────────────────────────────────────

def aggregate_audio_feature_by_year(
    df: pd.DataFrame,
    feature: str,
    year_min: int = YEAR_MIN,
    year_max: int = YEAR_MAX,
    method: str = "mean",
) -> dict[str, Any]:
    """
    Aggregate a single audio feature by release_year.

    Feature must be in the allow-list (is_valid_feature).
    Unit and label are taken from the display registry.

    Returns structured dict. Never interpolates missing years.
    """
    if not is_valid_feature(feature):
        return _empty_trend(f"audio_{feature}_by_year", error=f"Feature '{feature}' not in allow-list")

    if feature not in df.columns:
        return _empty_trend(f"audio_{feature}_by_year", error=f"Column '{feature}' not in dataset")

    subset = filter_by_year(df, year_min, year_max)
    if subset.empty:
        return _empty_trend(f"audio_{feature}_by_year")

    if method not in ("mean", "median"):
        method = "mean"
    agg_fn = "mean" if method == "mean" else "median"

    total_rows = len(subset)
    valid_rows = subset[feature].notna().sum()
    meta = get_feature_metadata(feature)

    year_feat = (
        subset[[FIELD_TEMPORAL, feature]]
        .dropna(subset=[feature])
        .groupby(FIELD_TEMPORAL, as_index=False)
        .agg(value=(feature, agg_fn))
    )
    year_feat = year_feat.sort_values(FIELD_TEMPORAL)

    points = []
    for _, row in year_feat.iterrows():
        yr = int(row[FIELD_TEMPORAL])
        count_in_year = int(subset[subset[FIELD_TEMPORAL] == yr].shape[0])
        valid_in_year = int(
            subset[subset[FIELD_TEMPORAL] == yr][feature].notna().sum()
        )
        points.append({
            "year": yr,
            "feature_value": round(float(row["value"]), meta.get("decimal_places", 3) if meta else 3),
            "aggregation": method,
            "valid_rows": valid_in_year,
            "total_rows": count_in_year,
            "coverage": _coverage(valid_in_year, count_in_year),
        })

    return {
        "feature": feature,
        "display_name": meta.get("display_name", feature) if meta else feature,
        "unit": meta.get("unit") if meta else None,
        "chart_ylabel": meta.get("chart_ylabel", feature) if meta else feature,
        "aggregation": method,
        "time_granularity": "year",
        "year_min": int(year_min),
        "year_max": int(year_max),
        "data_points": points,
        "total_years": len(points),
        "overall_valid_rows": int(valid_rows),
        "overall_total_rows": int(total_rows),
        "overall_coverage": _coverage(valid_rows, total_rows),
        "missing_years": [
            y for y in range(int(year_min), int(year_max) + 1)
            if y not in [p["year"] for p in points]
        ],
        "status": "OK" if points else "NO_DATA",
    }


# ── Audio Feature by Decade ─────────────────────────────────────────────────

def aggregate_audio_feature_by_decade(
    df: pd.DataFrame,
    feature: str,
    method: str = "mean",
) -> dict[str, Any]:
    """
    Aggregate a single audio feature by decade.

    2020 is treated as a SINGLE-YEAR (not a full decade).
    """
    if not is_valid_feature(feature):
        return _empty_trend(f"audio_{feature}_by_decade", error=f"Feature '{feature}' not in allow-list")

    if feature not in df.columns:
        return _empty_trend(f"audio_{feature}_by_decade", error=f"Column '{feature}' not in dataset")

    if FIELD_DECADE not in df.columns:
        df = df.copy()
        df[FIELD_DECADE] = (df[FIELD_TEMPORAL] // 10) * 10

    if method not in ("mean", "median"):
        method = "mean"
    agg_fn = "mean" if method == "mean" else "median"

    total_rows = len(df)
    valid_rows = df[feature].notna().sum()
    meta = get_feature_metadata(feature)

    decade_feat = (
        df[[FIELD_DECADE, feature]]
        .dropna(subset=[feature])
        .groupby(FIELD_DECADE, as_index=False)
        .agg(value=(feature, agg_fn))
    )
    decade_feat = decade_feat.sort_values(FIELD_DECADE)

    points = []
    for _, row in decade_feat.iterrows():
        dec = int(row[FIELD_DECADE])
        years_in_decade = df[df[FIELD_DECADE] == dec][FIELD_TEMPORAL].unique()
        is_single_2020 = (dec == 2020 and set(years_in_decade) == {2020})
        label = f"{dec}s" if not is_single_2020 else f"{dec} (single year)"

        count_in_decade = int(df[df[FIELD_DECADE] == dec].shape[0])
        valid_in_decade = int(
            df[df[FIELD_DECADE] == dec][feature].notna().sum()
        )
        points.append({
            "decade": dec,
            "decade_label": label,
            "feature_value": round(float(row["value"]), meta.get("decimal_places", 3) if meta else 3),
            "aggregation": method,
            "is_single_year_2020": is_single_2020,
            "valid_rows": valid_in_decade,
            "total_rows": count_in_decade,
            "coverage": _coverage(valid_in_decade, count_in_decade),
        })

    return {
        "feature": feature,
        "display_name": meta.get("display_name", feature) if meta else feature,
        "unit": meta.get("unit") if meta else None,
        "chart_ylabel": meta.get("chart_ylabel", feature) if meta else feature,
        "aggregation": method,
        "time_granularity": "decade",
        "data_points": points,
        "total_decades": len(points),
        "overall_valid_rows": int(valid_rows),
        "overall_total_rows": int(total_rows),
        "overall_coverage": _coverage(valid_rows, total_rows),
        "status": "OK" if points else "NO_DATA",
    }


# ── Empty State ─────────────────────────────────────────────────────────────

def _empty_trend(chart_id: str, error: str | None = None) -> dict[str, Any]:
    return {
        "chart_id": chart_id,
        "data_points": [],
        "total_years": 0,
        "total_decades": 0,
        "status": "NO_DATA",
        "error": error,
    }

"""
Duration Trend Aggregation — Feature 3.4 Phase 3.

Provides:
- duration aggregation by decade (mean, median)
- invalid value tracking
- coverage reporting

Field: duration_min (minutes, already converted from source)

Unit policy (Phase 1):
  Source: duration_min (MINUTES, NOT milliseconds)
  No further conversion needed.
  To display in seconds: duration_min * 60
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from dashboard.loaders.trend_data_loader import (
    FIELD_TEMPORAL,
    FIELD_DURATION,
    FIELD_DECADE,
)


# Valid duration range in minutes
# These bounds are based on Spotify metadata conventions.
# Tracks shorter than 0.1 min (6s) or longer than 30 min are considered outliers.
DURATION_MIN_VALID = 0.1   # 6 seconds
DURATION_MAX_VALID = 30.0  # 30 minutes


def _is_valid_duration(val) -> bool:
    """Check if a duration value is valid (finite and within plausible range)."""
    import math
    try:
        v = float(val)
        return math.isfinite(v) and DURATION_MIN_VALID <= v <= DURATION_MAX_VALID
    except (TypeError, ValueError):
        return False


def aggregate_duration_by_decade(df: pd.DataFrame) -> dict[str, Any]:
    """
    Aggregate track duration by decade.

    Metric: mean and median duration (in minutes).
    Invalid durations (NaN, non-finite, outside 0.1–30 min) are excluded
    from aggregation but counted in invalid_count.

    Returns structured dict.
    """
    if FIELD_DURATION not in df.columns:
        return _empty_duration()

    if FIELD_DECADE not in df.columns:
        df = df.copy()
        df[FIELD_DECADE] = (df[FIELD_TEMPORAL] // 10) * 10

    total_rows = len(df)
    valid_mask = df[FIELD_DURATION].apply(_is_valid_duration)
    valid_df = df[valid_mask]
    invalid_df = df[~valid_mask]

    if valid_df.empty:
        return _empty_duration()

    decade_stats = (
        valid_df
        .groupby(FIELD_DECADE, as_index=False)
        .agg(
            duration_mean=(FIELD_DURATION, "mean"),
            duration_median=(FIELD_DURATION, "median"),
            valid_count=(FIELD_DURATION, "count"),
        )
    )
    decade_stats = decade_stats.sort_values(FIELD_DECADE)

    points = []
    for _, row in decade_stats.iterrows():
        dec = int(row[FIELD_DECADE])
        valid_in_decade = int(valid_df[valid_df[FIELD_DECADE] == dec].shape[0])
        invalid_in_decade = int(df[df[FIELD_DECADE] == dec].shape[0]) - valid_in_decade

        years_in_decade = df[df[FIELD_DECADE] == dec][FIELD_TEMPORAL].unique()
        is_single_2020 = (dec == 2020 and set(years_in_decade) == {2020})
        label = f"{dec}s" if not is_single_2020 else f"{dec} (single year)"

        points.append({
            "decade": dec,
            "decade_label": label,
            "duration_mean_min": round(float(row["duration_mean"]), 3),
            "duration_median_min": round(float(row["duration_median"]), 3),
            "valid_count": valid_in_decade,
            "invalid_count": invalid_in_decade,
            "is_single_year_2020": is_single_2020,
        })

    return {
        "metric": "duration",
        "unit": "minutes",
        "aggregation": "mean and median",
        "time_granularity": "decade",
        "duration_range": {"min_valid_min": DURATION_MIN_VALID, "max_valid_min": DURATION_MAX_VALID},
        "total_rows": total_rows,
        "total_valid": len(valid_df),
        "total_invalid": len(invalid_df),
        "overall_coverage": round(len(valid_df) / total_rows, 6) if total_rows > 0 else 0.0,
        "data_points": points,
        "status": "OK" if points else "NO_DATA",
    }

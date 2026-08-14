"""
Explicit Trend Aggregation — Feature 3.4 Phase 3.

Provides:
- explicit_rate by decade (percentage of tracks marked explicit)
- invalid value tracking
- coverage reporting

Field: explicit (bool — Python True/False)
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from dashboard.loaders.trend_data_loader import (
    FIELD_TEMPORAL,
    FIELD_EXPLICIT,
    FIELD_DECADE,
)


def aggregate_explicit_by_decade(df: pd.DataFrame) -> dict[str, Any]:
    """
    Aggregate explicit marking rate by decade.

    Metric: explicit_rate = explicit_count / valid_count (per decade)
    Where:
      - explicit_count: rows where explicit == True
      - valid_count: rows where explicit is True or False (not null)
      - invalid_count: rows where explicit is null or non-boolean

    Returns structured dict. Never interpolates or imputes.
    """
    if FIELD_EXPLICIT not in df.columns:
        return _empty_explicit()

    if FIELD_DECADE not in df.columns:
        df = df.copy()
        df[FIELD_DECADE] = (df[FIELD_TEMPORAL] // 10) * 10

    # Identify valid explicit values (True or False)
    valid_mask = df[FIELD_EXPLICIT].isin([True, False])
    valid_df = df[valid_mask]
    invalid_df = df[~valid_mask]

    total_rows = len(df)
    total_valid = len(valid_df)
    total_invalid = len(invalid_df)

    if valid_df.empty:
        return _empty_explicit()

    decade_stats = (
        valid_df
        .groupby(FIELD_DECADE, as_index=False)
        .agg(
            explicit_count=(FIELD_EXPLICIT, "sum"),  # True=1, False=0
            valid_count=(FIELD_EXPLICIT, "count"),
        )
    )
    # explicit_count is sum of bools (True=1, False=0)
    # But pandas sum on bool col may overflow — cast to int
    decade_stats["explicit_count"] = decade_stats[FIELD_EXPLICIT].astype(int)
    decade_stats = decade_stats.sort_values(FIELD_DECADE)

    points = []
    for _, row in decade_stats.iterrows():
        dec = int(row[FIELD_DECADE])
        explicit_count = int(row["explicit_count"])
        valid_count = int(row["valid_count"])
        invalid_in_decade = int(df[df[FIELD_DECADE] == dec].shape[0]) - valid_count
        explicit_rate = round(explicit_count / valid_count, 6) if valid_count > 0 else None

        years_in_decade = df[df[FIELD_DECADE] == dec][FIELD_TEMPORAL].unique()
        is_single_2020 = (dec == 2020 and set(years_in_decade) == {2020})
        label = f"{dec}s" if not is_single_2020 else f"{dec} (single year)"

        points.append({
            "decade": dec,
            "decade_label": label,
            "explicit_count": explicit_count,
            "non_explicit_count": valid_count - explicit_count,
            "valid_count": valid_count,
            "invalid_count": invalid_in_decade,
            "explicit_rate": explicit_rate,
            "explicit_percentage": round(explicit_rate * 100, 2) if explicit_rate is not None else None,
            "is_single_year_2020": is_single_2020,
        })

    return {
        "metric": "explicit_rate",
        "aggregation": "rate (explicit_count / valid_count)",
        "time_granularity": "decade",
        "total_rows": total_rows,
        "total_valid": total_valid,
        "total_invalid": total_invalid,
        "overall_coverage": round(total_valid / total_rows, 6) if total_rows > 0 else 0.0,
        "data_points": points,
        "status": "OK" if points else "NO_DATA",
    }


def _empty_explicit() -> dict[str, Any]:
    return {
        "metric": "explicit_rate",
        "aggregation": "rate",
        "time_granularity": "decade",
        "total_rows": 0,
        "total_valid": 0,
        "total_invalid": 0,
        "overall_coverage": 0.0,
        "data_points": [],
        "status": "NO_DATA",
    }

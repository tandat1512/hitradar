"""
Caption Generator Engine — Feature 3.4 Phase 4.

Deterministic caption generators for all dashboard charts.
Captions are derived from actual aggregate data — no guessing.
No causal language. No unsupported generalizations.

Key principles:
- "increased" / "decreased" only when first != last value is verified.
- "highest" / "lowest" only when min/max are verified from data.
- All trend language uses "in the dataset" / "in the available data" qualifier.
- Causal language is banned.
- Industry/general-population generalization is banned.
"""
from __future__ import annotations

from dashboard.analytics.audio_feature_engine import get_feature_metadata

# ── Threshold for "broadly similar" vs directional language ────────────────

# If absolute net change < this fraction of overall mean, describe as "broadly similar"
_SIMILARITY_THRESHOLD = 0.05

# ── Helpers ─────────────────────────────────────────────────────────────────

def _round(value: float, decimals: int = 2) -> float:
    return round(value, decimals)


def _describe_change(first: float, last: float, metric_label: str) -> str:
    """
    Return a descriptive change phrase based on actual values.
    Returns a short phrase like "increased over the period" or "broadly similar".
    """
    if first is None or last is None:
        return "varied across the period"
    diff = last - first
    if abs(diff) < _SIMILARITY_THRESHOLD * max(abs(first), abs(last), 1e-9):
        return "remained broadly similar over the period"
    elif diff > 0:
        return f"increased from {_round(first)} to {_round(last)} over the period"
    else:
        return f"decreased from {_round(first)} to {_round(last)} over the period"


# ── Coverage caption ─────────────────────────────────────────────────────────

def coverage_caption(data: dict) -> str:
    """Append coverage note if significant missing values exist."""
    coverage = data.get("overall_coverage", 1.0)
    null_count = data.get("total_rows", 0) - data.get("total_valid", data.get("total_rows", 0))
    if null_count > 0:
        return f" (Based on {int(data.get('overall_valid_rows', 0)):,} records with available data of {int(data.get('total_rows', 0)):,} total)"
    return ""


# ── Popularity by Year ───────────────────────────────────────────────────────

def popularity_year_caption(data: dict, year_min: int, year_max: int) -> str:
    """
    Generate caption for average popularity by release year.

    Shows: first value, last value, min/max year, net change direction.
    Always qualifies trend language with "in the dataset".
    """
    points = data.get("data_points", [])
    if not points:
        return "No popularity data available for the selected period."

    years = sorted([p["year"] for p in points])
    first_yr, last_yr = years[0], years[-1]
    first_val = next((p["popularity_value"] for p in points if p["year"] == first_yr), None)
    last_val = next((p["popularity_value"] for p in points if p["year"] == last_yr), None)
    all_vals = [p["popularity_value"] for p in points]
    max_val = max(all_vals)
    min_val = min(all_vals)
    max_yr = next((p["year"] for p in points if p["popularity_value"] == max_val))
    min_yr = next((p["year"] for p in points if p["popularity_value"] == min_val)
)
    max_str = f"{_round(max_val)} in {max_yr}" if max_yr != min_yr else f"{_round(max_val)}"
    min_str = f"{_round(min_val)} in {min_yr}" if max_yr != min_yr else ""

    change = _describe_change(first_val, last_val, "popularity")

    parts = [
        f"Mean popularity ranged from {min_str} to {max_str} in the available data.",
        f"Values {change} across {year_min}–{year_max}.",
    ]
    parts.append(coverage_caption(data))
    return " ".join(parts).strip()


# ── Popularity by Decade ─────────────────────────────────────────────────────

def popularity_decade_caption(data: dict) -> str:
    """Generate caption for average popularity by decade."""
    points = data.get("data_points", [])
    if not points:
        return "No popularity data available."

    decades_sorted = sorted([p["decade"] for p in points])
    first_dec = decades_sorted[0]
    last_dec = decades_sorted[-1]
    first_val = next((p["popularity_value"] for p in points if p["decade"] == first_dec), None)
    last_val = next((p["popularity_value"] for p in points if p["decade"] == last_dec), None)
    all_vals = [p["popularity_value"] for p in points]
    max_val = max(all_vals)
    min_val = min(all_vals)
    max_dec = next((p["decade"] for p in points if p["popularity_value"] == max_val))
    min_dec = next((p["decade"] for p in points if p["popularity_value"] == min_val))

    parts = [
        f"Mean popularity per decade ranged from {_round(min_val)} ({min_dec}s) to {_round(max_val)} ({max_dec}s) in the available data.",
    ]
    # 2020 edge case
    has_2020_single = any(p.get("is_single_year_2020") for p in points)
    if has_2020_single:
        val_2020 = next((p["popularity_value"] for p in points if p.get("is_single_year_2020")), None)
        parts.append(f" Note: '2020' represents only the year 2020, not a full decade.")

    parts.append(coverage_caption(data))
    return " ".join(parts).strip()


# ── Audio Feature by Year ──────────────────────────────────────────────────

def audio_year_caption(data: dict, year_min: int, year_max: int) -> str:
    """Generate caption for a single audio feature trend by year."""
    points = data.get("data_points", [])
    if not points:
        return "No data available for the selected feature and period."

    feature = data.get("feature", "feature")
    display = data.get("display_name", feature)
    unit = data.get("unit")
    unit_str = f" {unit}" if unit else ""

    years = sorted([p["year"] for p in points])
    first_yr, last_yr = years[0], years[-1]
    first_val = next((p["feature_value"] for p in points if p["year"] == first_yr), None)
    last_val = next((p["feature_value"] for p in points if p["year"] == last_yr), None)
    all_vals = [p["feature_value"] for p in points if p["feature_value"] is not None]
    max_val = max(all_vals)
    min_val = min(all_vals)
    max_yr = next((p["year"] for p in points if p["feature_value"] == max_val), None)
    min_yr = next((p["year"] for p in points if p["feature_value"] == min_val), None)

    parts = [
        f"{display} values {unit_str} ranged from {_round(min_val)} ({min_yr}) to {_round(max_val)} ({max_yr}) in the available data.",
        f"Values {_describe_change(first_val, last_val, feature)} across {year_min}–{year_max}.",
    ]
    parts.append(coverage_caption(data))
    return " ".join(parts).strip()


# ── Audio Feature by Decade ─────────────────────────────────────────────────

def audio_decade_caption(data: dict) -> str:
    """Generate caption for a single audio feature trend by decade."""
    points = data.get("data_points", [])
    if not points:
        return "No data available."

    feature = data.get("feature", "feature")
    display = data.get("display_name", feature)
    unit = data.get("unit")
    unit_str = f" {unit}" if unit else ""

    decades_sorted = sorted([p["decade"] for p in points])
    all_vals = [p["feature_value"] for p in points if p["feature_value"] is not None]
    if not all_vals:
        return "No valid data."
    max_val = max(all_vals)
    min_val = min(all_vals)
    max_dec = next((p["decade"] for p in points if p["feature_value"] == max_val), None)
    min_dec = next((p["decade"] for p in points if p["feature_value"] == min_val), None)

    parts = [
        f"{display} values{unit_str} ranged from {_round(min_val)} ({min_dec}s) to {_round(max_val)} ({max_dec}s) in the available data.",
    ]
    has_2020 = any(p.get("is_single_year_2020") for p in points)
    if has_2020:
        parts.append(" Note: '2020' represents only the year 2020, not a full decade.")

    parts.append(coverage_caption(data))
    return " ".join(parts).strip()


# ── Track Count by Year ─────────────────────────────────────────────────────

def track_count_caption(data: dict, year_min: int, year_max: int) -> str:
    """Generate caption for track count by release year."""
    points = data.get("data_points", [])
    if not points:
        return "No track data available."

    years = sorted([p["year"] for p in points])
    all_counts = [p.get("total_rows", 0) for p in points]
    total = sum(all_counts)
    max_count = max(all_counts)
    max_yr = next((p["year"] for p in points if p.get("total_rows", 0) == max_count), None)
    min_count = min(all_counts)
    min_yr = next((p["year"] for p in points if p.get("total_rows", 0) == min_count), None)

    parts = [
        f"Dataset contains {total:,} tracks from {year_min}–{year_max}.",
        f"Track count ranged from {min_count:,} ({min_yr}) to {max_count:,} ({max_yr}) per year.",
        f"Coverage: values reflect records available in the project dataset — not the global music industry.",
    ]
    return " ".join(parts).strip()


# ── Explicit Trend ───────────────────────────────────────────────────────────

def explicit_trend_caption(data: dict) -> str:
    """
    Generate caption for percentage of tracks marked explicit by decade.

    Metric: explicit_rate = explicit_count / valid_count (%)
    Always uses "share of tracks" not "societal" language.
    """
    points = data.get("data_points", [])
    if not points:
        return "No explicit marking data available."

    decades_sorted = sorted([p["decade"] for p in points])
    first_dec = decades_sorted[0]
    last_dec = decades_sorted[-1]
    first_rate = next((p["explicit_percentage"] for p in points if p["decade"] == first_dec), None)
    last_rate = next((p["explicit_percentage"] for p in points if p["decade"] == last_dec), None)
    all_rates = [p["explicit_percentage"] for p in points if p["explicit_percentage"] is not None]
    if not all_rates:
        return "No explicit rate data available."
    max_rate = max(all_rates)
    min_rate = min(all_rates)
    max_dec = next((p["decade"] for p in points if p["explicit_percentage"] == max_rate), None)
    min_dec = next((p["decade"] for p in points if p["explicit_percentage"] == min_rate), None)

    parts = [
        f"Share of tracks marked explicit ranged from {min_rate}% ({min_dec}s) to {max_rate}% ({max_dec}s) in the available data.",
        "These values describe the records in this dataset — they do not indicate broader societal trends.",
    ]
    has_2020 = any(p.get("is_single_year_2020") for p in points)
    if has_2020:
        parts.append(" Note: '2020' represents only the year 2020, not a full decade.")

    parts.append(coverage_caption(data))
    return " ".join(parts).strip()


# ── Duration Trend ───────────────────────────────────────────────────────────

def duration_trend_caption(data: dict) -> str:
    """
    Generate caption for average track duration by decade.

    Unit: minutes.
    Always qualifies with "in the available data".
    """
    points = data.get("data_points", [])
    if not points:
        return "No duration data available."

    decades_sorted = sorted([p["decade"] for p in points])
    all_means = [p["duration_mean_min"] for p in points if p.get("duration_mean_min") is not None]
    if not all_means:
        return "No valid duration data."
    max_mean = max(all_means)
    min_mean = min(all_means)
    max_dec = next((p["decade"] for p in points if p.get("duration_mean_min") == max_mean), None)
    min_dec = next((p["decade"] for p in points if p.get("duration_mean_min") == min_mean), None)

    parts = [
        f"Mean track duration ranged from {min_mean} min ({min_dec}s) to {max_mean} min ({max_dec}s) in the available data.",
        "These values describe records in the project dataset.",
    ]
    has_2020 = any(p.get("is_single_year_2020") for p in points)
    if has_2020:
        parts.append(" Note: '2020' represents only the year 2020, not a full decade.")

    parts.append(coverage_caption(data))
    return " ".join(parts).strip()


# ── Artist/Genre NOT AVAILABLE ─────────────────────────────────────────────

ARTIST_GENRE_NOT_AVAILABLE_CAPTION = (
    "Artist and genre data are not available in this dataset. "
    "The dataset contains only audio features and track metadata "
    "(e.g., release year, duration, popularity). "
    "Artist-level or genre-level summaries cannot be generated."
)

def artist_genre_caption() -> str:
    return ARTIST_GENRE_NOT_AVAILABLE_CAPTION


# ── Global coverage disclaimer ──────────────────────────────────────────────

GLOBAL_DISCLAIMER = (
    "All visualizations describe records available in the project dataset. "
    "They do not represent the global music industry or broader population trends."
)

def global_disclaimer_caption() -> str:
    return GLOBAL_DISCLAIMER

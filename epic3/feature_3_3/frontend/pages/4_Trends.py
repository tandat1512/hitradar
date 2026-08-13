"""
Music Trends Page — Feature 3.3 Phase 5.

Aggregates audio feature trends from the processed dataset.
Source: 5.DATA/processed/ml_ready_dataset.csv
+ yearly model evaluation: 7.ML/7.8.model_evaluation/temporal/yearly_evaluation.csv

Data is READ-ONLY. No training. No model loading.
Aggregation: mean by release_year.
"""
from __future__ import annotations

import os
import streamlit as st

# Canonical paths relative to repository root
_REPO_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)
_DATASET_PATH = os.path.join(_REPO_ROOT, "5.DATA", "processed", "ml_ready_dataset.csv")
_EVALUATION_PATH = os.path.join(
    _REPO_ROOT, "7.ML", "7.8.model_evaluation", "temporal", "yearly_evaluation.csv"
)

_AUDIO_FEATURES = [
    "danceability", "energy", "speechiness", "acousticness",
    "instrumentalness", "liveness", "valence", "tempo", "loudness",
]

_ST_METRICS = ["MAE", "RMSE", "R²", "actual_mean", "predicted_mean"]


# ── Data Loading ───────────────────────────────────────────────────────────────

@st.cache_data
def load_yearly_features(path: str) -> dict:
    """Aggregate mean audio features by release_year from ml_ready_dataset.csv."""
    import csv

    if not os.path.exists(path):
        return {}

    yearly: dict[int, dict] = {}
    counts: dict[int, int] = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                year = int(float(row.get("release_year", "").strip()))
            except (ValueError, TypeError):
                continue

            counts[year] = counts.get(year, 0) + 1

            if year not in yearly:
                yearly[year] = {feat: 0.0 for feat in _AUDIO_FEATURES}
                yearly[year]["_count"] = 0

            yearly[year]["_count"] += 1
            for feat in _AUDIO_FEATURES:
                try:
                    yearly[year][feat] += float(row.get(feat, 0) or 0)
                except (ValueError, TypeError):
                    pass

    # Compute mean
    result = {}
    for year, vals in yearly.items():
        count = vals["_count"]
        if count > 0:
            result[year] = {feat: vals[feat] / count for feat in _AUDIO_FEATURES}
            result[year]["_count"] = count

    return result


@st.cache_data
def load_yearly_evaluation(path: str) -> dict:
    """Load yearly model evaluation metrics."""
    import csv

    if not os.path.exists(path):
        return {}

    result = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                year = int(row.get("", "").strip())
            except (ValueError, TypeError):
                continue
            result[year] = {
                "rows": int(row.get("rows", 0)),
                "actual_mean": float(row.get("actual_mean", 0) or 0),
                "predicted_mean": float(row.get("predicted_mean", 0) or 0),
                "MAE": float(row.get("MAE", 0) or 0),
                "RMSE": float(row.get("RMSE", 0) or 0),
                "R2": float(row.get("R2", 0) or 0),
            }
    return result


# ── Page ───────────────────────────────────────────────────────────────────

st.header("📊 Music Trends")

st.caption(
    "Historical trends from the training dataset. "
    "Interpret these as descriptive statistics of the data — "
    "not causal relationships or predictions."
)

# ── Load data ───────────────────────────────────────────────────────────────

with st.spinner("Loading trend data..."):
    yearly_features = load_yearly_features(_DATASET_PATH)
    yearly_eval = load_yearly_evaluation(_EVALUATION_PATH)

if not yearly_features:
    st.error("Could not load trend data. Ensure the dataset file exists.")
    st.stop()

all_years = sorted(yearly_features.keys())
min_year, max_year = min(all_years), max(all_years)

st.caption(
    f"**Dataset coverage:** {min_year}–{max_year} "
    f"({len(all_years)} years, ~{sum(v['_count'] for v in yearly_features.values()):,} tracks). "
    f"Evaluation data available: 2014–2021."
)

st.divider()

# ── Chart 1: Song Count per Year ───────────────────────────────────────────

st.subheader("📈 Songs per Year")

counts = {year: yearly_features[year]["_count"] for year in all_years}

chart_data_count = {
    "year": list(counts.keys()),
    "count": list(counts.values()),
}

st.bar_chart(chart_data_count, x="year", y="count", use_container_width=True)

st.caption(
    f"Number of tracks per release year in the dataset. "
    f"Coverage: {min_year}–{max_year}."
)

st.divider()

# ── Chart 2: Audio Feature Trends ─────────────────────────────────────────

st.subheader("🎵 Audio Feature Trends")

available_features = [f for f in _AUDIO_FEATURES if f in next(iter(yearly_features.values()), {})]

selected_feature = st.selectbox(
    "Select feature to trend:",
    options=available_features,
    index=0,
    help="Mean value of selected audio feature per release year",
)

feature_data = {
    "year": all_years,
    selected_feature: [yearly_features[y].get(selected_feature, 0) for y in all_years],
}

st.line_chart(feature_data, x="year", y=selected_feature, use_container_width=True)

st.caption(
    f"Mean **{selected_feature}** per release year. "
    "Higher values indicate more of that characteristic."
)

st.divider()

# ── Chart 3: Popularity Trend (from yearly evaluation) ───────────────────

if yearly_eval:
    st.subheader("📉 Model Prediction vs Actual Popularity (2014–2021)")

    eval_years = sorted(yearly_eval.keys())
    pop_data = {
        "year": eval_years,
        "Actual Mean": [yearly_eval[y]["actual_mean"] for y in eval_years],
        "Predicted Mean": [yearly_eval[y]["predicted_mean"] for y in eval_years],
    }

    st.line_chart(pop_data, x="year", y=["Actual Mean", "Predicted Mean"], use_container_width=True)

    st.caption(
        "Actual vs model-predicted mean popularity per year. "
        "The gap shows model bias — not that the model causes popularity to change."
    )
else:
    st.info("Yearly evaluation data not available.")

st.divider()

# ── Chart 4: Model Error Metrics ──────────────────────────────────────────

if yearly_eval:
    st.subheader("📐 Model Error by Year (2014–2021)")

    eval_years = sorted(yearly_eval.keys())
    selected_metric = st.selectbox(
        "Select metric:",
        options=_ST_METRICS,
        index=0,
        help="Yearly model evaluation metric",
    )

    metric_key = selected_metric.lower().replace("²", "_squared").replace("²", "").replace("²", "")

    # Normalize key
    key_map = {
        "mae": "MAE", "rmse": "RMSE", "r²": "R2",
        "r2": "R2", "actual_mean": "actual_mean", "predicted_mean": "predicted_mean",
    }
    actual_key = key_map.get(selected_metric.lower(), selected_metric)

    metric_data = {
        "year": eval_years,
        selected_metric: [yearly_eval[y].get(actual_key, 0) for y in eval_years],
    }

    st.line_chart(metric_data, x="year", y=selected_metric, use_container_width=True)

    metric_helps = {
        "MAE": "Mean Absolute Error — average absolute prediction error (lower = better)",
        "RMSE": "Root Mean Squared Error — penalizes large errors (lower = better)",
        "R²": "R-squared — proportion of variance explained (higher = better, can be negative)",
    }
    if selected_metric in metric_helps:
        st.caption(metric_helps[selected_metric])

st.divider()

# ── Limitations ─────────────────────────────────────────────────────────────

st.warning(
    "⚠️ **Trend Limitations:**\n"
    "- Trends describe the available **training dataset only** — not all music globally\n"
    "- Correlation ≠ causation: feature trends do not imply one feature causes another\n"
    "- Model error metrics are computed on the test set, not live predictions\n"
    "- Popularity definition may have changed over time"
)

"""
Model Info Page — Feature 3.3 Phase 5.

Displays model metadata from GET /model-info.
No model loading. No hardcoded metadata.
"""
from __future__ import annotations

import streamlit as st

from api import HitRadarAPIClient
from api.exceptions import APIClientError
from core.config import get_settings
from core.session import init_session_state
from components.error_states import render_error


init_session_state()
settings = get_settings()
client = HitRadarAPIClient(
    base_url=settings.backend_base_url,
    connect_timeout=settings.connect_timeout,
    read_timeout=settings.read_timeout,
)


def _metric_card(label: str, value: str, help_text: str = "") -> None:
    st.metric(label=label, value=value, help=help_text)


# ── Page ───────────────────────────────────────────────────────────────────

st.header("ℹ️ Model Information")

# ── Fetch ─────────────────────────────────────────────────────────────────

try:
    info = client.get_model_info()
except APIClientError as e:
    render_error(e)
    st.stop()

# Cache for Home page
st.session_state["cached_model_info"] = info.to_dict()

# ── Identity ──────────────────────────────────────────────────────────────

st.subheader("Model Identity")
id_col1, id_col2, id_col3 = st.columns(3)
with id_col1:
    st.metric("Model ID", info.model_id)
with id_col2:
    st.metric("Family", info.model_family)
with id_col3:
    st.metric("Version", info.model_version)

st.divider()

# ── Versions ──────────────────────────────────────────────────────────────

st.subheader("Version Information")
ver_col1, ver_col2, ver_col3 = st.columns(3)
with ver_col1:
    st.metric("Data Version", info.data_version)
with ver_col2:
    st.metric("Package Version", info.package_version)
with ver_col3:
    st.metric("API Timestamp", info.timestamp[:10] if info.timestamp else "N/A")

if info.training_date:
    st.caption(f"**Training Date:** {info.training_date}")

st.divider()

# ── Training Data ─────────────────────────────────────────────────────────

st.subheader("Training Data")
st.caption(
    f"**Feature Set:** {info.feature_set}  "
    f"*(selected features from canonical 18)*"
)

st.divider()

# ── Evaluation Metrics ────────────────────────────────────────────────────

st.subheader("Evaluation Metrics")

st.caption(
    "Metrics computed on the held-out test set. "
    "These measure how well the model fits the data — they are **not accuracy**."
)

metrics = getattr(info, "metrics", None)
if metrics and (metrics.MAE is not None or metrics.RMSE is not None or metrics.R2 is not None):
    mae_col, rmse_col, r2_col = st.columns(3)
    with mae_col:
        st.metric(
            "MAE",
            f"{metrics.MAE:.2f}" if metrics.MAE is not None else "N/A",
            help="Mean Absolute Error — average absolute difference between predicted and actual popularity scores (lower = better).",
        )
    with rmse_col:
        st.metric(
            "RMSE",
            f"{metrics.RMSE:.2f}" if metrics.RMSE is not None else "N/A",
            help="Root Mean Squared Error — penalizes large errors more than MAE (lower = better).",
        )
    with r2_col:
        st.metric(
            "R²",
            f"{metrics.R2:.3f}" if metrics.R2 is not None else "N/A",
            help="R-squared — proportion of variance explained. 1.0 = perfect; 0.0 = predicting the mean; can be negative.",
        )
else:
    st.info(
        "📊 Detailed evaluation metrics (MAE, RMSE, R²) are available in "
        "the EPIC 2 model evaluation reports. "
        "Contact the project maintainer for access."
    )

st.divider()

# ── Explainability ─────────────────────────────────────────────────────────

st.subheader("Explainability")
st.markdown(
    "- **SHAP Explanations:** Available via the **Explain** page\n"
    "- **What-If Simulator:** Available via the **What-If** page\n"
    "- **Global Feature Importance:** Available in `7.ML/7.9.explainability/global/`"
)

st.divider()

# ── Limitations ──────────────────────────────────────────────────────────

st.subheader("Model Limitations")

st.warning(
    "⚠️ **Important:** This model is a **decision-support and demonstration tool**. "
    "Predictions reflect patterns in the training data and may contain biases. "
    "See the **Limitations** page for full details."
)

st.markdown(
    "- This is a **regression model** — it outputs a popularity score, not a probability\n"
    "- Predictions are **not guarantees** of a song's commercial success\n"
    "- The model was trained on a specific Spotify-derived dataset — "
    "it may not generalize to other markets or time periods\n"
    "- SHAP values describe **model behavior**, not causal effects"
)

st.caption(
    f"Request ID: `{info.request_id or 'N/A'}`"
)

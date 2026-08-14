"""
Prediction Result Component — Feature 3.3 Phase 2.

Renders a parsed PredictResponse.
No network calls. No model loading. No SHAP computation.
"""
from __future__ import annotations

import streamlit as st

from api.models import PredictResponse


def render_prediction_result(result: PredictResponse) -> None:
    """
    Render a prediction result from the API.

    Displays:
    - Primary score (display value)
    - Score range context
    - Raw / clipped values
    - Model metadata
    - Warnings if any
    - Request ID for debug

    Never interprets the score as a probability.
    """
    st.subheader("Prediction Result")

    # Primary display score
    score = result.prediction_display
    st.metric(
        label="Predicted Popularity",
        value=f"{score}",
        help="Model's popularity score on a 0–100 scale. Higher = more popular.",
    )

    # Score range note
    st.caption("Score range: 0–100 (clipped)")

    # Raw vs clipped — shown only if they differ
    if result.prediction_raw != result.prediction_clipped:
        col_raw, col_clip = st.columns(2)
        with col_raw:
            st.metric("Raw Score", f"{result.prediction_raw:.2f}")
        with col_clip:
            st.metric("Clipped Score", f"{result.prediction_clipped:.2f}")

    st.divider()

    # Metadata row
    meta_col1, meta_col2, meta_col3 = st.columns(3)
    with meta_col1:
        st.caption(f"**Model ID:** {result.model_id}")
    with meta_col2:
        st.caption(f"**Version:** {result.model_version}")
    with meta_col3:
        st.caption(f"**Request ID:** `{result.request_id or 'N/A'}`")

    # Status badge
    status_label = result.status.upper()
    if result.status.upper() == "SUCCESS":
        st.success(f"Status: {status_label}")
    else:
        st.info(f"Status: {status_label}")

    # Warnings from the backend
    if result.warnings:
        render_prediction_warnings(result.warnings)


def render_prediction_warnings(warnings: list[str]) -> None:
    """Render a list of backend-returned warnings."""
    for w in warnings:
        st.warning(f"⚠️ {w}")

"""
SHAP Explanation Component — Feature 3.3 Phase 2.

Renders an ExplainResponse.
No SHAP computation in frontend. No causal claims.
"""
from __future__ import annotations

import streamlit as st

from api.models import ExplainResponse


def render_shap_explanation(result: ExplainResponse) -> None:
    """
    Render SHAP explanation from the API.

    Displays:
    - Prediction score
    - Base value
    - Top feature contributions (positive and negative)
    - Attribution chart (horizontal bars)

    SHAP describes model behavior — NOT causal relationships.
    """
    st.subheader("Prediction Explanation (SHAP)")

    # Attribution caption — must appear on every render
    st.info(
        "ℹ️ SHAP explains how the model arrived at this prediction. "
        "It describes **model behavior**, not causal relationships."
    )

    # Score summary
    score_col, base_col = st.columns(2)
    with score_col:
        st.metric("Prediction", f"{result.prediction:.1f}")
    with base_col:
        st.metric("Base Value", f"{result.base_value:.1f}")

    st.divider()

    # Contributions table
    if result.contributions:
        _render_contribution_table(result.contributions)
    else:
        st.info("No contribution data available.")

    # Request ID
    st.caption(f"Request ID: `{result.request_id or 'N/A'}`")


def _render_contribution_table(contributions: list[dict]) -> None:
    """Render contributions as a sorted table with direction icons."""
    # Sort: positive first, then negative
    sorted_contribs = sorted(
        contributions,
        key=lambda x: x.get("contribution", 0),
        reverse=True,
    )

    table_data = []
    for c in sorted_contribs:
        contrib = c.get("contribution", 0)
        direction = "🔺" if contrib > 0 else "🔻" if contrib < 0 else "➖"
        table_data.append({
            "Feature": c.get("feature", ""),
            "Value": c.get("value", ""),
            "Direction": direction,
            "Contribution": f"{contrib:+.2f}",
        })

    st.dataframe(table_data, use_container_width=True, hide_index=True)


def render_shap_empty_state() -> None:
    """Render guidance when no explanation is available."""
    st.info(
        "📋 **SHAP Explanation**  \n"
        "Enter song features and click **Explain** to see how each feature "
        "influenced the model's prediction."
    )
    st.caption(
        "SHAP values show feature importance, not causation."
    )

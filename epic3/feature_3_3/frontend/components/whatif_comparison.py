"""
What-If Comparison Component — Feature 3.3 Phase 2.

Renders a WhatIfResponse.
No backend calls. No model loading. No causal claims.
"""
from __future__ import annotations

import streamlit as st

from api.models import WhatIfResponse


def render_whatif_comparison(result: WhatIfResponse) -> None:
    """
    Render what-if scenario comparison from the API.

    Displays:
    - Prediction before (baseline)
    - Prediction after (modified)
    - Delta (change in model prediction)
    - Changed fields with before/after values

    The delta shows how the model predicts differently — NOT actual effect.
    """
    st.subheader("What-If Comparison")

    # Attribution note
    st.info(
        "ℹ️ This shows how the **model's prediction** changes, not an actual effect. "
        "SHAP values describe model behavior, not causal relationships."
    )

    # Score comparison
    before = result.prediction_before
    after = result.prediction_after
    delta = result.delta

    col_before, col_delta, col_after = st.columns(3)
    with col_before:
        st.metric("Before", f"{before:.1f}")
    with col_after:
        st.metric("After", f"{after:.1f}")
    with col_delta:
        # Delta with semantic arrow
        arrow = "▲" if delta > 0 else "▼" if delta < 0 else "➖"
        st.metric(
            "Change",
            f"{arrow} {abs(delta):.1f}",
            help="Change in model's predicted popularity score",
        )

    st.divider()

    # Direction summary
    if delta > 0:
        st.success(f"The model's prediction increased by **{delta:.1f}** points.")
    elif delta < 0:
        st.warning(f"The model's prediction decreased by **{abs(delta):.1f}** points.")
    else:
        st.info("No change in the model's prediction.")

    # Changed fields
    if result.changed_fields:
        st.markdown("**Changed Features:**")
        for field in result.changed_fields:
            st.markdown(f"- `{field}`")
    else:
        st.info("No fields were changed in this scenario.")

    # Request ID
    st.caption(f"Request ID: `{result.request_id or 'N/A'}`")


def render_whatif_empty_state() -> None:
    """Render guidance when no comparison is available."""
    st.info(
        "📋 **What-If Simulator**  \n"
        "1. Enter baseline song features on the **Predict** page and submit.  \n"
        "2. Return here, adjust features, and click **Compare** to see "
        "how the model's prediction changes."
    )
    st.caption(
        "Comparisons show model behavior, not causation."
    )

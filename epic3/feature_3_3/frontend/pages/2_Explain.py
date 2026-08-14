"""
SHAP Explanation Page — Feature 3.3 Phase 4.

Flow:
  Load cached input → POST /explain → render_shap_explanation.

NO direct SHAP computation. NO SHAP artifact access.
"""
from __future__ import annotations

import streamlit as st

from api import HitRadarAPIClient
from api.exceptions import APIClientError
from core.config import get_settings
from core.session import init_session_state
from components.shap_explanation import render_shap_explanation, render_shap_empty_state
from components.error_states import with_loading


init_session_state()
settings = get_settings()
client = HitRadarAPIClient(
    base_url=settings.backend_base_url,
    connect_timeout=settings.connect_timeout,
    read_timeout=settings.read_timeout,
)


def _get_baseline_input() -> dict | None:
    """Return cached prediction input if available."""
    return st.session_state.get("current_prediction_input") or None


def _version_match() -> bool:
    """Check if cached result version matches current model."""
    cached = st.session_state.get("current_prediction_result", {})
    if not cached:
        return True
    cached_version = cached.get("model_version", "")
    try:
        current = client.get_model_info()
        current_version = current.model_version
        st.session_state["cached_model_info"] = current.to_dict()
        return cached_version == current_version
    except APIClientError:
        return True  # assume match if can't check


# ── Page ───────────────────────────────────────────────────────────────────

st.header("🔍 SHAP Explanation")

st.info(
    "ℹ️ **How it works:** Enter song features on the **Predict** page first, "
    "then return here to see which features drove that prediction. "
    "SHAP values are computed by the backend."
)

# ── Baseline input ───────────────────────────────────────────────────────

baseline_input = _get_baseline_input()

if not baseline_input:
    render_shap_empty_state()
    st.stop()

# ── Version warning ────────────────────────────────────────────────────────

if not _version_match():
    st.warning(
        "⚠️ The cached prediction was made with a different model version. "
        "Results below may not reflect the current model. "
        "Please re-run prediction first."
    )

# ── Show current input summary ───────────────────────────────────────────

st.markdown("### Current Prediction Input")

input_cols = st.columns(3)
short_fields = ["release_year", "danceability", "energy", "valence", "tempo", "explicit"]
for i, field_name in enumerate(short_fields):
    if field_name in baseline_input:
        val = baseline_input[field_name]
        with input_cols[i % 3]:
            st.caption(f"**{field_name}:** {val}")

with st.expander("Show all 18 input fields"):
    for k, v in sorted(baseline_input.items()):
        st.write(f"- **{k}:** {v}")

st.divider()

# ── Call /explain ───────────────────────────────────────────────────────

result = with_loading(
    "Generating SHAP explanation...",
    client.explain,
    baseline_input,
)

if result:
    # Save to session
    st.session_state["current_explanation"] = {
        "prediction": result.prediction,
        "base_value": result.base_value,
        "contributions": result.contributions,
        "request_id": result.request_id,
    }

    st.divider()
    render_shap_explanation(result)

    st.divider()

    # Attribution reminder
    st.caption(
        "⚠️ SHAP values show how the model produced this prediction. "
        "They describe **model behavior**, not causal relationships."
    )

    # Navigation CTA
    st.info("💡 Try the **What-If** page to see how changing features affects the prediction.")

"""
Session State Contract — Feature 3.3.

Defines canonical keys for Streamlit session state.
No model objects or secrets are stored here.
"""
from __future__ import annotations

import streamlit as st

# ── Canonical Session Keys ───────────────────────────────────────────────────────

SESSION_KEYS = {
    # Backend connectivity
    "backend_status": str,      # "Connected" | "Degraded" | "Unavailable"
    "latest_request_id": str,   # X-Request-ID from last API call

    # Prediction
    "current_prediction_input": dict,   # PredictRequest as dict
    "current_prediction_result": dict,  # Raw API response

    # Explanation
    "current_explanation": dict,        # ExplainResponse as dict

    # What-If
    "current_whatif": dict,             # WhatIfResponse as dict
    "whatif_base_prediction": float,    # Cached base prediction for delta display

    # Model info (cached)
    "cached_model_info": dict,
    "cached_features": dict,

    # UI state
    "form_defaults_loaded": bool,
}


def init_session_state() -> None:
    """Initialize all canonical session state keys with defaults."""
    defaults = {
        "backend_status": "Unknown",
        "latest_request_id": "",
        "current_prediction_input": {},
        "current_prediction_result": {},
        "current_explanation": {},
        "current_whatif": {},
        "whatif_base_prediction": 0.0,
        "cached_model_info": {},
        "cached_features": {},
        "form_defaults_loaded": False,
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def clear_prediction_state() -> None:
    """Clear all prediction-related session state."""
    st.session_state["current_prediction_input"] = {}
    st.session_state["current_prediction_result"] = {}
    st.session_state["current_explanation"] = {}
    st.session_state["current_whatif"] = {}
    st.session_state["whatif_base_prediction"] = 0.0

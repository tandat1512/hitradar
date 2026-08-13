"""
Predict Popularity Page — Feature 3.3 Phase 3.

End-to-end workflow:
  User form → validation → POST /predict → result component → errors.

Architecture:
  Page → API Client → FastAPI Backend.
  NO direct model access.
"""
from __future__ import annotations

import streamlit as st

from api import HitRadarAPIClient
from api.exceptions import APIClientError
from core.config import get_settings
from core.session import init_session_state
from core.navigation import PAGES
from components.predict_form import render_predict_form
from components.prediction_result import render_prediction_result
from components.error_states import render_error, with_loading


# ── Page State ───────────────────────────────────────────────────────────────

init_session_state()

settings = get_settings()
client = HitRadarAPIClient(
    base_url=settings.backend_base_url,
    connect_timeout=settings.connect_timeout,
    read_timeout=settings.read_timeout,
)


# ── Page ───────────────────────────────────────────────────────────────────

st.header("🎯 Predict Song Popularity")

# ── Load features for form ────────────────────────────────────────────────

if "cached_features" not in st.session_state or not st.session_state["cached_features"]:
    with st.spinner("Loading feature definitions..."):
        try:
            features_resp = client.get_features()
            st.session_state["cached_features"] = {
                "canonical_fields": [
                    {"name": f["name"], "data_type": f.get("data_type", "number"),
                     "minimum": f.get("minimum"), "maximum": f.get("maximum"),
                     "allowed_categories": f.get("allowed_categories"),
                     "default_policy": f.get("default_policy", "PIPELINE_IMPUTE")}
                    for f in features_resp.canonical_fields
                ],
                "selected_features": features_resp.selected_features,
                "total_input_fields": features_resp.total_input_fields,
                "total_selected_features": features_resp.total_selected_features,
            }
        except APIClientError as e:
            st.session_state["cached_features"] = {}
            render_error(e)
            st.stop()

cached = st.session_state.get("cached_features", {})
if not cached:
    st.info("Feature definitions could not be loaded. The backend may be unavailable.")
    st.stop()

# ── Render form ──────────────────────────────────────────────────────────

from api.models import PredictResponse

# Reconstruct a lightweight FeaturesResponse for the form
class _CachedFeatures:
    def __init__(self, data):
        self.canonical_fields = data.get("canonical_fields", [])
        self.selected_features = data.get("selected_features", [])
        self.total_input_fields = data.get("total_input_fields", 0)
        self.total_selected_features = data.get("total_selected_features", 0)
        self.request_id = None

features = _CachedFeatures(cached)

payload = render_predict_form(features)

# ── Submit handler ───────────────────────────────────────────────────────

if payload is not None:
    # Guard: no 'target' field in payload
    if "target" in payload:
        st.error("Invalid: 'target' field must not be in prediction request.")
        st.stop()

    result = with_loading(
        "Predicting popularity...",
        client.predict,
        payload,
    )

    if result:
        # Save to session state for SHAP / What-If pages
        st.session_state["current_prediction_input"] = payload
        st.session_state["current_prediction_result"] = {
            "prediction_raw": result.prediction_raw,
            "prediction_clipped": result.prediction_clipped,
            "prediction_display": result.prediction_display,
            "status": result.status,
            "warnings": result.warnings,
            "model_id": result.model_id,
            "model_version": result.model_version,
            "package_version": result.package_version,
            "request_id": result.request_id,
        }
        st.session_state["latest_request_id"] = result.request_id or ""

        # Cache model info if not cached
        if not st.session_state.get("cached_model_info"):
            try:
                mi = client.get_model_info()
                st.session_state["cached_model_info"] = mi.to_dict()
            except APIClientError:
                pass

        st.divider()
        st.markdown("### Result")
        render_prediction_result(result)

        st.divider()

        # Navigation CTAs
        cta_col1, cta_col2 = st.columns(2)
        with cta_col1:
            if PAGES.get("🔍 Explain", {}).get("requires_backend", False):
                st.info("💡 Navigate to **🔍 Explain** to see feature contributions.")
        with cta_col2:
            if PAGES.get("🔄 What-If", {}).get("requires_backend", False):
                st.info("💡 Navigate to **🔄 What-If** to compare scenarios.")

elif not payload and not st.session_state.get("current_prediction_result"):
    # Empty state
    st.info(
        "📋 Enter song audio features above and click **Predict Popularity** "
        "to get a score from the model."
    )
    st.caption("All 18 features are required. Default values are shown in each field.")

elif st.session_state.get("current_prediction_result"):
    # Show last result if available
    prev = st.session_state["current_prediction_result"]
    st.divider()
    st.markdown("### Previous Result")
    prev_resp = PredictResponse(prev)
    render_prediction_result(prev_resp)
    st.caption("Submit the form again for a new prediction.")

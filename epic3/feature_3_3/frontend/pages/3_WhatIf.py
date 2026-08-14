"""
What-If Simulator Page — Feature 3.3 Phase 4.

Flow:
  Load baseline from session → user modifies fields →
  POST /what-if → render comparison.

NO direct model prediction. NO causal claims.
"""
from __future__ import annotations

import streamlit as st

from api import HitRadarAPIClient
from api.exceptions import APIClientError
from core.config import get_settings
from core.session import init_session_state
from components.whatif_comparison import render_whatif_comparison, render_whatif_empty_state
from components.error_states import with_loading


init_session_state()
settings = get_settings()
client = HitRadarAPIClient(
    base_url=settings.backend_base_url,
    connect_timeout=settings.connect_timeout,
    read_timeout=settings.read_timeout,
)


# ── Helpers ──────────────────────────────────────────────────────────────

def _get_baseline() -> tuple[dict, float] | None:
    """Return (baseline_input, baseline_score) or None."""
    inp = st.session_state.get("current_prediction_input")
    res = st.session_state.get("current_prediction_result")
    if not inp:
        return None
    score = res.get("prediction_display", 0) if res else 0
    return inp, score


def _load_features() -> dict:
    """Load feature definitions from session or API."""
    cached = st.session_state.get("cached_features", {})
    if cached:
        return cached
    with st.spinner("Loading feature definitions..."):
        try:
            fresp = client.get_features()
            cached = {
                "canonical_fields": [
                    {"name": f["name"], "data_type": f.get("data_type", "number"),
                     "minimum": f.get("minimum"), "maximum": f.get("maximum"),
                     "allowed_categories": f.get("allowed_categories"),
                     "default_policy": f.get("default_policy", "PIPELINE_IMPUTE")}
                    for f in fresp.canonical_fields
                ],
                "selected_features": fresp.selected_features,
            }
            st.session_state["cached_features"] = cached
            return cached
        except APIClientError:
            return {"canonical_fields": []}


def _get_modifiable_fields(fields: list[dict]) -> list[dict]:
    """Return fields the user can modify for what-if (excludes non-input fields)."""
    excluded = {"target", "model_version_override", "selected_features", "request_id",
                "model_path", "feature_set"}
    return [f for f in fields if f.get("name") not in excluded]


# ── Page ───────────────────────────────────────────────────────────────────

st.header("🔄 What-If Simulator")

st.info(
    "ℹ️ **How it works:** Start from your last prediction, "
    "modify one or more features, and compare how the model's "
    "prediction changes. Modifications are hypothetical — "
    "they describe the model's behavior, not real-world effects."
)

# ── Baseline check ───────────────────────────────────────────────────────

baseline = _get_baseline()

if not baseline:
    render_whatif_empty_state()
    st.stop()

baseline_input, baseline_score = baseline

# ── Show baseline ────────────────────────────────────────────────────────

st.markdown("### Baseline Prediction")
baseline_cols = st.columns(3)
with baseline_cols[0]:
    st.metric("Score", f"{baseline_score}")
with baseline_cols[1]:
    st.caption(f"**Input fields:** {len(baseline_input)}")
with baseline_cols[2]:
    model_ver = st.session_state.get("current_prediction_result", {}).get("model_version", "N/A")
    st.caption(f"**Model version:** {model_ver}")

st.divider()

# ── Modification form ───────────────────────────────────────────────────

features = _load_features()
modifiable = _get_modifiable_fields(features.get("canonical_fields", []))

if not modifiable:
    st.warning("Feature definitions could not be loaded. Please visit the Predict page first.")
    st.stop()

# User selects which field to modify
st.markdown("### Modify a Feature")

modified_fields = st.multiselect(
    "Select features to modify:",
    options=[f["name"] for f in modifiable],
    default=[],
    help="Pick one or more features to change. The baseline values are pre-filled.",
)

# Build changed_features dict from sliders/inputs
changed_features: dict = {}

if modified_fields:
    with st.form(key="whatif_modify_form", clear_on_submit=False):
        update_cols = st.columns(min(3, len(modified_fields)))
        for i, fname in enumerate(modified_fields):
            field = next((f for f in modifiable if f["name"] == fname), None)
            if not field:
                continue

            dtype = field.get("data_type", "number")
            min_v = field.get("minimum")
            max_v = field.get("maximum")
            allowed = field.get("allowed_categories", [])
            baseline_val = baseline_input.get(fname, 0)

            with update_cols[i % 3]:
                if allowed:
                    options = allowed if baseline_val in allowed else [baseline_val] + allowed
                    new_val = st.selectbox(
                        fname,
                        options=options,
                        index=options.index(baseline_val) if baseline_val in options else 0,
                        key=f"wi_{fname}",
                    )
                elif dtype == "boolean":
                    new_val = st.checkbox(
                        fname,
                        value=bool(baseline_val),
                        key=f"wi_{fname}",
                    )
                elif dtype == "integer" and min_v is not None and max_v is not None:
                    new_val = st.number_input(
                        fname,
                        min_value=int(min_v),
                        max_value=int(max_v),
                        value=int(baseline_val),
                        key=f"wi_{fname}",
                    )
                elif min_v is not None and max_v is not None:
                    new_val = st.slider(
                        fname,
                        min_value=float(min_v),
                        max_value=float(max_v),
                        value=float(baseline_val),
                        step=0.01,
                        key=f"wi_{fname}",
                    )
                else:
                    new_val = st.text_input(
                        fname,
                        value=str(baseline_val),
                        key=f"wi_{fname}",
                    )

                if new_val != baseline_val:
                    changed_features[fname] = new_val

        st.divider()
        submitted = st.form_submit_button(
            "🔄 Compare Predictions",
            use_container_width=True,
        )

        if submitted and changed_features:
            result = with_loading(
                "Comparing predictions...",
                client.what_if,
                baseline_input,
                changed_features,
            )

            if result:
                st.session_state["current_whatif"] = {
                    "prediction_before": result.prediction_before,
                    "prediction_after": result.prediction_after,
                    "delta": result.delta,
                    "changed_fields": result.changed_fields,
                    "request_id": result.request_id,
                }

                st.divider()
                render_whatif_comparison(result)

elif not modified_fields:
    st.info("👆 Select one or more features above to compare scenarios.")

# ── Reset ────────────────────────────────────────────────────────────────

if st.button("🔄 Reset modifications"):
    st.session_state.pop("current_whatif", None)
    st.rerun()

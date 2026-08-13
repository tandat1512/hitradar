"""
Home — Project Overview — Feature 3.3 Phase 3.

Shows project overview and backend status.
Does not depend on model being loaded.
"""
from __future__ import annotations

import streamlit as st

# ── Backend status helper ───────────────────────────────────────────────────────

def _backend_status() -> str:
    if "backend_status" not in st.session_state:
        return "Unknown"
    return st.session_state["backend_status"]


# ── Main ──────────────────────────────────────────────────────────────────────

st.subheader("🎵 HitRadar Pro — AI Music Popularity Prediction")

col_intro, col_nav = st.columns([3, 1])

with col_intro:
    st.markdown(
        "**HitRadar Pro** is a student research project that predicts song popularity "
        "scores (0–100) using a trained XGBoost model and audio features from Spotify data. "
        "Predictions are for demonstration and research purposes only."
    )

with col_nav:
    st.caption(f"**Backend:** {_backend_status()}")
    if _backend_status() != "Connected":
        if st.button("🔄 Retry connection"):
            st.rerun()

st.divider()

# ── Project Overview ───────────────────────────────────────────────────────────

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📋 What It Does")
    st.markdown(
        "- Enter song audio features (danceability, energy, tempo, etc.)\n"
        "- Get a **predicted popularity score** from a trained ML model\n"
        "- See which features most influenced the prediction (SHAP)\n"
        "- Compare scenarios: what if energy were higher?"
    )

with col_right:
    st.markdown("### 🔬 The Model")
    st.markdown(
        "- Algorithm: XGBoost (gradient boosting)\n"
        "- Trained on a curated Spotify dataset\n"
        "- 18 audio features as inputs\n"
        "- Predictions are **demonstration only** — not commercial"
    )

st.divider()

# ── Navigation Guide ──────────────────────────────────────────────────────────

st.markdown("### 🧭 Navigate")

nav_cols = st.columns(3)

nav_items = [
    ("🎯", "Predict", "predict", "Enter features → get a popularity score"),
    ("🔍", "Explain", "explain", "See which features drove the prediction"),
    ("🔄", "What-If", "whatif", "Compare two scenarios side by side"),
]

for i, (icon, title, page_key, desc) in enumerate(nav_items[:3]):
    with nav_cols[i]:
        st.markdown(f"**{icon} {title}**")
        st.caption(desc)

st.divider()

# ── Model Info ────────────────────────────────────────────────────────────────

st.markdown("### ℹ️ Model Information")

# Try to show model info if available from session
model_info = st.session_state.get("cached_model_info", {})
if model_info:
    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.metric("Model ID", model_info.get("model_id", "N/A"))
    with info_col2:
        st.metric("Family", model_info.get("model_family", "N/A"))
    with info_col3:
        st.metric("Version", model_info.get("model_version", "N/A"))
else:
    st.info(
        "ℹ️ Model information will appear here once the Predict page is visited. "
        "The backend must be running and connected."
    )

st.divider()

# ── Limitations Warning ─────────────────────────────────────────────────────────

st.warning(
    "⚠️ **Important:** This is a student research prototype. "
    "Predictions reflect the model's training data and may contain biases. "
    "Do not use for commercial or critical decisions. "
    "See the **Limitations** page for full details."
)

"""
Limitations & Responsible Use — Feature 3.3 Phase 6.

Sources: EPIC 2 ML Report, Model Card, Feature 3.2 model-info,
Product Contract, EPIC 3 requirements.

No unsupported claims. No causal attributions.
"""
from __future__ import annotations

import streamlit as st

st.header("⚠️ Limitations & Responsible Use")

# ── Project Context ─────────────────────────────────────────────────────────

st.markdown(
    "**HitRadar Pro** is a **student research prototype** developed as part of a "
    "university project. The model was trained on a curated Spotify dataset "
    "and is intended for demonstration and educational purposes only. "
    "It must not be used for commercial or critical decision-making."
)

st.divider()

# ── Intended vs Non-Intended Use ─────────────────────────────────────────────

st.subheader("Intended Use")
st.markdown(
    "- Exploring how audio features correlate with popularity scores in the training dataset\n"
    "- Understanding ML model behavior (XGBoost regression)\n"
    "- Learning about SHAP-based feature explanations\n"
    "- Research and educational demonstrations"
)

st.subheader("Non-Intended Use")
st.markdown(
    "- Predicting commercial success of real songs\n"
    "- Making music industry investment or A&R decisions\n"
    "- Claims about causation: *\"this feature causes songs to be popular\"*\n"
    "- Replacing human musical judgment or industry expertise\n"
    "- Production or commercial music pipelines"
)

st.divider()

# ── What the Model Outputs ───────────────────────────────────────────────────

st.subheader("What the Model Outputs")
st.markdown(
    "The model outputs a **popularity score (0–100)** — a regression output. "
    "This score is:\n"
    "- **Not a probability** of a song being a \"hit\"\n"
    "- **Not a guarantee** of commercial success\n"
    "- **Not causally meaningful** — SHAP values describe how the model "
    "processed the inputs, not why a song would succeed"
)

st.divider()

# ── Data Limitations ─────────────────────────────────────────────────────────

st.subheader("Data Limitations")
st.markdown(
    "- **Source:** A curated Spotify-derived dataset — not a comprehensive "
    "sample of all music globally or across all markets\n"
    "- **Temporal coverage:** The current ML-ready dataset covers 1900–2021. "
    "The model was trained on data that may not reflect current music trends\n"
    "- **Popularity definition:** The `popularity` metric in the dataset is a "
    "Spotify platform metric (stream/engagement-based), not a universal "
    "measure of musical quality or commercial success\n"
    "- **Geographic bias:** Music from certain regions or markets may be "
    "over- or under-represented"
)

st.divider()

# ── Model Performance ─────────────────────────────────────────────────────────

st.subheader("Model Performance")
st.markdown(
    "Evaluation metrics (from test set):\n"
    "- **MAE:** Mean Absolute Error — typical prediction error in popularity points\n"
    "- **RMSE:** Root Mean Squared Error — penalizes large errors\n"
    "- **R²:** Proportion of variance explained — can be low or negative\n\n"
    "These metrics describe **model fit to the training data**, not prediction reliability. "
    "See the **Model Info** page for current metric values."
)

st.divider()

# ── SHAP Explanations ───────────────────────────────────────────────────────

st.subheader("SHAP Explanations")
st.markdown(
    "SHAP values show **how the model weighed each input feature** to arrive "
    "at its prediction. They describe:\n"
    "- Feature importance in the context of this specific prediction\n"
    "- Direction of influence (positive or negative contribution)\n\n"
    "SHAP values do NOT establish:\n"
    "- That a feature *causes* popularity to change\n"
    "- That modifying a feature will change real-world outcomes\n"
    "- That the training data relationship holds for new songs"
)

st.divider()

# ── What-If Simulations ──────────────────────────────────────────────────────

st.subheader("What-If Simulator")

st.markdown(
    "The **Music Trends** page reads from read-only dataset artifacts "
    "(`ml_ready_dataset.csv`, `yearly_evaluation.csv`) via the local filesystem. "
    "This means both the Streamlit frontend and the data files must be deployed "
    "on the same server or filesystem. The Trends page does not call the FastAPI backend. "
    "If deploying frontend and backend as separate services, the Trends page "
    "will need a dedicated API endpoint to serve aggregated trend data."
)
st.markdown(
    "The What-If Simulator shows how the **model's prediction** changes when "
    "you modify input features. It does NOT show:\n"
    "- How the actual popularity of a song would change\n"
    "- Causal effects of feature changes\n"
    "- Real-world music industry outcomes\n\n"
    "Use it to explore model behavior, not to plan production decisions."
)

st.divider()

# ── Bias & Fairness ───────────────────────────────────────────────────────────

st.subheader("Bias & Fairness")
st.markdown(
    "- The model may reflect and amplify biases present in the training data\n"
    "- Historical popularity data may correlate with marketing spend, platform "
    "visibility, and other non-musical factors\n"
    "- Audio features alone cannot capture artistic, cultural, or contextual "
    "factors that contribute to a song's success\n"
    "- Results should not be used to make judgments about musical quality"
)

st.divider()

# ── Human Judgment Requirement ────────────────────────────────────────────────

st.subheader("Human Judgment Required")
st.markdown(
    "Any use of this application must involve:\n"
    "- Human review of predictions and explanations\n"
    "- Consideration of factors outside the model's feature set\n"
    "- Explicit acknowledgment that predictions are model outputs, not facts\n"
    "- Awareness that model behavior may change with retraining or version updates"
)

st.divider()

# ── No Causal Interpretation ──────────────────────────────────────────────────

st.subheader("No Causal Interpretation")
st.warning(
    "⚠️ **Important:** This model captures **correlational patterns** in its "
    "training data. Correlational does not mean causal. "
    "You cannot conclude that increasing a feature (e.g., danceability) "
    "will causally increase a song's popularity. "
    "SHAP values and What-If results describe model behavior only."
)

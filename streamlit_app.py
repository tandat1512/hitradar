"""Four-tab Streamlit client for HitRadar Pro's deployed capabilities."""

import json
from pathlib import Path
import sys

import requests
import streamlit as st


def find_project_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "4.MODELS").exists() and (candidate / "5.DATA").exists():
            return candidate
    raise RuntimeError("HitRadar project root was not found.")


PROJECT_ROOT = find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.prediction_policy import (  # noqa: E402
    FINAL_HOLDOUT_MAX_YEAR,
    EXTRAPOLATION_NOTE,
    OBSERVED_DATA_MAX_YEAR,
    PRODUCT_SUPPORT_END_YEAR,
    TRAIN_END_YEAR,
)

METRICS_PATH = PROJECT_ROOT / "4.MODELS" / "hitradar_popularity" / "final_test_metrics.json"
CLUSTER_META_PATH = PROJECT_ROOT / "4.MODELS" / "hitradar_secondary" / "cluster_metadata.json"
API_URL = "http://127.0.0.1:8000"


def track_inputs(prefix: str) -> dict:
    """Render raw-only inputs with unique keys for each tab."""
    c1, c2, c3 = st.columns(3)
    with c1:
        duration_min = st.number_input("Duration (minutes)", 0.1, 60.0, 3.5, key=f"{prefix}_duration")
        release_year = st.number_input("Release year", 1900, 2100, 2020, key=f"{prefix}_year")
        release_month = st.number_input("Release month", 1, 12, 6, key=f"{prefix}_month")
        release_precision = st.selectbox("Release precision", ["day", "month", "year"], key=f"{prefix}_precision")
        explicit = st.checkbox("Explicit", key=f"{prefix}_explicit")
        key = st.selectbox("Musical key", list(range(12)), key=f"{prefix}_key")
    with c2:
        danceability = st.slider("Danceability", 0.0, 1.0, 0.65, 0.01, key=f"{prefix}_dance")
        energy = st.slider("Energy", 0.0, 1.0, 0.70, 0.01, key=f"{prefix}_energy")
        valence = st.slider("Valence", 0.0, 1.0, 0.55, 0.01, key=f"{prefix}_valence")
        acousticness = st.slider("Acousticness", 0.0, 1.0, 0.20, 0.01, key=f"{prefix}_acoustic")
        instrumentalness = st.slider("Instrumentalness", 0.0, 1.0, 0.05, 0.01, key=f"{prefix}_instrumental")
        liveness = st.slider("Liveness", 0.0, 1.0, 0.15, 0.01, key=f"{prefix}_live")
    with c3:
        loudness = st.number_input("Loudness (dB)", -80.0, 10.0, -7.0, key=f"{prefix}_loud")
        speechiness = st.slider("Speechiness", 0.0, 1.0, 0.08, 0.01, key=f"{prefix}_speech")
        tempo = st.number_input("Tempo (BPM)", 1.0, 300.0, 120.0, key=f"{prefix}_tempo")
        time_signature = st.selectbox("Time signature", [1, 2, 3, 4, 5, 6, 7], index=3, key=f"{prefix}_signature")
        mode = st.selectbox("Mode", [0, 1], index=1, key=f"{prefix}_mode")
    return {
        "duration_min": duration_min, "explicit": explicit,
        "release_year": release_year, "release_month": release_month,
        "release_precision": release_precision, "danceability": danceability,
        "energy": energy, "key": key, "loudness": loudness, "mode": mode,
        "speechiness": speechiness, "acousticness": acousticness,
        "instrumentalness": instrumentalness, "liveness": liveness,
        "valence": valence, "tempo": tempo, "time_signature": time_signature,
    }


def call_api(method: str, path: str, **kwargs):
    response = requests.request(method, f"{API_URL}{path}", timeout=20, **kwargs)
    response.raise_for_status()
    return response.json()


def cluster_inputs() -> dict:
    """Render only the ten audio fields consumed by clustering."""
    c1, c2 = st.columns(2)
    with c1:
        duration_min = st.number_input("Cluster duration (minutes)", 0.1, 60.0, 3.5)
        danceability = st.slider("Cluster danceability", 0.0, 1.0, 0.65, 0.01)
        energy = st.slider("Cluster energy", 0.0, 1.0, 0.70, 0.01)
        loudness = st.number_input("Cluster loudness (dB)", -80.0, 10.0, -7.0)
        speechiness = st.slider("Cluster speechiness", 0.0, 1.0, 0.08, 0.01)
    with c2:
        acousticness = st.slider("Cluster acousticness", 0.0, 1.0, 0.20, 0.01)
        instrumentalness = st.slider("Cluster instrumentalness", 0.0, 1.0, 0.05, 0.01)
        liveness = st.slider("Cluster liveness", 0.0, 1.0, 0.15, 0.01)
        valence = st.slider("Cluster valence", 0.0, 1.0, 0.55, 0.01)
        tempo = st.number_input("Cluster tempo (BPM)", 1.0, 300.0, 120.0)
    return {
        "duration_min": duration_min, "danceability": danceability,
        "energy": energy, "loudness": loudness, "speechiness": speechiness,
        "acousticness": acousticness, "instrumentalness": instrumentalness,
        "liveness": liveness, "valence": valence, "tempo": tempo,
    }


st.set_page_config(page_title="HitRadar Pro", page_icon="🎵", layout="wide")
st.title("HitRadar Pro")
st.caption("Popularity prediction, audio clustering, and content-based song similarity.")

overview_tab, prediction_tab, cluster_tab, similar_tab = st.tabs(
    ["Overview", "Popularity Prediction", "Song Clustering", "Similar Songs"]
)

with overview_tab:
    st.subheader("Model overview")
    st.info(
        f"The popularity model was trained through {TRAIN_END_YEAR}. Its documented "
        f"product-support cutoff is {PRODUCT_SUPPORT_END_YEAR}; later releases remain "
        "available but are temporal extrapolations. Actual observed dataset/final-holdout "
        f"coverage ends in {OBSERVED_DATA_MAX_YEAR}/{FINAL_HOLDOUT_MAX_YEAR} respectively; "
        "row presence does not extend the product support guarantee."
    )
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        cols = st.columns(4)
        cols[0].metric("Locked experiment", metrics.get("selection_winner_experiment", "N/A"))
        cols[1].metric("Locked model", metrics.get("selection_winner_model", "N/A"))
        cols[2].metric("Production MAE", f"{metrics.get('clipped_test_metrics', {}).get('MAE', float('nan')):.3f}")
        cols[3].metric("Production RMSE", f"{metrics.get('clipped_test_metrics', {}).get('RMSE', float('nan')):.3f}")
        st.write("Prediction metrics are newly generated by Notebook 06 after the feature hotfix.")
    else:
        st.warning("Run Notebook 06 to create the final popularity artifact.")
    if CLUSTER_META_PATH.exists():
        cluster_meta = json.loads(CLUSTER_META_PATH.read_text(encoding="utf-8"))
        st.write(f"KMeans selected k = **{cluster_meta.get('chosen_k')}** using maximum sampled silhouette.")

with prediction_tab:
    st.subheader("Predict Spotify popularity")
    st.caption("Enter raw track attributes; the server creates the exact training features.")
    st.caption(
        f"Predictions after the {PRODUCT_SUPPORT_END_YEAR} product cutoff are allowed with an explicit temporal-extrapolation warning."
    )
    with st.form("prediction_form"):
        prediction_payload = track_inputs("prediction")
        predict_submitted = st.form_submit_button("Predict popularity", use_container_width=True)
    if prediction_payload["release_year"] > PRODUCT_SUPPORT_END_YEAR:
        st.warning(EXTRAPOLATION_NOTE)
    if predict_submitted:
        try:
            result = call_api("POST", "/predict", json=prediction_payload)
            st.success(f"Predicted popularity: {result['predicted_popularity']:.2f} / 100")
            st.json(result)
        except requests.RequestException as exc:
            st.error(f"FastAPI request failed: {exc}")

with cluster_tab:
    st.subheader("Assign an audio cluster")
    st.caption("Clustering uses audio content only—never target popularity or release time.")
    with st.form("cluster_form"):
        cluster_payload = cluster_inputs()
        cluster_submitted = st.form_submit_button("Find cluster", use_container_width=True)
    if cluster_submitted:
        try:
            result = call_api("POST", "/cluster", json=cluster_payload)
            st.success(f"Assigned cluster: {result['cluster']} of k={result['chosen_k']}")
            st.json(result)
        except requests.RequestException as exc:
            st.error(f"FastAPI request failed: {exc}")

with similar_tab:
    st.subheader("Find similar songs")
    st.caption("The local ML-ready source has track IDs but no track/artist names; no metadata is fabricated.")
    with st.form("similar_form"):
        track_id = st.text_input("Spotify track_id")
        n_results = st.slider("Number of recommendations", 1, 20, 5)
        recommend_submitted = st.form_submit_button("Find similar songs", use_container_width=True)
    if recommend_submitted:
        try:
            result = call_api("GET", f"/recommend/{track_id}", params={"n": n_results})
            st.dataframe(result["recommendations"], use_container_width=True)
            st.caption(result["metadata_note"])
        except requests.RequestException as exc:
            st.error(f"FastAPI request failed: {exc}")

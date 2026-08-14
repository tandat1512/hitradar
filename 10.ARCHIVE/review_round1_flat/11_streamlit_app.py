"""Streamlit client for the HitRadar FastAPI prediction endpoint."""

import json
from pathlib import Path

import requests
import streamlit as st


def find_project_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "4.MODELS").exists() and (candidate / "5.DATA").exists():
            return candidate
    raise RuntimeError("Không tìm thấy project root.")


PROJECT_ROOT = find_project_root()
METRICS_PATH = PROJECT_ROOT / "4.MODELS" / "hitradar_popularity" / "metrics.json"
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="HitRadar", page_icon="🎵", layout="wide")
st.title("HitRadar — Dự đoán Spotify Popularity")
st.caption("Người dùng nhập raw features; server tự tạo toàn bộ engineered features.")

if METRICS_PATH.exists():
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    cols = st.columns(4)
    cols[0].metric("Final model", metrics.get("final_model", "N/A"))
    cols[1].metric("Test MAE", f"{metrics.get('final_test_metrics', {}).get('MAE', float('nan')):.3f}")
    cols[2].metric("Test RMSE", f"{metrics.get('final_test_metrics', {}).get('RMSE', float('nan')):.3f}")
    cols[3].metric("Test R²", f"{metrics.get('final_test_metrics', {}).get('R2', float('nan')):.3f}")

with st.form("track_form"):
    c1, c2, c3 = st.columns(3)
    with c1:
        duration_min = st.number_input("Duration (minutes)", 0.1, 60.0, 3.5)
        release_year = st.number_input("Release year", 1900, 2100, 2020)
        release_month = st.number_input("Release month", 1, 12, 6)
        release_precision = st.selectbox("Release precision", ["day", "month", "year"])
        explicit = st.checkbox("Explicit")
        key = st.selectbox("Musical key", list(range(12)), index=0)
    with c2:
        danceability = st.slider("Danceability", 0.0, 1.0, 0.65, 0.01)
        energy = st.slider("Energy", 0.0, 1.0, 0.70, 0.01)
        valence = st.slider("Valence", 0.0, 1.0, 0.55, 0.01)
        acousticness = st.slider("Acousticness", 0.0, 1.0, 0.20, 0.01)
        instrumentalness = st.slider("Instrumentalness", 0.0, 1.0, 0.05, 0.01)
        liveness = st.slider("Liveness", 0.0, 1.0, 0.15, 0.01)
    with c3:
        loudness = st.number_input("Loudness (dB)", -80.0, 10.0, -7.0)
        speechiness = st.slider("Speechiness", 0.0, 1.0, 0.08, 0.01)
        tempo = st.number_input("Tempo (BPM)", 1.0, 300.0, 120.0)
        time_signature = st.selectbox("Time signature", [1, 2, 3, 4, 5, 6, 7], index=3)
        mode = st.selectbox("Mode", [0, 1], index=1)
    submitted = st.form_submit_button("Dự đoán popularity", use_container_width=True)

if submitted:
    payload = {
        "duration_min": duration_min,
        "explicit": explicit,
        "release_year": release_year,
        "release_month": release_month,
        "release_precision": release_precision,
        "danceability": danceability,
        "energy": energy,
        "key": key,
        "loudness": loudness,
        "mode": mode,
        "speechiness": speechiness,
        "acousticness": acousticness,
        "instrumentalness": instrumentalness,
        "liveness": liveness,
        "valence": valence,
        "tempo": tempo,
        "time_signature": time_signature,
    }
    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        st.success(f"Predicted popularity: {result['predicted_popularity']:.2f} / 100")
        st.write(f"Tier: **{result['popularity_tier']}**")
        st.json(result)
    except requests.RequestException as exc:
        st.error(f"Không gọi được FastAPI: {exc}")

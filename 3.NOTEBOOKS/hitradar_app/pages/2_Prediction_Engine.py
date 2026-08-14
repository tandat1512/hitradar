import streamlit as st
import requests
import time
import pandas as pd

st.markdown("## 🚀 HitRadar Prediction Engine")
st.markdown("Thiết lập các tham số để cấu hình vec-tơ đặc trưng đầu vào.")

st.markdown("---")
col_1, col_2, col_3 = st.columns(3)

with col_1:
    st.markdown("#### Metadata & Thời gian")
    release_year = st.slider("Năm phát hành", 1980, 2025, 2024)
    duration_min = st.slider("Thời lượng (phút)", 1.0, 10.0, 3.2, step=0.1)
    tempo = st.slider("Tốc độ Nhịp (BPM)", 50, 200, 122)
    time_signature = st.selectbox("Nhịp phách", [3, 4, 5], index=1)

with col_2:
    st.markdown("#### Động lực học (Dynamics)")
    danceability = st.slider("Danceability", 0.0, 1.0, 0.75, step=0.01)
    energy = st.slider("Energy", 0.0, 1.0, 0.85, step=0.01)
    valence = st.slider("Valence", 0.0, 1.0, 0.65, step=0.01)
    liveness = st.slider("Liveness", 0.0, 1.0, 0.10, step=0.01)

with col_3:
    st.markdown("#### Cấu trúc Âm thanh (Acoustics)")
    acousticness = st.slider("Acousticness", 0.0, 1.0, 0.15, step=0.01)
    instrumentalness = st.slider("Instrumentalness", 0.0, 1.0, 0.00, step=0.01)
    loudness = st.slider("Loudness (dB)", -25.0, 0.0, -5.5, step=0.5)

st.markdown("---")

if st.button("Tiến hành Phân tích (Run Inference)", use_container_width=True):
    payload = {
        "duration_min": duration_min, "release_year": release_year,
        "danceability": danceability, "energy": energy, "loudness": loudness,
        "acousticness": acousticness, "instrumentalness": instrumentalness,
        "liveness": liveness, "valence": valence, "tempo": tempo,
        "time_signature": time_signature
    }

    with st.spinner('Đang tính toán suy luận (Computing Inference)...'):
        time.sleep(0.5) 

        try:
            response = requests.post("http://localhost:8000/predict", json=payload)
            if response.status_code == 200:
                result = response.json()
                score = result['predicted_score']
                tier = result['classification']

                # Trực quan hóa KPI và Bar chart (Trực quan kết quả dự báo)
                st.success(f"### Kết quả Suy luận: {score:.2f} / 100")
                st.info(f"**Phân loại Cấp độ (Classification Tier):** {tier}")

                # Vẽ biểu đồ thanh ngang
                chart_data = pd.DataFrame(
                    {"Điểm số": [score, 100-score]},
                    index=["Popularity Potential", "Gap to max"]
                )
                st.bar_chart(chart_data, color="#8b5cf6")
            else:
                st.error("Lỗi từ Dịch vụ Hậu cảnh.")
        except requests.exceptions.ConnectionError:
            st.error("Lỗi Kết nối: Không thể thiết lập TCP connection với FastAPI. Đảm bảo port 8000 đang mở.")

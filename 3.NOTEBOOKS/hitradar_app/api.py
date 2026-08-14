from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np

app = FastAPI(title="HitRadar Inference API", version="1.0.0")

# --- Khởi tạo Khối Suy Luận ---
try:
    model = joblib.load("xgboost_model.pkl")
    scaler = joblib.load("scaler.pkl")
except Exception as e:
    raise RuntimeError(f"Lỗi tải mô hình tại API: {e}")

# --- Định nghĩa Lược đồ Dữ liệu Đầu vào (Schema Validation) ---
class TrackInput(BaseModel):
    duration_min: float = Field(..., ge=0.5, le=30.0)
    release_year: int = Field(..., ge=1900, le=2030)
    danceability: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    loudness: float = Field(..., ge=-60.0, le=5.0)
    acousticness: float = Field(..., ge=0.0, le=1.0)
    instrumentalness: float = Field(..., ge=0.0, le=1.0)
    liveness: float = Field(..., ge=0.0, le=1.0)
    valence: float = Field(..., ge=0.0, le=1.0)
    tempo: float = Field(..., ge=20.0, le=250.0)
    time_signature: int = Field(..., ge=1, le=5)

@app.get("/")
def check_health():
    return {"status": "Operational", "service": "HitRadar API"}

@app.post("/predict")
def predict_popularity(track: TrackInput):
    try:
        # Tiền xử lý Dữ liệu Động (Online Preprocessing)
        data = pd.DataFrame([track.model_dump()])

        # Áp dụng hàm logarit tương đương bước xử lý ngoại tuyến
        data['speechiness_log'] = np.log1p(data['instrumentalness']) 

        FEATURES_ORDER = [
            'duration_min', 'release_year', 'danceability', 'energy', 'loudness', 
            'acousticness', 'liveness', 'valence', 'tempo', 'time_signature', 'speechiness_log'
        ]

        # Định chuẩn không gian (Scaling)
        data_scaled = scaler.transform(data[FEATURES_ORDER])

        # Suy luận
        prediction = model.predict(data_scaled)[0]
        final_score = float(np.clip(prediction, 0.0, 100.0))

        # Phân loại hạng mục
        if final_score >= 70:
            tier = "High Potential (Tier 1)"
        elif final_score >= 50:
            tier = "Moderate Potential (Tier 2)"
        elif final_score >= 30:
            tier = "Low Potential (Tier 3)"
        else:
            tier = "Negligible Potential (Tier 4)"

        return {
            "predicted_score": final_score,
            "classification": tier,
            "status_code": 200
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

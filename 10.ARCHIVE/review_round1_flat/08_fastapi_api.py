"""HitRadar FastAPI application using the exact Notebook 06 pipeline."""

from functools import lru_cache
import json
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
import joblib
import numpy as np
import pandas as pd


def _find_project_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here.parent, *here.parents]:
        if (candidate / "5.DATA").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Không tìm thấy project root của HitRadar.")


PROJECT_ROOT = _find_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.prediction import PredictionResponse, TrackInput  # noqa: E402
from src.features import (  # noqa: E402
    EXPECTED_ENGINEERED_FEATURES,
    MODEL_FEATURES,
    RAW_INPUT_FEATURES,
)


ARTIFACT_DIR = PROJECT_ROOT / "4.MODELS" / "hitradar_popularity"
PIPELINE_PATH = ARTIFACT_DIR / "popularity_pipeline.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"

app = FastAPI(
    title="HitRadar Popularity API",
    version="2.0.0",
    description="RAW INPUT → shared FeatureBuilder → preprocessing → model → prediction",
)


@lru_cache(maxsize=1)
def load_pipeline():
    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(
            f"Chưa có model artifact: {PIPELINE_PATH}. Hãy chạy Notebook 06."
        )
    return joblib.load(PIPELINE_PATH)


def load_metrics() -> dict:
    if not METRICS_PATH.exists():
        return {}
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def popularity_tier(score: float) -> str:
    if score >= 70:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "emerging"
    return "low"


@app.get("/")
def root():
    return {"service": "HitRadar Popularity API", "docs": "/docs"}


@app.get("/health")
def health():
    try:
        pipeline = load_pipeline()
        model_name = pipeline.named_steps["model"].__class__.__name__
        return {
            "status": "ready",
            "model_loaded": True,
            "model_name": model_name,
            "raw_input_count": len(RAW_INPUT_FEATURES),
            "engineered_feature_count": len(EXPECTED_ENGINEERED_FEATURES),
            "model_feature_count": len(MODEL_FEATURES),
        }
    except Exception as exc:
        return {"status": "not_ready", "model_loaded": False, "detail": str(exc)}


@app.post("/predict", response_model=PredictionResponse)
def predict(track: TrackInput):
    try:
        pipeline = load_pipeline()
        raw = pd.DataFrame([track.model_dump()])[RAW_INPUT_FEATURES]
        prediction = float(pipeline.predict(raw)[0])
        score = float(np.clip(prediction, 0.0, 100.0))
        metrics = load_metrics()
        model_name = metrics.get(
            "final_model", pipeline.named_steps["model"].__class__.__name__
        )
        return PredictionResponse(
            predicted_popularity=round(score, 4),
            popularity_tier=popularity_tier(score),
            model_name=model_name,
            engineered_feature_count=len(EXPECTED_ENGINEERED_FEATURES),
            feature_count=len(MODEL_FEATURES),
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

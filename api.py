"""HitRadar FastAPI app serving regression, clustering and recommendation."""

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
    raise RuntimeError("HitRadar project root was not found.")


PROJECT_ROOT = _find_project_root()
BACKEND_DIR = Path(__file__).resolve().parent
for import_path in (PROJECT_ROOT, BACKEND_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from models.prediction import (  # noqa: E402
    ClusterResponse,
    ClusterInput,
    PredictionResponse,
    RecommendationResponse,
    TrackInput,
)
from src.features import (  # noqa: E402
    CLUSTER_FEATURES,
    RAW_INPUT_FEATURES,
    RECOMMENDATION_FEATURES,
    get_model_features,
)
from src.secondary_tasks import predict_cluster, recommend_by_track_id  # noqa: E402
from src.prediction_policy import prediction_support_status  # noqa: E402


ARTIFACT_DIR = PROJECT_ROOT / "4.MODELS" / "hitradar_popularity"
PIPELINE_PATH = ARTIFACT_DIR / "popularity_pipeline.joblib"
METRICS_PATH = ARTIFACT_DIR / "final_test_metrics.json"
SECONDARY_DIR = PROJECT_ROOT / "4.MODELS" / "hitradar_secondary"
CLUSTER_PATH = SECONDARY_DIR / "kmeans_pipeline.joblib"
CLUSTER_META_PATH = SECONDARY_DIR / "cluster_metadata.json"
RECOMMENDER_PATH = SECONDARY_DIR / "content_recommender.joblib"

app = FastAPI(
    title="HitRadar Pro API",
    version="3.0.0",
    description="RAW INPUT -> shared feature logic -> model/cluster/recommendation",
)


@lru_cache(maxsize=1)
def load_pipeline():
    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(f"Missing popularity artifact: {PIPELINE_PATH}")
    return joblib.load(PIPELINE_PATH)


@lru_cache(maxsize=1)
def load_cluster_pipeline():
    if not CLUSTER_PATH.exists():
        raise FileNotFoundError(f"Missing clustering artifact: {CLUSTER_PATH}")
    return joblib.load(CLUSTER_PATH)


@lru_cache(maxsize=1)
def load_recommender():
    if not RECOMMENDER_PATH.exists():
        raise FileNotFoundError(f"Missing recommender artifact: {RECOMMENDER_PATH}")
    return joblib.load(RECOMMENDER_PATH)


def load_metrics() -> dict:
    return json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else {}


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
    return {"service": "HitRadar Pro API", "docs": "/docs"}


@app.get("/health")
def health():
    errors = {}
    loaded = {}
    for name, loader in {
        "model": load_pipeline,
        "cluster": load_cluster_pipeline,
        "recommender": load_recommender,
    }.items():
        try:
            loaded[name] = loader()
        except Exception as exc:
            errors[name] = str(exc)
    metrics = load_metrics()
    model_features = get_model_features(
        include_engineered=bool(metrics.get("include_engineered", True)),
        include_time=bool(metrics.get("include_time", True)),
    )
    all_ready = len(loaded) == 3
    return {
        "status": "ready" if all_ready else "degraded",
        "model_ready": "model" in loaded,
        "cluster_ready": "cluster" in loaded,
        "recommender_ready": "recommender" in loaded,
        "model_file_exists": PIPELINE_PATH.exists(),
        "cluster_file_exists": CLUSTER_PATH.exists(),
        "recommender_file_exists": RECOMMENDER_PATH.exists(),
        "model_name": (
            loaded["model"].named_steps["model"].__class__.__name__
            if "model" in loaded
            else None
        ),
        "selection_winner_experiment": metrics.get("selection_winner_experiment"),
        "raw_input_count": len(RAW_INPUT_FEATURES),
        "model_feature_count": len(model_features),
        "load_errors": errors,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(track: TrackInput):
    try:
        pipeline = load_pipeline()
        raw = pd.DataFrame([track.model_dump()])[RAW_INPUT_FEATURES]
        prediction = float(pipeline.predict(raw)[0])
        score = float(np.clip(prediction, 0.0, 100.0))
        metrics = load_metrics()
        support = prediction_support_status(track.release_year)
        model_features = get_model_features(
            include_engineered=bool(metrics.get("include_engineered", True)),
            include_time=bool(metrics.get("include_time", True)),
        )
        return PredictionResponse(
            predicted_popularity=round(score, 4),
            popularity_tier=popularity_tier(score),
            model_name=metrics.get("selection_winner_model", pipeline.named_steps["model"].__class__.__name__),
            engineered_feature_count=(
                len(metrics.get("selected_engineered_features", []))
                if metrics.get("include_engineered", True)
                else 0
            ),
            feature_count=len(model_features),
            **support,
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/cluster", response_model=ClusterResponse)
def cluster(track: ClusterInput):
    try:
        raw = pd.DataFrame([track.model_dump()])[CLUSTER_FEATURES]
        label = int(predict_cluster(load_cluster_pipeline(), raw)[0])
        metadata = (
            json.loads(CLUSTER_META_PATH.read_text(encoding="utf-8"))
            if CLUSTER_META_PATH.exists()
            else {}
        )
        return ClusterResponse(
            cluster=label,
            chosen_k=int(metadata.get("chosen_k", 0)),
            feature_count=len(CLUSTER_FEATURES),
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/recommend/{track_id}", response_model=RecommendationResponse)
def recommend(track_id: str, n: int = 5):
    if not 1 <= n <= 20:
        raise HTTPException(status_code=422, detail="n must be between 1 and 20")
    try:
        rows = recommend_by_track_id(load_recommender(), track_id, n)
        return RecommendationResponse(
            query_track_id=track_id,
            recommendations=rows.to_dict(orient="records"),
            feature_count=len(RECOMMENDATION_FEATURES),
            metadata_note=(
                "Local ML-ready dataset has track_id but no track/artist names; "
                "no metadata was fabricated."
            ),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

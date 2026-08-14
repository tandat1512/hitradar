"""
FastAPI Application — EPIC 3 HitRadar Pro Backend
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import numpy as np
import shap
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import config
from models.prediction import (
    ExplainResponse,
    FeaturesResponse,
    FieldDescriptor,
    HealthResponse,
    ModelInfoResponse,
    Metrics,
    PredictRequest,
    PredictResponse,
    PredictionShort,
    TopFeature,
    WhatIfRequest,
    WhatIfResponse,
)
from pipeline_loader import PipelineLoader

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Lifespan: load model at startup ──────────────────────────────────────────

pipeline_loader: PipelineLoader | None = None
shap_explainer: shap.Explainer | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global pipeline_loader, shap_explainer

    logger.info("Loading HitRadarInferencePipeline at startup ...")
    pipeline_loader = PipelineLoader(
        artifacts_path=config.ARTIFACTS_PATH,
        epic2_fe_path=str(config.FE_TRANSFORMERS_PATH),
    )
    _ = pipeline_loader.pipeline  # ← eager load (triggers joblib.load + patches)
    logger.info("Pipeline ready.")

    yield

    logger.info("Application shutting down.")
    pipeline_loader = None
    shap_explainer = None


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="HitRadar Pro API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _merge_request(base: PredictRequest, changes: dict) -> PredictRequest:
    """Merge changed_features into base to produce a full PredictRequest dict."""
    base_dict = base.model_dump()
    base_dict.update(changes)
    return PredictRequest(**base_dict)


def _build_shap_explainer():
    """Build a SHAP TreeExplainer from the loaded model."""
    global shap_explainer
    if shap_explainer is not None:
        return shap_explainer

    pl = pipeline_loader
    model = pl.pipeline.champion_pipeline.named_steps["model"]
    shap_explainer = shap.TreeExplainer(model)
    return shap_explainer


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health():
    """Check service and model readiness."""
    pl = pipeline_loader
    model_loaded = pl is not None and pl.is_loaded()
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        timestamp=PipelineLoader.now_iso(),
    )


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    """Return model metadata."""
    pl = pipeline_loader
    if pl is None or not pl.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded — service degraded")

    try:
        meta = pl.get_model_info()
        mv = meta.get("model_version", {})
        dv = meta.get("data_version", {})
        pv = meta.get("package_version", {})

        # Load model_metrics.json if present and non-empty
        metrics_path = config.ARTIFACTS_PATH + "/model_metrics.json"
        metrics = None
        try:
            import os
            if os.path.getsize(metrics_path) > 0:
                import json
                with open(metrics_path, encoding="utf-8") as f:
                    mm = json.load(f)
                metrics = Metrics(
                    MAE=mm.get("MAE"),
                    RMSE=mm.get("RMSE"),
                    R2=mm.get("R2"),
                )
        except Exception:
            pass

        return ModelInfoResponse(
            model_id=mv.get("model_id", "UNKNOWN"),
            model_version=mv.get("model_version", "1.0.0"),
            model_family="XGBoost",
            package_version=pv.get("version", "1.0.0"),
            data_version=dv.get("version", "1.0.0"),
            feature_set="FS23-SELECTED",
            training_date=mv.get("training_date"),
            metrics=metrics,
            timestamp=PipelineLoader.now_iso(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/features", response_model=FeaturesResponse)
def features():
    """Return 18 canonical input fields and 31 selected features."""
    pl = pipeline_loader
    if pl is None:
        raise HTTPException(status_code=503, detail="Model not loaded — service degraded")

    try:
        schema = pl.get_input_schema()
        selected = pl.get_selected_features()

        fields = []
        for f in sorted(schema["fields"], key=lambda x: x["position"]):
            dtype_map = {"number": "number", "integer": "integer", "boolean": "boolean", "string": "string"}
            fields.append(FieldDescriptor(
                name=f["name"],
                position=f["position"],
                data_type=dtype_map.get(f.get("type", "number"), "number"),
                required=True,
                minimum=f.get("min"),
                maximum=f.get("max"),
                allowed_categories=f.get("enum"),
                default_policy=f.get("default_policy", "PIPELINE_IMPUTE"),
            ))

        return FeaturesResponse(
            canonical_fields=fields,
            selected_features=selected,
            total_input_fields=18,
            total_selected_features=31,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """Predict track popularity from 18 audio features."""
    pl = pipeline_loader
    if pl is None or not pl.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded — service degraded")

    try:
        input_dict = req.model_dump()
        result = pl.pipeline.predict_popularity(input_dict)

        return PredictResponse(
            status=result["status"],
            prediction_raw=result["prediction_raw"],
            prediction_clipped=result["prediction_clipped"],
            prediction_display=result["prediction_display"],
            warnings=result.get("warnings", []),
            model_id=result["model_id"],
            model_version=result["model_version"],
            package_version=result["package_version"],
            timestamp=PipelineLoader.now_iso(),
        )
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/explain", response_model=ExplainResponse)
def explain(req: PredictRequest):
    """Predict and return SHAP feature contributions."""
    pl = pipeline_loader
    if pl is None or not pl.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded — service degraded")

    try:
        input_dict = req.model_dump()
        result = pl.pipeline.predict_popularity(input_dict)

        # Get raw feature values for SHAP output
        feature_values = input_dict.copy()

        # Build SHAP values using TreeExplainer
        explainer = _build_shap_explainer()
        model = pl.pipeline.champion_pipeline

        # Get the 31-feature representation
        import pandas as pd
        df_in = pd.DataFrame([input_dict])
        fe_out = model.named_steps["fe"].transform(df_in)
        prep_out = model.named_steps["prep"].transform(fe_out)

        shap_values = explainer.shap_values(prep_out)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        base_value = float(explainer.expected_value)
        if isinstance(base_value, (list, np.ndarray)):
            base_value = float(base_value[0])

        shap_values = shap_values.flatten().tolist()

        # Map to feature names
        feature_names = pl.get_selected_features()
        shap_dict = dict(zip(feature_names, shap_values))

        # Top 5 by absolute SHAP value
        top5 = sorted(
            shap_dict.items(),
            key=lambda x: abs(x[1]),
            reverse=True,
        )[:5]

        top_features = []
        for name, sv in top5:
            raw_val = feature_values.get(name)
            if raw_val is None:
                raw_val = feature_values.get(name, 0.0)
            top_features.append(TopFeature(
                name=name,
                shap_value=round(sv, 6),
                feature_value=raw_val,
            ))

        return ExplainResponse(
            status="SUCCESS",
            prediction_raw=result["prediction_raw"],
            prediction_clipped=result["prediction_clipped"],
            prediction_display=result["prediction_display"],
            base_value=round(base_value, 6),
            shap_values={k: round(v, 6) for k, v in shap_dict.items()},
            top_features=top_features,
            model_id=result["model_id"],
            model_version=result["model_version"],
            timestamp=PipelineLoader.now_iso(),
        )
    except Exception as e:
        logger.exception("Explain failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/what-if", response_model=WhatIfResponse)
def what_if(req: WhatIfRequest):
    """Compare predictions before and after changing features."""
    pl = pipeline_loader
    if pl is None or not pl.is_loaded():
        raise HTTPException(status_code=503, detail="Model not loaded — service degraded")

    try:
        # Validate changed_features only contain canonical field names
        allowed = _FEATURE_NAMES  # already a set of field names
        bad_keys = [k for k in req.changed_features if k not in allowed]
        if bad_keys:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid field(s) in changed_features: {bad_keys}",
            )

        before_req = req.base_features
        after_dict = _merge_request(before_req, req.changed_features)

        before_result = pl.pipeline.predict_popularity(before_req.model_dump())
        after_result = pl.pipeline.predict_popularity(after_dict.model_dump())

        delta = after_result["prediction_clipped"] - before_result["prediction_clipped"]

        return WhatIfResponse(
            status="SUCCESS",
            prediction_before=PredictionShort(
                prediction_raw=before_result["prediction_raw"],
                prediction_clipped=before_result["prediction_clipped"],
                prediction_display=before_result["prediction_display"],
            ),
            prediction_after=PredictionShort(
                prediction_raw=after_result["prediction_raw"],
                prediction_clipped=after_result["prediction_clipped"],
                prediction_display=after_result["prediction_display"],
            ),
            delta=round(delta, 6),
            delta_display=int(round(delta)),
            changes_applied=req.changed_features,
            model_id=before_result["model_id"],
            model_version=before_result["model_version"],
            timestamp=PipelineLoader.now_iso(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("What-if failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ── Static feature name set for /what-if validation ─────────────────────────

_FEATURE_NAMES = {
    "duration_min", "explicit", "release_year", "release_month", "decade",
    "release_precision", "danceability", "energy", "key", "loudness",
    "mode", "speechiness", "acousticness", "instrumentalness",
    "liveness", "valence", "tempo", "time_signature",
}

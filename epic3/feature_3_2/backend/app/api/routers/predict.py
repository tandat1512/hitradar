"""
POST /predict endpoint — Feature 3.2 FastAPI Backend.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictRequest, PredictResponse
from app.schemas.common import ErrorResponse
from app.services.model_service import ModelService
from app.services.pipeline_loader import PipelineLoader


router = APIRouter(tags=["prediction"])


def _model_service() -> ModelService:
    pl = PipelineLoader.get_instance()
    if pl is None or not pl.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded — service degraded",
        )
    return ModelService(pl)


@router.post(
    "/predict",
    response_model=PredictResponse,
    responses={503: {"model": ErrorResponse}},
)
def predict(req: PredictRequest):
    """
    Predict track popularity from 18 audio features.

    Returns raw and clipped (0–100) predictions plus model metadata.
    Raises 503 if the model is not loaded.
    """
    svc = _model_service()
    input_dict = req.model_dump()
    result = svc.predict(input_dict)

    return PredictResponse(
        status=result.status,
        prediction_raw=result.prediction_raw,
        prediction_clipped=result.prediction_clipped,
        prediction_display=result.prediction_display,
        warnings=result.warnings,
        model_id=result.model_id,
        model_version=result.model_version,
        package_version=result.package_version,
    )

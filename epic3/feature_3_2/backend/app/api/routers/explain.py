"""
POST /explain endpoint — Feature 3.2 FastAPI Backend.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.explanation import ExplainRequest, ExplainResponse, TopFeature
from app.schemas.common import ErrorResponse
from app.services.explain_service import ExplainService
from app.services.model_service import ModelService
from app.services.pipeline_loader import PipelineLoader


router = APIRouter(tags=["explanation"])


def _explain_service() -> ExplainService:
    pl = PipelineLoader.get_instance()
    if pl is None or not pl.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded — service degraded",
        )
    model_svc = ModelService(pl)
    return ExplainService(model_svc)


@router.post(
    "/explain",
    response_model=ExplainResponse,
    responses={503: {"model": ErrorResponse}},
)
def explain(req: ExplainRequest):
    """
    Predict and return SHAP feature attribution.

    Computes shap.TreeExplainer values for the 31 selected features.
    Returns top-5 features by absolute SHAP magnitude.

    IMPORTANT: SHAP values show feature importance, NOT causal relationships.
    Raises 503 if the model is not loaded.
    """
    svc = _explain_service()
    result = svc.explain(req.model_dump())

    return ExplainResponse(
        status=result.prediction.status,
        prediction_raw=result.prediction.prediction_raw,
        prediction_clipped=result.prediction.prediction_clipped,
        prediction_display=result.prediction.prediction_display,
        base_value=result.base_value,
        shap_values=result.shap_values,
        top_features=[
            TopFeature(
                name=f["name"],
                shap_value=f["shap_value"],
                feature_value=f["feature_value"],
            )
            for f in result.top_features
        ],
        model_id=result.prediction.model_id,
        model_version=result.prediction.model_version,
    )

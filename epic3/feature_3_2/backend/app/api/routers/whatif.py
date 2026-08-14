"""
POST /what-if endpoint — Feature 3.2 FastAPI Backend.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.what_if import WhatIfRequest, WhatIfResponse, PredictionShort
from app.schemas.common import ErrorResponse
from app.services.whatif_service import WhatIfService
from app.services.model_service import ModelService
from app.services.pipeline_loader import PipelineLoader


router = APIRouter(tags=["what-if"])


def _whatif_service() -> WhatIfService:
    pl = PipelineLoader.get_instance()
    if pl is None or not pl.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded — service degraded",
        )
    model_svc = ModelService(pl)
    return WhatIfService(model_svc)


@router.post(
    "/what-if",
    response_model=WhatIfResponse,
    responses={503: {"model": ErrorResponse}},
)
def what_if(req: WhatIfRequest):
    """
    Compare predictions before and after feature changes.

    Sends base_features + changed_features dict.
    Returns before/after predictions and delta.

    Raises 503 if the model is not loaded.
    Raises 422 if any key in changed_features is not a canonical field name.
    """
    svc = _whatif_service()
    result = svc.compare(
        base_input=req.base_features.model_dump(),
        changed_features=req.changed_features,
    )

    return WhatIfResponse(
        status=result.status,
        prediction_before=PredictionShort(
            prediction_raw=result.prediction_before.prediction_raw,
            prediction_clipped=result.prediction_before.prediction_clipped,
            prediction_display=result.prediction_before.prediction_display,
        ),
        prediction_after=PredictionShort(
            prediction_raw=result.prediction_after.prediction_raw,
            prediction_clipped=result.prediction_after.prediction_clipped,
            prediction_display=result.prediction_after.prediction_display,
        ),
        delta=result.delta,
        delta_display=result.delta_display,
        changes_applied=result.changes_applied,
        model_id=result.model_id,
        model_version=result.model_version,
    )

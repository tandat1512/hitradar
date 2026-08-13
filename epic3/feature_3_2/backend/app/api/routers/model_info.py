"""
GET /model-info, GET /features endpoints — Feature 3.2 FastAPI Backend.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.common import (
    ErrorResponse,
    FeaturesResponse,
    FieldDescriptor,
    Metrics,
    ModelInfoResponse,
)
from app.services.model_service import ModelService
from app.services.pipeline_loader import PipelineLoader


router = APIRouter(tags=["model"])


def _model_service() -> ModelService:
    pl = PipelineLoader.get_instance()
    if pl is None or not pl.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded — service degraded",
        )
    return ModelService(pl)


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    responses={503: {"model": ErrorResponse}},
)
def model_info():
    """
    Return model metadata and test-set metrics.

    Raises 503 if the model is not loaded.
    """
    pl = PipelineLoader.get_instance()
    if pl is None or not pl.is_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded — service degraded",
        )
    svc = ModelService(pl)

    try:
        info = svc.get_model_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    # Load champion_test_metrics.json for MAE/RMSE/R2
    metrics: Metrics | None = None
    try:
        import json
        # artifacts/epic2 -> DUAN1 github/ -> repo root (2 parents up)
        from app.core.config import _REPO_ROOT
        metrics_path = (
            _REPO_ROOT
            / "7.ML" / "7.8.model_evaluation"
            / "metrics" / "champion_test_metrics.json"
        ).resolve()
        if metrics_path.exists():
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
        model_id=info["model_id"],
        model_version=info["model_version"],
        model_family=info["model_family"],
        package_version=info["package_version"],
        data_version=info["data_version"],
        feature_set=info["feature_set"],
        training_date=info.get("training_date"),
        metrics=metrics,
    )


@router.get(
    "/features",
    response_model=FeaturesResponse,
    responses={503: {"model": ErrorResponse}},
)
def features():
    """
    Return the 18 canonical input fields and 31 selected feature names.

    Raises 503 if the model is not loaded.
    """
    svc = _model_service()

    try:
        feat = svc.get_features()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    fields = [
        FieldDescriptor(
            name=f["name"],
            position=f["position"],
            data_type=f["data_type"],
            required=f["required"],
            minimum=f["minimum"],
            maximum=f["maximum"],
            allowed_categories=f["allowed_categories"],
            default_policy=f["default_policy"],
        )
        for f in sorted(feat["canonical_fields"], key=lambda x: x["position"])
    ]

    return FeaturesResponse(
        canonical_fields=fields,
        selected_features=feat["selected_features"],
        total_input_fields=feat["total_input_fields"],
        total_selected_features=feat["total_selected_features"],
    )

"""
ModelService — Feature 3.2 FastAPI Backend.

Encapsulates all prediction-related business logic:
- predict() → PredictResult (raw, clipped, display, metadata)
- get_health() → bool
- get_model_info() → dict
- get_features() → dict

No routing logic lives here.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.core.exceptions import ModelNotLoadedError, SchemaNotFoundError
from app.services.pipeline_loader import PipelineLoader


logger = logging.getLogger(__name__)


@dataclass
class PredictResult:
    status: str
    prediction_raw: float
    prediction_clipped: float
    prediction_display: int
    warnings: list[str]
    model_id: str
    model_version: str
    package_version: str


class ModelService:
    """
    Business logic for prediction and model metadata.

    Requires a PipelineLoader instance to be injected (dependency inversion).
    """

    def __init__(self, loader: PipelineLoader):
        self._loader = loader

    # ── Health ───────────────────────────────────────────────────────────────

    def is_healthy(self) -> bool:
        """Return True if the pipeline is loaded and ready."""
        return self._loader.is_loaded()

    # ── Prediction ──────────────────────────────────────────────────────────

    def predict(self, input_dict: dict) -> PredictResult:
        """
        Run prediction on a single input record.

        Parameters
        ----------
        input_dict : dict
            18 canonical fields from PredictRequest.model_dump()

        Returns
        -------
        PredictResult
            Raw and clipped predictions plus model metadata.

        Raises
        ------
        ModelNotLoadedError
            If the pipeline is not loaded.
        """
        if not self._loader.is_loaded():
            raise ModelNotLoadedError()

        try:
            pipe = self._loader.pipeline
            result = pipe.predict_popularity(input_dict)
            return PredictResult(
                status=result.get("status", "SUCCESS"),
                prediction_raw=result["prediction_raw"],
                prediction_clipped=result["prediction_clipped"],
                prediction_display=result["prediction_display"],
                warnings=result.get("warnings", []),
                model_id=result["model_id"],
                model_version=result["model_version"],
                package_version=result["package_version"],
            )
        except Exception as e:
            logger.exception("Prediction failed")
            raise e

    # ── Model info ──────────────────────────────────────────────────────────

    def get_model_info(self) -> dict:
        """
        Return raw model metadata dict from PipelineLoader.

        Contains: model_version, data_version, package_version.
        Raises ModelNotLoadedError if pipeline not loaded.
        """
        if not self._loader.is_loaded():
            raise ModelNotLoadedError()

        meta = self._loader.get_model_info()
        mv = meta.get("model_version", {})
        dv = meta.get("data_version", {})
        pv = meta.get("package_version", {})
        return {
            "model_id": mv.get("model_id", "UNKNOWN"),
            "model_version": mv.get("model_version", "1.0.0"),
            "model_family": "XGBoost",
            "package_version": pv.get("version", "1.0.0"),
            "data_version": dv.get("version", "1.0.0"),
            "feature_set": "FS23-SELECTED",
            "training_date": mv.get("training_date"),
        }

    # ── Features ────────────────────────────────────────────────────────────

    def get_features(self) -> dict:
        """
        Return canonical input fields and selected features list.

        Raises SchemaNotFoundError if schemas are unreadable.
        """
        if not self._loader.is_loaded():
            raise ModelNotLoadedError()

        try:
            schema = self._loader.get_input_schema()
            selected = self._loader.get_selected_features()
        except Exception as e:
            raise SchemaNotFoundError(
                message=f"Failed to load schemas: {e}",
                details={"artifact": "input_schema or selected_features"},
            ) from e

        dtype_map = {"number": "number", "integer": "integer", "boolean": "boolean", "string": "string"}
        fields = []
        for f in sorted(schema["fields"], key=lambda x: x.get("position", 0)):
            fields.append({
                "name": f["name"],
                "position": f.get("position", 0),
                "data_type": dtype_map.get(f.get("type", "number"), "number"),
                "required": f.get("required", True),
                "minimum": f.get("min"),
                "maximum": f.get("max"),
                "allowed_categories": f.get("enum"),
                "default_policy": f.get("default_policy", "PIPELINE_IMPUTE"),
            })

        return {
            "canonical_fields": fields,
            "selected_features": selected,
            "total_input_fields": len(fields),
            "total_selected_features": len(selected),
        }

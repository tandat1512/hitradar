"""
ExplainService — Feature 3.2 FastAPI Backend.

Computes SHAP feature attribution for a single prediction.
Uses shap.TreeExplainer (from loaded XGBoost model) at request time.

IMPORTANT: SHAP values show feature importance, NOT causal relationships.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import shap

from app.core.exceptions import ExplanationError, ModelNotLoadedError
from app.services.model_service import ModelService, PredictResult


logger = logging.getLogger(__name__)


# ── Result dataclasses ──────────────────────────────────────────────────────────

@dataclass
class ExplainResult:
    prediction: PredictResult
    base_value: float
    shap_values: dict[str, float]
    top_features: list[dict]


# ── ExplainService ─────────────────────────────────────────────────────────────

class ExplainService:
    """
    SHAP-based explanation for a single prediction.

    Wraps ModelService for the base prediction.
    Builds a TreeExplainer on first call and caches it.
    """

    def __init__(self, model_service: ModelService):
        self._model = model_service
        self._explainer: shap.Explainer | None = None

    # ── Explainer (lazy init) ───────────────────────────────────────────────

    def _get_explainer(self) -> shap.Explainer:
        if self._explainer is not None:
            return self._explainer

        loader = self._model._loader
        # Pass the XGBoost model step directly, not the full Pipeline
        xgb_model = loader.pipeline.champion_pipeline.named_steps["model"]
        self._explainer = shap.TreeExplainer(xgb_model)
        return self._explainer

    # ── Core explain ───────────────────────────────────────────────────────

    def explain(self, input_dict: dict, top_k: int = 5) -> ExplainResult:
        """
        Predict and return SHAP feature attribution.

        Parameters
        ----------
        input_dict : dict
            18 canonical fields.
        top_k : int
            Number of top features to return (default 5).

        Returns
        -------
        ExplainResult
            prediction + base_value + shap_values dict + top_k features.

        Raises
        ------
        ModelNotLoadedError
            If pipeline not loaded.
        ExplanationError
            If SHAP computation fails.
        """
        # Step 1: base prediction
        prediction = self._model.predict(input_dict)

        try:
            # Step 2: transform input to 31-feature matrix
            import pandas as pd

            loader = self._model._loader
            model = loader.pipeline.champion_pipeline
            df_in = pd.DataFrame([input_dict])
            fe_out = model.named_steps["fe"].transform(df_in)
            prep_out = model.named_steps["prep"].transform(fe_out)

            # Step 3: SHAP values
            explainer = self._get_explainer()
            shap_values = explainer.shap_values(prep_out)

            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            shap_values = shap_values.flatten()

            # Step 4: base value
            base_value = float(explainer.expected_value)
            if isinstance(base_value, (list, np.ndarray)):
                base_value = float(base_value[0])

            # Step 5: map to feature names
            feature_names = loader.get_selected_features()
            shap_dict = dict(zip(feature_names, [round(float(v), 6) for v in shap_values]))

            # Step 6: top-k by absolute magnitude
            top_raw = sorted(
                shap_dict.items(),
                key=lambda x: abs(x[1]),
                reverse=True,
            )[:top_k]

            top_features = [
                {
                    "name": name,
                    "shap_value": round(sv, 6),
                    "feature_value": input_dict.get(name, 0.0),
                }
                for name, sv in top_raw
            ]

            return ExplainResult(
                prediction=prediction,
                base_value=round(base_value, 6),
                shap_values=shap_dict,
                top_features=top_features,
            )

        except Exception as e:
            logger.exception("SHAP explanation failed")
            raise ExplanationError(
                message=f"Explanation computation failed: {e}",
                details={"input_keys": list(input_dict.keys())},
            ) from e

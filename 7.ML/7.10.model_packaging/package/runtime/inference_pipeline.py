"""
HitRadar Pro — Full Inference Pipeline
Feature 2.7 — Model Packaging & Handoff to EPIC 3

This module defines the canonical inference pipeline wrapper that accepts
raw 18-field API input and produces popularity predictions.

IMPORTANT: This module does NOT call fit/train/tune. All internal
components are pre-fitted and loaded from serialized artifacts.
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PACKAGE_VERSION = "1.0.0"
MODEL_VERSION = "1.0.0"

CANONICAL_INPUT_FIELDS = [
    "duration_min", "explicit", "release_year", "release_month", "decade",
    "release_precision", "danceability", "energy", "key", "loudness",
    "mode", "speechiness", "acousticness", "instrumentalness",
    "liveness", "valence", "tempo", "time_signature"
]

EXCLUDED_FIELDS = ["target_popularity", "track_id"]


class HitRadarInferencePipeline:
    """
    Inference-only pipeline wrapping the fitted champion model.
    
    Architecture:
        Raw 18-field input
        → input validation & column ordering
        → fitted FeatureEngineeringTransformer  (18 → 31 features)
        → fitted ColumnTransformer               (31 → 49 matrix)
        → fitted XGBRegressor                    (49 → prediction)
        → post-processing (clip, round)
    """

    def __init__(self, champion_pipeline, model_id, input_schema=None):
        """
        Parameters
        ----------
        champion_pipeline : sklearn.pipeline.Pipeline
            The fitted champion bundle with steps: fe, prep, model.
        model_id : str
            Champion model identifier (e.g. EXP24-XGB-FINAL-001).
        input_schema : dict or None
            Loaded input_schema.json for validation.
        """
        self.champion_pipeline = champion_pipeline
        self.model_id = model_id
        self.model_version = MODEL_VERSION
        self.package_version = PACKAGE_VERSION
        self.input_schema = input_schema
        self.input_fields = list(CANONICAL_INPUT_FIELDS)
        self.input_field_count = len(self.input_fields)

    # ------------------------------------------------------------------
    # Input validation
    # ------------------------------------------------------------------
    def _validate_and_normalize(self, input_data):
        """
        Accept dict, Series, or DataFrame; return a validated DataFrame.
        """
        warnings_list = []

        # Normalize to DataFrame
        if isinstance(input_data, dict):
            df = pd.DataFrame([input_data])
        elif isinstance(input_data, pd.Series):
            df = pd.DataFrame([input_data.to_dict()])
        elif isinstance(input_data, pd.DataFrame):
            df = input_data.copy()
        else:
            raise TypeError(
                f"input_data must be dict, Series, or DataFrame, "
                f"got {type(input_data).__name__}"
            )

        # Check duplicate columns
        if df.columns.duplicated().any():
            dupes = list(df.columns[df.columns.duplicated()])
            raise ValueError(f"Duplicate columns detected: {dupes}")

        # Strip excluded fields if present
        for excl in EXCLUDED_FIELDS:
            if excl in df.columns:
                df = df.drop(columns=[excl])
                warnings_list.append(
                    f"Excluded field '{excl}' was present and removed."
                )

        # Check for missing required fields
        missing = [f for f in self.input_fields if f not in df.columns]
        if missing:
            raise ValueError(
                f"Missing required input fields: {missing}"
            )

        # Check for extra fields
        extra = [c for c in df.columns if c not in self.input_fields]
        if extra:
            warnings_list.append(
                f"Extra fields ignored: {extra}"
            )

        # Select and reorder to canonical order
        df = df[self.input_fields].copy()

        # Check for Inf values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if numeric_cols.any():
            inf_mask = np.isinf(df[numeric_cols]).any()
            inf_cols = list(inf_mask[inf_mask].index)
            if inf_cols:
                raise ValueError(
                    f"Infinite values detected in columns: {inf_cols}"
                )

        return df, warnings_list

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    def _predict_raw(self, df):
        """Run the champion pipeline on validated DataFrame."""
        return self.champion_pipeline.predict(df)

    def predict_popularity(self, input_data, *, include_metadata=True):
        """
        Predict track popularity from raw 18-field input.

        Parameters
        ----------
        input_data : dict | pd.Series | pd.DataFrame
            Raw input with the 18 canonical fields.
        include_metadata : bool
            If True, include model metadata in the output.

        Returns
        -------
        dict | list[dict]
            Prediction result(s).
        """
        df, warnings_list = self._validate_and_normalize(input_data)
        is_single = len(df) == 1 and not isinstance(input_data, pd.DataFrame)

        raw_preds = self._predict_raw(df)

        results = []
        for i, raw in enumerate(raw_preds):
            raw_val = float(raw)
            clipped = float(np.clip(raw_val, 0.0, 100.0))
            display = int(round(clipped))

            record = {
                "status": "SUCCESS",
                "prediction_raw": round(raw_val, 6),
                "prediction_clipped": round(clipped, 6),
                "prediction_display": display,
                "warnings": list(warnings_list),
            }
            if include_metadata:
                record["model_id"] = self.model_id
                record["model_version"] = self.model_version
                record["package_version"] = self.package_version

            results.append(record)

        if is_single:
            return results[0]
        return results

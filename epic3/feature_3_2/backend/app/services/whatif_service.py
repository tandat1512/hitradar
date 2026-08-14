"""
WhatIfService — Feature 3.2 FastAPI Backend.

Compares predictions before and after user-specified feature changes.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.core.exceptions import InvalidFeatureError, ModelNotLoadedError
from app.services.model_service import ModelService, PredictResult


logger = logging.getLogger(__name__)

# ── Field constraints (mirrors PredictRequest validation) ─────────────────────
_RANGE_CONSTRAINTS: dict[str, tuple[float | None, float | None]] = {
    "duration_min":       (0.0, 120.0),
    "explicit":           (None, None),   # bool — no range
    "release_year":        (1900, 2100),
    "release_month":       (1.0, 12.0),
    "decade":              (1900, 2100),
    "release_precision":   (None, None),   # enum — validated separately
    "danceability":        (0.0, 1.0),
    "energy":              (0.0, 1.0),
    "key":                 (0, 11),
    "loudness":            (-60.0, 0.0),
    "mode":                (0, 1),
    "speechiness":         (0.0, 1.0),
    "acousticness":        (0.0, 1.0),
    "instrumentalness":    (0.0, 1.0),
    "liveness":           (0.0, 1.0),
    "valence":            (0.0, 1.0),
    "tempo":              (0.0, 300.0),
    "time_signature":      (None, None),   # no constraint in schema
}
_VALID_PRECISION = frozenset({"day", "month", "year"})


# ── Result dataclasses ──────────────────────────────────────────────────────────

@dataclass
class WhatIfResult:
    status: str
    prediction_before: PredictResult
    prediction_after: PredictResult
    delta: float
    delta_display: int
    changes_applied: dict
    model_id: str
    model_version: str


# ── WhatIfService ───────────────────────────────────────────────────────────────

class WhatIfService:
    """
    What-if scenario comparison.

    Merges changed_features into base_features to produce a full input record,
    then runs two predictions and computes the delta.
    """

    def __init__(self, model_service: ModelService):
        self._model = model_service

    # ── Core what-if ───────────────────────────────────────────────────────

    def compare(
        self,
        base_input: dict,
        changed_features: dict[str, float | bool | int | str],
    ) -> WhatIfResult:
        """
        Compare predictions before and after feature changes.

        Parameters
        ----------
        base_input : dict
            18 canonical fields from PredictRequest.
        changed_features : dict
            Feature overrides to apply.

        Returns
        -------
        WhatIfResult
            before/after predictions, delta, and applied changes.

        Raises
        ------
        ModelNotLoadedError
            If pipeline not loaded.
        InvalidFeatureError
            If any key in changed_features is not a canonical field name.
        """
        if not self._model.is_healthy():
            raise ModelNotLoadedError()

        # Validate changed keys
        invalid = [
            k for k in changed_features
            if k not in self._CANONICAL_FIELD_NAMES
        ]
        if invalid:
            raise InvalidFeatureError(
                message=f"Invalid field(s) in changed_features: {invalid}",
                details={"invalid_keys": invalid},
            )

        # Validate changed values against field constraints
        out_of_range = []
        for field, value in changed_features.items():
            constraint = _RANGE_CONSTRAINTS.get(field)
            if constraint is None or value is None:
                continue
            lo, hi = constraint
            if lo is not None and float(value) < lo:
                out_of_range.append(f"{field}={value} (min={lo})")
            if hi is not None and float(value) > hi:
                out_of_range.append(f"{field}={value} (max={hi})")
            if field == "release_precision" and value not in _VALID_PRECISION:
                out_of_range.append(f"{field}={value} (must be day|month|year)")
        if out_of_range:
            raise InvalidFeatureError(
                message=f"Value(s) out of range in changed_features: {out_of_range}",
                details={"out_of_range": out_of_range},
            )

        # Build after input
        after_input = {**base_input, **changed_features}

        # Two predictions
        before_result = self._model.predict(base_input)
        after_result = self._model.predict(after_input)

        delta = after_result.prediction_clipped - before_result.prediction_clipped

        return WhatIfResult(
            status="SUCCESS",
            prediction_before=before_result,
            prediction_after=after_result,
            delta=round(delta, 6),
            delta_display=int(round(delta)),
            changes_applied=dict(changed_features),
            model_id=before_result.model_id,
            model_version=before_result.model_version,
        )

    # ── Canonical field names (same 18 as PredictRequest) ─────────────────
    _CANONICAL_FIELD_NAMES: frozenset[str] = frozenset({
        "duration_min", "explicit", "release_year", "release_month", "decade",
        "release_precision", "danceability", "energy", "key", "loudness",
        "mode", "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo", "time_signature",
    })

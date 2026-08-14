"""Shared product-support policy with data coverage loaded from canonical evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, TypedDict


TRAIN_END_YEAR = 2018
PRODUCT_SUPPORT_END_YEAR = 2020
TEMPORAL_COVERAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "5.UNG_DUNG"
    / "validation"
    / "temporal_year_coverage.json"
)


def load_temporal_year_coverage() -> dict:
    """Load data-derived coverage; never infer product support from row presence."""
    if not TEMPORAL_COVERAGE_PATH.is_file():
        raise FileNotFoundError(
            "Missing temporal coverage evidence. Run "
            "9.SCRIPTS/generate_temporal_year_coverage.py first."
        )
    coverage = json.loads(TEMPORAL_COVERAGE_PATH.read_text(encoding="utf-8"))
    if coverage["product_support_end_year"] != PRODUCT_SUPPORT_END_YEAR:
        raise ValueError("Temporal coverage and product-support policy disagree.")
    return coverage


_COVERAGE = load_temporal_year_coverage()
OBSERVED_DATA_MAX_YEAR = int(_COVERAGE["max_release_year"])
FINAL_HOLDOUT_MAX_YEAR = int(_COVERAGE["final_temporal_holdout"]["max_year"])

WITHIN_SUPPORT_NOTE = (
    "The release year is within HitRadar's documented product-support cutoff through 2020. "
    "Observed data coverage is reported separately and is not a support guarantee."
)
EXTRAPOLATION_NOTE = (
    "The model was trained through 2018. The product support cutoff is 2020. "
    "Predictions after 2020 are treated as temporal extrapolations. Observed dataset/"
    "final-holdout coverage is reported separately and does not extend the product "
    "support guarantee."
)


class PredictionSupport(TypedDict):
    prediction_support_status: Literal[
        "within_product_support", "temporal_extrapolation"
    ]
    temporal_extrapolation: bool
    support_note: str
    train_end_year: int
    product_support_end_year: int
    observed_data_max_year: int
    final_holdout_max_year: int


def prediction_support_status(release_year: int | float) -> PredictionSupport:
    """Describe product support without blocking or changing the model prediction."""
    year = int(release_year)
    extrapolation = year > PRODUCT_SUPPORT_END_YEAR
    return {
        "prediction_support_status": (
            "temporal_extrapolation" if extrapolation else "within_product_support"
        ),
        "temporal_extrapolation": extrapolation,
        "support_note": EXTRAPOLATION_NOTE if extrapolation else WITHIN_SUPPORT_NOTE,
        "train_end_year": TRAIN_END_YEAR,
        "product_support_end_year": PRODUCT_SUPPORT_END_YEAR,
        "observed_data_max_year": OBSERVED_DATA_MAX_YEAR,
        "final_holdout_max_year": FINAL_HOLDOUT_MAX_YEAR,
    }

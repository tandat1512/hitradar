"""Temporal model-selection governance shared by Notebook 06 and tests."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

import pandas as pd


SELECTION_TRAIN_SCOPE = "release_year <= 2017"
VALIDATION_SCOPE = "release_year == 2018"
DEVELOPMENT_SCOPE = "release_year < 2019"
FINAL_TEST_SCOPE = "release_year >= 2019"
FIT_SCOPE_LABEL = "selection train"
EVALUATION_SCOPE_LABEL = "validation 2018"
HISTORICAL_HOLDOUT_NOTE = (
    "The 2019+ horizon was not used for corrected Round-2 winner selection, "
    "but had been inspected during an earlier development iteration."
)


def temporal_masks(frame: pd.DataFrame) -> dict[str, pd.Series]:
    """Create mutually exclusive chronological selection/validation/test masks."""
    year = pd.to_numeric(frame["release_year"], errors="coerce")
    masks = {
        "selection_train": year <= 2017,
        "validation": year == 2018,
        "development": year < 2019,
        "final_test": year >= 2019,
    }
    if (masks["selection_train"] & masks["validation"]).any():
        raise AssertionError("Selection train overlaps validation.")
    if (masks["development"] & masks["final_test"]).any():
        raise AssertionError("Development overlaps final test.")
    if not (masks["selection_train"] | masks["validation"]).equals(
        masks["development"]
    ):
        raise AssertionError("Development must equal selection train plus validation.")
    return masks


def validate_temporal_partitions(
    frame: pd.DataFrame, target: str, minimum_validation_rows: int = 1000
) -> pd.DataFrame:
    masks = temporal_masks(frame)
    rows = []
    scopes = {
        "selection_train": SELECTION_TRAIN_SCOPE,
        "validation": VALIDATION_SCOPE,
        "development": DEVELOPMENT_SCOPE,
        "final_test": FINAL_TEST_SCOPE,
    }
    for name, mask in masks.items():
        values = pd.to_numeric(frame.loc[mask, target], errors="coerce")
        rows.append(
            {
                "Partition": name,
                "Scope": scopes[name],
                "Rows": int(mask.sum()),
                "Target Mean": float(values.mean()),
                "Target Std": float(values.std()),
                "Target Min": float(values.min()),
                "Target Q25": float(values.quantile(0.25)),
                "Target Median": float(values.median()),
                "Target Q75": float(values.quantile(0.75)),
                "Target Max": float(values.max()),
            }
        )
    summary = pd.DataFrame(rows)
    validation_rows = int(summary.loc[summary["Partition"] == "validation", "Rows"].iloc[0])
    if validation_rows < minimum_validation_rows:
        raise ValueError(
            f"2018 validation has only {validation_rows} rows; expected at least "
            f"{minimum_validation_rows}."
        )
    if (summary["Rows"] == 0).any():
        raise ValueError("Temporal protocol created an empty partition.")
    return summary


def select_validation_winner(metrics: pd.DataFrame) -> pd.Series:
    """Lock a winner using clipped temporal-validation metrics and nothing else."""
    required = {
        "Experiment",
        "Model",
        "Prediction Variant",
        "MAE",
        "RMSE",
        "Fit Scope",
        "Evaluation Scope",
    }
    missing = required.difference(metrics.columns)
    if missing:
        raise ValueError(f"Selection metrics missing columns: {sorted(missing)}")
    if not metrics["Fit Scope"].eq(FIT_SCOPE_LABEL).all():
        raise ValueError("Winner selection received a non-selection-train fit scope.")
    if not metrics["Evaluation Scope"].eq(EVALUATION_SCOPE_LABEL).all():
        raise ValueError("Winner selection received labels outside validation 2018.")
    eligible = metrics.loc[metrics["Prediction Variant"] == "Clipped [0,100]"].copy()
    if eligible.empty:
        raise ValueError("No clipped validation metrics are eligible for selection.")
    return eligible.sort_values(
        ["RMSE", "MAE", "Experiment", "Model"], kind="mergesort"
    ).iloc[0]


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_winner_lock(
    path: Path,
    *,
    winner: pd.Series,
    validation_metrics_path: Path,
    include_engineered: bool,
    include_time: bool,
) -> dict:
    """Persist immutable evidence before any final-test prediction is calculated."""
    payload = {
        "locked_at_utc": datetime.now(timezone.utc).isoformat(),
        "selection_protocol": (
            f"fit {SELECTION_TRAIN_SCOPE}; evaluate {VALIDATION_SCOPE}; "
            "minimum clipped validation RMSE, MAE then stable lexical tie-break"
        ),
        "selection_winner_experiment": str(winner["Experiment"]),
        "selection_winner_model": str(winner["Model"]),
        "include_engineered": bool(include_engineered),
        "include_time": bool(include_time),
        "validation_clipped_metrics": {
            "MAE": float(winner["MAE"]),
            "RMSE": float(winner["RMSE"]),
            "R2": float(winner["R2"]),
        },
        "fit_scope": FIT_SCOPE_LABEL,
        "evaluation_scope": EVALUATION_SCOPE_LABEL,
        # Backward-compatible field scoped to this corrected Round-2 lock event.
        "final_test_labels_observed": False,
        "final_test_labels_observed_field_scope": "before corrected Round-2 winner lock",
        "final_test_labels_observed_before_round2_lock": False,
        "historically_never_observed_claim": False,
        "historical_holdout_note": HISTORICAL_HOLDOUT_NOTE,
        "validation_metrics_file": validation_metrics_path.name,
        "validation_metrics_sha256": file_sha256(validation_metrics_path),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload

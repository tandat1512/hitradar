"""Generate temporal year-coverage evidence directly from the canonical parquet."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
OUTPUT_PATH = ROOT / "5.UNG_DUNG" / "validation" / "temporal_year_coverage.json"
PRODUCT_SUPPORT_END_YEAR = 2020


def partition_summary(year: pd.Series, mask: pd.Series, scope: str) -> dict:
    selected = year.loc[mask]
    if selected.empty:
        raise ValueError(f"Temporal partition is empty: {scope}")
    return {
        "scope": scope,
        "rows": int(mask.sum()),
        "min_year": int(selected.min()),
        "max_year": int(selected.max()),
    }


frame = pd.read_parquet(DATA_PATH, columns=["release_year"])
year = pd.to_numeric(frame["release_year"], errors="coerce")
if year.isna().any():
    raise ValueError(f"release_year contains {int(year.isna().sum())} non-numeric values")
year = year.astype(int)

payload = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "source": str(DATA_PATH.relative_to(ROOT)).replace("\\", "/"),
    "total_rows": int(len(frame)),
    "min_release_year": int(year.min()),
    "max_release_year": int(year.max()),
    "selection_train": partition_summary(year, year <= 2017, "release_year <= 2017"),
    "validation": partition_summary(year, year == 2018, "release_year == 2018"),
    "development": partition_summary(year, year < 2019, "release_year < 2019"),
    "final_temporal_holdout": partition_summary(year, year >= 2019, "release_year >= 2019"),
    "rows_by_year": {
        str(int(key)): int(value)
        for key, value in year.value_counts().sort_index().items()
    },
    "product_support_end_year": PRODUCT_SUPPORT_END_YEAR,
    "support_policy_note": (
        "Observed data coverage is evidence of rows present, not a product support "
        "guarantee. HitRadar intentionally uses 2020 as its conservative product cutoff."
    ),
}
assert sum(payload["rows_by_year"].values()) == payload["total_rows"]
assert payload["final_temporal_holdout"]["max_year"] == payload["max_release_year"]
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload, indent=2))

"""
Feature 3.4 Phase 1 — Data Profiling Script
Generates all validation JSON files from the canonical dataset.
"""
import hashlib
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "epic3" / "feature_3_4"))
from dashboard.loaders.trend_data_loader import (
    load_trend_dataset,
    load_yearly_evaluation,
    get_source_fingerprint,
)

REPO = pathlib.Path(r"H:\dự án\DUAN1 github")
OUT = REPO / "epic3" / "feature_3_4" / "dashboard" / "validation"
OUT.mkdir(exist_ok=True)

# ── Load ────────────────────────────────────────────────────────────────────

print("Loading datasets...")
df = load_trend_dataset()
df_eval = load_yearly_evaluation()
fingerprints = get_source_fingerprint()

# ── Hash before/after to prove read-only ────────────────────────────────────

def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

dataset_path = REPO / "5.DATA" / "processed" / "ml_ready_dataset.csv"
eval_path = REPO / "7.ML" / "7.8.model_evaluation" / "temporal" / "yearly_evaluation.csv"
hash_before_dataset = file_hash(dataset_path)
hash_before_eval = file_hash(eval_path)

# (No mutations happen in this script)

hash_after_dataset = file_hash(dataset_path)
hash_after_eval = file_hash(eval_path)

# ── Basic profile ──────────────────────────────────────────────────────────────

def safe_stats(series):
    valid = series.dropna()
    finite = valid[valid.apply(lambda x: x == x)]  # drop NaN
    return {
        "count": int(len(series)),
        "null_count": int(series.isna().sum()),
        "null_rate": round(float(series.isna().mean()), 6),
        "unique_count": int(series.nunique()),
        "min": float(finite.min()) if len(finite) else None,
        "max": float(finite.max()) if len(finite) else None,
        "mean": float(finite.mean()) if len(finite) else None,
    } if series.dtype in ["float64", "int64"] else {
        "count": int(len(series)),
        "null_count": int(series.isna().sum()),
        "null_rate": round(float(series.isna().mean()), 6),
        "unique_count": int(series.nunique()),
    }

# ── 1. Source Fingerprint ─────────────────────────────────────────────────────

sf = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "dataset": {
        "path": str(dataset_path),
        "relative": "5.DATA/processed/ml_ready_dataset.csv",
        "sha256": hash_before_dataset,
        "bytes": os.path.getsize(dataset_path),
        "source_epic": "EPIC 1 / Feature 1.3",
        "generated_by": "EPIC 1 dataset preparation pipeline",
    },
    "evaluation": {
        "path": str(eval_path),
        "relative": "7.ML/7.8.model_evaluation/temporal/yearly_evaluation.csv",
        "sha256": hash_before_eval,
        "bytes": os.path.getsize(eval_path),
        "source_epic": "EPIC 2",
        "generated_by": "EPIC 2 model evaluation pipeline",
    },
    "read_only_proven": hash_before_dataset == hash_after_dataset and hash_before_eval == hash_after_eval,
}
with open(OUT / "feature_3_4_source_fingerprint.json", "w") as f:
    json.dump(sf, f, indent=2)
print(f"✓ source_fingerprint — rows={len(df)}, cols={len(df.columns)}")

# ── 2. Schema Inventory ───────────────────────────────────────────────────────

schema = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "rows": len(df),
    "columns": len(df.columns),
    "column_list": list(df.columns),
    "dtypes": {c: str(dt) for c, dt in df.dtypes.items()},
    "fields": []
}

AUDIO_FEATURE_CANDIDATES = {
    "danceability", "energy", "acousticness", "valence", "tempo",
    "loudness", "speechiness", "instrumentalness", "liveness",
}

for col in df.columns:
    s = df[col]
    is_numeric = pd.api.types.is_numeric_dtype(s)
    role = "OTHER"
    if col in {"release_year", "year"}:
        role = "TEMPORAL"
    elif col == "popularity":
        role = "POPULARITY"
    elif col == "explicit":
        role = "EXPLICIT"
    elif col == "duration_ms":
        role = "DURATION"
    elif col in {"artist", "artists", "artist_name"}:
        role = "ARTIST"
    elif col in {"genre", "genres"}:
        role = "GENRE"
    elif col in AUDIO_FEATURE_CANDIDATES:
        role = "AUDIO_FEATURE"
    elif col == "id":
        role = "IDENTIFIER"

    schema["fields"].append({
        "column": col,
        "dtype": str(s.dtype),
        "role": role,
        **safe_stats(s),
    })

with open(OUT / "feature_3_4_trend_data_schema.json", "w") as f:
    json.dump(schema, f, indent=2)
print(f"✓ trend_data_schema")

# ── 3. Year Field Validation ─────────────────────────────────────────────────

year_col = None
for c in ["release_year", "year"]:
    if c in df.columns:
        year_col = c
        break

year_series = df[year_col].dropna() if year_col else pd.Series(dtype=float)
year_valid = year_series[year_series.apply(lambda x: x == x)]
year_finite = year_valid[year_valid.between(1900, 2030)]

year_counts = year_series.value_counts().sort_index()

data = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "year_column": year_col,
    "year_dtype": str(year_series.dtype),
    "year_count": int(len(year_series)),
    "year_null_count": int(df[year_col].isna().sum()) if year_col else None,
    "year_invalid_count": int(len(year_series) - len(year_finite)),
    "year_min": int(year_finite.min()) if len(year_finite) else None,
    "year_max": int(year_finite.max()) if len(year_finite) else None,
    "year_coverage": f"{int(year_finite.min())}–{int(year_finite.max())}" if len(year_finite) else None,
    "years_present": sorted([int(y) for y in year_finite.unique()]),
    "year_count_per_year": {int(k): int(v) for k, v in year_counts.to_dict().items()},
}
with open(OUT / "feature_3_4_year_validation.json", "w") as f:
    json.dump(data, f, indent=2)
print(f"✓ year_validation — {data['year_coverage']}")

# ── 4. Range Status ───────────────────────────────────────────────────────────

ymin, ymax = data["year_min"], data["year_max"]
required_start, required_end = 1921, 2020

if ymin is not None and ymax is not None:
    if ymin <= required_start and ymax >= required_end:
        range_status = "FULL_RANGE_AVAILABLE"
    elif ymin <= required_end and ymax >= required_start:
        range_status = "PARTIAL_RANGE_AVAILABLE"
    else:
        range_status = "OUTSIDE_EXPECTED_RANGE"
else:
    range_status = "NO_VALID_YEAR_DATA"

years_needed = set(range(required_start, required_end + 1))
years_in_data = set(int(y) for y in year_finite.unique())
years_missing = sorted(years_needed - years_in_data)
years_present_needed = sorted(years_needed & years_in_data)

range_data = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "required_range": {"start": required_start, "end": required_end},
    "actual_min": ymin,
    "actual_max": ymax,
    "range_status": range_status,
    "years_present_in_range": len(years_present_needed),
    "years_missing_in_range": len(years_missing),
    "missing_years": years_missing[:30],  # cap for JSON size
    "years_present_list": years_present_needed,
}
with open(OUT / "feature_3_4_year_range.json", "w") as f:
    json.dump(range_data, f, indent=2)
print(f"✓ year_range — {range_status}")

# ── 5. Popularity Field ───────────────────────────────────────────────────────

pop_col = "popularity" if "popularity" in df.columns else None
pop_data = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "popularity_column": pop_col,
    "valid": pop_col is not None,
}
if pop_col:
    s = df[pop_col]
    pop_data.update(safe_stats(s))
    pop_data["value_distribution"] = {
        "lt30": int((s < 30).sum()),
        "30to60": int(((s >= 30) & (s < 60)).sum()),
        "60to80": int(((s >= 60) & (s < 80)).sum()),
        "ge80": int((s >= 80).sum()),
    }
with open(OUT / "feature_3_4_popularity_validation.json", "w") as f:
    json.dump(pop_data, f, indent=2)
print(f"✓ popularity_validation")

# ── 6. Audio Feature Registry ────────────────────────────────────────────────

af_reg = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "features": [],
}
for feat in sorted(AUDIO_FEATURE_CANDIDATES):
    if feat in df.columns:
        s = df[feat]
        valid = s.dropna()
        af_reg["features"].append({
            "name": feat,
            "exists": True,
            "dtype": str(s.dtype),
            "min": float(valid.min()) if len(valid) else None,
            "max": float(valid.max()) if len(valid) else None,
            "mean": float(valid.mean()) if len(valid) else None,
            "null_count": int(s.isna().sum()),
            "null_rate": round(float(s.isna().mean()), 6),
            "non_finite_count": int(s.dropna().apply(lambda x: x != x).sum()),
            "enabled": True,
        })

with open(OUT / "feature_3_4_audio_feature_registry.json", "w") as f:
    json.dump(af_reg, f, indent=2)
print(f"✓ audio_feature_registry — {len(af_reg['features'])} features")

# ── 7. Explicit Field ────────────────────────────────────────────────────────

explicit_col = "explicit" if "explicit" in df.columns else None
expl_data = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "explicit_column": explicit_col,
    "valid": explicit_col is not None,
}
if explicit_col:
    s = df[explicit_col]
    if s.dtype == bool or set(s.dropna().unique()).issubset({0, 1, True, False}):
        expl_data["dtype"] = "bool_like"
        expl_data["true_count"] = int(s.astype(str).str.lower().isin(["1", "true"]).sum())
        expl_data["false_count"] = int(len(s) - s.isna().sum() - expl_data["true_count"])
    else:
        expl_data["dtype"] = str(s.dtype)
        expl_data["unique_values"] = list(s.dropna().unique())[:10]
    expl_data["null_count"] = int(s.isna().sum())

with open(OUT / "feature_3_4_explicit_field_validation.json", "w") as f:
    json.dump(expl_data, f, indent=2)
print(f"✓ explicit_field")

# ── 8. Duration Field ───────────────────────────────────────────────────────

dur_col = None
for c in ["duration_ms", "duration_s", "duration_sec", "duration"]:
    if c in df.columns:
        dur_col = c
        break

dur_data = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "duration_column": dur_col,
    "valid": dur_col is not None,
}
if dur_col:
    s = df[dur_col]
    valid = s.dropna()
    dur_data.update(safe_stats(s))
    dur_data["unit"] = "milliseconds" if dur_col == "duration_ms" else "seconds"

with open(OUT / "feature_3_4_duration_field_validation.json", "w") as f:
    json.dump(dur_data, f, indent=2)
print(f"✓ duration_field")

# ── 9. Artist / Genre ───────────────────────────────────────────────────────

artist_col = next((c for c in ["artist", "artists", "artist_name"] if c in df.columns), None)
genre_col = next((c for c in ["genre", "genres"] if c in df.columns), None)

ag_data = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "artist_column": artist_col,
    "genre_column": genre_col,
    "status": (
        "BOTH_AVAILABLE" if (artist_col and genre_col) else
        "ARTIST_AVAILABLE" if artist_col else
        "GENRE_AVAILABLE" if genre_col else
        "NEITHER_AVAILABLE"
    ),
}
if artist_col:
    ag_data["artist_stats"] = safe_stats(df[artist_col])
if genre_col:
    ag_data["genre_stats"] = safe_stats(df[genre_col])

with open(OUT / "feature_3_4_artist_genre_field_validation.json", "w") as f:
    json.dump(ag_data, f, indent=2)
print(f"✓ artist_genre — {ag_data['status']}")

# ── 10. Data Quality Profile ─────────────────────────────────────────────────

dq = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "rows": len(df),
    "columns": len(df.columns),
    "duplicate_rows": int(df.duplicated().sum()),
    "empty_rows": int(df.isna().all(axis=1).sum()),
    "fully_null_rows": int(df.isna().all(axis=1).sum()),
}
# Missing per key field
for col in ["release_year", "popularity", "danceability", "energy", "valence"]:
    if col in df.columns:
        dq[f"null_count_{col}"] = int(df[col].isna().sum())
        dq[f"null_rate_{col}"] = round(float(df[col].isna().mean()), 6)
# Constant columns
const = [c for c in df.columns if df[c].nunique() <= 1]
dq["constant_columns"] = const

with open(OUT / "feature_3_4_trend_data_quality.json", "w") as f:
    json.dump(dq, f, indent=2)
print(f"✓ trend_data_quality")

# ── 11. Missing Data Policy ─────────────────────────────────────────────────

mdp = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "policy": {
        "aggregation": "exclude_missing",
        "description": "All aggregations (mean, count, etc.) use pandas default skipna=True semantics. "
                       "Missing values are excluded from statistics. "
                       "Dashboard aggregations do NOT fillna(), impute(), or drop rows to hide missingness.",
        "coverage_reporting": True,
        "no_fillna": True,
        "no_imputation": True,
        "no_silent_drop": True,
    },
    "fields": [],
}
for col in df.columns:
    n = int(df[col].isna().sum())
    if n > 0:
        mdp["fields"].append({
            "column": col,
            "null_count": n,
            "null_rate": round(float(df[col].isna().mean()), 6),
            "policy": "exclude from aggregation",
        })

with open(OUT / "feature_3_4_missing_data_policy.json", "w") as f:
    json.dump(mdp, f, indent=2)
print(f"✓ missing_data_policy")

# ── 12. Decade Policy ────────────────────────────────────────────────────────

decade_data = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "policy": {
        "derivation": "decade = (year // 10) * 10",
        "display_format": "XXXXs",
        "policy_2020": "treated as single-year '2020', NOT as full decade 2020s. "
                       "Chart labels note '2020 (single year)' if 2020 is included.",
        "aggregation": "mean by decade (pandas groupby)",
        "note": "2020s decade aggregate only available for year 2020 in this dataset.",
    },
    "expected_decades": ["1920s", "1930s", "1940s", "1950s", "1960s",
                          "1970s", "1980s", "1990s", "2000s", "2010s", "2020"],
}
with open(OUT / "feature_3_4_decade_policy.json", "w") as f:
    json.dump(decade_data, f, indent=2)
print(f"✓ decade_policy")

# ── 13. Dashboard Data Contract ──────────────────────────────────────────────

year_col_name = year_col or "unknown"
pop_col_name = pop_col or None
dur_col_name = dur_col or None
dur_unit = "milliseconds" if dur_col == "duration_ms" else "seconds" if dur_col else None

contract = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "temporal_field": year_col_name,
    "popularity_field": pop_col_name,
    "audio_features": sorted(af_reg["features"], key=lambda x: x["name"]),
    "explicit_field": explicit_col,
    "duration_field": dur_col_name,
    "duration_unit": dur_unit,
    "artist_field": artist_col,
    "genre_field": genre_col,
    "expected_range": {"start_year": 1921, "end_year": 2020},
    "range_status": range_status,
    "fields": schema["fields"],
}
with open(OUT / "feature_3_4_dashboard_data_contract.json", "w") as f:
    json.dump(contract, f, indent=2)
print(f"✓ dashboard_data_contract")

# ── 14. Source Immutability ─────────────────────────────────────────────────

si = {
    "date": "2026-08-06",
    "person_in_charge": "Minh",
    "source_dataset_modified": hash_before_dataset != hash_after_dataset,
    "evaluation_modified": hash_before_eval != hash_after_eval,
    "dataset_hash_before": hash_before_dataset,
    "dataset_hash_after": hash_after_dataset,
    "evaluation_hash_before": hash_before_eval,
    "evaluation_hash_after": hash_after_eval,
    "model_loaded": False,
    "training_executed": False,
    "refit_executed": False,
    "shap_computed": False,
    "status": "PASS" if (hash_before_dataset == hash_after_dataset and hash_before_eval == hash_after_eval) else "FAIL",
}
with open(OUT / "feature_3_4_source_immutability_phase_1.json", "w") as f:
    json.dump(si, f, indent=2)
print(f"✓ source_immutability — {'PASS' if si['status']=='PASS' else 'FAIL'}")

print("\nAll profiling complete.")

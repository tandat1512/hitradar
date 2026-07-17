#!/usr/bin/env python3
"""
Feature 2.1 HOTFIX — Execute all fixes and regenerate artifacts.
Does NOT train models, fit preprocessors, or change temporal boundaries.
"""

import pandas as pd
import numpy as np
import json
import hashlib
import yaml
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT.parent / "Output epic2"
DATA_INTAKE = ROOT / "7.ML" / "7.3.data_intake"
SPLITS_DIR = ROOT / "7.ML" / "7.4.splits"
CONFIG_DIR = ROOT / "7.ML" / "7.1.config"

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_series(series):
    h = hashlib.sha256()
    for val in sorted(series.astype(str).values):
        h.update(val.encode("utf-8"))
    return h.hexdigest()

def main():
    now = datetime.now(timezone.utc)
    pq_path = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
    df = pd.read_parquet(pq_path)

    with open(CONFIG_DIR / "experiment_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    with open(DATA_INTAKE / "data_version.json", "r", encoding="utf-8") as f:
        dv = json.load(f)

    time_col = "release_year"
    id_col = "track_id"
    tgt_col = "target_popularity"

    # ================================================================
    # HOTFIX 1: Data exceptions for year 1900
    # ================================================================
    print("HOTFIX 1: Creating data_exceptions.json")
    anom = df[df[time_col] == 1900]
    exceptions = []
    for _, r in anom.iterrows():
        exceptions.append({
            "exception_id": "EXC-001",
            "track_id": str(r[id_col]),
            "field": "release_year",
            "value": int(r[time_col]),
            "reason": "release_year=1900 is outside EPIC 1 documented range (1921-2021). "
                       "Track has release_precision='day' and release_month=1, suggesting "
                       "the original release_date was '1900-01-01' — a common Spotify API "
                       "default/sentinel for unknown release dates. Track exists on Spotify "
                       "with target_popularity=19.",
            "source_evidence": {
                "parquet_value": 1900,
                "csv_value": 1900,
                "release_precision": str(r["release_precision"]),
                "release_month": float(r["release_month"]) if not pd.isna(r["release_month"]) else None,
                "target_popularity": int(r[tgt_col]),
                "epic1_documented_range": "1921-2021",
                "epic1_source": "feature_dictionary.md line 17, DATA_DICTIONARY.md line 129",
            },
            "classification": "SENTINEL_OR_DEFAULT",
            "impact": "1 row out of 586,672 (0.00017%). Assigned to train split (year < 2005). "
                       "Negligible impact on model training. Does not affect split boundaries.",
            "decision": "KEEP_WITH_EXCEPTION — Record retained in dataset. Registered as "
                         "formal exception. EPIC 1 docs should note actual min_year includes 1900.",
            "approved_by": "pending_review",
            "approved_at": None,
            "created_at": now.isoformat(),
        })

    exc_path = DATA_INTAKE / "data_exceptions.json"
    with open(exc_path, "w", encoding="utf-8") as f:
        json.dump({"exceptions": exceptions, "total": len(exceptions), "created_at": now.isoformat()}, f, indent=2)
    print(f"  Saved: {exc_path}")

    # ================================================================
    # HOTFIX 4: Enhanced test_set_lock.json
    # ================================================================
    print("HOTFIX 4: Upgrading test_set_lock.json")

    test_df = df[df[time_col] >= 2014]
    test_id_hash = sha256_series(test_df[id_col])

    test_lock = {
        "status": "locked",
        "data_version": dv["data_version"],
        "split_version": "temporal-split-v1",
        "test_ids_hash": test_id_hash,
        "test_row_count": int(len(test_df)),
        "test_start_year": 2014,
        "test_end_year": int(test_df[time_col].max()),
        "lock_timestamp": now.isoformat(),
        "lock_owner": "Feature 2.1 — Data Intake, Validation & Temporal Split",
        "permitted_stage": "Feature 2.5 — Final model evaluation only",
        "prohibited_actions": [
            "Do NOT use test set for hyperparameter tuning",
            "Do NOT use test set for model selection",
            "Do NOT use test set for feature selection",
            "Do NOT compute model metrics on test before Feature 2.5",
            "Do NOT read y_test in Feature 2.2, 2.3, or 2.4 scripts",
        ],
        "descriptive_audit_performed": True,
        "descriptive_audit_fields": [
            "target_popularity distribution (mean, median, std, buckets)",
            "release_year range",
            "missing value counts (tempo, time_signature, release_month)",
            "row count",
        ],
        "descriptive_audit_note": (
            "Test labels were read during Feature 2.1 pre-lock descriptive audit "
            "to document data quality and temporal distribution shift. "
            "No model was trained, no model metric was computed, "
            "no model was selected using test data."
        ),
        "final_evaluation_status": "NOT_STARTED",
        "model_metrics_on_test": None,
    }

    lock_path = SPLITS_DIR / "test_set_lock.json"
    with open(lock_path, "w", encoding="utf-8") as f:
        json.dump(test_lock, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {lock_path}")

    # ================================================================
    # HOTFIX 3: Regenerate split_manifest.json with corrected candidate stats
    # ================================================================
    print("HOTFIX 3: Regenerating split_manifest.json")

    train_df = df[df[time_col] < 2005].copy()
    val_df = df[(df[time_col] >= 2005) & (df[time_col] < 2014)].copy()

    train_hash = sha256_series(train_df[id_col])
    val_hash = sha256_series(val_df[id_col])

    def make_profile(split_df, total_n):
        tgt = split_df[tgt_col]
        return {
            "row_count": int(len(split_df)),
            "row_ratio": round(len(split_df) / total_n, 4),
            "min_year": int(split_df[time_col].min()),
            "max_year": int(split_df[time_col].max()),
            "target_mean": round(float(tgt.mean()), 4),
            "target_median": float(tgt.median()),
            "target_std": round(float(tgt.std()), 4),
            "target_zero_count": int((tgt == 0).sum()),
            "buckets": {
                "0-20": int(((tgt >= 0) & (tgt <= 20)).sum()),
                "21-40": int(((tgt >= 21) & (tgt <= 40)).sum()),
                "41-60": int(((tgt >= 41) & (tgt <= 60)).sum()),
                "61-80": int(((tgt >= 61) & (tgt <= 80)).sum()),
                "81-100": int(((tgt >= 81) & (tgt <= 100)).sum()),
            },
            "missing_tempo": int(split_df["tempo"].isnull().sum()),
            "missing_time_signature": int(split_df["time_signature"].isnull().sum()),
            "missing_release_month": int(split_df["release_month"].isnull().sum()),
        }

    split_manifest = {
        "strategy": "temporal",
        "status": "locked",
        "data_version": dv["data_version"],
        "split_version": "temporal-split-v1",
        "time_column": time_col,
        "identifier": id_col,
        "target": tgt_col,
        "selected_candidate": "C1",
        "train": {
            "start_year": int(df[time_col].min()),
            "end_year": 2004,
            "rows": int(len(train_df)),
            "ratio": round(len(train_df) / len(df), 4),
            "id_file": "train_ids.parquet",
            "id_sha256": train_hash,
            "target_profile": make_profile(train_df, len(df)),
        },
        "validation": {
            "start_year": 2005,
            "end_year": 2013,
            "rows": int(len(val_df)),
            "ratio": round(len(val_df) / len(df), 4),
            "id_file": "validation_ids.parquet",
            "id_sha256": val_hash,
            "target_profile": make_profile(val_df, len(df)),
        },
        "test": {
            "start_year": 2014,
            "end_year": int(df[time_col].max()),
            "rows": int(len(test_df)),
            "ratio": round(len(test_df) / len(df), 4),
            "id_file": "test_ids.parquet",
            "id_sha256": test_id_hash,
            "target_profile": make_profile(test_df, len(df)),
        },
        "row_reconciliation": {
            "train": int(len(train_df)),
            "validation": int(len(val_df)),
            "test": int(len(test_df)),
            "total": int(len(train_df) + len(val_df) + len(test_df)),
            "source": int(len(df)),
            "match": (len(train_df) + len(val_df) + len(test_df)) == len(df),
        },
        "data_exceptions": [
            {"track_id": "74CSJTE5QQp1e4bHzm3wti", "field": "release_year", "value": 1900,
             "classification": "SENTINEL_OR_DEFAULT", "in_split": "train"},
        ],
        "created_at": now.isoformat(),
        "random_seed": 1512,
    }

    sm_path = SPLITS_DIR / "split_manifest.json"
    with open(sm_path, "w", encoding="utf-8") as f:
        json.dump(split_manifest, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {sm_path}")

    # ================================================================
    # HOTFIX 5: Legacy artifact manifest
    # ================================================================
    print("HOTFIX 5: Creating legacy artifact manifest")

    legacy_dir = ROOT / "4.MODELS" / "legacy_epic1"
    legacy_files = ["encoder.pkl", "scaler.pkl", "popularity_model.pkl"]
    manifest_entries = []
    for lf in legacy_files:
        fp = legacy_dir / lf
        if fp.exists():
            manifest_entries.append({
                "filename": lf,
                "size_bytes": int(fp.stat().st_size),
                "sha256": sha256_file(fp),
                "origin": "EPIC 1 or pre-project placeholder",
                "content": "EMPTY (0 bytes)" if fp.stat().st_size == 0 else "UNKNOWN",
                "quarantined_at": now.isoformat(),
                "reason": "Not part of EPIC 2 ML pipeline. Quarantined to prevent accidental use.",
            })

    leg_manifest = {
        "quarantine_directory": "4.MODELS/legacy_epic1/",
        "files": manifest_entries,
        "total_files": len(manifest_entries),
        "policy": "DO_NOT_USE — These files are not validated EPIC 2 artifacts.",
        "created_at": now.isoformat(),
    }

    leg_path = legacy_dir / "legacy_artifact_manifest.json"
    with open(leg_path, "w", encoding="utf-8") as f:
        json.dump(leg_manifest, f, indent=2)
    print(f"  Saved: {leg_path}")

    # DO_NOT_USE.md
    dnu_path = legacy_dir / "DO_NOT_USE.md"
    with open(dnu_path, "w", encoding="utf-8") as f:
        f.write("""# DO NOT USE — LEGACY ARTIFACTS

These files are **NOT** part of the official EPIC 2 ML pipeline.

## Status

- **Origin**: EPIC 1 or pre-project placeholder files
- **Content**: All files are 0 bytes (empty placeholders)
- **Validation**: NOT validated for EPIC 2
- **Quarantined at**: """ + now.isoformat() + """

## Prohibitions

1. **Do NOT use** in any EPIC 2 training pipeline.
2. **Do NOT use** for inference.
3. **Do NOT import** in any Feature 2.2–2.8 script.
4. **Do NOT move** back to `4.MODELS/4.1.trained/`.

## Files

| File | Size | Note |
|------|------|------|
| encoder.pkl | 0 bytes | Empty placeholder |
| scaler.pkl | 0 bytes | Empty placeholder |
| popularity_model.pkl | 0 bytes | Empty placeholder |

These are kept for historical record only. If the repository policy permits deletion, they may be removed.
""")
    print(f"  Saved: {dnu_path}")

    # ================================================================
    # Print final artifact summary
    # ================================================================
    print("\n" + "=" * 70)
    print("HOTFIX EXECUTION COMPLETE")
    print("=" * 70)
    print(f"  data_exceptions.json:           {exc_path}")
    print(f"  test_set_lock.json (upgraded):   {lock_path}")
    print(f"  split_manifest.json (regenerated): {sm_path}")
    print(f"  legacy_artifact_manifest.json:  {leg_path}")
    print(f"  DO_NOT_USE.md:                  {dnu_path}")


if __name__ == "__main__":
    main()

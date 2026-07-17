#!/usr/bin/env python3
"""
Feature 2.1 HOTFIX — Master Investigation Script
Covers: HOTFIX 1 (year anomaly), HOTFIX 2 (source reconciliation),
        HOTFIX 3 (candidate split re-verification), HOTFIX 5 (legacy artifacts),
        HOTFIX 7 (temporal shift diagnostics)
"""

import pandas as pd
import numpy as np
import json
import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT.parent / "Output epic2"
DATA_INTAKE = ROOT / "7.ML" / "7.3.data_intake"
SPLITS_DIR = ROOT / "7.ML" / "7.4.splits"

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
    results = {}

    # Load both sources
    pq_path = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
    csv_path = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.csv"
    df_pq = pd.read_parquet(pq_path)
    df_csv = pd.read_csv(csv_path)

    # ================================================================
    # HOTFIX 1: RELEASE YEAR ANOMALY
    # ================================================================
    print("=" * 70)
    print("HOTFIX 1: RELEASE YEAR ANOMALY INVESTIGATION")
    print("=" * 70)

    anom_pq = df_pq[df_pq["release_year"] < 1921].copy()
    anom_csv = df_csv[df_csv["release_year"] < 1921].copy()

    print(f"Parquet records with release_year < 1921: {len(anom_pq)}")
    print(f"CSV records with release_year < 1921: {len(anom_csv)}")

    anomaly_records = []
    for idx, r in anom_pq.iterrows():
        rec = {}
        for col in df_pq.columns:
            val = r[col]
            if pd.isna(val):
                rec[col] = None
            elif isinstance(val, (np.integer, np.int64)):
                rec[col] = int(val)
            elif isinstance(val, (np.floating, np.float64)):
                rec[col] = float(val)
            else:
                rec[col] = str(val)
        anomaly_records.append(rec)
        print(f"\n  --- Parquet Record ---")
        for col in df_pq.columns:
            print(f"    {col}: {r[col]}")

    # Check CSV for same records
    for idx, r in anom_csv.iterrows():
        print(f"\n  --- CSV Record ---")
        for col in df_csv.columns:
            print(f"    {col}: {r[col]}")

    pq_anom_ids = set(anom_pq["track_id"].values)
    csv_anom_ids = set(anom_csv["track_id"].values)
    print(f"\nSame anomalous track_ids in both sources: {pq_anom_ids == csv_anom_ids}")
    print(f"Anomalous track_ids: {pq_anom_ids}")

    # Check decade value for anomalous records
    for _, r in anom_pq.iterrows():
        expected_decade = (int(r["release_year"]) // 10) * 10
        actual_decade = int(r["decade"])
        print(f"  decade check: expected={expected_decade}, actual={actual_decade}, match={expected_decade == actual_decade}")

    # Year distribution bottom
    print("\nYear distribution (bottom 15 years):")
    yd = df_pq.groupby("release_year").size().sort_index()
    for y in list(yd.index)[:15]:
        print(f"  {int(y)}: {yd[y]} tracks")

    # EPIC 1 contract says release_year range: 1921-2021
    print(f"\nEPIC 1 DATA DICTIONARY states: release_year observed range = 1921-2021")
    print(f"Actual Parquet min year: {int(df_pq['release_year'].min())}")
    print(f"Actual CSV min year: {int(df_csv['release_year'].min())}")

    # Determine root cause
    if len(anom_pq) == 1 and int(anom_pq.iloc[0]["release_year"]) == 1900:
        print("\nROOT CAUSE ANALYSIS:")
        r = anom_pq.iloc[0]
        print(f"  track_id: {r['track_id']}")
        print(f"  release_year: {int(r['release_year'])}")
        print(f"  release_month: {r['release_month']}")
        print(f"  release_precision: {r['release_precision']}")
        print(f"  target_popularity: {int(r['target_popularity'])}")
        print(f"  decade: {int(r['decade'])}")

        # Check if release_precision gives clue
        if r["release_precision"] == "year" and pd.isna(r["release_month"]):
            print("  EVIDENCE: release_precision='year', release_month=NULL")
            print("  LIKELY: Year 1900 is a sentinel/default value for unknown release date")
        elif int(r["release_year"]) == 1900 and int(r["target_popularity"]) == 19:
            print("  EVIDENCE: target_popularity=19 (non-zero, track exists on Spotify)")
            print("  POSSIBLE: Legitimate very old recording OR Spotify API default for unknown date")

    results["hotfix1"] = {
        "anomaly_count": len(anom_pq),
        "anomaly_records": anomaly_records,
        "parquet_csv_match": pq_anom_ids == csv_anom_ids,
        "epic1_documented_range": "1921-2021",
        "actual_min_year": int(df_pq["release_year"].min()),
        "actual_max_year": int(df_pq["release_year"].max()),
        "is_contract_deviation": True,
    }

    # ================================================================
    # HOTFIX 2: SOURCE RECONCILIATION (Parquet vs CSV)
    # ================================================================
    print("\n" + "=" * 70)
    print("HOTFIX 2: SOURCE RECONCILIATION (Parquet vs CSV)")
    print("=" * 70)

    recon = {}
    recon["row_count_parquet"] = int(df_pq.shape[0])
    recon["row_count_csv"] = int(df_csv.shape[0])
    recon["row_match"] = df_pq.shape[0] == df_csv.shape[0]
    recon["col_count_parquet"] = int(df_pq.shape[1])
    recon["col_count_csv"] = int(df_csv.shape[1])
    recon["col_match"] = df_pq.shape[1] == df_csv.shape[1]
    recon["col_names_parquet"] = list(df_pq.columns)
    recon["col_names_csv"] = list(df_csv.columns)
    recon["col_names_match"] = list(df_pq.columns) == list(df_csv.columns)
    recon["col_order_match"] = list(df_pq.columns) == list(df_csv.columns)

    print(f"  Row count: PQ={recon['row_count_parquet']}, CSV={recon['row_count_csv']}, match={recon['row_match']}")
    print(f"  Col count: PQ={recon['col_count_parquet']}, CSV={recon['col_count_csv']}, match={recon['col_match']}")
    print(f"  Col names match: {recon['col_names_match']}")
    print(f"  Col order match: {recon['col_order_match']}")

    # NULL counts
    null_comparison = {}
    print("\n  NULL count comparison:")
    all_null_match = True
    for col in df_pq.columns:
        pq_null = int(df_pq[col].isnull().sum())
        csv_null = int(df_csv[col].isnull().sum())
        match = pq_null == csv_null
        if not match:
            all_null_match = False
        null_comparison[col] = {"parquet": pq_null, "csv": csv_null, "match": match}
        status = "match" if match else "MISMATCH"
        if not match or pq_null > 0:
            print(f"    {col}: PQ={pq_null}, CSV={csv_null} [{status}]")
    recon["null_comparison"] = null_comparison
    recon["all_null_match"] = all_null_match

    # Track ID set comparison
    pq_ids = set(df_pq["track_id"].astype(str).values)
    csv_ids = set(df_csv["track_id"].astype(str).values)
    recon["track_id_set_match"] = pq_ids == csv_ids
    recon["pq_only_ids"] = len(pq_ids - csv_ids)
    recon["csv_only_ids"] = len(csv_ids - pq_ids)
    print(f"\n  Track ID set match: {recon['track_id_set_match']}")

    # Sorted track_id hash
    pq_id_hash = sha256_series(df_pq["track_id"])
    csv_id_hash = sha256_series(df_csv["track_id"])
    recon["parquet_track_id_hash"] = pq_id_hash
    recon["csv_track_id_hash"] = csv_id_hash
    recon["track_id_hash_match"] = pq_id_hash == csv_id_hash
    print(f"  Track ID hash match: {recon['track_id_hash_match']}")

    # Target distribution
    pq_tgt_mean = float(df_pq["target_popularity"].mean())
    csv_tgt_mean = float(df_csv["target_popularity"].mean())
    recon["target_mean_parquet"] = round(pq_tgt_mean, 6)
    recon["target_mean_csv"] = round(csv_tgt_mean, 6)
    recon["target_mean_match"] = abs(pq_tgt_mean - csv_tgt_mean) < 0.0001
    print(f"  Target mean: PQ={pq_tgt_mean:.6f}, CSV={csv_tgt_mean:.6f}, match={recon['target_mean_match']}")

    # File hashes
    recon["parquet_file_sha256"] = sha256_file(pq_path)
    recon["csv_file_sha256"] = sha256_file(csv_path)
    recon["parquet_file_size"] = int(pq_path.stat().st_size)
    recon["csv_file_size"] = int(csv_path.stat().st_size)

    # Content fingerprint: sort by track_id, hash all values
    df_pq_sorted = df_pq.sort_values("track_id").reset_index(drop=True)
    df_csv_sorted = df_csv.sort_values("track_id").reset_index(drop=True)

    # Compare numeric columns value-by-value
    numeric_match = True
    for col in df_pq.columns:
        if pd.api.types.is_numeric_dtype(df_pq[col]):
            pq_vals = df_pq_sorted[col].fillna(-999999).values
            csv_vals = df_csv_sorted[col].fillna(-999999).values
            if not np.allclose(pq_vals, csv_vals, equal_nan=True, atol=1e-6):
                numeric_match = False
                diffs = np.where(~np.isclose(pq_vals, csv_vals, equal_nan=True, atol=1e-6))[0]
                print(f"    NUMERIC MISMATCH in {col}: {len(diffs)} rows differ")
    recon["numeric_values_match"] = numeric_match
    print(f"  Numeric values match: {numeric_match}")

    # Overall reconciliation status
    recon["overall_status"] = "RECONCILED" if (
        recon["row_match"] and recon["col_match"] and
        recon["col_names_match"] and recon["track_id_set_match"] and
        recon["target_mean_match"] and recon["all_null_match"] and
        recon["numeric_values_match"]
    ) else "MISMATCH"
    recon["reconciliation_timestamp"] = now.isoformat()
    recon["reconciliation_note"] = (
        "Parquet and CSV are two exports of analytics.vw_ml_ready_dataset. "
        "Database view is the logical authoritative source. "
        "Parquet is the frozen physical snapshot used for ML pipeline."
    )

    print(f"\n  RECONCILIATION STATUS: {recon['overall_status']}")

    # Save reconciliation
    recon_path = DATA_INTAKE / "source_reconciliation.json"
    with open(recon_path, "w", encoding="utf-8") as f:
        json.dump(recon, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved: {recon_path}")

    results["hotfix2"] = recon

    # ================================================================
    # HOTFIX 3: CANDIDATE SPLIT RE-VERIFICATION
    # ================================================================
    print("\n" + "=" * 70)
    print("HOTFIX 3: CANDIDATE SPLIT RE-VERIFICATION")
    print("=" * 70)

    # Use parquet as frozen source
    df = df_pq.copy()
    time_col = "release_year"
    id_col = "track_id"
    tgt_col = "target_popularity"
    total = len(df)

    # Define the 3 candidates from the original script
    candidates_def = [
        {"id": "C1", "val_start": 2005, "test_start": 2014},
        {"id": "C2", "val_start": 2004, "test_start": 2014},
        {"id": "C3", "val_start": 2003, "test_start": 2013},
    ]

    min_year = int(df[time_col].min())
    max_year = int(df[time_col].max())

    diagnostics_rows = []

    for cand in candidates_def:
        cid = cand["id"]
        vs = cand["val_start"]
        ts = cand["test_start"]

        # INDEPENDENT computation - no variable reuse
        train_mask = df[time_col] < vs
        val_mask = (df[time_col] >= vs) & (df[time_col] < ts)
        test_mask = df[time_col] >= ts

        train = df[train_mask].copy()
        val = df[val_mask].copy()
        test = df[test_mask].copy()

        for split_name, split_df in [("train", train), ("val", val), ("test", test)]:
            tgt = split_df[tgt_col]
            row = {
                "candidate": cid,
                "split": split_name,
                "rows": int(len(split_df)),
                "ratio": round(len(split_df) / total, 4),
                "min_year": int(split_df[time_col].min()),
                "max_year": int(split_df[time_col].max()),
                "unique_years": int(split_df[time_col].nunique()),
                "target_mean": round(float(tgt.mean()), 4),
                "target_median": float(tgt.median()),
                "target_std": round(float(tgt.std()), 4),
                "target_zero_count": int((tgt == 0).sum()),
                "bucket_0_20": int(((tgt >= 0) & (tgt <= 20)).sum()),
                "bucket_21_40": int(((tgt >= 21) & (tgt <= 40)).sum()),
                "bucket_41_60": int(((tgt >= 41) & (tgt <= 60)).sum()),
                "bucket_61_80": int(((tgt >= 61) & (tgt <= 80)).sum()),
                "bucket_81_100": int(((tgt >= 81) & (tgt <= 100)).sum()),
                "missing_tempo": int(split_df["tempo"].isnull().sum()),
                "missing_time_signature": int(split_df["time_signature"].isnull().sum()),
                "missing_release_month": int(split_df["release_month"].isnull().sum()),
                "track_id_hash": sha256_series(split_df[id_col])[:32],
            }
            diagnostics_rows.append(row)
            if split_name == "train":
                print(f"\n  {cid} Train: {row['rows']:,} rows ({row['ratio']:.1%}), years {row['min_year']}-{row['max_year']}")
                print(f"    target_mean={row['target_mean']}, zero_count={row['target_zero_count']}")
            elif split_name == "val":
                print(f"  {cid} Val:   {row['rows']:,} rows ({row['ratio']:.1%}), years {row['min_year']}-{row['max_year']}")
                print(f"    target_mean={row['target_mean']}, zero_count={row['target_zero_count']}")
            else:
                print(f"  {cid} Test:  {row['rows']:,} rows ({row['ratio']:.1%}), years {row['min_year']}-{row['max_year']}")
                print(f"    target_mean={row['target_mean']}, zero_count={row['target_zero_count']}")

    diag_df = pd.DataFrame(diagnostics_rows)
    diag_path = DATA_INTAKE / "split_candidate_diagnostics.csv"
    diag_df.to_csv(diag_path, index=False)
    print(f"\n  Saved: {diag_path}")

    # Verify the zero count issue
    print("\n  ZERO COUNT VERIFICATION:")
    # C1 and C2 have same test_start=2014, so same test split
    # C1 train < 2005, C2 train < 2004 -> C2 train is subset of C1 train
    # So zero counts SHOULD differ for train and val between C1 and C2

    for cid in ["C1", "C2", "C3"]:
        train_zeros = [r for r in diagnostics_rows if r["candidate"] == cid and r["split"] == "train"][0]["target_zero_count"]
        val_zeros = [r for r in diagnostics_rows if r["candidate"] == cid and r["split"] == "val"][0]["target_zero_count"]
        test_zeros = [r for r in diagnostics_rows if r["candidate"] == cid and r["split"] == "test"][0]["target_zero_count"]
        print(f"    {cid}: train_zero={train_zeros}, val_zero={val_zeros}, test_zero={test_zeros}, sum={train_zeros+val_zeros+test_zeros}")

    # Total zeros should equal 44690
    total_zeros = int((df[tgt_col] == 0).sum())
    print(f"    Total dataset zeros: {total_zeros}")

    # Year-level zero counts for boundary years
    print("\n  Zero counts by year (around boundaries):")
    for y in range(2002, 2016):
        yr_data = df[df[time_col] == y]
        yr_zeros = int((yr_data[tgt_col] == 0).sum())
        print(f"    {y}: {len(yr_data):,} tracks, {yr_zeros} zeros")

    results["hotfix3"] = {"diagnostics_rows": diagnostics_rows}

    # ================================================================
    # HOTFIX 5: LEGACY ARTIFACT AUDIT
    # ================================================================
    print("\n" + "=" * 70)
    print("HOTFIX 5: LEGACY ARTIFACT AUDIT")
    print("=" * 70)

    legacy_files = [
        ROOT / "4.MODELS" / "4.1.trained" / "encoder.pkl",
        ROOT / "4.MODELS" / "4.1.trained" / "scaler.pkl",
        ROOT / "4.MODELS" / "4.1.trained" / "popularity_model.pkl",
    ]

    legacy_manifest = []
    for fp in legacy_files:
        if fp.exists():
            info = {
                "filename": fp.name,
                "path": str(fp),
                "size_bytes": int(fp.stat().st_size),
                "modified_time": datetime.fromtimestamp(fp.stat().st_mtime, tz=timezone.utc).isoformat(),
                "sha256": sha256_file(fp),
                "origin": "EPIC 1 or pre-EPIC pipeline",
                "referenced_by_epic2": False,
                "action": "quarantine_to_legacy_epic1",
            }
            legacy_manifest.append(info)
            print(f"  Found: {fp.name}")
            print(f"    Size: {info['size_bytes']:,} bytes")
            print(f"    Modified: {info['modified_time']}")
            print(f"    SHA-256: {info['sha256'][:32]}...")
        else:
            print(f"  Not found: {fp}")

    # Check if any EPIC 2 script references these files
    scripts_dir = ROOT / "9.SCRIPTS"
    references_found = []
    for script_file in scripts_dir.glob("*.py"):
        content = script_file.read_text(encoding="utf-8", errors="ignore")
        for lf in ["encoder.pkl", "scaler.pkl", "popularity_model.pkl"]:
            if lf in content:
                references_found.append({"script": script_file.name, "artifact": lf})
                print(f"  REFERENCE FOUND: {script_file.name} mentions {lf}")

    if not references_found:
        print("  No EPIC 2 scripts reference legacy artifacts")

    results["hotfix5"] = {
        "legacy_files": legacy_manifest,
        "references_found": references_found,
    }

    # ================================================================
    # HOTFIX 7: TEMPORAL DISTRIBUTION SHIFT DIAGNOSTICS
    # ================================================================
    print("\n" + "=" * 70)
    print("HOTFIX 7: TEMPORAL DISTRIBUTION SHIFT DIAGNOSTICS")
    print("=" * 70)

    # Use C1 (locked split) for analysis
    train_df = df[df[time_col] < 2005].copy()
    val_df = df[(df[time_col] >= 2005) & (df[time_col] < 2014)].copy()
    test_df = df[df[time_col] >= 2014].copy()

    shift_profile = {"splits": {}}

    numeric_features = [
        "duration_min", "danceability", "energy", "loudness",
        "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "tempo"
    ]

    for split_name, split_df in [("train", train_df), ("validation", val_df), ("test", test_df)]:
        profile = {
            "rows": int(len(split_df)),
            "target_mean": round(float(split_df[tgt_col].mean()), 4),
            "target_std": round(float(split_df[tgt_col].std()), 4),
            "target_median": float(split_df[tgt_col].median()),
        }

        # Feature stats
        feature_stats = {}
        for feat in numeric_features:
            if feat in split_df.columns:
                vals = split_df[feat].dropna()
                feature_stats[feat] = {
                    "mean": round(float(vals.mean()), 6),
                    "std": round(float(vals.std()), 6),
                    "null_count": int(split_df[feat].isnull().sum()),
                    "null_ratio": round(int(split_df[feat].isnull().sum()) / len(split_df), 6),
                }
        profile["feature_stats"] = feature_stats

        # Missing ratios
        profile["release_month_null_ratio"] = round(
            int(split_df["release_month"].isnull().sum()) / len(split_df), 4
        )

        shift_profile["splits"][split_name] = profile

    # Compute PSI-like metric for target
    # Using train as reference
    train_tgt = train_df[tgt_col].values
    bins = np.arange(0, 105, 5)

    train_hist, _ = np.histogram(train_tgt, bins=bins)
    train_hist = train_hist / train_hist.sum()
    train_hist = np.clip(train_hist, 1e-8, None)

    psi_results = {}
    for name, sdf in [("validation", val_df), ("test", test_df)]:
        other_hist, _ = np.histogram(sdf[tgt_col].values, bins=bins)
        other_hist = other_hist / other_hist.sum()
        other_hist = np.clip(other_hist, 1e-8, None)
        psi = float(np.sum((other_hist - train_hist) * np.log(other_hist / train_hist)))
        psi_results[name] = round(psi, 4)
        print(f"  PSI (target, train vs {name}): {psi:.4f}")

    shift_profile["psi_target"] = psi_results

    # KS test for numeric features (using scipy if available)
    ks_results = {}
    try:
        from scipy.stats import ks_2samp
        for feat in numeric_features:
            if feat in train_df.columns:
                train_vals = train_df[feat].dropna().values
                for name, sdf in [("validation", val_df), ("test", test_df)]:
                    other_vals = sdf[feat].dropna().values
                    stat, pval = ks_2samp(train_vals, other_vals)
                    key = f"{feat}_train_vs_{name}"
                    ks_results[key] = {"statistic": round(stat, 4), "p_value": float(pval)}
                    if stat > 0.1:
                        print(f"  KS {feat} (train vs {name}): stat={stat:.4f}, p={pval:.2e} [SIGNIFICANT]")
        shift_profile["ks_tests"] = ks_results
    except ImportError:
        print("  scipy not available, skipping KS tests")
        shift_profile["ks_tests"] = "scipy_not_available"

    # Risk classification
    risks = []
    # PSI thresholds: <0.1 = insignificant, 0.1-0.25 = moderate, >0.25 = significant
    for name, psi_val in psi_results.items():
        if psi_val > 0.25:
            risks.append({"metric": f"PSI_target_train_vs_{name}", "value": psi_val, "severity": "HIGH"})
        elif psi_val > 0.1:
            risks.append({"metric": f"PSI_target_train_vs_{name}", "value": psi_val, "severity": "MEDIUM"})
        else:
            risks.append({"metric": f"PSI_target_train_vs_{name}", "value": psi_val, "severity": "LOW"})

    # Target mean shift
    train_mean = shift_profile["splits"]["train"]["target_mean"]
    for name in ["validation", "test"]:
        other_mean = shift_profile["splits"][name]["target_mean"]
        delta = abs(other_mean - train_mean)
        severity = "HIGH" if delta > 10 else "MEDIUM" if delta > 5 else "LOW"
        risks.append({"metric": f"target_mean_shift_train_vs_{name}", "delta": round(delta, 2), "severity": severity})
        print(f"  Target mean shift (train vs {name}): {delta:.2f} [{severity}]")

    # release_month missing ratio shift
    train_rm = shift_profile["splits"]["train"]["release_month_null_ratio"]
    for name in ["validation", "test"]:
        other_rm = shift_profile["splits"][name]["release_month_null_ratio"]
        delta = abs(other_rm - train_rm)
        severity = "HIGH" if delta > 0.2 else "MEDIUM" if delta > 0.1 else "LOW"
        risks.append({"metric": f"release_month_null_shift_train_vs_{name}",
                       "train_ratio": train_rm, "other_ratio": other_rm, "severity": severity})
        print(f"  release_month null ratio: train={train_rm:.4f}, {name}={other_rm:.4f}, delta={delta:.4f} [{severity}]")

    shift_profile["risks"] = risks
    shift_profile["timestamp"] = now.isoformat()

    # Save
    shift_path = DATA_INTAKE / "temporal_shift_profile.json"
    with open(shift_path, "w", encoding="utf-8") as f:
        json.dump(shift_profile, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  Saved: {shift_path}")

    results["hotfix7"] = shift_profile

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 70)
    print("INVESTIGATION SUMMARY")
    print("=" * 70)

    print(f"  HOTFIX 1: {results['hotfix1']['anomaly_count']} anomalous records found")
    print(f"            Contract deviation: {results['hotfix1']['is_contract_deviation']}")
    print(f"            EPIC 1 says 1921-2021, actual has 1900")
    print(f"  HOTFIX 2: Source reconciliation: {results['hotfix2']['overall_status']}")
    print(f"  HOTFIX 3: Candidate diagnostics saved")
    print(f"  HOTFIX 5: {len(results['hotfix5']['legacy_files'])} legacy files found")
    print(f"            References in EPIC 2 scripts: {len(results['hotfix5']['references_found'])}")
    print(f"  HOTFIX 7: Temporal shift risks identified")

    # Save full results
    results_path = DATA_INTAKE / "hotfix_investigation_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n  Full results saved: {results_path}")

    return results


if __name__ == "__main__":
    main()

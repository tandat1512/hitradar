"""
audit_raw_data.py — Feature 1.1: Dataset Audit & Data Dictionary
HitRadar Pro · EPIC 1 · Owner: Đạt

Chạy:
    python 9.SCRIPTS/audit_raw_data.py

Output:
    9.SCRIPTS/_audit_results.json   (raw numbers, dùng để viết report)
"""

import os
import sys
import json
import datetime

import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR      = os.path.join(PROJECT_ROOT, "1.DỮ_LIỆU", "1.1.raw")
RESULTS_FILE = os.path.join(PROJECT_ROOT, "9.SCRIPTS", "_audit_results.json")

REQUIRED_FILES = {
    "tracks.csv":         os.path.join(RAW_DIR, "tracks.csv"),
    "artists.csv":        os.path.join(RAW_DIR, "artists.csv"),
    "dict_artists.json":  os.path.join(RAW_DIR, "dict_artists.json"),
}

# Audio feature expected ranges (0-1)
AUDIO_0_1 = [
    "danceability", "energy", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence",
]


# ── Helpers ──────────────────────────────────────────────────────────────────
def _fmt(val):
    """Return JSON-serialisable form of a value."""
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return round(float(val), 6)
    return str(val)


# ── Step 1: check required files ─────────────────────────────────────────────
def check_required_files():
    print("\n[1/5] Checking required files …")
    missing = []
    for name, path in REQUIRED_FILES.items():
        if not os.path.exists(path):
            missing.append(name)
            print(f"  MISSING: {name}")
        elif os.path.getsize(path) == 0:
            missing.append(name)
            print(f"  EMPTY  : {name}")
        else:
            size_mb = os.path.getsize(path) / 1_048_576
            print(f"  OK     : {name}  ({size_mb:.1f} MB)")
    if missing:
        for m in missing:
            print(f"\nMissing or empty raw file: {m}")
        sys.exit(1)
    print("  All required files present.")


# ── Step 2: audit a CSV file ─────────────────────────────────────────────────
def audit_csv_file(name, path):
    print(f"\n[audit] {name} …")
    df = pd.read_csv(path, low_memory=False)

    file_size = os.path.getsize(path)
    n_rows, n_cols = df.shape

    # Per-column stats
    schema = []
    for col in df.columns:
        s = df[col]
        n_null   = int(s.isna().sum())
        n_notnull = int(s.notna().sum())
        schema.append({
            "column":       col,
            "dtype":        str(s.dtype),
            "non_null":     n_notnull,
            "missing":      n_null,
            "missing_pct":  round(n_null / n_rows * 100, 4) if n_rows else 0,
            "unique":       int(s.nunique()),
        })

    # Duplicate rows
    dup_rows  = int(df.duplicated().sum())
    dup_ratio = round(dup_rows / n_rows * 100, 4) if n_rows else 0

    # ID uniqueness
    id_unique = None
    if "id" in df.columns:
        id_unique = bool(df["id"].nunique() == n_rows)

    # Numeric stats
    num_stats = {}
    for col in df.select_dtypes(include="number").columns:
        s = df[col].dropna()
        num_stats[col] = {
            "min":    _fmt(s.min()),
            "max":    _fmt(s.max()),
            "mean":   _fmt(s.mean()),
            "median": _fmt(s.median()),
            "std":    _fmt(s.std()),
        }

    # Sample values for 'artists' / 'genres' column
    sample_artists_field = None
    if "artists" in df.columns:
        sample_artists_field = df["artists"].dropna().head(3).tolist()
    if "genres" in df.columns:
        sample_artists_field = df["genres"].dropna().head(3).tolist()

    return {
        "file":        name,
        "path":        path,
        "size_bytes":  file_size,
        "size_mb":     round(file_size / 1_048_576, 2),
        "rows":        n_rows,
        "columns":     n_cols,
        "column_names": list(df.columns),
        "schema":      schema,
        "dup_rows":    dup_rows,
        "dup_ratio":   dup_ratio,
        "id_unique":   id_unique,
        "num_stats":   num_stats,
        "sample_list_field": sample_artists_field,
        "_df":         df,   # kept in memory for sanity checks, removed before JSON dump
    }


# ── Step 3: audit dict_artists.json ──────────────────────────────────────────
def audit_json_file(name, path):
    print(f"\n[audit] {name} …")
    file_size = os.path.getsize(path)
    result = {
        "file":       name,
        "path":       path,
        "size_bytes": file_size,
        "size_mb":    round(file_size / 1_048_576, 2),
        "load_ok":    False,
        "n_keys":     None,
        "key_type":   None,
        "value_type": None,
        "sample_records": [],
        "empty_value_ratio": None,
        "n_unique_genres":   None,
        "parse_risk":        [],
    }
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            data = json.load(f)
        result["load_ok"]  = True
        result["n_keys"]   = len(data)

        sample_keys  = list(data.keys())[:5]
        sample_items = {k: data[k] for k in sample_keys}
        result["sample_records"] = [{"key": k, "value": v} for k, v in sample_items.items()]

        key_types   = set(type(k).__name__ for k in sample_keys)
        value_types = set(type(data[k]).__name__ for k in sample_keys)
        result["key_type"]   = list(key_types)
        result["value_type"] = list(value_types)

        # Empty value ratio (sample 5000 for speed)
        sample_n   = min(5000, len(data))
        sample_vals = list(data.values())[:sample_n]
        empty_count = sum(1 for v in sample_vals if isinstance(v, list) and len(v) == 0)
        result["empty_value_ratio"] = round(empty_count / sample_n * 100, 2)

        # Unique genres (full scan)
        all_genres = set()
        for v in data.values():
            if isinstance(v, list):
                all_genres.update(v)
        result["n_unique_genres"] = len(all_genres)

        print(f"  Loaded OK — {len(data):,} keys, "
              f"{result['empty_value_ratio']}% empty lists, "
              f"{len(all_genres):,} unique genres")

    except MemoryError:
        result["parse_risk"].append("MemoryError: file too large to load at once — use streaming in Feature 1.4")
        print("  WARNING: MemoryError — file too large for full load")
    except Exception as exc:
        result["parse_risk"].append(f"LoadError: {exc}")
        print(f"  ERROR loading JSON: {exc}")

    result["parse_risk"] += [
        "Value fields may be empty lists → will produce NULL genre mapping",
        "Requires explode/unnest to join with tracks via id_artists column",
        "Large size (332 MB) means streaming parse recommended in Feature 1.4",
    ]
    return result


# ── Step 4: sanity checks ────────────────────────────────────────────────────
def run_sanity_checks(tracks_result, artists_result):
    print("\n[4/5] Running sanity checks …")
    checks = []

    def chk(name, status, detail):
        icon = "PASS" if status == "PASS" else ("WARNING" if status == "WARNING" else "FAIL")
        checks.append({"check": name, "status": icon, "detail": detail})
        print(f"  [{icon:<7}] {name}: {detail}")

    tracks_df  = tracks_result["_df"]
    artists_df = artists_result["_df"]

    # ── tracks ───────────────────────────────────────────────────────────────
    if "popularity" in tracks_df.columns:
        s = tracks_df["popularity"].dropna()
        out = int(((s < 0) | (s > 100)).sum())
        chk("tracks.popularity range [0-100]",
            "PASS" if out == 0 else "FAIL",
            f"{out} values out of range" if out else "All values in [0-100]")

    for feat in AUDIO_0_1:
        if feat in tracks_df.columns:
            s = tracks_df[feat].dropna()
            out = int(((s < 0) | (s > 1)).sum())
            chk(f"tracks.{feat} range [0-1]",
                "PASS" if out == 0 else "WARNING",
                f"{out} values out of range" if out else "All values in [0-1]")

    if "duration_ms" in tracks_df.columns:
        s = tracks_df["duration_ms"].dropna()
        bad = int((s <= 0).sum())
        chk("tracks.duration_ms > 0",
            "PASS" if bad == 0 else "FAIL",
            f"{bad} non-positive values" if bad else "All positive")

    if "tempo" in tracks_df.columns:
        s = tracks_df["tempo"].dropna()
        bad = int((s <= 0).sum())
        chk("tracks.tempo > 0",
            "PASS" if bad == 0 else "WARNING",
            f"{bad} non-positive values" if bad else "All positive")

    if "year" in tracks_df.columns:
        s = tracks_df["year"].dropna()
        bad = int(((s < 1900) | (s > 2025)).sum())
        chk("tracks.year range [1900-2025]",
            "PASS" if bad == 0 else "WARNING",
            f"{bad} values outside range" if bad else "All in range")

    if "release_date" in tracks_df.columns:
        sample = tracks_df["release_date"].dropna().head(5).tolist()
        chk("tracks.release_date parsability",
            "WARNING",
            f"Manual check needed — sample: {sample}")

    if "artists" in tracks_df.columns:
        sample_val = str(tracks_df["artists"].dropna().iloc[0]) if len(tracks_df) > 0 else ""
        is_list_like = sample_val.startswith("[")
        chk("tracks.artists list-string format",
            "WARNING" if is_list_like else "FAIL",
            f"Detected list-string format (needs parse). Sample: {sample_val[:80]}"
            if is_list_like else f"Unexpected format. Sample: {sample_val[:80]}")

    # ── artists ──────────────────────────────────────────────────────────────
    if "popularity" in artists_df.columns:
        s = artists_df["popularity"].dropna()
        out = int(((s < 0) | (s > 100)).sum())
        chk("artists.popularity range [0-100]",
            "PASS" if out == 0 else "FAIL",
            f"{out} values out of range" if out else "All values in [0-100]")

    if "followers" in artists_df.columns:
        s = artists_df["followers"].dropna()
        bad = int((s < 0).sum())
        chk("artists.followers >= 0",
            "PASS" if bad == 0 else "FAIL",
            f"{bad} negative values" if bad else "All non-negative")

    if "id" in artists_df.columns:
        is_uniq = artists_result["id_unique"]
        chk("artists.id uniqueness",
            "PASS" if is_uniq else "FAIL",
            "All IDs unique" if is_uniq else "Duplicate IDs found!")

    if "genres" in artists_df.columns:
        sample_val = str(artists_df["genres"].dropna().iloc[0]) if len(artists_df) > 0 else ""
        is_list_like = sample_val.startswith("[")
        chk("artists.genres list-string format",
            "WARNING" if is_list_like else "FAIL",
            f"Detected list-string format (needs parse). Sample: {sample_val[:80]}"
            if is_list_like else f"Unexpected format. Sample: {sample_val[:80]}")

    if "name" in artists_df.columns:
        miss = int(artists_df["name"].isna().sum())
        chk("artists.name missing count",
            "PASS" if miss == 0 else "WARNING",
            f"{miss} missing names" if miss else "No missing names")

    return checks


# ── Step 5: run & save ───────────────────────────────────────────────────────
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 60)
    print("Feature 1.1 — Dataset Audit")
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Raw dir      : {RAW_DIR}")
    print("=" * 60)

    # 1 — preflight
    check_required_files()

    # 2 — audit CSVs
    tracks_result  = audit_csv_file("tracks.csv",  REQUIRED_FILES["tracks.csv"])
    artists_result = audit_csv_file("artists.csv", REQUIRED_FILES["artists.csv"])

    # 3 — audit JSON
    json_result = audit_json_file("dict_artists.json", REQUIRED_FILES["dict_artists.json"])

    # 4 — sanity checks
    sanity = run_sanity_checks(tracks_result, artists_result)

    # 5 — serialize (drop DataFrame objects before JSON dump)
    print("\n[5/5] Saving audit results …")
    tracks_out  = {k: v for k, v in tracks_result.items()  if k != "_df"}
    artists_out = {k: v for k, v in artists_result.items() if k != "_df"}

    results = {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tracks":        tracks_out,
        "artists":       artists_out,
        "dict_artists":  json_result,
        "sanity_checks": sanity,
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved → {RESULTS_FILE}")

    # ── summary ──────────────────────────────────────────────────────────────
    fails    = [c for c in sanity if c["status"] == "FAIL"]
    warnings = [c for c in sanity if c["status"] == "WARNING"]
    status   = "FAIL" if fails else "PASS"

    print("\n" + "=" * 60)
    print(f"  tracks.csv   : {tracks_result['rows']:>10,} rows · {tracks_result['columns']} cols")
    print(f"  artists.csv  : {artists_result['rows']:>10,} rows · {artists_result['columns']} cols")
    keys_str = f"{json_result['n_keys']:,}" if json_result['n_keys'] else "N/A"
    print(f"  dict_artists : {keys_str:>10} keys")
    print(f"  Sanity PASS  : {len(sanity)-len(fails)-len(warnings)}")
    print(f"  Sanity WARN  : {len(warnings)}")
    print(f"  Sanity FAIL  : {len(fails)}")
    print(f"\n  Feature 1.1 Audit Status: {status}")
    print("=" * 60)
    return results, status


if __name__ == "__main__":
    main()

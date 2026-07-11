"""
validate_ml_ready_dataset.py — Feature 1.8: ML-Ready Dataset Validation
HitRadar Pro | EPIC 1 — Data Foundation

Read-only validation of analytics.vw_ml_ready_dataset and exported files.
Writes: 6.TAI_LIEU/6.1.bao_cao/ML_READY_DATASET_VALIDATION_REPORT.md

Password: set PGPASSWORD env var (never hardcode).

Usage:
  python 9.SCRIPTS/validate_ml_ready_dataset.py [--base-dir PATH]
    [--database DATABASE] [--host HOST] [--port PORT] [--user USER]
"""
import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: pip install psycopg2-binary")
    sys.exit(1)

VIEW = "analytics.vw_ml_ready_dataset"
EXPECTED_ROWS = 586_672

REQUIRED_COLUMNS = [
    "track_id", "target_popularity", "duration_min", "explicit",
    "release_year", "release_month", "decade", "release_precision",
    "danceability", "energy", "key", "loudness", "mode",
    "speechiness", "acousticness", "instrumentalness", "liveness",
    "valence", "tempo", "time_signature",
]

FORBIDDEN_EXACT = {
    "popularity", "artist_popularity", "artists_popularity",
    "artist_popularity_dashboard_only", "avg_artist_popularity",
    "avg_track_popularity", "avg_genre_popularity",
    "popularity_bucket", "popularity_group", "future_popularity",
    "train_split", "test_split", "split", "label_encoded",
}

FORBIDDEN_PREFIXES = ("scaled_", "imputed_")

NUMERIC_COLUMNS = [
    "target_popularity", "duration_min", "release_year", "release_month",
    "decade", "danceability", "energy", "key", "loudness", "mode",
    "speechiness", "acousticness", "instrumentalness", "liveness",
    "valence", "tempo", "time_signature",
]

AUDIO_FEATURES = [
    "danceability", "energy", "key", "loudness", "mode",
    "speechiness", "acousticness", "instrumentalness", "liveness",
    "valence", "tempo", "time_signature",
]

POPULARITY_BUCKETS = [
    (0, 20, "0-20"),
    (21, 40, "21-40"),
    (41, 60, "41-60"),
    (61, 80, "61-80"),
    (81, 100, "81-100"),
]

PASS = "PASS"
WARN = "PASS_WITH_WARNINGS"
FAIL = "FAIL"


def parse_args():
    p = argparse.ArgumentParser(description="HitRadar Feature 1.8 ML-Ready Dataset Validation")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=5432)
    p.add_argument("--user", default="postgres")
    p.add_argument("--database", default="hitradar")
    p.add_argument("--base-dir", dest="base_dir", default=None)
    return p.parse_args()


def resolve_paths(args):
    base = Path(args.base_dir).resolve() if args.base_dir else Path(__file__).resolve().parents[1]
    report_dir = base / "6.TAI_LIEU" / "6.1.bao_cao"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "ML_READY_DATASET_VALIDATION_REPORT.md"
    csv_path = base / "5.DATA" / "processed" / "ml_ready_dataset.csv"
    parquet_path = base / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
    return base, report_path, csv_path, parquet_path


def get_conn(args):
    password = os.environ.get("PGPASSWORD")
    if not password:
        print("ERROR: PGPASSWORD not set.")
        sys.exit(1)
    return psycopg2.connect(
        host=args.host, port=args.port, user=args.user,
        password=password, dbname=args.database, connect_timeout=30,
    )


def sev(s):
    return f"**{s}**"


def check_view_exists(cur):
    cur.execute("""
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'analytics' AND table_name = 'vw_ml_ready_dataset'
    """)
    exists = cur.fetchone() is not None
    return {"exists": exists, "status": PASS if exists else FAIL}


def check_row_count(cur):
    cur.execute(f"SELECT COUNT(*) FROM {VIEW}")
    count = cur.fetchone()[0]
    status = PASS if count == EXPECTED_ROWS else FAIL
    note = f"{count:,} (expected {EXPECTED_ROWS:,})"
    return {"count": count, "expected": EXPECTED_ROWS, "status": status, "note": note}


def get_columns(cur):
    cur.execute("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = 'analytics' AND table_name = 'vw_ml_ready_dataset'
        ORDER BY ordinal_position
    """)
    return cur.fetchall()


def check_required_columns(columns):
    col_names = [c[0] for c in columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in col_names]
    extra = [c for c in col_names if c not in REQUIRED_COLUMNS]
    status = PASS if not missing and not extra else FAIL
    return {
        "col_names": col_names,
        "missing": missing,
        "extra": extra,
        "status": status,
    }


def check_forbidden_columns(col_names):
    leakage = []
    for col in col_names:
        low = col.lower()
        if low in FORBIDDEN_EXACT:
            leakage.append(col)
        elif low.startswith(FORBIDDEN_PREFIXES):
            leakage.append(col)
        elif low == "popularity" and low != "target_popularity":
            leakage.append(col)
    # popularity raw (not target_popularity)
    for col in col_names:
        if col.lower() == "popularity":
            leakage.append(col)
    leakage = list(dict.fromkeys(leakage))
    status = PASS if not leakage else FAIL
    return {"leakage": leakage, "status": status}


def check_track_id(cur):
    cur.execute(f"""
        SELECT
            COUNT(*) FILTER (WHERE track_id IS NULL) AS null_count,
            COUNT(*) - COUNT(DISTINCT track_id) AS dup_count
        FROM {VIEW}
    """)
    null_count, dup_count = cur.fetchone()
    status = PASS if null_count == 0 and dup_count == 0 else FAIL
    return {
        "null_count": null_count,
        "dup_count": dup_count,
        "non_training": True,
        "status": status,
    }


def check_target(cur):
    cur.execute(f"""
        SELECT
            COUNT(*) FILTER (WHERE target_popularity IS NULL) AS null_count,
            MIN(target_popularity) AS min_val,
            MAX(target_popularity) AS max_val,
            COUNT(*) FILTER (WHERE target_popularity = 0) AS zero_count
        FROM {VIEW}
    """)
    null_count, min_val, max_val, zero_count = cur.fetchone()

    bucket_rows = []
    for lo, hi, label in POPULARITY_BUCKETS:
        cur.execute(f"""
            SELECT COUNT(*) FROM {VIEW}
            WHERE target_popularity >= %s AND target_popularity <= %s
        """, (lo, hi))
        bucket_rows.append((label, cur.fetchone()[0]))

    valid_range = (min_val is not None and min_val >= 0
                   and max_val is not None and max_val <= 100)
    status = PASS if null_count == 0 and valid_range else FAIL
    return {
        "null_count": null_count,
        "min_val": min_val,
        "max_val": max_val,
        "zero_count": zero_count,
        "buckets": bucket_rows,
        "status": status,
    }


def check_nulls(cur):
    metrics = {}
    for col in ["tempo", "time_signature", "release_month"] + AUDIO_FEATURES:
        cur.execute(f"""
            SELECT COUNT(*) FROM {VIEW} WHERE {col} IS NULL
        """)
        metrics[col] = cur.fetchone()[0]
    # Carry-forward nulls in tempo, time_signature, release_month → PASS_WITH_WARNINGS
    has_known_nulls = any(
        metrics.get(col, 0) > 0
        for col in ["tempo", "time_signature", "release_month"]
    )
    status = WARN if has_known_nulls else PASS
    return {"metrics": metrics, "status": status}


def check_dtypes(columns):
    col_map = {c[0]: (c[1], c[2]) for c in columns}
    issues = []
    numeric_types = {"integer", "bigint", "smallint", "numeric", "real", "double precision"}

    for col in NUMERIC_COLUMNS:
        if col not in col_map:
            issues.append(f"{col}: missing")
            continue
        dtype, udt = col_map[col]
        if dtype not in numeric_types and udt not in ("int2", "int4", "int8", "float4", "float8", "numeric"):
            issues.append(f"{col}: expected numeric, got {dtype}/{udt}")

    if "explicit" in col_map:
        dtype, udt = col_map["explicit"]
        if dtype != "boolean" and udt != "bool":
            issues.append(f"explicit: expected boolean, got {dtype}/{udt}")

    if "release_precision" in col_map:
        dtype, udt = col_map["release_precision"]
        if dtype not in ("text", "character varying", "USER-DEFINED") and udt not in ("text", "varchar"):
            # enum-like is OK as USER-DEFINED
            if udt not in ("text", "varchar"):
                issues.append(f"release_precision: expected text/string, got {dtype}/{udt}")

    status = PASS if not issues else FAIL
    return {"issues": issues, "col_map": col_map, "status": status}


def check_exports(csv_path, parquet_path, db_row_count):
    results = {"csv": {}, "parquet": {}}

    if csv_path.exists():
        try:
            import pandas as pd
            csv_rows = sum(1 for _ in open(csv_path, encoding="utf-8")) - 1
            results["csv"] = {
                "exists": True,
                "rows": csv_rows,
                "match": csv_rows == db_row_count,
                "path": str(csv_path),
                "size_mb": csv_path.stat().st_size / (1024 * 1024),
            }
        except Exception as e:
            results["csv"] = {"exists": True, "error": str(e), "match": False}
    else:
        results["csv"] = {"exists": False, "match": False}

    csv_status = PASS if results["csv"].get("exists") and results["csv"].get("match") else FAIL

    if parquet_path.exists():
        results["parquet"] = {
            "exists": True,
            "path": str(parquet_path),
            "size_mb": parquet_path.stat().st_size / (1024 * 1024),
        }
        parquet_status = PASS
    else:
        # Check if pyarrow/fastparquet available
        try:
            import pyarrow  # noqa: F401
            has_dep = True
        except ImportError:
            try:
                import fastparquet  # noqa: F401
                has_dep = True
            except ImportError:
                has_dep = False
        results["parquet"] = {
            "exists": False,
            "missing_dep": not has_dep,
            "note": "Parquet file not found" + (
                " — pyarrow/fastparquet not installed (WARNING only)"
                if not has_dep else " — dependency available but file missing"
            ),
        }
        parquet_status = WARN if not has_dep else FAIL

    export_status = FAIL if csv_status == FAIL else (WARN if parquet_status == WARN else PASS)
    return results, csv_status, parquet_status, export_status


def compute_overall(checks):
    hard_fail_keys = [
        "exist", "row_count", "required", "forbidden",
        "track_id", "target", "dtype", "export_csv",
    ]
    for k in hard_fail_keys:
        if checks.get(k) == FAIL:
            return FAIL

    warn_keys = ["nulls", "export_parquet"]
    if any(checks.get(k) == WARN for k in warn_keys):
        return WARN
    return PASS


def write_report(args, report_path, results, overall, now):
    r = results
    bucket_table = "\n".join(
        f"| {label} | {cnt:,} |"
        for label, cnt in r["target"]["buckets"]
    )
    null_table = "\n".join(
        f"| `{col}` | {cnt:,} |"
        for col, cnt in sorted(r["nulls"]["metrics"].items())
    )
    dtype_rows = "\n".join(
        f"| `{col}` | {info[0]} | {info[1]} |"
        for col, info in sorted(r["dtype"]["col_map"].items())
    )

    md = f"""# ML-READY DATASET VALIDATION REPORT — FEATURE 1.8

## 1. Metadata

| Field | Value |
|-------|-------|
| Feature | 1.8 — ML-Safe Dataset Handoff |
| Owner | Đạt |
| Database | `{args.database}` @ `{args.host}:{args.port}` |
| User | `{args.user}` |
| Date/Time | {now} |
| Script | `9.SCRIPTS/validate_ml_ready_dataset.py` |
| View | `{VIEW}` |
| **Overall** | **{overall}** |

---

## 2. View Existence

| Check | Result | Status |
|-------|--------|--------|
| `analytics.vw_ml_ready_dataset` exists | {'Yes' if r['exist']['exists'] else 'No'} | {sev(r['exist']['status'])} |

---

## 3. Row Count

| Metric | Value | Status |
|--------|-------|--------|
| Row count | {r['row_count']['note']} | {sev(r['row_count']['status'])} |

---

## 4. Required Columns (20)

| Check | Result | Status |
|-------|--------|--------|
| Missing columns | {r['required']['missing'] or 'None'} | {sev(r['required']['status'])} |
| Extra columns | {r['required']['extra'] or 'None'} | {sev(r['required']['status'])} |

**Columns in view:** {', '.join(f'`{c}`' for c in r['required']['col_names'])}

---

## 5. Forbidden Leakage Columns

| Check | Result | Status |
|-------|--------|--------|
| Leakage columns found | {r['forbidden']['leakage'] or 'None'} | {sev(r['forbidden']['status'])} |

---

## 6. Identifier Check — track_id

| Check | Value | Status |
|-------|-------|--------|
| NULL count | {r['track_id']['null_count']:,} | {sev(r['track_id']['status'])} |
| Duplicate count | {r['track_id']['dup_count']:,} | {sev(r['track_id']['status'])} |
| Non-training column | Yes (identifier only) | {sev(PASS)} |

---

## 7. Target Check — target_popularity

| Check | Value | Status |
|-------|-------|--------|
| NULL count | {r['target']['null_count']:,} | {sev(r['target']['status'])} |
| Min | {r['target']['min_val']} | {sev(r['target']['status'])} |
| Max | {r['target']['max_val']} | {sev(r['target']['status'])} |
| Count = 0 | {r['target']['zero_count']:,} | {sev(PASS)} |

### Popularity Bucket Distribution

| Bucket | Count |
|--------|-------|
{bucket_table}

---

## 8. Null Check (report only — no imputation)

| Column | NULL Count |
|--------|------------|
{null_table}

**Status:** {sev(r['nulls']['status'])} — NULLs in tempo/time_signature/release_month are carry-forward warnings for EPIC 2.

---

## 9. Data Type Check

| Column | data_type | udt_name |
|--------|-----------|----------|
{dtype_rows}

| Issues | {r['dtype']['issues'] or 'None'} | {sev(r['dtype']['status'])} |

---

## 10. Export File Check

### CSV

| Check | Value | Status |
|-------|-------|--------|
| File exists | {r['export']['csv'].get('exists', False)} | {sev(r['export_csv_status'])} |
| Row count | {r['export']['csv'].get('rows', 'N/A'):,} | {sev(r['export_csv_status'])} |
| Matches DB | {r['export']['csv'].get('match', False)} | {sev(r['export_csv_status'])} |
| Path | `{r['export']['csv'].get('path', 'N/A')}` | |
| Size (MB) | {r['export']['csv'].get('size_mb', 0):.2f} | |

### Parquet

| Check | Value | Status |
|-------|-------|--------|
| File exists | {r['export']['parquet'].get('exists', False)} | {sev(r['export_parquet_status'])} |
| Path | `{r['export']['parquet'].get('path', 'N/A')}` | |
| Note | {r['export']['parquet'].get('note', 'OK' if r['export']['parquet'].get('exists') else '—')} | |

---

## 11. Overall Status

**{overall}**

### Criteria
- **FAIL** if: view missing, row count wrong, missing/extra columns, leakage columns,
  track_id invalid, target invalid, dtype issues, CSV missing or row mismatch.
- **PASS_WITH_WARNINGS** if: only carry-forward nulls and/or parquet dependency warning.
- **PASS** if: no failures and no warnings.

---

*Generated by `9.SCRIPTS/validate_ml_ready_dataset.py` — Feature 1.8*
"""
    report_path.write_text(md, encoding="utf-8")
    print(f"Report written: {report_path}")


def main():
    args = parse_args()
    _, report_path, csv_path, parquet_path = resolve_paths(args)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print(f"=== Feature 1.8 — Validate ML-Ready Dataset ===")
    print(f"Time: {now}")

    conn = get_conn(args)
    cur = conn.cursor()
    results = {}

    print("1. View existence...")
    results["exist"] = check_view_exists(cur)

    print("2. Row count...")
    results["row_count"] = check_row_count(cur)

    print("3. Required columns...")
    columns = get_columns(cur)
    results["required"] = check_required_columns(columns)

    print("4. Forbidden leakage columns...")
    results["forbidden"] = check_forbidden_columns(results["required"]["col_names"])

    print("5. track_id check...")
    results["track_id"] = check_track_id(cur)

    print("6. target_popularity check...")
    results["target"] = check_target(cur)

    print("7. Null check...")
    results["nulls"] = check_nulls(cur)

    print("8. Data type check...")
    results["dtype"] = check_dtypes(columns)

    cur.close()
    conn.close()

    print("9. Export file check...")
    export_results, csv_st, parquet_st, export_st = check_exports(
        csv_path, parquet_path, results["row_count"]["count"]
    )
    results["export"] = export_results
    results["export_csv_status"] = csv_st
    results["export_parquet_status"] = parquet_st

    checks = {
        "exist": results["exist"]["status"],
        "row_count": results["row_count"]["status"],
        "required": results["required"]["status"],
        "forbidden": results["forbidden"]["status"],
        "track_id": results["track_id"]["status"],
        "target": results["target"]["status"],
        "nulls": results["nulls"]["status"],
        "dtype": results["dtype"]["status"],
        "export_csv": csv_st,
        "export_parquet": parquet_st,
    }
    overall = compute_overall(checks)

    write_report(args, report_path, results, overall, now)

    print(f"\n=== Validation Summary ===")
    print(f"  view_exists      : {results['exist']['exists']}")
    print(f"  row_count        : {results['row_count']['count']:,}")
    print(f"  column_count     : {len(results['required']['col_names'])}")
    print(f"  leakage_columns  : {results['forbidden']['leakage'] or 'None'}")
    print(f"  leakage_status   : {results['forbidden']['status']}")
    print(f"  csv_exists       : {results['export']['csv'].get('exists', False)}")
    print(f"  parquet_exists   : {results['export']['parquet'].get('exists', False)}")
    print(f"  overall_status   : {overall}")

    sys.exit(0 if overall in (PASS, WARN) else 1)


if __name__ == "__main__":
    main()

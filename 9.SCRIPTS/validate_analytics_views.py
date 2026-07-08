"""
validate_analytics_views.py — Feature 1.6: Validate Analytics Views
HitRadar Pro | EPIC 1 — Data Foundation

Checks:
  1. View existence (10 views)
  2. Query smoke test (SELECT LIMIT 5 per view)
  3. Row count sanity
  4. ML-safe column audit on vw_ml_training_dataset
  5. Genre duplicate-weighting confirmation
  6. Data quality carry-forward (vw_data_quality_report metrics)
  7. EXPLAIN ANALYZE for 4 key views

Exit codes:
  0 = PASS or PASS_WITH_WARNINGS
  1 = FAIL

Usage:
  python 9.SCRIPTS/validate_analytics_views.py [--base-dir PATH]
    [--database DATABASE] [--host HOST] [--port PORT] [--user USER]
  Password: set PGPASSWORD env var.
"""
import sys, os, argparse, time
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: pip install psycopg2-binary")
    sys.exit(1)

PASS = "PASS"
WARN = "WARNING"
FAIL = "FAIL"

ALL_VIEWS = [
    "analytics.vw_tracks_overview",
    "analytics.vw_tracks_by_decade",
    "analytics.vw_audio_trends",
    "analytics.vw_popularity_stats",
    "analytics.vw_top_artists",
    "analytics.vw_genre_trends",
    "analytics.vw_explicit_by_decade",
    "analytics.vw_duration_trends",
    "analytics.vw_data_quality_report",
    "analytics.vw_ml_training_dataset",
]

ML_LEAKAGE_COLS = {
    "artist_popularity", "artists_popularity", "artist_popularity_dashboard_only",
    "avg_track_popularity", "avg_artist_popularity", "avg_genre_popularity",
    "popularity_bucket", "popularity_group", "future_popularity",
    "aggregate_popularity",
}

REQUIRED_DQ_METRICS = {
    "duration_short_count", "duration_long_count", "loudness_positive_count",
    "track_artists_coverage_pct", "data_quality_status",
}

def parse_args():
    p = argparse.ArgumentParser(description="HitRadar Feature 1.6 Analytics View Validator")
    p.add_argument("--host",     default="localhost")
    p.add_argument("--port",     type=int, default=5432)
    p.add_argument("--user",     default="postgres")
    p.add_argument("--database", default="hitradar")
    p.add_argument("--base-dir", dest="base_dir", default=None)
    return p.parse_args()

def resolve_log_dir(args):
    base = Path(args.base_dir).resolve() if args.base_dir else Path(__file__).resolve().parents[1]
    log_dir = base / "6.TAI_LIEU" / "6.1.bao_cao"
    log_dir.mkdir(parents=True, exist_ok=True)
    return base, log_dir

def resolve_sql_dir(base):
    return base / "2.DATABASE_SQL" / "2.4.views"

def get_conn(args):
    password = os.environ.get("PGPASSWORD")
    if not password:
        print("ERROR: PGPASSWORD not set.")
        sys.exit(1)
    return psycopg2.connect(
        host=args.host, port=args.port, user=args.user,
        password=password, dbname=args.database, connect_timeout=10,
    )

def q1(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]

# ── Check 1: View existence ────────────────────────────────────────────────
def check_view_existence(cur):
    print("\n=== 1. View Existence ===")
    results = {}
    for view in ALL_VIEWS:
        schema, name = view.split(".")
        exists = q1(cur, f"""
            SELECT COUNT(*) FROM information_schema.views
            WHERE table_schema = '{schema}' AND table_name = '{name}'
        """)
        status = PASS if exists else FAIL
        print(f"  {view}: {'EXISTS' if exists else 'MISSING'} → {status}")
        results[view] = {"exists": bool(exists), "status": status}
    return results

# ── Check 2: Query smoke test ──────────────────────────────────────────────
def check_smoke_tests(cur):
    print("\n=== 2. Query Smoke Tests (LIMIT 5) ===")
    results = {}
    for view in ALL_VIEWS:
        try:
            cur.execute(f"SELECT * FROM {view} LIMIT 5")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            status = PASS
            note   = f"{len(rows)} rows returned, {len(cols)} columns"
        except Exception as e:
            status = FAIL
            note   = f"ERROR: {e}"
            rows   = []
            cols   = []
        print(f"  {view}: {note} → {status}")
        results[view] = {"status": status, "note": note, "cols": cols, "sample_rows": len(rows)}
    return results

# ── Check 3: Row count sanity ──────────────────────────────────────────────
def check_row_counts(cur):
    print("\n=== 3. Row Count Sanity ===")
    results = {}
    clean_tracks = q1(cur, "SELECT COUNT(*) FROM clean.tracks")

    checks = [
        ("analytics.vw_tracks_overview",    clean_tracks, "="),
        ("analytics.vw_ml_training_dataset", clean_tracks, "="),
        ("analytics.vw_tracks_by_decade",    1,            ">"),
        ("analytics.vw_audio_trends",        1,            ">"),
        ("analytics.vw_top_artists",         1,            ">"),
        ("analytics.vw_genre_trends",        1,            ">"),
        ("analytics.vw_data_quality_report", 1,            ">"),
    ]
    for view, expected, op in checks:
        try:
            cnt = q1(cur, f"SELECT COUNT(*) FROM {view}")
            if op == "=":
                status = PASS if cnt == expected else FAIL
                note   = f"{cnt:,} {'=' if cnt==expected else '≠'} {expected:,}"
            else:
                status = PASS if cnt > 0 else FAIL
                note   = f"{cnt:,} rows"
        except Exception as e:
            cnt    = -1
            status = FAIL
            note   = f"ERROR: {e}"
        print(f"  {view}: {note} → {status}")
        results[view] = {"count": cnt, "status": status, "note": note}
    return results

# ── Check 4: ML-safe column audit ─────────────────────────────────────────
def check_ml_safe(cur):
    print("\n=== 4. ML-safe Column Audit (vw_ml_training_dataset) ===")
    try:
        cur.execute("SELECT * FROM analytics.vw_ml_training_dataset LIMIT 0")
        cols = {d[0].lower() for d in cur.description}
    except Exception as e:
        print(f"  ERROR reading columns: {e}")
        return {"status": FAIL, "leakage": [], "has_target": False, "error": str(e)}

    leakage = [c for c in cols if c in ML_LEAKAGE_COLS]
    has_target = "target_popularity" in cols

    if leakage:
        status = FAIL
        print(f"  LEAKAGE columns found: {leakage}")
    else:
        status = PASS
        print(f"  No leakage columns detected")

    if not has_target:
        status = FAIL
        print(f"  FAIL: 'target_popularity' column missing")
    else:
        print(f"  target_popularity: present")

    print(f"  All columns: {sorted(cols)}")
    print(f"  → {status}")
    return {"status": status, "leakage": leakage, "has_target": has_target, "cols": sorted(cols)}

# ── Check 5: Genre duplicate-weighting sanity ─────────────────────────────
def check_genre_dedup(cur, sql_dir):
    print("\n=== 5. Genre Duplicate-Weighting Sanity ===")
    results = {"status": PASS}
    try:
        cnt = q1(cur, "SELECT COUNT(*) FROM analytics.vw_genre_trends")
        results["row_count"] = cnt
        print(f"  vw_genre_trends row count: {cnt:,}")

        # Verify SQL file uses DISTINCT
        sql_file = sql_dir / "01_create_analytics_views.sql"
        if sql_file.exists():
            content = sql_file.read_text(encoding="utf-8")
            has_distinct_cte = "SELECT DISTINCT" in content and "track_genres" in content
            results["distinct_cte_confirmed"] = has_distinct_cte
            if has_distinct_cte:
                print(f"  CTE DISTINCT confirmed in SQL source → PASS")
            else:
                print(f"  WARNING: Could not confirm CTE DISTINCT in SQL source")
                results["status"] = WARN
        else:
            print(f"  WARNING: SQL file not found for inspection")
            results["status"] = WARN

        # Top genre sample
        cur.execute("""
            SELECT genre_name, decade, track_count
            FROM analytics.vw_genre_trends
            ORDER BY track_count DESC LIMIT 3
        """)
        sample = cur.fetchall()
        results["sample"] = sample
        print(f"  Top 3 genre-decade combos: {sample}")
    except Exception as e:
        print(f"  ERROR: {e}")
        results["status"] = FAIL
        results["error"]  = str(e)
    return results

# ── Check 6: Data quality carry-forward ───────────────────────────────────
def check_dq_carryforward(cur):
    print("\n=== 6. Data Quality Carry-Forward (vw_data_quality_report) ===")
    try:
        cur.execute("SELECT metric_name, metric_value, severity FROM analytics.vw_data_quality_report")
        rows = cur.fetchall()
        metrics = {r[0]: {"value": r[1], "severity": r[2]} for r in rows}
    except Exception as e:
        print(f"  ERROR: {e}")
        return {"status": FAIL, "error": str(e)}

    missing = REQUIRED_DQ_METRICS - set(metrics.keys())
    status  = WARN if missing else PASS

    # Verify data_quality_status value
    dq_status_val = metrics.get("data_quality_status", {}).get("value", "")
    if dq_status_val != "PASS_WITH_WARNINGS":
        print(f"  WARNING: data_quality_status = '{dq_status_val}' (expected PASS_WITH_WARNINGS)")
        status = WARN

    for name in sorted(REQUIRED_DQ_METRICS):
        val = metrics.get(name, {}).get("value", "MISSING")
        print(f"  {name}: {val}")

    if missing:
        print(f"  Missing metrics: {missing}")
    print(f"  → {status}")
    return {"status": status, "metrics": metrics, "missing": missing}

# ── Check 7: EXPLAIN ANALYZE ──────────────────────────────────────────────
def check_explain_analyze(cur):
    print("\n=== 7. EXPLAIN ANALYZE ===")
    views_to_explain = [
        ("vw_tracks_by_decade",    "SELECT * FROM analytics.vw_tracks_by_decade"),
        ("vw_top_artists",         "SELECT * FROM analytics.vw_top_artists LIMIT 100"),
        ("vw_genre_trends",        "SELECT * FROM analytics.vw_genre_trends LIMIT 100"),
        ("vw_ml_training_dataset", "SELECT * FROM analytics.vw_ml_training_dataset LIMIT 100"),
    ]
    results = {}
    TIMEOUT_WARN_MS = 10_000   # 10 seconds = WARNING threshold

    for name, sql in views_to_explain:
        try:
            t0 = time.perf_counter()
            cur.execute(f"EXPLAIN ANALYZE {sql}")
            plan_rows = cur.fetchall()
            elapsed_ms = (time.perf_counter() - t0) * 1000

            # Extract execution time from plan
            exec_time_line = next((r[0] for r in plan_rows if "Execution Time" in r[0]), None)
            plan_time_line = next((r[0] for r in plan_rows if "Planning Time" in r[0]), None)

            status = WARN if elapsed_ms > TIMEOUT_WARN_MS else PASS
            note   = f"{elapsed_ms:.0f} ms total | {exec_time_line or 'no exec time'}"
        except Exception as e:
            status = FAIL
            note   = f"ERROR: {e}"

        print(f"  {name}: {note} → {status}")
        results[name] = {"status": status, "note": note}

    return results

# ── Write report ──────────────────────────────────────────────────────────
def write_validation_report(args, base, log_dir, r_exist, r_smoke, r_counts,
                             r_ml, r_genre, r_dq, r_explain, overall, now):
    report_path = log_dir / "ANALYTICS_VIEW_VALIDATION_REPORT.md"

    def sev(s):
        return f"**{s}**"

    exist_rows  = "\n".join(f"| `{v}` | {'✓' if r['exists'] else '✗'} | {sev(r['status'])} |"
                            for v, r in r_exist.items())
    smoke_rows  = "\n".join(f"| `{v}` | {r['note']} | {sev(r['status'])} |"
                            for v, r in r_smoke.items())
    count_rows  = "\n".join(f"| `{v}` | {r['note']} | {sev(r['status'])} |"
                            for v, r in r_counts.items())
    explain_rows= "\n".join(f"| `{k}` | {v['note']} | {sev(v['status'])} |"
                            for k, v in r_explain.items())
    ml_cols     = ", ".join(f"`{c}`" for c in r_ml.get("cols", []))
    ml_leakage  = ", ".join(r_ml.get("leakage", [])) or "None"
    dq_rows     = "\n".join(
        f"| `{k}` | {v['value']} | {v['severity']} |"
        for k, v in sorted(r_dq.get("metrics", {}).items())
    )

    md = f"""# ANALYTICS VIEW VALIDATION REPORT — FEATURE 1.6

## 1. Metadata

| Field | Value |
|-------|-------|
| Feature | 1.6 — Analytics Views & Indexes |
| Owner | Đạt |
| Database | `{args.database}` @ `{args.host}:{args.port}` |
| User | `{args.user}` |
| Date/Time | {now} |
| Script | `9.SCRIPTS/validate_analytics_views.py` |
| **Overall** | **{overall}** |

---

## 2. View Existence (10 views required)

| View | Exists | Status |
|------|--------|--------|
{exist_rows}

---

## 3. Query Smoke Test

| View | Result | Status |
|------|--------|--------|
{smoke_rows}

---

## 4. Row Count Sanity

| View | Count | Status |
|------|-------|--------|
{count_rows}

---

## 5. ML-safe Column Audit — vw_ml_training_dataset

| Check | Result | Status |
|-------|--------|--------|
| `target_popularity` present | {'Yes' if r_ml.get('has_target') else 'No'} | {sev(PASS if r_ml.get('has_target') else FAIL)} |
| Leakage columns found | {ml_leakage} | {sev(FAIL if r_ml.get('leakage') else PASS)} |
| **Overall** | | {sev(r_ml.get('status', FAIL))} |

**All columns in view:**
{ml_cols}

---

## 6. Genre Duplicate-Weighting Confirmation — vw_genre_trends

| Check | Result | Status |
|-------|--------|--------|
| CTE DISTINCT confirmed in SQL source | {'Yes' if r_genre.get('distinct_cte_confirmed') else 'No'} | {sev(PASS if r_genre.get('distinct_cte_confirmed') else WARN)} |
| Row count > 0 | {r_genre.get('row_count', '?'):,} | {sev(PASS if r_genre.get('row_count', 0) > 0 else FAIL)} |
| **Overall** | | {sev(r_genre.get('status', FAIL))} |

> SQL uses `WITH track_genres AS (SELECT DISTINCT t.track_id, g.genre_id, ...)` to prevent
> duplicate-weighting when a track has multiple artists sharing the same genre.

---

## 7. Data Quality Carry-Forward — vw_data_quality_report

| Metric | Value | Severity |
|--------|-------|---------|
{dq_rows}

Missing required metrics: {r_dq.get('missing', set()) or 'None'}

**Overall:** {sev(r_dq.get('status', FAIL))}

---

## 8. EXPLAIN ANALYZE Summary

| View | Timing / Note | Status |
|------|--------------|--------|
{explain_rows}

> Threshold: > 10,000 ms = WARNING. Views on large tables without filters may be slow.

---

## 9. Overall Decision

**{overall}**

{"All checks PASS. Proceed to Feature 1.7." if overall == PASS
 else "Structural checks PASS; warnings present. Proceed to Feature 1.7 with carry-forward warnings."
 if "WARNING" in overall
 else "One or more FAIL. Do NOT proceed to Feature 1.7 until resolved."}
"""
    with open(str(report_path), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Validation report written → {report_path}")
    return report_path

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    base, log_dir = resolve_log_dir(args)
    sql_dir = resolve_sql_dir(base)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("HitRadar Feature 1.6 — Analytics View Validation")
    print(f"Database: {args.database} @ {args.host}:{args.port}")
    print(f"Base directory: {base}")

    conn = get_conn(args)
    cur  = conn.cursor()

    r_exist   = check_view_existence(cur)
    r_smoke   = check_smoke_tests(cur)
    r_counts  = check_row_counts(cur)
    r_ml      = check_ml_safe(cur)
    r_genre   = check_genre_dedup(cur, sql_dir)
    r_dq      = check_dq_carryforward(cur)
    r_explain = check_explain_analyze(cur)

    cur.close()
    conn.close()

    # Determine overall
    all_statuses = (
        [r["status"] for r in r_exist.values()]
        + [r["status"] for r in r_smoke.values()]
        + [r["status"] for r in r_counts.values()]
        + [r_ml["status"], r_genre["status"], r_dq["status"]]
        + [r["status"] for r in r_explain.values()]
    )
    if FAIL in all_statuses:
        overall = FAIL
    elif WARN in all_statuses:
        overall = "PASS_WITH_WARNINGS"
    else:
        overall = PASS

    report_path = write_validation_report(
        args, base, log_dir, r_exist, r_smoke, r_counts,
        r_ml, r_genre, r_dq, r_explain, overall, now
    )

    print("\n=== VALIDATION SUMMARY ===")
    print(f"  View existence:    {'PASS' if all(r['status']==PASS for r in r_exist.values()) else 'FAIL'}")
    print(f"  Smoke tests:       {'PASS' if all(r['status']==PASS for r in r_smoke.values()) else 'FAIL'}")
    print(f"  Row counts:        {'PASS' if all(r['status']==PASS for r in r_counts.values()) else 'FAIL'}")
    print(f"  ML-safe audit:     {r_ml['status']}")
    print(f"  Genre dedup:       {r_genre['status']}")
    print(f"  DQ carry-forward:  {r_dq['status']}")
    ea_ov = PASS if all(r["status"]==PASS for r in r_explain.values()) else WARN
    print(f"  EXPLAIN ANALYZE:   {ea_ov}")
    print(f"\nOverall: {overall}")
    print(f"Report: {report_path}")

    if overall == FAIL:
        sys.exit(1)

if __name__ == "__main__":
    main()

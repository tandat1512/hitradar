"""
validate_raw_import.py — Feature 1.3: Validate raw import
Kiểm tra row count, column count, ID uniqueness, và sample records.

Usage:
  python 9.SCRIPTS/validate_raw_import.py [--host HOST] [--port PORT]
                                           [--user USER] [--database DATABASE]
                                           [--base-dir PATH]

Password: set PGPASSWORD env variable trước khi chạy.
  Windows: $env:PGPASSWORD = "your_password"
  Linux/Mac: export PGPASSWORD=your_password

Ví dụ:
  $env:PGPASSWORD="your_pw"; python 9.SCRIPTS/validate_raw_import.py --database hitradar --user postgres
  $env:PGPASSWORD="your_pw"; python 9.SCRIPTS/validate_raw_import.py --base-dir "X:\\DUAN1\\HitRadar_Pro" --database hitradar --user postgres
"""
import sys, os, json, argparse
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
except ImportError:
    print("ERROR: pip install psycopg2-binary")
    sys.exit(1)

EXPECTED_ROWS = {
    "raw.raw_tracks":      586_672,
    "raw.raw_artists":   1_162_095,
    "raw.raw_artist_json": 573_856,
}
EXPECTED_COLS = {
    "raw.raw_tracks":      21,   # 20 data cols + _import_ts
    "raw.raw_artists":      6,   # 5 data cols + _import_ts
    "raw.raw_artist_json":  6,   # artist_id, raw_values, value_count, semantic_status, source_file, _import_ts
}

def parse_args():
    p = argparse.ArgumentParser(description="HitRadar raw import validator")
    p.add_argument("--host",     default="localhost")
    p.add_argument("--port",     type=int, default=5432)
    p.add_argument("--user",     default="postgres")
    p.add_argument("--database", default="hitradar")
    p.add_argument("--base-dir", dest="base_dir", default=None,
                   help="Project root directory. Defaults to parent of this script's folder.")
    return p.parse_args()

def resolve_log_dir(args):
    if args.base_dir:
        base = Path(args.base_dir).resolve()
    else:
        base = Path(__file__).resolve().parents[1]
    log_dir = base / "6.TAI_LIEU" / "6.1.bao_cao"
    log_dir.mkdir(parents=True, exist_ok=True)
    return base, log_dir

def get_conn(args):
    password = os.environ.get("PGPASSWORD")
    if not password:
        print("ERROR: PGPASSWORD not set.")
        print("  Windows: $env:PGPASSWORD = 'your_password'")
        print("  Linux/Mac: export PGPASSWORD=your_password")
        sys.exit(1)
    return psycopg2.connect(
        host=args.host, port=args.port, user=args.user,
        password=password, dbname=args.database, connect_timeout=10,
    )

def check_row_counts(cur):
    print("\n=== 1. Row Count Validation ===")
    results = {}
    for table, expected in EXPECTED_ROWS.items():
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        actual = cur.fetchone()[0]
        status = "PASS" if actual == expected else "FAIL"
        print(f"  {table}: {actual:,} / {expected:,} → {status}")
        results[table] = {"expected": expected, "actual": actual, "status": status}
    return results

def check_column_counts(cur):
    print("\n=== 2. Column Count Validation ===")
    results = {}
    for table, expected_cnt in EXPECTED_COLS.items():
        schema, tname = table.split(".")
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema=%s AND table_name=%s ORDER BY ordinal_position",
            (schema, tname)
        )
        cols = [r[0] for r in cur.fetchall()]
        actual_cnt = len(cols)
        status = "PASS" if actual_cnt == expected_cnt else "FAIL"
        print(f"  {table}: {actual_cnt} cols → {status}")
        print(f"    Columns: {', '.join(cols)}")
        results[table] = {"expected": expected_cnt, "actual": actual_cnt,
                          "columns": cols, "status": status}
    return results

def check_id_uniqueness(cur):
    print("\n=== 3. ID Validation ===")
    checks = [
        ("raw.raw_tracks",      "id"),
        ("raw.raw_artists",     "id"),
        ("raw.raw_artist_json", "artist_id"),
    ]
    results = {}
    for table, id_col in checks:
        cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {id_col} IS NULL")
        null_cnt = cur.fetchone()[0]
        cur.execute(f"SELECT COUNT(*) - COUNT(DISTINCT {id_col}) FROM {table}")
        dup_cnt = cur.fetchone()[0]
        status = "PASS" if null_cnt == 0 and dup_cnt == 0 else "FAIL"
        print(f"  {table}.{id_col}: nulls={null_cnt}, duplicates={dup_cnt} → {status}")
        results[table] = {"id_col": id_col, "nulls": null_cnt,
                          "duplicates": dup_cnt, "status": status}
    return results

def get_samples(cur):
    print("\n=== 4. Sample Records ===")
    samples = {}

    cur.execute(
        "SELECT id, name, popularity, duration_ms, release_date, artists "
        "FROM raw.raw_tracks LIMIT 5"
    )
    rows = cur.fetchall()
    samples["raw.raw_tracks"] = [dict(zip(
        ["id","name","popularity","duration_ms","release_date","artists"], r
    )) for r in rows]
    print(f"  raw.raw_tracks: {len(rows)} samples")

    cur.execute(
        "SELECT id, name, popularity, followers, genres "
        "FROM raw.raw_artists LIMIT 5"
    )
    rows = cur.fetchall()
    samples["raw.raw_artists"] = [dict(zip(
        ["id","name","popularity","followers","genres"], r
    )) for r in rows]
    print(f"  raw.raw_artists: {len(rows)} samples")

    cur.execute(
        "SELECT artist_id, value_count, semantic_status "
        "FROM raw.raw_artist_json WHERE value_count > 0 LIMIT 5"
    )
    rows = cur.fetchall()
    samples["raw.raw_artist_json"] = [dict(zip(
        ["artist_id","value_count","semantic_status"], r
    )) for r in rows]
    print(f"  raw.raw_artist_json: {len(rows)} non-empty samples")

    return samples

def write_validation_report(args, base, log_dir, row_results, col_results, id_results, samples):
    report_path = log_dir / "RAW_IMPORT_VALIDATION_REPORT.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    all_statuses = (
        [v["status"] for v in row_results.values()] +
        [v["status"] for v in col_results.values()] +
        [v["status"] for v in id_results.values()]
    )
    overall = "PASS" if all(s == "PASS" for s in all_statuses) else "FAIL"

    def row_table(results):
        rows = ""
        for tbl, v in results.items():
            rows += f"| `{tbl}` | {v['expected']:,} | {v['actual']:,} | **{v['status']}** |\n"
        return rows

    def col_table(results):
        rows = ""
        for tbl, v in results.items():
            rows += (f"| `{tbl}` | {v['expected']} | {v['actual']} | "
                     f"{', '.join(v['columns'])} | **{v['status']}** |\n")
        return rows

    def id_table(results):
        rows = ""
        for tbl, v in results.items():
            rows += (f"| `{tbl}.{v['id_col']}` | {v['nulls']} | "
                     f"{v['duplicates']} | **{v['status']}** |\n")
        return rows

    def sample_section(tbl_key, fields):
        rows_list = samples.get(tbl_key, [])
        if not rows_list:
            return "_No data_\n"
        header    = "| " + " | ".join(fields) + " |"
        sep       = "| " + " | ".join(["---"] * len(fields)) + " |"
        data_rows = ""
        for r in rows_list:
            vals = [str(r.get(f, ""))[:60].replace("|", "\\|") for f in fields]
            data_rows += "| " + " | ".join(vals) + " |\n"
        return header + "\n" + sep + "\n" + data_rows

    row_summary  = "PASS" if all(v["status"] == "PASS" for v in row_results.values()) else "FAIL"
    col_summary  = "PASS" if all(v["status"] == "PASS" for v in col_results.values()) else "FAIL"
    id_summary   = "PASS" if all(v["status"] == "PASS" for v in id_results.values()) else "FAIL"

    md = f"""# RAW IMPORT VALIDATION REPORT — FEATURE 1.3

## 1. Metadata

| Field | Value |
|-------|-------|
| Database | `{args.database}` @ `{args.host}:{args.port}` |
| User | `{args.user}` |
| Date/Time | {now} |
| Base directory | `{base}` |
| Overall status | **{overall}** |

---

## 2. Row Count Validation

| Table | Expected | Actual | Status |
|-------|---------|--------|--------|
{row_table(row_results)}
---

## 3. Column Validation

| Table | Expected cols | Actual cols | Columns | Status |
|-------|-------------|------------|---------|--------|
{col_table(col_results)}
---

## 4. ID Validation

| Column | Null count | Duplicate count | Status |
|--------|-----------|-----------------|--------|
{id_table(id_results)}
---

## 5. Sample Records

### raw.raw_tracks (5 rows)

{sample_section("raw.raw_tracks", ["id","name","popularity","duration_ms","release_date","artists"])}

### raw.raw_artists (5 rows)

{sample_section("raw.raw_artists", ["id","name","popularity","followers","genres"])}

### raw.raw_artist_json (5 non-empty rows)

{sample_section("raw.raw_artist_json", ["artist_id","value_count","semantic_status"])}

---

## 6. Validation Summary

| Check | Result |
|-------|--------|
| Row counts | {row_summary} |
| Column counts | {col_summary} |
| ID uniqueness | {id_summary} |
| **Overall** | **{overall}** |
"""
    with open(str(report_path), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Validation report written → {report_path}")
    return report_path, overall

def main():
    args = parse_args()
    base, log_dir = resolve_log_dir(args)

    print("HitRadar Feature 1.3 — Raw Import Validation")
    print(f"Database: {args.database} @ {args.host}:{args.port}")
    print(f"Base directory: {base}")

    conn = get_conn(args)
    cur  = conn.cursor()

    row_results = check_row_counts(cur)
    col_results = check_column_counts(cur)
    id_results  = check_id_uniqueness(cur)
    samples     = get_samples(cur)

    cur.close()
    conn.close()

    report_path, overall = write_validation_report(
        args, base, log_dir, row_results, col_results, id_results, samples
    )

    print("\n=== VALIDATION SUMMARY ===")
    for tbl, v in row_results.items():
        print(f"  {tbl}: {v['actual']:,} rows → {v['status']}")
    print(f"\nOverall: {overall}")
    print(f"Report: {report_path}")

    if overall != "PASS":
        sys.exit(1)

if __name__ == "__main__":
    main()

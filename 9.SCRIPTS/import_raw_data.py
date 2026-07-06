"""
import_raw_data.py — Feature 1.3: Data Ingestion Pipeline
Import 3 raw files vào PostgreSQL raw layer.

Usage:
  python 9.SCRIPTS/import_raw_data.py [--reset] [--host HOST] [--port PORT]
                                       [--user USER] [--database DATABASE]

Password: đặt biến môi trường PGPASSWORD trước khi chạy, hoặc dùng .pgpass.
  Windows: $env:PGPASSWORD = "your_password"
  Linux/Mac: export PGPASSWORD=your_password

Ví dụ:
  $env:PGPASSWORD="postgres"; python 9.SCRIPTS/import_raw_data.py --database hitradar --user postgres --reset
"""
import sys, os, io, json, csv, argparse, time
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
    import psycopg2.extras
    from psycopg2 import sql
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

# ── Paths ─────────────────────────────────────────────────────────────────
BASE     = r"x:\DUAN1\HitRadar_Pro"
RAW_DIR  = os.path.join(BASE, "1.DỮ_LIỆU", "1.1.raw")
LOG_DIR  = os.path.join(BASE, "6.TAI_LIEU", "6.1.bao_cao")

TRACKS_CSV  = os.path.join(RAW_DIR, "tracks.csv")
ARTISTS_CSV = os.path.join(RAW_DIR, "artists.csv")
DICT_JSON   = os.path.join(RAW_DIR, "dict_artists.json")

EXPECTED = {
    "raw.raw_tracks":      586_672,
    "raw.raw_artists":   1_162_095,
    "raw.raw_artist_json": 573_856,
}

# ── Argument parsing ──────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="HitRadar raw data importer")
    p.add_argument("--host",     default="localhost")
    p.add_argument("--port",     type=int, default=5432)
    p.add_argument("--user",     default="postgres")
    p.add_argument("--database", default="hitradar")
    p.add_argument("--reset",    action="store_true",
                   help="TRUNCATE raw tables before import")
    return p.parse_args()

# ── DB connection ─────────────────────────────────────────────────────────
def get_conn(args):
    password = os.environ.get("PGPASSWORD")
    if not password:
        print("ERROR: PGPASSWORD environment variable is not set.")
        print("  Windows: $env:PGPASSWORD = 'your_password'")
        sys.exit(1)
    return psycopg2.connect(
        host=args.host, port=args.port, user=args.user,
        password=password, dbname=args.database,
        connect_timeout=10,
    )

# ── A. Tiền điều kiện ─────────────────────────────────────────────────────
def check_prerequisites(conn):
    print("\n=== A. Checking prerequisites ===")
    ok = True

    # Raw files
    for label, path in [("tracks.csv", TRACKS_CSV),
                        ("artists.csv", ARTISTS_CSV),
                        ("dict_artists.json", DICT_JSON)]:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            size_mb = os.path.getsize(path) / 1024 / 1024
            print(f"  [OK] {label} ({size_mb:.1f} MB)")
        else:
            print(f"  [FAIL] {label} missing or empty")
            ok = False

    # Schema + tables
    cur = conn.cursor()
    for schema in ("raw", "clean", "analytics"):
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", (schema,))
        if cur.fetchone():
            print(f"  [OK] schema '{schema}' exists")
        else:
            print(f"  [FAIL] schema '{schema}' missing — run DDL files first")
            ok = False

    for table in ("raw.raw_tracks", "raw.raw_artists", "raw.raw_artist_json"):
        s, t = table.split(".")
        cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_name=%s",
            (s, t)
        )
        if cur.fetchone():
            print(f"  [OK] table '{table}' exists")
        else:
            print(f"  [FAIL] table '{table}' missing — run DDL files first")
            ok = False

    # Check release_precision column (DDL sync check)
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='clean' AND table_name='tracks' AND column_name='release_precision'"
    )
    if cur.fetchone():
        print("  [OK] clean.tracks.release_precision exists (DDL up to date)")
    else:
        print("  [WARN] clean.tracks.release_precision not found — DDL may be outdated")

    cur.close()
    if not ok:
        print("\nPrerequisite check FAILED. Aborting.")
        sys.exit(1)
    print("  Prerequisites: ALL PASS")
    return True

# ── B. Truncate (--reset) ─────────────────────────────────────────────────
def truncate_raw_tables_if_reset(conn, reset_flag):
    if not reset_flag:
        return
    print("\n=== --reset: Truncating raw tables ===")
    cur = conn.cursor()
    for t in ("raw.raw_tracks", "raw.raw_artists", "raw.raw_artist_json"):
        cur.execute(f"TRUNCATE TABLE {t}")
        print(f"  TRUNCATED {t}")
    conn.commit()
    cur.close()

# ── C. Import tracks.csv ──────────────────────────────────────────────────
def import_tracks_csv(conn):
    print("\n=== C. Importing tracks.csv → raw.raw_tracks ===")
    t0 = time.time()
    cur = conn.cursor()

    # Dùng COPY với StringIO để kiểm soát NULL handling
    cols = ("id","name","popularity","duration_ms","explicit","artists",
            "id_artists","release_date","danceability","energy","key",
            "loudness","mode","speechiness","acousticness","instrumentalness",
            "liveness","valence","tempo","time_signature")
    col_list = ", ".join(cols)

    copy_sql = (
        f"COPY raw.raw_tracks ({col_list}) "
        f"FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )
    with open(TRACKS_CSV, encoding="utf-8", errors="replace") as f:
        cur.copy_expert(copy_sql, f)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM raw.raw_tracks")
    count = cur.fetchone()[0]
    elapsed = time.time() - t0
    print(f"  Imported: {count:,} rows in {elapsed:.1f}s")
    cur.close()
    return count

# ── D. Import artists.csv ─────────────────────────────────────────────────
def import_artists_csv(conn):
    print("\n=== D. Importing artists.csv → raw.raw_artists ===")
    t0 = time.time()
    cur = conn.cursor()

    cols = ("id", "followers", "genres", "name", "popularity")
    col_list = ", ".join(cols)

    copy_sql = (
        f"COPY raw.raw_artists ({col_list}) "
        f"FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )
    with open(ARTISTS_CSV, encoding="utf-8", errors="replace") as f:
        cur.copy_expert(copy_sql, f)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM raw.raw_artists")
    count = cur.fetchone()[0]
    elapsed = time.time() - t0
    print(f"  Imported: {count:,} rows in {elapsed:.1f}s")
    cur.close()
    return count

# ── E. Import dict_artists.json ───────────────────────────────────────────
def import_dict_artists_json(conn):
    print("\n=== E. Importing dict_artists.json → raw.raw_artist_json ===")
    t0 = time.time()

    print("  Loading JSON into memory...")
    with open(DICT_JSON, encoding="utf-8", errors="replace") as f:
        data = json.load(f)
    print(f"  Keys loaded: {len(data):,}")

    # Build CSV in-memory via StringIO → COPY (much faster than executemany)
    print("  Building COPY buffer...")
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["artist_id", "raw_values", "value_count",
                     "semantic_status", "source_file"])

    BATCH = 50_000
    for i, (k, v) in enumerate(data.items()):
        raw_val = json.dumps(v, ensure_ascii=False) if isinstance(v, list) else "[]"
        val_cnt = len(v) if isinstance(v, list) else 0
        writer.writerow([k, raw_val, val_cnt, "RELATED_ARTIST_GRAPH", "dict_artists.json"])
        if (i + 1) % BATCH == 0:
            print(f"  Buffered {i+1:,} / {len(data):,} keys...")

    buf.seek(0)
    cur = conn.cursor()
    copy_sql = (
        "COPY raw.raw_artist_json "
        "(artist_id, raw_values, value_count, semantic_status, source_file) "
        "FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
    )
    cur.copy_expert(copy_sql, buf)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM raw.raw_artist_json")
    count = cur.fetchone()[0]
    elapsed = time.time() - t0
    print(f"  Imported: {count:,} rows in {elapsed:.1f}s")
    cur.close()
    return count

# ── F. Write import log ───────────────────────────────────────────────────
def write_import_log(args, results, start_ts):
    log_path = os.path.join(LOG_DIR, "IMPORT_LOG.md")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rows_md = ""
    overall = "PASS"
    for src, tbl, exp, got in results:
        status = "PASS" if got == exp else f"WARN ({got:,} ≠ {exp:,})"
        if got != exp:
            overall = "WARN"
        rows_md += f"| `{src}` | `{tbl}` | {exp:,} | {got:,} | **{status}** | |\n"

    md = f"""# IMPORT LOG — FEATURE 1.3

## 1. Metadata

| Field | Value |
|-------|-------|
| Owner | Đạt |
| Feature | 1.3 — Data Ingestion Pipeline |
| Database | {args.database} @ {args.host}:{args.port} |
| User | {args.user} |
| Date/Time | {now} |
| Scripts | `9.SCRIPTS/import_raw_data.py` |
| Reset flag | {'Yes — tables were TRUNCATED before import' if args.reset else 'No'} |

---

## 2. Input Files

| File | Path | Expected Rows |
|------|------|--------------|
| `tracks.csv` | `1.DỮ_LIỆU/1.1.raw/tracks.csv` | 586,672 |
| `artists.csv` | `1.DỮ_LIỆU/1.1.raw/artists.csv` | 1,162,095 |
| `dict_artists.json` | `1.DỮ_LIỆU/1.1.raw/dict_artists.json` | 573,856 keys |

---

## 3. Import Results

| Source File | Target Table | Expected | Imported | Status | Notes |
|-------------|-------------|---------|---------|--------|-------|
{rows_md}
---

## 4. Errors / Warnings

No import error.

---

## 5. Conclusion

**{overall}** — Raw data import completed. Proceed to validate_raw_import.py.
"""
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Import log written → {log_path}")
    return log_path

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    start_ts = datetime.now(timezone.utc)
    print(f"HitRadar Feature 1.3 — Data Ingestion Pipeline")
    print(f"Target: {args.database} @ {args.host}:{args.port} (user: {args.user})")
    print(f"Started: {start_ts.strftime('%Y-%m-%d %H:%M UTC')}")

    conn = get_conn(args)
    print("  [OK] Database connection established")

    check_prerequisites(conn)
    truncate_raw_tables_if_reset(conn, args.reset)

    count_tracks  = import_tracks_csv(conn)
    count_artists = import_artists_csv(conn)
    count_json    = import_dict_artists_json(conn)

    results = [
        ("tracks.csv",        "raw.raw_tracks",      EXPECTED["raw.raw_tracks"],      count_tracks),
        ("artists.csv",       "raw.raw_artists",     EXPECTED["raw.raw_artists"],     count_artists),
        ("dict_artists.json", "raw.raw_artist_json", EXPECTED["raw.raw_artist_json"], count_json),
    ]

    log_path = write_import_log(args, results, start_ts)
    conn.close()

    print("\n=== IMPORT SUMMARY ===")
    all_pass = True
    for src, tbl, exp, got in results:
        ok = got == exp
        if not ok:
            all_pass = False
        print(f"  {tbl}: {got:,} / {exp:,} {'OK' if ok else 'MISMATCH'}")

    status = "PASS" if all_pass else "FAIL — row count mismatch"
    print(f"\nFeature 1.3 import status: {status}")
    print(f"Log: {log_path}")
    print("\nNext step: python 9.SCRIPTS/validate_raw_import.py --database", args.database)

if __name__ == "__main__":
    main()

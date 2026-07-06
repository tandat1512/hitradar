"""
import_raw_data.py — Feature 1.3: Data Ingestion Pipeline
Import 3 raw files vào PostgreSQL raw layer.

Usage:
  python 9.SCRIPTS/import_raw_data.py [--reset] [--host HOST] [--port PORT]
                                       [--user USER] [--database DATABASE]
                                       [--base-dir PATH]

Password: đặt biến môi trường PGPASSWORD trước khi chạy, hoặc dùng .pgpass.
  Windows: $env:PGPASSWORD = "your_password"
  Linux/Mac: export PGPASSWORD=your_password

Ví dụ:
  $env:PGPASSWORD="your_pw"; python 9.SCRIPTS/import_raw_data.py --database hitradar --user postgres --reset
  $env:PGPASSWORD="your_pw"; python 9.SCRIPTS/import_raw_data.py --base-dir "X:\\DUAN1\\HitRadar_Pro" --database hitradar --user postgres --reset
"""
import sys, os, io, json, csv, argparse, time
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
    import psycopg2.extras
    from psycopg2 import sql
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

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
    p.add_argument("--base-dir", dest="base_dir", default=None,
                   help="Project root directory. Defaults to parent of this script's folder.")
    return p.parse_args()

def resolve_paths(args):
    """Resolve BASE, RAW_DIR, LOG_DIR from --base-dir or script location."""
    if args.base_dir:
        base = Path(args.base_dir).resolve()
    else:
        base = Path(__file__).resolve().parents[1]

    raw_dir = base / "1.DỮ_LIỆU" / "1.1.raw"
    log_dir = base / "6.TAI_LIEU" / "6.1.bao_cao"
    log_dir.mkdir(parents=True, exist_ok=True)

    return {
        "base":        base,
        "raw_dir":     raw_dir,
        "log_dir":     log_dir,
        "tracks_csv":  raw_dir / "tracks.csv",
        "artists_csv": raw_dir / "artists.csv",
        "dict_json":   raw_dir / "dict_artists.json",
    }

# ── DB connection ─────────────────────────────────────────────────────────
def get_conn(args):
    password = os.environ.get("PGPASSWORD")
    if not password:
        print("ERROR: PGPASSWORD environment variable is not set.")
        print("  Windows: $env:PGPASSWORD = 'your_password'")
        print("  Linux/Mac: export PGPASSWORD=your_password")
        sys.exit(1)
    return psycopg2.connect(
        host=args.host, port=args.port, user=args.user,
        password=password, dbname=args.database,
        connect_timeout=10,
    )

# ── A. Tiền điều kiện ─────────────────────────────────────────────────────
def check_prerequisites(conn, paths):
    print("\n=== A. Checking prerequisites ===")
    ok = True

    for label, path in [("tracks.csv",        paths["tracks_csv"]),
                        ("artists.csv",        paths["artists_csv"]),
                        ("dict_artists.json",  paths["dict_json"])]:
        if path.exists() and path.stat().st_size > 0:
            size_mb = path.stat().st_size / 1024 / 1024
            print(f"  [OK] {label} ({size_mb:.1f} MB)")
        else:
            print(f"  [FAIL] {label} not found or empty: {path}")
            ok = False

    cur = conn.cursor()
    for schema in ("raw", "clean", "analytics"):
        cur.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
            (schema,)
        )
        if cur.fetchone():
            print(f"  [OK] schema '{schema}' exists")
        else:
            print(f"  [FAIL] schema '{schema}' missing — run DDL files first")
            ok = False

    for table in ("raw.raw_tracks", "raw.raw_artists", "raw.raw_artist_json"):
        s, t = table.split(".")
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema=%s AND table_name=%s",
            (s, t)
        )
        if cur.fetchone():
            print(f"  [OK] table '{table}' exists")
        else:
            print(f"  [FAIL] table '{table}' missing — run DDL files first")
            ok = False

    # DDL sync check: release_precision is mandatory — proves 03_create_clean_tables.sql ran correctly
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='clean' AND table_name='tracks' AND column_name='release_precision'"
    )
    if cur.fetchone():
        print("  [OK] clean.tracks.release_precision exists (DDL up to date)")
    else:
        print("  [FAIL] clean.tracks.release_precision NOT FOUND")
        print("         DDL is outdated — re-run 03_create_clean_tables.sql before importing.")
        ok = False

    cur.close()
    if not ok:
        print("\n  Prerequisite check FAILED. Aborting.")
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
def import_tracks_csv(conn, paths):
    print("\n=== C. Importing tracks.csv → raw.raw_tracks ===")
    t0 = time.time()
    cur = conn.cursor()

    cols = ("id","name","popularity","duration_ms","explicit","artists",
            "id_artists","release_date","danceability","energy","key",
            "loudness","mode","speechiness","acousticness","instrumentalness",
            "liveness","valence","tempo","time_signature")
    col_list = ", ".join(cols)

    copy_sql = (
        f"COPY raw.raw_tracks ({col_list}) "
        f"FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )
    with open(str(paths["tracks_csv"]), encoding="utf-8", errors="replace") as f:
        cur.copy_expert(copy_sql, f)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM raw.raw_tracks")
    count = cur.fetchone()[0]
    elapsed = time.time() - t0
    print(f"  Imported: {count:,} rows in {elapsed:.1f}s")
    cur.close()
    return count

# ── D. Import artists.csv ─────────────────────────────────────────────────
def import_artists_csv(conn, paths):
    print("\n=== D. Importing artists.csv → raw.raw_artists ===")
    t0 = time.time()
    cur = conn.cursor()

    cols = ("id", "followers", "genres", "name", "popularity")
    col_list = ", ".join(cols)

    copy_sql = (
        f"COPY raw.raw_artists ({col_list}) "
        f"FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )
    with open(str(paths["artists_csv"]), encoding="utf-8", errors="replace") as f:
        cur.copy_expert(copy_sql, f)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM raw.raw_artists")
    count = cur.fetchone()[0]
    elapsed = time.time() - t0
    print(f"  Imported: {count:,} rows in {elapsed:.1f}s")
    cur.close()
    return count

# ── E. Import dict_artists.json ───────────────────────────────────────────
def import_dict_artists_json(conn, paths):
    print("\n=== E. Importing dict_artists.json → raw.raw_artist_json ===")
    t0 = time.time()

    print("  Loading JSON into memory...")
    with open(str(paths["dict_json"]), encoding="utf-8", errors="replace") as f:
        data = json.load(f)
    print(f"  Keys loaded: {len(data):,}")

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
def write_import_log(args, paths, results, start_ts):
    log_path = paths["log_dir"] / "IMPORT_LOG.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rows_md = ""
    overall = "PASS"
    for src, tbl, exp, got in results:
        if got == exp:
            status = "PASS"
        else:
            status = f"FAIL ({got:,} ≠ {exp:,})"
            overall = "FAIL"
        rows_md += f"| `{src}` | `{tbl}` | {exp:,} | {got:,} | **{status}** | |\n"

    errors_section = "No import error." if overall == "PASS" else \
        "**Row count mismatch detected — import FAILED. Re-run with --reset and investigate source files.**"

    md = f"""# IMPORT LOG — FEATURE 1.3

## 1. Metadata

| Field | Value |
|-------|-------|
| Owner | Đạt |
| Feature | 1.3 — Data Ingestion Pipeline |
| Database | {args.database} @ {args.host}:{args.port} |
| User | {args.user} |
| Date/Time | {now} |
| Base directory | `{paths['base']}` |
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

{errors_section}

---

## 5. Conclusion

**{overall}** — Raw data import {"completed successfully" if overall == "PASS" else "FAILED — see section 4"}.
{"Proceed to validate_raw_import.py." if overall == "PASS" else "Do NOT proceed to validation until mismatch is resolved."}
"""
    with open(str(log_path), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Import log written → {log_path}")
    return log_path, overall

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    args  = parse_args()
    paths = resolve_paths(args)
    start_ts = datetime.now(timezone.utc)

    print("HitRadar Feature 1.3 — Data Ingestion Pipeline")
    print(f"Target: {args.database} @ {args.host}:{args.port} (user: {args.user})")
    print(f"Base directory: {paths['base']}")
    print(f"Started: {start_ts.strftime('%Y-%m-%d %H:%M UTC')}")

    conn = get_conn(args)
    print("  [OK] Database connection established")

    check_prerequisites(conn, paths)
    truncate_raw_tables_if_reset(conn, args.reset)

    count_tracks  = import_tracks_csv(conn, paths)
    count_artists = import_artists_csv(conn, paths)
    count_json    = import_dict_artists_json(conn, paths)

    results = [
        ("tracks.csv",        "raw.raw_tracks",      EXPECTED["raw.raw_tracks"],      count_tracks),
        ("artists.csv",       "raw.raw_artists",     EXPECTED["raw.raw_artists"],     count_artists),
        ("dict_artists.json", "raw.raw_artist_json", EXPECTED["raw.raw_artist_json"], count_json),
    ]

    log_path, overall = write_import_log(args, paths, results, start_ts)
    conn.close()

    print("\n=== IMPORT SUMMARY ===")
    for src, tbl, exp, got in results:
        ok_row = got == exp
        print(f"  {tbl}: {got:,} / {exp:,} {'OK' if ok_row else 'MISMATCH — FAIL'}")

    print(f"\nFeature 1.3 import status: {overall}")
    print(f"Log: {log_path}")
    if overall == "PASS":
        print(f"\nNext step: python 9.SCRIPTS/validate_raw_import.py --database {args.database}")
    else:
        print("\nAborting: resolve row count mismatch before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()

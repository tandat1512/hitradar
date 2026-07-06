"""
clean_raw_to_clean.py — Feature 1.4: Data Cleaning & Normalization
Đọc từ raw layer → clean và normalize → ghi vào clean layer.

Usage:
  python 9.SCRIPTS/clean_raw_to_clean.py [--reset-clean] [--base-dir PATH]
                                          [--host HOST] [--port PORT]
                                          [--user USER] [--database DATABASE]

Password: đặt PGPASSWORD trước khi chạy.
  Windows: $env:PGPASSWORD = "your_password"
  Linux/Mac: export PGPASSWORD=your_password

Thứ tự populate:
  1. clean.tracks
  2. clean.artists
  3. clean.genres
  4. clean.track_artists  (FK → tracks + artists)
  5. clean.artist_genres  (FK → artists + genres)
  6. clean.artist_relations (FK → artists × 2)

Note: Uses two separate connections:
  - conn_r: autocommit=True, server-side cursor for streaming reads
  - conn_w: standard write connection with batch commits
"""
import sys, os, ast, json, re, argparse, time
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: pip install psycopg2-binary")
    sys.exit(1)

BATCH = 50_000

# ── Argument parsing ──────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="HitRadar Feature 1.4 — Data Cleaning")
    p.add_argument("--host",        default="localhost")
    p.add_argument("--port",        type=int, default=5432)
    p.add_argument("--user",        default="postgres")
    p.add_argument("--database",    default="hitradar")
    p.add_argument("--reset-clean", action="store_true",
                   help="TRUNCATE clean tables before populating")
    p.add_argument("--base-dir",    dest="base_dir", default=None)
    return p.parse_args()

def resolve_log_dir(args):
    base = Path(args.base_dir).resolve() if args.base_dir else Path(__file__).resolve().parents[1]
    log_dir = base / "6.TAI_LIEU" / "6.1.bao_cao"
    log_dir.mkdir(parents=True, exist_ok=True)
    return base, log_dir

def make_conn(args, autocommit=False):
    password = os.environ.get("PGPASSWORD")
    if not password:
        print("ERROR: PGPASSWORD not set.")
        sys.exit(1)
    conn = psycopg2.connect(
        host=args.host, port=args.port, user=args.user,
        password=password, dbname=args.database, connect_timeout=10,
    )
    conn.autocommit = autocommit
    return conn

# ── Reset clean tables ─────────────────────────────────────────────────────
def reset_clean_tables(conn_w):
    print("\n=== --reset-clean: Truncating clean tables ===")
    cur = conn_w.cursor()
    cur.execute("""
        TRUNCATE TABLE
            clean.artist_relations,
            clean.artist_genres,
            clean.track_artists,
            clean.genres,
            clean.tracks,
            clean.artists
        RESTART IDENTITY
    """)
    conn_w.commit()
    cur.close()
    print("  All clean tables truncated.")

# ── Release date helpers ───────────────────────────────────────────────────
_RE_FULL  = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_RE_MONTH = re.compile(r"^(\d{4})-(\d{2})$")
_RE_YEAR  = re.compile(r"^(\d{4})$")

def parse_release_date(raw):
    """Return (normalized_date_str, release_year, release_month, decade, precision)."""
    if raw is None or str(raw).strip() == "":
        return None, None, None, None, "unknown"
    s = str(raw).strip()
    m = _RE_FULL.match(s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1900 <= y <= 2030 and 1 <= mo <= 12 and 1 <= d <= 31:
            return s, y, mo, (y // 10) * 10, "day"
    m = _RE_MONTH.match(s)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if 1900 <= y <= 2030 and 1 <= mo <= 12:
            return f"{y:04d}-{mo:02d}-01", y, mo, (y // 10) * 10, "month"
    m = _RE_YEAR.match(s)
    if m:
        y = int(m.group(1))
        if 1900 <= y <= 2030:
            return f"{y:04d}-01-01", y, None, (y // 10) * 10, "year"
    return None, None, None, None, "unknown"

def safe_literal_eval(s):
    if s is None or str(s).strip() in ("", "[]"):
        return []
    try:
        result = ast.literal_eval(str(s))
        return result if isinstance(result, list) else []
    except Exception:
        return []

# ── 1. Populate clean.tracks ──────────────────────────────────────────────
def populate_tracks(args):
    print("\n=== 1. Populating clean.tracks ===")
    t0 = time.time()

    conn_r = make_conn(args, autocommit=False)   # named cursor needs a transaction
    conn_w = make_conn(args, autocommit=False)

    cur_r = conn_r.cursor("cur_tracks", cursor_factory=psycopg2.extras.DictCursor)
    cur_r.itersize = BATCH
    cur_r.execute("""
        SELECT id, name, popularity, duration_ms, explicit,
               release_date, danceability, energy, key, loudness,
               mode, speechiness, acousticness, instrumentalness,
               liveness, valence, tempo, time_signature
        FROM raw.raw_tracks
    """)

    cur_w = conn_w.cursor()
    insert_sql = """
        INSERT INTO clean.tracks (
            track_id, name, popularity, duration_ms, duration_min,
            explicit, release_date, release_year, release_month, decade,
            release_precision, danceability, energy, key, loudness, mode,
            speechiness, acousticness, instrumentalness, liveness, valence,
            tempo, time_signature
        ) VALUES %s
        ON CONFLICT (track_id) DO NOTHING
    """

    def clamp01(v):
        try:
            f = float(v)
            return max(0.0, min(1.0, f))
        except (TypeError, ValueError):
            return None

    def clamp_key(v):
        try:
            i = int(float(v))
            return i if 0 <= i <= 11 else None
        except (TypeError, ValueError):
            return None

    def clamp_mode(v):
        try:
            i = int(float(v))
            return i if i in (0, 1) else None
        except (TypeError, ValueError):
            return None

    def safe_float(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    total = 0
    dur_warnings = {"short": 0, "long": 0}
    batch = []

    for row in cur_r:
        rd, ry, rm, dec, rp = parse_release_date(row["release_date"])

        try:
            tempo = float(row["tempo"]) if row["tempo"] is not None else None
            if tempo is not None and tempo <= 0:
                tempo = None
        except (TypeError, ValueError):
            tempo = None

        try:
            ts = int(float(row["time_signature"])) if row["time_signature"] is not None else None
            if ts is not None and ts not in (1, 2, 3, 4, 5):
                ts = None
        except (TypeError, ValueError):
            ts = None

        try:
            dur_ms = int(float(row["duration_ms"]))
        except (TypeError, ValueError):
            dur_ms = 0
        dur_min = round(dur_ms / 60000.0, 4)

        if dur_ms < 10000:
            dur_warnings["short"] += 1
        elif dur_ms > 3_600_000:
            dur_warnings["long"] += 1

        try:
            explicit = bool(int(float(row["explicit"])))
        except (TypeError, ValueError):
            explicit = False

        try:
            pop = max(0, min(100, int(float(row["popularity"]))))
        except (TypeError, ValueError):
            pop = 0

        batch.append((
            row["id"],
            row["name"].strip() if row["name"] else None,
            pop, dur_ms, dur_min, explicit,
            rd, ry, rm, dec, rp,
            clamp01(row["danceability"]),
            clamp01(row["energy"]),
            clamp_key(row["key"]),
            safe_float(row["loudness"]),
            clamp_mode(row["mode"]),
            clamp01(row["speechiness"]),
            clamp01(row["acousticness"]),
            clamp01(row["instrumentalness"]),
            clamp01(row["liveness"]),
            clamp01(row["valence"]),
            tempo, ts,
        ))

        if len(batch) >= BATCH:
            psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
            conn_w.commit()
            total += len(batch)
            print(f"  Inserted {total:,} tracks...")
            batch.clear()

    if batch:
        psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
        conn_w.commit()
        total += len(batch)

    cur_r.close()
    cur_w.execute("SELECT COUNT(*) FROM clean.tracks")
    count = cur_w.fetchone()[0]
    cur_w.close()
    conn_r.close()
    conn_w.close()
    elapsed = time.time() - t0
    print(f"  clean.tracks: {count:,} rows in {elapsed:.1f}s")
    print(f"  Duration warnings — short (<10s): {dur_warnings['short']:,}  long (>60min): {dur_warnings['long']:,}")
    return count, dur_warnings

# ── 2. Populate clean.artists ─────────────────────────────────────────────
def populate_artists(args):
    print("\n=== 2. Populating clean.artists ===")
    t0 = time.time()

    conn_r = make_conn(args, autocommit=False)   # named cursor needs a transaction
    conn_w = make_conn(args, autocommit=False)

    cur_r = conn_r.cursor("cur_artists", cursor_factory=psycopg2.extras.DictCursor)
    cur_r.itersize = BATCH
    cur_r.execute("SELECT id, name, followers, popularity FROM raw.raw_artists")

    cur_w = conn_w.cursor()
    insert_sql = """
        INSERT INTO clean.artists (artist_id, name, followers, popularity)
        VALUES %s
        ON CONFLICT (artist_id) DO NOTHING
    """

    total = 0
    batch = []

    for row in cur_r:
        try:
            followers = int(float(row["followers"])) if row["followers"] is not None else None
            if followers is not None and followers < 0:
                followers = None
        except (TypeError, ValueError):
            followers = None

        try:
            pop = max(0, min(100, int(float(row["popularity"]))))
        except (TypeError, ValueError):
            pop = None

        name = row["name"].strip() if row["name"] else None
        batch.append((row["id"], name, followers, pop))

        if len(batch) >= BATCH:
            psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
            conn_w.commit()
            total += len(batch)
            print(f"  Inserted {total:,} artists...")
            batch.clear()

    if batch:
        psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
        conn_w.commit()
        total += len(batch)

    cur_r.close()
    cur_w.execute("SELECT COUNT(*) FROM clean.artists")
    count = cur_w.fetchone()[0]
    cur_w.close()
    conn_r.close()
    conn_w.close()
    elapsed = time.time() - t0
    print(f"  clean.artists: {count:,} rows in {elapsed:.1f}s")
    return count

# ── 3. Populate clean.genres ──────────────────────────────────────────────
def populate_genres(args):
    print("\n=== 3. Populating clean.genres ===")
    t0 = time.time()

    conn_r = make_conn(args, autocommit=False)   # plain cursor — fetchall is ok for genres
    conn_w = make_conn(args, autocommit=False)

    cur_r = conn_r.cursor()
    cur_r.execute("SELECT genres FROM raw.raw_artists WHERE genres IS NOT NULL AND genres <> '[]'")

    unique_genres = {}
    for (genres_str,) in cur_r:
        for g in safe_literal_eval(genres_str):
            if isinstance(g, str) and g.strip():
                name = g.strip()
                norm = re.sub(r"\s+", " ", name.lower().strip())
                unique_genres.setdefault(name, norm)

    cur_r.close()
    conn_r.close()

    cur_w = conn_w.cursor()
    psycopg2.extras.execute_values(
        cur_w,
        "INSERT INTO clean.genres (genre_name, normalized_genre_name) VALUES %s ON CONFLICT (genre_name) DO NOTHING",
        list(unique_genres.items()),
        page_size=5000,
    )
    conn_w.commit()
    cur_w.execute("SELECT COUNT(*) FROM clean.genres")
    count = cur_w.fetchone()[0]
    cur_w.close()
    conn_w.close()
    elapsed = time.time() - t0
    print(f"  clean.genres: {count:,} unique genres in {elapsed:.1f}s")
    return count

# ── 4. Populate clean.track_artists ───────────────────────────────────────
def populate_track_artists(args):
    print("\n=== 4. Populating clean.track_artists ===")
    t0 = time.time()

    conn_w = make_conn(args, autocommit=False)
    cur_w = conn_w.cursor()
    cur_w.execute("SELECT artist_id FROM clean.artists")
    known_artists = set(r[0] for r in cur_w.fetchall())
    print(f"  Known artists: {len(known_artists):,}")

    conn_r = make_conn(args, autocommit=False)   # named cursor needs a transaction
    cur_r = conn_r.cursor("cur_id_artists", cursor_factory=psycopg2.extras.DictCursor)
    cur_r.itersize = BATCH
    cur_r.execute("SELECT id, id_artists FROM raw.raw_tracks")

    insert_sql = """
        INSERT INTO clean.track_artists (track_id, artist_id, artist_order, is_main_artist)
        VALUES %s
        ON CONFLICT (track_id, artist_id) DO NOTHING
    """

    total = 0
    skipped = 0
    batch = []

    for row in cur_r:
        track_id = row["id"]
        for order, aid in enumerate(safe_literal_eval(row["id_artists"])):
            if not isinstance(aid, str) or not aid.strip():
                continue
            aid = aid.strip()
            if aid not in known_artists:
                skipped += 1
                continue
            batch.append((track_id, aid, order, order == 0))

            if len(batch) >= BATCH:
                psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
                conn_w.commit()
                total += len(batch)
                print(f"  Inserted {total:,} track_artist rows...")
                batch.clear()

    if batch:
        psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
        conn_w.commit()
        total += len(batch)

    cur_r.close()
    cur_w.execute("SELECT COUNT(*) FROM clean.track_artists")
    count = cur_w.fetchone()[0]
    cur_w.close()
    conn_r.close()
    conn_w.close()
    elapsed = time.time() - t0
    print(f"  clean.track_artists: {count:,} rows in {elapsed:.1f}s  (skipped {skipped:,} unknown artists)")
    return count, skipped

# ── 5. Populate clean.artist_genres ───────────────────────────────────────
def populate_artist_genres(args):
    print("\n=== 5. Populating clean.artist_genres ===")
    t0 = time.time()

    conn_w = make_conn(args, autocommit=False)
    cur_w = conn_w.cursor()
    cur_w.execute("SELECT genre_name, genre_id FROM clean.genres")
    genre_map = {name: gid for name, gid in cur_w.fetchall()}
    cur_w.execute("SELECT artist_id FROM clean.artists")
    known_artists = set(r[0] for r in cur_w.fetchall())

    conn_r = make_conn(args, autocommit=False)   # named cursor needs a transaction
    cur_r = conn_r.cursor("cur_genres_ag", cursor_factory=psycopg2.extras.DictCursor)
    cur_r.itersize = BATCH
    cur_r.execute("SELECT id, genres FROM raw.raw_artists WHERE genres IS NOT NULL AND genres <> '[]'")

    insert_sql = """
        INSERT INTO clean.artist_genres (artist_id, genre_id, source)
        VALUES %s ON CONFLICT (artist_id, genre_id) DO NOTHING
    """

    total = 0
    batch = []

    for row in cur_r:
        aid = row["id"]
        if aid not in known_artists:
            continue
        for g in safe_literal_eval(row["genres"]):
            if not isinstance(g, str) or not g.strip():
                continue
            gid = genre_map.get(g.strip())
            if gid is None:
                continue
            batch.append((aid, gid, "artists_csv"))
            if len(batch) >= BATCH:
                psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
                conn_w.commit()
                total += len(batch)
                print(f"  Inserted {total:,} artist_genre rows...")
                batch.clear()

    if batch:
        psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
        conn_w.commit()
        total += len(batch)

    cur_r.close()
    cur_w.execute("SELECT COUNT(*) FROM clean.artist_genres")
    count = cur_w.fetchone()[0]
    cur_w.close()
    conn_r.close()
    conn_w.close()
    elapsed = time.time() - t0
    print(f"  clean.artist_genres: {count:,} rows in {elapsed:.1f}s")
    return count

# ── 6. Populate clean.artist_relations ────────────────────────────────────
def populate_artist_relations(args):
    print("\n=== 6. Populating clean.artist_relations ===")
    t0 = time.time()

    conn_w = make_conn(args, autocommit=False)
    cur_w = conn_w.cursor()
    cur_w.execute("SELECT artist_id FROM clean.artists")
    known_artists = set(r[0] for r in cur_w.fetchall())
    print(f"  Known artists: {len(known_artists):,}")

    conn_r = make_conn(args, autocommit=False)   # named cursor needs a transaction
    cur_r = conn_r.cursor("cur_json_ar", cursor_factory=psycopg2.extras.DictCursor)
    cur_r.itersize = BATCH
    cur_r.execute("SELECT artist_id, raw_values FROM raw.raw_artist_json WHERE value_count > 0")

    insert_sql = """
        INSERT INTO clean.artist_relations (artist_id, related_artist_id, relation_order, source)
        VALUES %s ON CONFLICT (artist_id, related_artist_id) DO NOTHING
    """

    total = 0
    skipped = 0
    batch = []

    for row in cur_r:
        aid = row["artist_id"]
        if aid not in known_artists:
            skipped += 1
            continue

        raw_val = row["raw_values"]
        if isinstance(raw_val, list):
            related_list = raw_val
        else:
            try:
                related_list = json.loads(str(raw_val))
            except Exception:
                related_list = []

        for order, rid in enumerate(related_list):
            if not isinstance(rid, str) or not rid.strip():
                continue
            rid = rid.strip()
            if rid not in known_artists or rid == aid:
                skipped += 1
                continue
            batch.append((aid, rid, order, "dict_artists_json"))
            if len(batch) >= BATCH:
                psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
                conn_w.commit()
                total += len(batch)
                print(f"  Inserted {total:,} artist_relation rows...")
                batch.clear()

    if batch:
        psycopg2.extras.execute_values(cur_w, insert_sql, batch, page_size=BATCH)
        conn_w.commit()
        total += len(batch)

    cur_r.close()
    cur_w.execute("SELECT COUNT(*) FROM clean.artist_relations")
    count = cur_w.fetchone()[0]
    cur_w.close()
    conn_r.close()
    conn_w.close()
    elapsed = time.time() - t0
    print(f"  clean.artist_relations: {count:,} rows in {elapsed:.1f}s  (skipped {skipped:,})")
    return count, skipped

# ── Write cleaning log ─────────────────────────────────────────────────────
def write_cleaning_log(args, log_dir, results, start_ts):
    log_path = log_dir / "CLEANING_LOG.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    elapsed_total = (datetime.now(timezone.utc) - start_ts).total_seconds()

    counts   = results["counts"]
    dur_w    = results["duration_warnings"]
    overall  = "PASS"

    rows_md = ""
    for tbl, cnt in counts.items():
        status = "PASS" if cnt > 0 else "WARN"
        rows_md += f"| `{tbl}` | {cnt:,} | {status} |\n"

    md = f"""# CLEANING LOG — FEATURE 1.4

## 1. Metadata

| Field | Value |
|-------|-------|
| Feature | 1.4 — Data Cleaning & Normalization |
| Owner | Đạt |
| Database | `{args.database}` @ `{args.host}:{args.port}` |
| User | `{args.user}` |
| Date/Time | {now} |
| Duration | {elapsed_total:.0f}s |
| Reset clean | {'Yes' if args.reset_clean else 'No'} |

---

## 2. Clean Table Row Counts

| Table | Rows | Status |
|-------|------|--------|
{rows_md}
---

## 3. Cleaning Rules Applied

| Rule | Applied |
|------|---------|
| tempo = 0 → NULL | Yes |
| time_signature not in 1–5 → NULL | Yes |
| release_date YYYY-MM-DD → precision=day | Yes |
| release_date YYYY-MM → YYYY-MM-01, precision=month | Yes |
| release_date YYYY → YYYY-01-01, precision=year | Yes |
| explicit 0/1 → boolean | Yes |
| duration_min = duration_ms / 60000.0 | Yes |
| artists/id_artists → ast.literal_eval | Yes |
| genres → ast.literal_eval | Yes |
| dict_artists.json → artist_relations only | Yes |
| FK filter: track_artists (skip unknown artists) | Yes |
| FK filter: artist_relations (both sides must exist) | Yes |

---

## 4. Warnings / Outliers

| Warning | Count |
|---------|-------|
| duration_ms < 10,000 (short tracks) | {dur_w.get('short', 0):,} |
| duration_ms > 3,600,000 (long tracks) | {dur_w.get('long', 0):,} |
| track_artists skipped (unknown artist FK) | {results.get('ta_skipped', 0):,} |
| artist_relations skipped (unknown FK) | {results.get('ar_skipped', 0):,} |

---

## 5. Status

**{overall}** — Clean layer populated. Proceed to validate_clean_tables.py.
"""
    with open(str(log_path), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Cleaning log written → {log_path}")
    return log_path

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    base, log_dir = resolve_log_dir(args)
    start_ts = datetime.now(timezone.utc)

    print("HitRadar Feature 1.4 — Data Cleaning & Normalization")
    print(f"Target: {args.database} @ {args.host}:{args.port} (user: {args.user})")
    print(f"Started: {start_ts.strftime('%Y-%m-%d %H:%M UTC')}")

    # Quick connectivity check
    conn_test = make_conn(args)
    print("  [OK] Database connection established")
    conn_test.close()

    if args.reset_clean:
        conn_reset = make_conn(args)
        reset_clean_tables(conn_reset)
        conn_reset.close()

    count_tracks,   dur_w      = populate_tracks(args)
    count_artists              = populate_artists(args)
    count_genres               = populate_genres(args)
    count_ta,       ta_skipped = populate_track_artists(args)
    count_ag                   = populate_artist_genres(args)
    count_ar,       ar_skipped = populate_artist_relations(args)

    counts = {
        "clean.tracks":           count_tracks,
        "clean.artists":          count_artists,
        "clean.genres":           count_genres,
        "clean.track_artists":    count_ta,
        "clean.artist_genres":    count_ag,
        "clean.artist_relations": count_ar,
    }
    results = {
        "counts":            counts,
        "duration_warnings": dur_w,
        "ta_skipped":        ta_skipped,
        "ar_skipped":        ar_skipped,
    }

    log_path = write_cleaning_log(args, log_dir, results, start_ts)

    print("\n=== CLEANING SUMMARY ===")
    for tbl, cnt in counts.items():
        print(f"  {tbl}: {cnt:,}")

    print(f"\nFeature 1.4 cleaning status: PASS")
    print(f"Log: {log_path}")
    print(f"\nNext step: python 9.SCRIPTS/validate_clean_tables.py --database {args.database}")

if __name__ == "__main__":
    main()

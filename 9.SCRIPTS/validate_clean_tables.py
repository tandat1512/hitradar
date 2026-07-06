"""
validate_clean_tables.py — Feature 1.4: Validate clean layer
Kiểm tra clean tables sau khi clean_raw_to_clean.py đã chạy.

Usage:
  python 9.SCRIPTS/validate_clean_tables.py [--base-dir PATH]
                                             [--database DATABASE] [--user USER]
Password: set PGPASSWORD trước khi chạy.
"""
import sys, os, argparse
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
except ImportError:
    print("ERROR: pip install psycopg2-binary")
    sys.exit(1)

def parse_args():
    p = argparse.ArgumentParser(description="HitRadar Feature 1.4 validator")
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

def get_conn(args):
    password = os.environ.get("PGPASSWORD")
    if not password:
        print("ERROR: PGPASSWORD not set.")
        sys.exit(1)
    return psycopg2.connect(
        host=args.host, port=args.port, user=args.user,
        password=password, dbname=args.database, connect_timeout=10,
    )

def q1(cur, sql, params=None):
    cur.execute(sql, params)
    return cur.fetchone()[0]

# ── Checks ────────────────────────────────────────────────────────────────

def check_row_counts(cur):
    print("\n=== 1. Row Count Validation ===")
    results = {}

    raw_tracks  = q1(cur, "SELECT COUNT(*) FROM raw.raw_tracks")
    raw_artists = q1(cur, "SELECT COUNT(*) FROM raw.raw_artists")
    clean_tracks  = q1(cur, "SELECT COUNT(*) FROM clean.tracks")
    clean_artists = q1(cur, "SELECT COUNT(*) FROM clean.artists")

    # tracks and artists must match raw exactly
    for name, raw_cnt, clean_cnt in [
        ("tracks",  raw_tracks,  clean_tracks),
        ("artists", raw_artists, clean_artists),
    ]:
        status = "PASS" if clean_cnt == raw_cnt else "FAIL"
        print(f"  {name}: raw={raw_cnt:,}  clean={clean_cnt:,} → {status}")
        results[name] = {"raw": raw_cnt, "clean": clean_cnt, "status": status}

    # junction tables must be > 0
    for tbl in ("clean.track_artists", "clean.genres", "clean.artist_genres", "clean.artist_relations"):
        cnt = q1(cur, f"SELECT COUNT(*) FROM {tbl}")
        status = "PASS" if cnt > 0 else "FAIL"
        print(f"  {tbl}: {cnt:,} → {status}")
        results[tbl] = {"count": cnt, "status": status}

    return results

def check_id_uniqueness(cur):
    print("\n=== 2. ID Uniqueness & Null Validation ===")
    results = {}
    for tbl, col in [("clean.tracks", "track_id"), ("clean.artists", "artist_id")]:
        nulls = q1(cur, f"SELECT COUNT(*) FROM {tbl} WHERE {col} IS NULL")
        dups  = q1(cur, f"SELECT COUNT(*) - COUNT(DISTINCT {col}) FROM {tbl}")
        status = "PASS" if nulls == 0 and dups == 0 else "FAIL"
        print(f"  {tbl}.{col}: nulls={nulls}, duplicates={dups} → {status}")
        results[tbl] = {"nulls": nulls, "duplicates": dups, "status": status}
    return results

def check_release_precision(cur):
    print("\n=== 3. release_precision Validation ===")
    results = {}
    cur.execute("""
        SELECT release_precision, COUNT(*) AS cnt
        FROM clean.tracks
        GROUP BY release_precision
        ORDER BY cnt DESC
    """)
    dist = {row[0]: row[1] for row in cur.fetchall()}
    print(f"  Distribution: {dist}")

    invalid = q1(cur, """
        SELECT COUNT(*) FROM clean.tracks
        WHERE release_precision NOT IN ('day', 'month', 'year', 'unknown')
           OR release_precision IS NULL
    """)
    status = "PASS" if invalid == 0 else "FAIL"
    print(f"  Invalid precision count: {invalid} → {status}")
    results["distribution"] = dist
    results["invalid_count"] = invalid
    results["status"] = status
    return results

def check_tempo_time_sig(cur):
    print("\n=== 4. Tempo / Time Signature Validation ===")
    results = {}

    tempo_bad   = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE tempo <= 0")
    tempo_null  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE tempo IS NULL")
    ts_bad      = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE time_signature = 0")
    ts_null     = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE time_signature IS NULL")

    status_tempo = "PASS" if tempo_bad == 0 else "FAIL"
    status_ts    = "PASS" if ts_bad == 0 else "FAIL"

    print(f"  tempo <= 0 remaining: {tempo_bad} → {status_tempo}")
    print(f"  tempo IS NULL: {tempo_null:,}")
    print(f"  time_signature = 0 remaining: {ts_bad} → {status_ts}")
    print(f"  time_signature IS NULL: {ts_null:,}")

    results["tempo_bad"]   = {"count": tempo_bad,  "status": status_tempo}
    results["tempo_null"]  = tempo_null
    results["ts_bad"]      = {"count": ts_bad,     "status": status_ts}
    results["ts_null"]     = ts_null
    return results

def check_duration_min(cur):
    print("\n=== 5. duration_min Validation ===")
    null_cnt  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_min IS NULL")
    short_cnt = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_ms < 10000")
    long_cnt  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_ms > 3600000")
    status = "PASS" if null_cnt == 0 else "FAIL"
    print(f"  duration_min IS NULL: {null_cnt} → {status}")
    print(f"  Short tracks (<10s): {short_cnt:,}  Long tracks (>60min): {long_cnt:,}")
    return {"null": null_cnt, "short": short_cnt, "long": long_cnt, "status": status}

def check_fk_basics(cur):
    print("\n=== 6. FK Sanity Checks ===")
    results = {}

    # track_artists → tracks
    orphan_ta_t = q1(cur, """
        SELECT COUNT(*) FROM clean.track_artists ta
        WHERE NOT EXISTS (SELECT 1 FROM clean.tracks t WHERE t.track_id = ta.track_id)
    """)
    # track_artists → artists
    orphan_ta_a = q1(cur, """
        SELECT COUNT(*) FROM clean.track_artists ta
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ta.artist_id)
    """)
    # artist_genres → artists
    orphan_ag_a = q1(cur, """
        SELECT COUNT(*) FROM clean.artist_genres ag
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ag.artist_id)
    """)
    # artist_relations → artists (both sides)
    orphan_ar_1 = q1(cur, """
        SELECT COUNT(*) FROM clean.artist_relations ar
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ar.artist_id)
    """)
    orphan_ar_2 = q1(cur, """
        SELECT COUNT(*) FROM clean.artist_relations ar
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ar.related_artist_id)
    """)

    for name, cnt in [
        ("track_artists → tracks", orphan_ta_t),
        ("track_artists → artists", orphan_ta_a),
        ("artist_genres → artists", orphan_ag_a),
        ("artist_relations → artists (src)", orphan_ar_1),
        ("artist_relations → artists (tgt)", orphan_ar_2),
    ]:
        status = "PASS" if cnt == 0 else "FAIL"
        print(f"  {name}: orphans={cnt} → {status}")
        results[name] = {"orphans": cnt, "status": status}

    return results

def get_samples(cur):
    samples = {}
    for tbl, sql in [
        ("clean.tracks",
         "SELECT track_id, name, popularity, duration_min, release_date, release_precision, tempo, time_signature FROM clean.tracks LIMIT 3"),
        ("clean.artists",
         "SELECT artist_id, name, followers, popularity FROM clean.artists LIMIT 3"),
        ("clean.track_artists",
         "SELECT track_id, artist_id, artist_order, is_main_artist FROM clean.track_artists LIMIT 3"),
        ("clean.genres",
         "SELECT genre_id, genre_name, normalized_genre_name FROM clean.genres LIMIT 3"),
        ("clean.artist_genres",
         "SELECT artist_id, genre_id, source FROM clean.artist_genres LIMIT 3"),
        ("clean.artist_relations",
         "SELECT artist_id, related_artist_id, relation_order FROM clean.artist_relations LIMIT 3"),
    ]:
        cur.execute(sql)
        rows = cur.fetchall()
        colnames = [d[0] for d in cur.description]
        samples[tbl] = [dict(zip(colnames, r)) for r in rows]
    return samples

# ── Write validation report ────────────────────────────────────────────────
def write_validation_report(args, base, log_dir, row_r, id_r, prec_r,
                             tempo_r, dur_r, fk_r, samples):
    report_path = log_dir / "CLEAN_TABLE_VALIDATION_REPORT.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    all_statuses = []
    all_statuses += [v["status"] for v in row_r.values()]
    all_statuses += [v["status"] for v in id_r.values()]
    all_statuses.append(prec_r["status"])
    all_statuses.append(tempo_r["tempo_bad"]["status"])
    all_statuses.append(tempo_r["ts_bad"]["status"])
    all_statuses.append(dur_r["status"])
    all_statuses += [v["status"] for v in fk_r.values()]

    overall = "PASS" if all(s == "PASS" for s in all_statuses) else "FAIL"

    def sample_md(tbl):
        rows = samples.get(tbl, [])
        if not rows:
            return "_No data_\n"
        cols = list(rows[0].keys())
        hdr = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        body = ""
        for r in rows:
            vals = [str(r.get(c, ""))[:50].replace("|", "\\|") for c in cols]
            body += "| " + " | ".join(vals) + " |\n"
        return hdr + "\n" + sep + "\n" + body

    prec_dist = "  ".join(f"{k}: {v:,}" for k, v in prec_r["distribution"].items())

    md = f"""# CLEAN TABLE VALIDATION REPORT — FEATURE 1.4

## 1. Metadata

| Field | Value |
|-------|-------|
| Database | `{args.database}` @ `{args.host}:{args.port}` |
| User | `{args.user}` |
| Date/Time | {now} |
| Base directory | `{base}` |
| **Overall** | **{overall}** |

---

## 2. Row Count Validation (Raw vs Clean)

| Table | Raw | Clean | Status |
|-------|-----|-------|--------|
| tracks  | {row_r.get('tracks',  {}).get('raw', '?'):,} | {row_r.get('tracks',  {}).get('clean', '?'):,} | **{row_r.get('tracks',  {}).get('status', '?')}** |
| artists | {row_r.get('artists', {}).get('raw', '?'):,} | {row_r.get('artists', {}).get('clean', '?'):,} | **{row_r.get('artists', {}).get('status', '?')}** |

| Junction Table | Row Count | Status |
|---------------|-----------|--------|
| clean.track_artists | {row_r.get('clean.track_artists', {}).get('count', '?'):,} | **{row_r.get('clean.track_artists', {}).get('status', '?')}** |
| clean.genres | {row_r.get('clean.genres', {}).get('count', '?'):,} | **{row_r.get('clean.genres', {}).get('status', '?')}** |
| clean.artist_genres | {row_r.get('clean.artist_genres', {}).get('count', '?'):,} | **{row_r.get('clean.artist_genres', {}).get('status', '?')}** |
| clean.artist_relations | {row_r.get('clean.artist_relations', {}).get('count', '?'):,} | **{row_r.get('clean.artist_relations', {}).get('status', '?')}** |

---

## 3. ID Uniqueness Validation

| Table | Null IDs | Duplicate IDs | Status |
|-------|---------|--------------|--------|
| clean.tracks | {id_r.get('clean.tracks', {}).get('nulls', '?')} | {id_r.get('clean.tracks', {}).get('duplicates', '?')} | **{id_r.get('clean.tracks', {}).get('status', '?')}** |
| clean.artists | {id_r.get('clean.artists', {}).get('nulls', '?')} | {id_r.get('clean.artists', {}).get('duplicates', '?')} | **{id_r.get('clean.artists', {}).get('status', '?')}** |

---

## 4. release_precision Validation

| Distribution | Count |
|-------------|-------|
{chr(10).join(f"| {k} | {v:,} |" for k, v in prec_r["distribution"].items())}

| Check | Count | Status |
|-------|-------|--------|
| Invalid precision | {prec_r["invalid_count"]} | **{prec_r["status"]}** |

---

## 5. Tempo / Time Signature Validation

| Check | Count | Status |
|-------|-------|--------|
| tempo <= 0 remaining | {tempo_r["tempo_bad"]["count"]} | **{tempo_r["tempo_bad"]["status"]}** |
| tempo IS NULL (converted) | {tempo_r["tempo_null"]:,} | INFO |
| time_signature = 0 remaining | {tempo_r["ts_bad"]["count"]} | **{tempo_r["ts_bad"]["status"]}** |
| time_signature IS NULL (converted) | {tempo_r["ts_null"]:,} | INFO |

---

## 6. Duration Validation

| Check | Count | Status |
|-------|-------|--------|
| duration_min IS NULL | {dur_r["null"]} | **{dur_r["status"]}** |
| Short tracks (< 10s) | {dur_r["short"]:,} | WARNING |
| Long tracks (> 60min) | {dur_r["long"]:,} | WARNING |

---

## 7. FK Sanity Checks

| Check | Orphan rows | Status |
|-------|------------|--------|
{chr(10).join(f"| {k} | {v['orphans']} | **{v['status']}** |" for k, v in fk_r.items())}

---

## 8. Sample Records

### clean.tracks

{sample_md("clean.tracks")}

### clean.artists

{sample_md("clean.artists")}

### clean.track_artists

{sample_md("clean.track_artists")}

### clean.genres

{sample_md("clean.genres")}

### clean.artist_genres

{sample_md("clean.artist_genres")}

### clean.artist_relations

{sample_md("clean.artist_relations")}

---

## 9. Overall Status

**{overall}**
"""
    with open(str(report_path), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Validation report written → {report_path}")
    return report_path, overall

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    base, log_dir = resolve_log_dir(args)

    print("HitRadar Feature 1.4 — Clean Table Validation")
    print(f"Database: {args.database} @ {args.host}:{args.port}")
    print(f"Base directory: {base}")

    conn = get_conn(args)
    cur  = conn.cursor()

    row_r   = check_row_counts(cur)
    id_r    = check_id_uniqueness(cur)
    prec_r  = check_release_precision(cur)
    tempo_r = check_tempo_time_sig(cur)
    dur_r   = check_duration_min(cur)
    fk_r    = check_fk_basics(cur)
    samples = get_samples(cur)

    cur.close()
    conn.close()

    report_path, overall = write_validation_report(
        args, base, log_dir, row_r, id_r, prec_r, tempo_r, dur_r, fk_r, samples
    )

    print("\n=== VALIDATION SUMMARY ===")
    print(f"  tracks:             {row_r.get('tracks',{}).get('status','?')}")
    print(f"  artists:            {row_r.get('artists',{}).get('status','?')}")
    print(f"  release_precision:  {prec_r['status']}")
    print(f"  tempo:              {tempo_r['tempo_bad']['status']}")
    print(f"  time_signature:     {tempo_r['ts_bad']['status']}")
    print(f"  duration_min:       {dur_r['status']}")
    fk_overall = "PASS" if all(v["status"] == "PASS" for v in fk_r.values()) else "FAIL"
    print(f"  FK checks:          {fk_overall}")
    print(f"\nOverall: {overall}")
    print(f"Report: {report_path}")

    if overall != "PASS":
        sys.exit(1)

if __name__ == "__main__":
    main()

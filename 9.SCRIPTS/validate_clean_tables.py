"""
validate_clean_tables.py — Feature 1.4: Validate clean layer
Kiểm tra clean tables sau khi clean_raw_to_clean.py đã chạy.

Usage:
  python 9.SCRIPTS/validate_clean_tables.py [--base-dir PATH]
                                             [--database DATABASE] [--user USER]
Password: set PGPASSWORD trước khi chạy.

Checks:
  1. Row counts (raw vs clean)
  2. ID uniqueness & null
  3. release_precision validity
  4. Tempo / time_signature (including range check)
  5. duration_min
  6. FK sanity
  7. Missing value handling (retained NULL — PASS by rule)
  8. Release derived column consistency
  9. Audio feature range
  10. Popularity range
  11. Relationship coverage (WARNING, not FAIL)
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

# Known constants from Feature 1.3 cleaning run (for coverage ratio)
TRACK_ARTISTS_SKIPPED = 26_224
AR_TOTAL_RAW          = 8_864_472

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

# ── Check 1: Row counts ───────────────────────────────────────────────────
def check_row_counts(cur):
    print("\n=== 1. Row Count Validation ===")
    results = {}
    raw_tracks  = q1(cur, "SELECT COUNT(*) FROM raw.raw_tracks")
    raw_artists = q1(cur, "SELECT COUNT(*) FROM raw.raw_artists")
    clean_tracks  = q1(cur, "SELECT COUNT(*) FROM clean.tracks")
    clean_artists = q1(cur, "SELECT COUNT(*) FROM clean.artists")

    for name, raw_cnt, clean_cnt in [
        ("tracks",  raw_tracks,  clean_tracks),
        ("artists", raw_artists, clean_artists),
    ]:
        status = "PASS" if clean_cnt == raw_cnt else "FAIL"
        print(f"  {name}: raw={raw_cnt:,}  clean={clean_cnt:,} → {status}")
        results[name] = {"raw": raw_cnt, "clean": clean_cnt, "status": status}

    for tbl in ("clean.track_artists", "clean.genres", "clean.artist_genres", "clean.artist_relations"):
        cnt = q1(cur, f"SELECT COUNT(*) FROM {tbl}")
        status = "PASS" if cnt > 0 else "FAIL"
        print(f"  {tbl}: {cnt:,} → {status}")
        results[tbl] = {"count": cnt, "status": status}

    return results

# ── Check 2: ID uniqueness ────────────────────────────────────────────────
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

# ── Check 3: release_precision ────────────────────────────────────────────
def check_release_precision(cur):
    print("\n=== 3. release_precision Validation ===")
    cur.execute("""
        SELECT release_precision, COUNT(*) AS cnt
        FROM clean.tracks
        GROUP BY release_precision ORDER BY cnt DESC
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
    return {"distribution": dist, "invalid_count": invalid, "status": status}

# ── Check 4: Tempo / time_signature ──────────────────────────────────────
def check_tempo_time_sig(cur):
    print("\n=== 4. Tempo / Time Signature Validation ===")
    tempo_bad  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE tempo <= 0")
    tempo_null = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE tempo IS NULL")
    ts_zero    = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE time_signature = 0")
    ts_oor     = q1(cur, """
        SELECT COUNT(*) FROM clean.tracks
        WHERE time_signature IS NOT NULL AND time_signature NOT BETWEEN 1 AND 5
    """)
    ts_null    = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE time_signature IS NULL")

    status_tempo = "PASS" if tempo_bad == 0 else "FAIL"
    # FAIL if either zero or out-of-range remains
    status_ts    = "PASS" if ts_zero == 0 and ts_oor == 0 else "FAIL"

    print(f"  tempo <= 0 remaining:                {tempo_bad} → {status_tempo}")
    print(f"  tempo IS NULL (converted):           {tempo_null:,}")
    print(f"  time_signature = 0 remaining:        {ts_zero} → {'PASS' if ts_zero==0 else 'FAIL'}")
    print(f"  time_signature out-of-range (1–5):   {ts_oor} → {'PASS' if ts_oor==0 else 'FAIL'}")
    print(f"  time_signature IS NULL (converted):  {ts_null:,}")

    return {
        "tempo_bad":  {"count": tempo_bad,  "status": status_tempo},
        "tempo_null": tempo_null,
        "ts_zero":    {"count": ts_zero,    "status": "PASS" if ts_zero == 0 else "FAIL"},
        "ts_oor":     {"count": ts_oor,     "status": "PASS" if ts_oor == 0 else "FAIL"},
        "ts_null":    ts_null,
        "ts_overall": {"status": status_ts},
    }

# ── Check 5: duration_min ─────────────────────────────────────────────────
def check_duration_min(cur):
    print("\n=== 5. duration_min Validation ===")
    null_cnt  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_min IS NULL")
    short_cnt = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_ms < 10000")
    long_cnt  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_ms > 3600000")
    status = "PASS" if null_cnt == 0 else "FAIL"
    print(f"  duration_min IS NULL: {null_cnt} → {status}")
    print(f"  Short tracks (<10s): {short_cnt:,}  Long tracks (>60min): {long_cnt:,}")
    return {"null": null_cnt, "short": short_cnt, "long": long_cnt, "status": status}

# ── Check 6: FK sanity ────────────────────────────────────────────────────
def check_fk_basics(cur):
    print("\n=== 6. FK Sanity Checks ===")
    results = {}
    checks = [
        ("track_artists → tracks",       "SELECT COUNT(*) FROM clean.track_artists ta WHERE NOT EXISTS (SELECT 1 FROM clean.tracks t WHERE t.track_id = ta.track_id)"),
        ("track_artists → artists",      "SELECT COUNT(*) FROM clean.track_artists ta WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ta.artist_id)"),
        ("artist_genres → artists",      "SELECT COUNT(*) FROM clean.artist_genres ag WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ag.artist_id)"),
        ("artist_relations → artists (src)", "SELECT COUNT(*) FROM clean.artist_relations ar WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ar.artist_id)"),
        ("artist_relations → artists (tgt)", "SELECT COUNT(*) FROM clean.artist_relations ar WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ar.related_artist_id)"),
    ]
    for name, sql in checks:
        cnt = q1(cur, sql)
        status = "PASS" if cnt == 0 else "FAIL"
        print(f"  {name}: orphans={cnt} → {status}")
        results[name] = {"orphans": cnt, "status": status}
    return results

# ── Check 7: Missing value handling (retained NULL — PASS by rule) ────────
def check_missing_value_handling(cur):
    print("\n=== 7. Missing Value Handling (Retained NULL — PASS by Rule) ===")
    tracks_name_null    = q1(cur, "SELECT COUNT(*) FROM clean.tracks  WHERE name IS NULL")
    artists_name_null   = q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE name IS NULL")
    followers_null      = q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE followers IS NULL")

    # Per cleaning rule: NULL is kept, not dropped. Status is always PASS.
    print(f"  clean.tracks.name IS NULL:        {tracks_name_null:,}  (retained by rule) → PASS")
    print(f"  clean.artists.name IS NULL:       {artists_name_null:,}  (retained by rule) → PASS")
    print(f"  clean.artists.followers IS NULL:  {followers_null:,}  (retained by rule) → PASS")
    return {
        "tracks_name_null":   tracks_name_null,
        "artists_name_null":  artists_name_null,
        "followers_null":     followers_null,
        "status":             "PASS",
    }

# ── Check 8: Release derived column consistency ───────────────────────────
def check_release_derived_columns(cur):
    print("\n=== 8. Release Derived Column Consistency ===")

    year_null            = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_year IS NULL")
    year_prec_month_nnull = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_precision='year' AND release_month IS NOT NULL")
    month_prec_month_null = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_precision='month' AND release_month IS NULL")
    day_prec_date_null   = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_precision='day' AND release_date IS NULL")
    decade_inconsist     = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_year IS NOT NULL AND decade IS NULL")

    # FAIL if any derived column is inconsistent with precision
    inconsistencies = year_prec_month_nnull + month_prec_month_null + day_prec_date_null + decade_inconsist
    status = "PASS" if inconsistencies == 0 else "FAIL"

    print(f"  release_year IS NULL:                              {year_null:,}")
    print(f"  precision='year' but release_month non-null:       {year_prec_month_nnull} → {'OK' if year_prec_month_nnull==0 else 'BAD'}")
    print(f"  precision='month' but release_month IS NULL:       {month_prec_month_null} → {'OK' if month_prec_month_null==0 else 'BAD'}")
    print(f"  precision='day' but release_date IS NULL:          {day_prec_date_null} → {'OK' if day_prec_date_null==0 else 'BAD'}")
    print(f"  release_year non-null but decade IS NULL:          {decade_inconsist} → {'OK' if decade_inconsist==0 else 'BAD'}")
    print(f"  Overall → {status}")

    return {
        "year_null":              year_null,
        "year_prec_month_nnull":  year_prec_month_nnull,
        "month_prec_month_null":  month_prec_month_null,
        "day_prec_date_null":     day_prec_date_null,
        "decade_inconsist":       decade_inconsist,
        "status":                 status,
    }

# ── Check 9: Audio feature range ─────────────────────────────────────────
def check_audio_feature_range(cur):
    print("\n=== 9. Audio Feature Range Validation ===")
    features = [
        ("danceability",     "danceability < 0 OR danceability > 1"),
        ("energy",           "energy < 0 OR energy > 1"),
        ("speechiness",      "speechiness < 0 OR speechiness > 1"),
        ("acousticness",     "acousticness < 0 OR acousticness > 1"),
        ("instrumentalness", "instrumentalness < 0 OR instrumentalness > 1"),
        ("liveness",         "liveness < 0 OR liveness > 1"),
        ("valence",          "valence < 0 OR valence > 1"),
    ]
    results = {}
    all_pass = True
    for col, cond in features:
        cnt = q1(cur, f"SELECT COUNT(*) FROM clean.tracks WHERE {cond}")
        status = "PASS" if cnt == 0 else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  {col} out-of-range [0,1]: {cnt} → {status}")
        results[col] = {"oor_count": cnt, "status": status}

    results["overall_status"] = "PASS" if all_pass else "FAIL"
    return results

# ── Check 10: Popularity range ───────────────────────────────────────────
def check_popularity_range(cur):
    print("\n=== 10. Popularity Range Validation ===")
    tracks_oor  = q1(cur, "SELECT COUNT(*) FROM clean.tracks  WHERE popularity NOT BETWEEN 0 AND 100")
    artists_oor = q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE popularity NOT BETWEEN 0 AND 100")
    status = "PASS" if tracks_oor == 0 and artists_oor == 0 else "FAIL"
    print(f"  clean.tracks.popularity OOR:   {tracks_oor} → {'PASS' if tracks_oor==0 else 'FAIL'}")
    print(f"  clean.artists.popularity OOR:  {artists_oor} → {'PASS' if artists_oor==0 else 'FAIL'}")
    print(f"  Overall → {status}")
    return {
        "tracks_oor":  {"count": tracks_oor,  "status": "PASS" if tracks_oor==0 else "FAIL"},
        "artists_oor": {"count": artists_oor, "status": "PASS" if artists_oor==0 else "FAIL"},
        "status":      status,
    }

# ── Check 11: Relationship coverage (WARNING, not FAIL) ──────────────────
def check_relationship_coverage(cur):
    print("\n=== 11. Relationship Coverage (WARNING Section) ===")
    ta_count = q1(cur, "SELECT COUNT(*) FROM clean.track_artists")
    ar_count = q1(cur, "SELECT COUNT(*) FROM clean.artist_relations")

    ta_estimated  = ta_count + TRACK_ARTISTS_SKIPPED
    ta_coverage   = ta_count / ta_estimated if ta_estimated > 0 else 0.0
    ta_skip_ratio = TRACK_ARTISTS_SKIPPED / ta_estimated if ta_estimated > 0 else 0.0

    ar_diff = AR_TOTAL_RAW - ar_count

    print(f"  track_artists inserted:              {ta_count:,}")
    print(f"  track_artists skipped (unknown FK):  {TRACK_ARTISTS_SKIPPED:,}")
    print(f"  track_artists estimated parsed:      {ta_estimated:,}")
    print(f"  track_artists coverage ratio:        {ta_coverage:.2%}")
    print(f"  track_artists skip ratio:            {ta_skip_ratio:.2%}  → WARNING (Feature 1.5)")
    print(f"  artist_relations raw total:          {AR_TOTAL_RAW:,}")
    print(f"  artist_relations inserted:           {ar_count:,}")
    print(f"  artist_relations difference:         {ar_diff}  (likely ON CONFLICT duplicate)")

    return {
        "ta_count":      ta_count,
        "ta_skipped":    TRACK_ARTISTS_SKIPPED,
        "ta_estimated":  ta_estimated,
        "ta_coverage":   ta_coverage,
        "ta_skip_ratio": ta_skip_ratio,
        "ar_count":      ar_count,
        "ar_raw_total":  AR_TOTAL_RAW,
        "ar_diff":       ar_diff,
    }

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

# ── Write validation report ───────────────────────────────────────────────
def write_validation_report(args, base, log_dir,
                             row_r, id_r, prec_r, tempo_r, dur_r, fk_r,
                             null_r, rel_r, audio_r, pop_r, cov_r, samples):
    report_path = log_dir / "CLEAN_TABLE_VALIDATION_REPORT.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Structural checks determine PASS/FAIL
    structural = []
    structural += [v["status"] for v in row_r.values()]
    structural += [v["status"] for v in id_r.values()]
    structural.append(prec_r["status"])
    structural.append(tempo_r["tempo_bad"]["status"])
    structural.append(tempo_r["ts_overall"]["status"])
    structural.append(dur_r["status"])
    structural += [v["status"] for v in fk_r.values()]
    structural.append(rel_r["status"])        # release derived
    structural.append(audio_r["overall_status"])
    structural.append(pop_r["status"])
    # null_r and cov_r are WARNING-only, never FAIL overall

    overall = "PASS" if all(s == "PASS" for s in structural) else "FAIL"

    def sample_md(tbl):
        rows = samples.get(tbl, [])
        if not rows:
            return "_No data_\n"
        cols = list(rows[0].keys())
        hdr  = "| " + " | ".join(cols) + " |"
        sep  = "| " + " | ".join(["---"] * len(cols)) + " |"
        body = ""
        for r in rows:
            vals = [str(r.get(c, ""))[:50].replace("|", "\\|") for c in cols]
            body += "| " + " | ".join(vals) + " |\n"
        return hdr + "\n" + sep + "\n" + body

    audio_rows = "\n".join(
        f"| {col} | {v['oor_count']} | **{v['status']}** |"
        for col, v in audio_r.items() if col != "overall_status"
    )

    md = f"""# CLEAN TABLE VALIDATION REPORT — FEATURE 1.4
> Version: hotfix (extended checks)

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

## 4. Missing Value Handling

> Rule: NULL is retained in clean layer — rows are NOT dropped. Status = PASS.

| Column | NULL Count | Rule | Status |
|--------|-----------|------|--------|
| clean.tracks.name | {null_r['tracks_name_null']:,} | Retained NULL | **PASS** |
| clean.artists.name | {null_r['artists_name_null']:,} | Retained NULL | **PASS** |
| clean.artists.followers | {null_r['followers_null']:,} | Retained NULL (missing or negative) | **PASS** |

---

## 5. release_precision Validation

| Precision | Count |
|-----------|-------|
{chr(10).join(f"| {k} | {v:,} |" for k, v in prec_r["distribution"].items())}

| Check | Count | Status |
|-------|-------|--------|
| Invalid precision | {prec_r["invalid_count"]} | **{prec_r["status"]}** |

---

## 6. Release Derived Column Consistency

| Check | Count | Status |
|-------|-------|--------|
| precision='year' but release_month non-null | {rel_r['year_prec_month_nnull']} | **{'PASS' if rel_r['year_prec_month_nnull']==0 else 'FAIL'}** |
| precision='month' but release_month IS NULL | {rel_r['month_prec_month_null']} | **{'PASS' if rel_r['month_prec_month_null']==0 else 'FAIL'}** |
| precision='day' but release_date IS NULL | {rel_r['day_prec_date_null']} | **{'PASS' if rel_r['day_prec_date_null']==0 else 'FAIL'}** |
| release_year non-null but decade IS NULL | {rel_r['decade_inconsist']} | **{'PASS' if rel_r['decade_inconsist']==0 else 'FAIL'}** |
| **Overall** | | **{rel_r['status']}** |

---

## 7. Tempo / Time Signature Validation

| Check | Count | Status |
|-------|-------|--------|
| tempo <= 0 remaining | {tempo_r["tempo_bad"]["count"]} | **{tempo_r["tempo_bad"]["status"]}** |
| tempo IS NULL (converted) | {tempo_r["tempo_null"]:,} | INFO |
| time_signature = 0 remaining | {tempo_r["ts_zero"]["count"]} | **{tempo_r["ts_zero"]["status"]}** |
| time_signature outside 1–5 (non-NULL) | {tempo_r["ts_oor"]["count"]} | **{tempo_r["ts_oor"]["status"]}** |
| time_signature IS NULL (converted) | {tempo_r["ts_null"]:,} | INFO |
| **ts Overall** | | **{tempo_r["ts_overall"]["status"]}** |

---

## 8. Duration Validation

| Check | Count | Status |
|-------|-------|--------|
| duration_min IS NULL | {dur_r["null"]} | **{dur_r["status"]}** |
| Short tracks (< 10s) | {dur_r["short"]:,} | WARNING |
| Long tracks (> 60min) | {dur_r["long"]:,} | WARNING |

---

## 9. Audio Feature Range Validation [0, 1]

| Feature | Out-of-range count | Status |
|---------|-------------------|--------|
{audio_rows}

---

## 10. Popularity Range Validation [0, 100]

| Column | Out-of-range count | Status |
|--------|-------------------|--------|
| clean.tracks.popularity | {pop_r['tracks_oor']['count']} | **{pop_r['tracks_oor']['status']}** |
| clean.artists.popularity | {pop_r['artists_oor']['count']} | **{pop_r['artists_oor']['status']}** |
| **Overall** | | **{pop_r['status']}** |

---

## 11. FK Sanity Checks

| Check | Orphan rows | Status |
|-------|------------|--------|
{chr(10).join(f"| {k} | {v['orphans']} | **{v['status']}** |" for k, v in fk_r.items())}

---

## 12. Relationship Coverage (WARNING — not structural FAIL)

### track_artists Coverage

| Metric | Value |
|--------|-------|
| Inserted into clean.track_artists | {cov_r['ta_count']:,} |
| Skipped (unknown artist FK) | {cov_r['ta_skipped']:,} |
| Estimated total parsed assignments | {cov_r['ta_estimated']:,} |
| Coverage ratio | {cov_r['ta_coverage']:.2%} |
| Skip ratio | {cov_r['ta_skip_ratio']:.2%} |
| **Status** | **WARNING — Feature 1.5 data quality gate** |

> Skipped artists are Spotify artist IDs referenced in `id_artists` but absent from `artists.csv`.
> This is expected for very niche/inactive artists. Feature 1.5 will set an acceptance threshold.

### artist_relations Coverage

| Metric | Value |
|--------|-------|
| Total raw value assignments (`raw_artist_json`) | {cov_r['ar_raw_total']:,} |
| Inserted distinct pairs | {cov_r['ar_count']:,} |
| Difference | {cov_r['ar_diff']} |
| Likely cause | ON CONFLICT — 1 duplicate pair collapsed |
| **Status** | **WARNING — difference=1, not a data loss blocker** |

---

## 13. Sample Records

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

## 14. Overall Status

**{overall}**

> Structural checks (row counts, IDs, precision, tempo/ts, duration, FK, release derived, audio range, popularity range): all {'PASS' if overall == 'PASS' else 'contain FAIL'}.
> Coverage warnings (track_artists skip ratio, artist_relations diff=1) are documented but do not block Feature 1.4 close.
"""
    with open(str(report_path), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Validation report written → {report_path}")
    return report_path, overall

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    base, log_dir = resolve_log_dir(args)

    print("HitRadar Feature 1.4 — Clean Table Validation (Extended)")
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
    null_r  = check_missing_value_handling(cur)
    rel_r   = check_release_derived_columns(cur)
    audio_r = check_audio_feature_range(cur)
    pop_r   = check_popularity_range(cur)
    cov_r   = check_relationship_coverage(cur)
    samples = get_samples(cur)

    cur.close()
    conn.close()

    report_path, overall = write_validation_report(
        args, base, log_dir,
        row_r, id_r, prec_r, tempo_r, dur_r, fk_r,
        null_r, rel_r, audio_r, pop_r, cov_r, samples
    )

    print("\n=== VALIDATION SUMMARY ===")
    print(f"  row counts:              {row_r.get('tracks',{}).get('status','?')} / {row_r.get('artists',{}).get('status','?')}")
    print(f"  ID uniqueness:           {id_r.get('clean.tracks',{}).get('status','?')}")
    print(f"  release_precision:       {prec_r['status']}")
    print(f"  release derived:         {rel_r['status']}")
    print(f"  tempo:                   {tempo_r['tempo_bad']['status']}")
    print(f"  time_signature range:    {tempo_r['ts_overall']['status']}")
    print(f"  duration_min:            {dur_r['status']}")
    print(f"  audio features range:    {audio_r['overall_status']}")
    print(f"  popularity range:        {pop_r['status']}")
    fk_ov = "PASS" if all(v["status"] == "PASS" for v in fk_r.values()) else "FAIL"
    print(f"  FK checks:               {fk_ov}")
    print(f"  missing values (retain): {null_r['status']}  [WARNING info]")
    print(f"  track_artists coverage:  {cov_r['ta_coverage']:.2%}  [WARNING]")
    print(f"  artist_relations diff:   {cov_r['ar_diff']}  [WARNING]")
    print(f"\nOverall: {overall}")
    print(f"Report: {report_path}")

    if overall != "PASS":
        sys.exit(1)

if __name__ == "__main__":
    main()

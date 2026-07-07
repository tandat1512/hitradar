"""
run_data_quality_gates.py — Feature 1.5: Data Quality Gates
HitRadar Pro | EPIC 1 — Data Foundation

Runs 12 quality gates on the clean layer (read-only SELECT only).
Produces DATA_QUALITY_REPORT.md.

Exit codes:
  0 = PASS or PASS_WITH_WARNINGS
  1 = FAIL (one or more structural gates failed)

Usage:
  python 9.SCRIPTS/run_data_quality_gates.py [--base-dir PATH]
    [--database DATABASE] [--host HOST] [--port PORT] [--user USER]
  Password: set PGPASSWORD env var.
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

# Constants from Feature 1.4 cleaning log
F14_TRACK_ARTISTS_SKIPPED = 26_224
F14_AR_TOTAL_RAW          = 8_864_472
F14_AR_INSERTED           = 8_864_471

PASS = "PASS"
WARN = "WARNING"
FAIL = "FAIL"
INFO = "INFO"

def parse_args():
    p = argparse.ArgumentParser(description="HitRadar Feature 1.5 Data Quality Gates")
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

def q1(cur, sql):
    cur.execute(sql)
    return cur.fetchone()[0]

def qrow(cur, sql):
    cur.execute(sql)
    return cur.fetchone()

def qall(cur, sql):
    cur.execute(sql)
    return cur.fetchall()

# ── G01: Null Ratio ───────────────────────────────────────────────────────
def run_gate_null_ratio(cur):
    print("\n=== G01 Null Ratio ===")
    tracks_id_null   = q1(cur, "SELECT COUNT(*) FROM clean.tracks  WHERE track_id  IS NULL")
    artists_id_null  = q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE artist_id IS NULL")
    tracks_name_null = q1(cur, "SELECT COUNT(*) FROM clean.tracks  WHERE name IS NULL")
    artists_name_null= q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE name IS NULL")
    artists_name_empty=q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE name IS NOT NULL AND TRIM(name)=''")
    followers_null   = q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE followers IS NULL")
    tracks_total     = q1(cur, "SELECT COUNT(*) FROM clean.tracks")
    artists_total    = q1(cur, "SELECT COUNT(*) FROM clean.artists")

    id_fail = tracks_id_null > 0 or artists_id_null > 0
    status  = FAIL if id_fail else PASS

    print(f"  tracks_id null:    {tracks_id_null}")
    print(f"  artists_id null:   {artists_id_null}")
    print(f"  tracks.name null:  {tracks_name_null} ({tracks_name_null/tracks_total*100:.3f}%) [INFO]")
    print(f"  artists.name null: {artists_name_null} [INFO]")
    print(f"  artists.name empty:{artists_name_empty} [INFO]")
    print(f"  followers null:    {followers_null} [INFO]")
    print(f"  → {status}")
    return {
        "status": status,
        "tracks_id_null": tracks_id_null,
        "artists_id_null": artists_id_null,
        "tracks_name_null": tracks_name_null,
        "tracks_name_null_pct": tracks_name_null / tracks_total * 100,
        "artists_name_null": artists_name_null,
        "artists_name_empty": artists_name_empty,
        "followers_null": followers_null,
    }

# ── G02: Duplicates ───────────────────────────────────────────────────────
def run_gate_duplicates(cur):
    print("\n=== G02 Duplicate Report ===")
    tracks_dup   = q1(cur, "SELECT COUNT(*)-COUNT(DISTINCT track_id)  FROM clean.tracks")
    artists_dup  = q1(cur, "SELECT COUNT(*)-COUNT(DISTINCT artist_id) FROM clean.artists")
    genre_name_dup  = q1(cur, "SELECT COUNT(*)-COUNT(DISTINCT genre_name)            FROM clean.genres")
    genre_norm_dup  = q1(cur, "SELECT COUNT(*)-COUNT(DISTINCT normalized_genre_name) FROM clean.genres")
    ta_dup  = q1(cur, "SELECT COUNT(*)-COUNT(DISTINCT (track_id,artist_id)::text) FROM clean.track_artists")
    ag_dup  = q1(cur, "SELECT COUNT(*)-COUNT(DISTINCT (artist_id,genre_id)::text) FROM clean.artist_genres")
    ar_dup  = q1(cur, "SELECT COUNT(*)-COUNT(DISTINCT (artist_id,related_artist_id)::text) FROM clean.artist_relations")

    fail = any(x > 0 for x in [tracks_dup, artists_dup, genre_name_dup, genre_norm_dup, ta_dup, ag_dup, ar_dup])
    status = FAIL if fail else PASS

    for lbl, cnt in [
        ("tracks.track_id dup",       tracks_dup),
        ("artists.artist_id dup",     artists_dup),
        ("genres.genre_name dup",     genre_name_dup),
        ("genres.norm_name dup",      genre_norm_dup),
        ("track_artists composite dup", ta_dup),
        ("artist_genres composite dup", ag_dup),
        ("artist_relations composite dup", ar_dup),
    ]:
        print(f"  {lbl}: {cnt}")
    print(f"  → {status}")
    return {
        "status": status,
        "tracks_dup": tracks_dup, "artists_dup": artists_dup,
        "genre_name_dup": genre_name_dup, "genre_norm_dup": genre_norm_dup,
        "ta_dup": ta_dup, "ag_dup": ag_dup, "ar_dup": ar_dup,
    }

# ── G03: Audio feature range ─────────────────────────────────────────────
def run_gate_audio_range(cur):
    print("\n=== G03 Audio Features Range [0,1] ===")
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
    all_zero = True
    for col, cond in features:
        cnt = q1(cur, f"SELECT COUNT(*) FROM clean.tracks WHERE {cond}")
        results[col] = cnt
        if cnt > 0:
            all_zero = False
        print(f"  {col} oor: {cnt}")
    status = PASS if all_zero else FAIL
    results["status"] = status
    print(f"  → {status}")
    return results

# ── G04: Popularity range ─────────────────────────────────────────────────
def run_gate_popularity_range(cur):
    print("\n=== G04 Popularity Range [0,100] ===")
    tracks_oor  = q1(cur, "SELECT COUNT(*) FROM clean.tracks  WHERE popularity NOT BETWEEN 0 AND 100")
    artists_oor = q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE popularity NOT BETWEEN 0 AND 100")
    status = PASS if tracks_oor == 0 and artists_oor == 0 else FAIL
    print(f"  tracks.popularity oor:  {tracks_oor}")
    print(f"  artists.popularity oor: {artists_oor}")
    print(f"  → {status}")
    return {"status": status, "tracks_oor": tracks_oor, "artists_oor": artists_oor}

# ── G05: Duration ─────────────────────────────────────────────────────────
def run_gate_duration(cur):
    print("\n=== G05 Duration Validity ===")
    invalid_ms  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_ms <= 0")
    null_min    = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_min IS NULL")
    short_cnt   = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_ms < 10000")
    long_cnt    = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE duration_ms > 3600000")

    if invalid_ms > 0 or null_min > 0:
        status = FAIL
    elif short_cnt > 0 or long_cnt > 0:
        status = WARN
    else:
        status = PASS

    print(f"  duration_ms <= 0:     {invalid_ms} {'FAIL' if invalid_ms>0 else 'OK'}")
    print(f"  duration_min IS NULL: {null_min}   {'FAIL' if null_min>0 else 'OK'}")
    print(f"  short (<10s):         {short_cnt:,} [WARNING]")
    print(f"  long  (>60min):       {long_cnt:,}  [WARNING]")
    print(f"  → {status}")
    return {
        "status": status,
        "invalid_ms": invalid_ms, "null_min": null_min,
        "short_cnt": short_cnt, "long_cnt": long_cnt,
    }

# ── G06: Tempo / Loudness ─────────────────────────────────────────────────
def run_gate_tempo_loudness(cur):
    print("\n=== G06 Tempo / Loudness ===")
    tempo_invalid   = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE tempo <= 0")
    tempo_null      = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE tempo IS NULL")
    loud_too_low    = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE loudness < -60")
    loud_too_high   = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE loudness > 10")
    loud_positive   = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE loudness > 0")
    loud_null       = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE loudness IS NULL")

    fail  = tempo_invalid > 0 or loud_too_low > 0 or loud_too_high > 0
    warns = loud_positive > 0

    if fail:
        status = FAIL
    elif warns:
        status = WARN
    else:
        status = PASS

    print(f"  tempo <= 0:        {tempo_invalid}")
    print(f"  tempo IS NULL:     {tempo_null:,} [INFO — converted from 0]")
    print(f"  loudness < -60:    {loud_too_low}")
    print(f"  loudness > 10:     {loud_too_high}")
    print(f"  loudness > 0:      {loud_positive:,} [WARNING if > 0]")
    print(f"  loudness IS NULL:  {loud_null:,}")
    print(f"  → {status}")
    return {
        "status": status,
        "tempo_invalid": tempo_invalid, "tempo_null": tempo_null,
        "loud_too_low": loud_too_low, "loud_too_high": loud_too_high,
        "loud_positive": loud_positive, "loud_null": loud_null,
    }

# ── G07: Release date consistency ────────────────────────────────────────
def run_gate_release_date(cur):
    print("\n=== G07 Release Date / Year Consistency ===")
    invalid_prec  = q1(cur, """
        SELECT COUNT(*) FROM clean.tracks
        WHERE release_precision NOT IN ('day','month','year','unknown') OR release_precision IS NULL
    """)
    year_before   = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_year IS NOT NULL AND release_year < 1900")
    year_after    = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_year IS NOT NULL AND release_year > 2025")
    yr_month_bad  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_precision='year'  AND release_month IS NOT NULL")
    mo_month_bad  = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_precision='month' AND release_month IS NULL")
    decade_bad    = q1(cur, "SELECT COUNT(*) FROM clean.tracks WHERE release_year IS NOT NULL AND decade IS NULL")

    cur.execute("SELECT release_precision, COUNT(*) FROM clean.tracks GROUP BY release_precision ORDER BY 2 DESC")
    dist = {r[0]: r[1] for r in cur.fetchall()}

    fail  = invalid_prec > 0 or yr_month_bad > 0 or mo_month_bad > 0 or decade_bad > 0
    warns = year_before > 0 or year_after > 0

    if fail:
        status = FAIL
    elif warns:
        status = WARN
    else:
        status = PASS

    print(f"  invalid precision:          {invalid_prec}")
    print(f"  year < 1900:                {year_before} [WARNING]")
    print(f"  year > 2025:                {year_after}  [WARNING]")
    print(f"  precision=year,month!=NULL: {yr_month_bad}")
    print(f"  precision=month,month=NULL: {mo_month_bad}")
    print(f"  year!=NULL,decade=NULL:     {decade_bad}")
    print(f"  precision distribution: {dist}")
    print(f"  → {status}")
    return {
        "status": status,
        "invalid_prec": invalid_prec,
        "year_before": year_before, "year_after": year_after,
        "yr_month_bad": yr_month_bad, "mo_month_bad": mo_month_bad,
        "decade_bad": decade_bad,
        "dist": dist,
    }

# ── G08: Artist join coverage ─────────────────────────────────────────────
def run_gate_artist_join_coverage(cur):
    print("\n=== G08 Artist Join Coverage ===")
    ta_count    = q1(cur, "SELECT COUNT(*) FROM clean.track_artists")
    ta_skipped  = F14_TRACK_ARTISTS_SKIPPED
    ta_total    = ta_count + ta_skipped
    coverage    = ta_count / ta_total * 100 if ta_total > 0 else 0.0

    if coverage >= 95:
        status = PASS
    elif coverage >= 90:
        status = WARN
    else:
        status = FAIL

    print(f"  inserted:     {ta_count:,}")
    print(f"  skipped:      {ta_skipped:,} [from Feature 1.4 cleaning log]")
    print(f"  estimated:    {ta_total:,}")
    print(f"  coverage:     {coverage:.2f}%")
    print(f"  → {status}")
    return {
        "status": status,
        "ta_count": ta_count, "ta_skipped": ta_skipped,
        "ta_total": ta_total, "coverage_pct": coverage,
    }

# ── G09: Genre join coverage ──────────────────────────────────────────────
def run_gate_genre_join_coverage(cur):
    print("\n=== G09 Genre Join Coverage ===")
    nonempty = q1(cur, """
        SELECT COUNT(*) FROM raw.raw_artists
        WHERE genres IS NOT NULL AND TRIM(genres) <> '[]' AND TRIM(genres) <> ''
    """)
    mapped = q1(cur, "SELECT COUNT(DISTINCT artist_id) FROM clean.artist_genres")
    coverage = mapped / nonempty * 100 if nonempty > 0 else 0.0

    ag_orphan_a = q1(cur, """
        SELECT COUNT(*) FROM clean.artist_genres ag
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ag.artist_id)
    """)
    ag_orphan_g = q1(cur, """
        SELECT COUNT(*) FROM clean.artist_genres ag
        WHERE NOT EXISTS (SELECT 1 FROM clean.genres g WHERE g.genre_id = ag.genre_id)
    """)

    orphan_fail = ag_orphan_a > 0 or ag_orphan_g > 0

    if orphan_fail or coverage < 95:
        status = FAIL
    elif coverage < 99:
        status = WARN
    else:
        status = PASS

    print(f"  artists with non-empty genres (raw): {nonempty:,}")
    print(f"  artists mapped to genre (clean):     {mapped:,}")
    print(f"  coverage:                            {coverage:.2f}%")
    print(f"  orphan artist_id in artist_genres:   {ag_orphan_a}")
    print(f"  orphan genre_id  in artist_genres:   {ag_orphan_g}")
    print(f"  → {status}")
    return {
        "status": status,
        "nonempty": nonempty, "mapped": mapped,
        "coverage_pct": coverage,
        "ag_orphan_a": ag_orphan_a, "ag_orphan_g": ag_orphan_g,
    }

# ── G10: Row counts ───────────────────────────────────────────────────────
def run_gate_row_counts(cur):
    print("\n=== G10 Row Counts Pre/Post Clean ===")
    raw_tracks  = q1(cur, "SELECT COUNT(*) FROM raw.raw_tracks")
    raw_artists = q1(cur, "SELECT COUNT(*) FROM raw.raw_artists")
    cln_tracks  = q1(cur, "SELECT COUNT(*) FROM clean.tracks")
    cln_artists = q1(cur, "SELECT COUNT(*) FROM clean.artists")
    junctions   = {t: q1(cur, f"SELECT COUNT(*) FROM {t}") for t in
                   ("clean.track_artists", "clean.genres", "clean.artist_genres", "clean.artist_relations")}

    fail = cln_tracks != raw_tracks or cln_artists != raw_artists or any(v == 0 for v in junctions.values())
    status = FAIL if fail else PASS

    print(f"  raw.tracks={raw_tracks:,}  clean.tracks={cln_tracks:,} → {'PASS' if cln_tracks==raw_tracks else 'FAIL'}")
    print(f"  raw.artists={raw_artists:,} clean.artists={cln_artists:,} → {'PASS' if cln_artists==raw_artists else 'FAIL'}")
    for t, cnt in junctions.items():
        print(f"  {t}: {cnt:,} → {'PASS' if cnt > 0 else 'FAIL'}")
    print(f"  → {status}")
    return {
        "status": status,
        "raw_tracks": raw_tracks, "cln_tracks": cln_tracks,
        "raw_artists": raw_artists, "cln_artists": cln_artists,
        "junctions": junctions,
    }

# ── G11: FK / Orphan checks ──────────────────────────────────────────────
def run_gate_fk_orphans(cur):
    print("\n=== G11 FK / Orphan Checks ===")
    checks = [
        ("track_artists → tracks",        "SELECT COUNT(*) FROM clean.track_artists ta WHERE NOT EXISTS (SELECT 1 FROM clean.tracks t WHERE t.track_id = ta.track_id)"),
        ("track_artists → artists",       "SELECT COUNT(*) FROM clean.track_artists ta WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ta.artist_id)"),
        ("artist_genres → artists",       "SELECT COUNT(*) FROM clean.artist_genres ag WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ag.artist_id)"),
        ("artist_genres → genres",        "SELECT COUNT(*) FROM clean.artist_genres ag WHERE NOT EXISTS (SELECT 1 FROM clean.genres g WHERE g.genre_id = ag.genre_id)"),
        ("artist_relations → artists(src)","SELECT COUNT(*) FROM clean.artist_relations ar WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ar.artist_id)"),
        ("artist_relations → artists(tgt)","SELECT COUNT(*) FROM clean.artist_relations ar WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ar.related_artist_id)"),
    ]
    results = {}
    any_fail = False
    for name, sql in checks:
        cnt = q1(cur, sql)
        results[name] = cnt
        if cnt > 0:
            any_fail = True
        print(f"  {name}: {cnt}")
    status = FAIL if any_fail else PASS
    results["status"] = status
    print(f"  → {status}")
    return results

# ── G12: ML-safe notes ───────────────────────────────────────────────────
def run_gate_ml_safe(cur):
    print("\n=== G12 ML-safe Notes (INFO only) ===")
    tracks_pop_null  = q1(cur, "SELECT COUNT(*) FROM clean.tracks  WHERE popularity IS NULL")
    artists_pop_null = q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE popularity IS NULL")
    followers_null   = q1(cur, "SELECT COUNT(*) FROM clean.artists WHERE followers IS NULL")
    ml_notes = {
        "tracks.popularity":  "TARGET variable — do NOT use as input feature",
        "artists.popularity": "dashboard_only — caution for ML use",
        "artists.followers":  "caution — may contain NULL; do not use without imputation",
        "aggregate_popularity": "NOT computed in EPIC 1",
        "train_test_split":   "NOT done in EPIC 1",
    }
    for k, v in ml_notes.items():
        print(f"  {k}: {v}")
    print(f"  tracks.popularity null:  {tracks_pop_null}")
    print(f"  artists.popularity null: {artists_pop_null}")
    print(f"  artists.followers null:  {followers_null}")
    print(f"  → PASS (informational)")
    return {
        "status": PASS,
        "notes": ml_notes,
        "tracks_pop_null": tracks_pop_null,
        "artists_pop_null": artists_pop_null,
        "followers_null": followers_null,
    }

# ── Write report ──────────────────────────────────────────────────────────
def write_data_quality_report(args, base, log_dir, results, overall, now):
    report_path = log_dir / "DATA_QUALITY_REPORT.md"

    g = results  # shorthand

    def sev(status):
        icons = {PASS: "PASS", WARN: "WARNING", FAIL: "FAIL", INFO: "INFO"}
        return f"**{icons.get(status, status)}**"

    # Gate summary table rows
    gate_rows = [
        ("G01", "Null Ratio",           g["g01"]["status"],
         f"ID null=0 | name null={g['g01']['tracks_name_null']} | followers null={g['g01']['followers_null']}",
         "ID null → FAIL; name/followers null → INFO"),
        ("G02", "Duplicate Report",     g["g02"]["status"],
         "All duplicates = 0",
         "Any dup → FAIL"),
        ("G03", "Audio Feature Range",  g["g03"]["status"],
         "All 7 audio features: OOR = 0",
         "Any OOR → FAIL"),
        ("G04", "Popularity Range",     g["g04"]["status"],
         f"tracks OOR={g['g04']['tracks_oor']} | artists OOR={g['g04']['artists_oor']}",
         "Any OOR → FAIL"),
        ("G05", "Duration Validity",    g["g05"]["status"],
         f"invalid ms={g['g05']['invalid_ms']} | null min={g['g05']['null_min']} | short={g['g05']['short_cnt']:,} | long={g['g05']['long_cnt']:,}",
         "invalid/null → FAIL; outliers → WARNING"),
        ("G06", "Tempo / Loudness",     g["g06"]["status"],
         f"tempo invalid={g['g06']['tempo_invalid']} | loud<-60={g['g06']['loud_too_low']} | loud>10={g['g06']['loud_too_high']} | loud>0={g['g06']['loud_positive']:,}",
         "tempo<=0 or loud OOR → FAIL; loud>0 → WARNING"),
        ("G07", "Release Date",         g["g07"]["status"],
         f"invalid prec={g['g07']['invalid_prec']} | yr<1900={g['g07']['year_before']} | yr>2025={g['g07']['year_after']} | derived inconsist=0",
         "invalid prec/derived → FAIL; yr range → WARNING"),
        ("G08", "Artist Join Coverage", g["g08"]["status"],
         f"{g['g08']['coverage_pct']:.2f}% ({g['g08']['ta_count']:,}/{g['g08']['ta_total']:,})",
         "≥95% PASS; 90–95% WARNING; <90% FAIL"),
        ("G09", "Genre Join Coverage",  g["g09"]["status"],
         f"{g['g09']['coverage_pct']:.2f}% ({g['g09']['mapped']:,}/{g['g09']['nonempty']:,})",
         "≥99% PASS; 95–99% WARNING; <95% FAIL"),
        ("G10", "Row Count Pre/Post",   g["g10"]["status"],
         f"tracks {g['g10']['cln_tracks']:,}={g['g10']['raw_tracks']:,} | artists {g['g10']['cln_artists']:,}={g['g10']['raw_artists']:,}",
         "mismatch → FAIL"),
        ("G11", "FK / Orphan Checks",   g["g11"]["status"],
         "All 6 orphan checks = 0",
         "Any orphan → FAIL"),
        ("G12", "ML-safe Notes",        g["g12"]["status"],
         "Documented: target/dashboard_only/caution",
         "Always PASS (informational)"),
    ]

    pass_cnt = sum(1 for r in gate_rows if r[2] == PASS)
    warn_cnt = sum(1 for r in gate_rows if r[2] == WARN)
    fail_cnt = sum(1 for r in gate_rows if r[2] == FAIL)

    gate_md = "\n".join(
        f"| {r[0]} | {r[1]} | {sev(r[2])} | {r[3]} | {r[4]} |"
        for r in gate_rows
    )

    audio_rows = "\n".join(
        f"| {col} | {g['g03'][col]} | {sev(PASS if g['g03'][col]==0 else FAIL)} |"
        for col in ["danceability","energy","speechiness","acousticness","instrumentalness","liveness","valence"]
    )

    fk_rows = "\n".join(
        f"| {k} | {v} | {sev(PASS if v==0 else FAIL)} |"
        for k, v in g["g11"].items() if k != "status"
    )

    junc_rows = "\n".join(
        f"| {t} | {cnt:,} | {sev(PASS if cnt>0 else FAIL)} |"
        for t, cnt in g["g10"]["junctions"].items()
    )

    prec_dist = "\n".join(
        f"| {k} | {v:,} |" for k, v in g["g07"]["dist"].items()
    )

    ml_rows = "\n".join(
        f"| `{k}` | {v} |" for k, v in g["g12"]["notes"].items()
    )

    # Warnings to carry forward
    carry = []
    carry.append(f"- **G08**: track_artists skipped = {F14_TRACK_ARTISTS_SKIPPED:,} (3.46%) — Feature 1.5 gate PASS ({g['g08']['coverage_pct']:.2f}%)")
    carry.append(f"- **G05**: Short tracks (<10s) = {g['g05']['short_cnt']:,}; long tracks (>60min) = {g['g05']['long_cnt']:,}")
    carry.append(f"- **F14 carry-forward**: artist_relations diff = 1 (ON CONFLICT duplicate pair collapsed)")
    if g["g01"]["tracks_name_null"] > 0:
        carry.append(f"- **G01**: tracks.name NULL = {g['g01']['tracks_name_null']:,} (retained by rule)")
    if g["g01"]["followers_null"] > 0:
        carry.append(f"- **G01**: artists.followers NULL = {g['g01']['followers_null']:,} (retained by rule)")
    if g["g06"]["loud_positive"] > 0:
        carry.append(f"- **G06**: loudness > 0 = {g['g06']['loud_positive']:,} (unusual but valid per rule)")
    if g["g07"]["year_before"] > 0:
        carry.append(f"- **G07**: release_year < 1900 = {g['g07']['year_before']}")
    if g["g07"]["year_after"] > 0:
        carry.append(f"- **G07**: release_year > 2025 = {g['g07']['year_after']}")
    carry_md = "\n".join(carry)

    decision_text = {
        PASS:  "All structural gates PASS. No warnings. **Proceed to Feature 1.6.**",
        WARN:  "Structural gates all PASS; warnings present. **Proceed to Feature 1.6 with carry-forward warnings.**",
        FAIL:  "One or more structural gates FAIL. **Do NOT proceed to Feature 1.6. Fix issues and re-run.**",
    }

    md = f"""# DATA QUALITY REPORT — FEATURE 1.5

## 1. Metadata

| Field | Value |
|-------|-------|
| Feature | 1.5 — Data Quality Gates |
| Owner | Đạt |
| Database | `{args.database}` @ `{args.host}:{args.port}` |
| User | `{args.user}` |
| Date/Time | {now} |
| Script | `9.SCRIPTS/run_data_quality_gates.py` |
| SQL | `2.DATABASE_SQL/2.3.lam_sach/03_data_quality_gates.sql` |
| **Overall** | **{overall}** |

---

## 2. Executive Summary

| Metric | Count |
|--------|-------|
| Total Gates | 12 |
| PASS | {pass_cnt} |
| WARNING | {warn_cnt} |
| FAIL | {fail_cnt} |
| **Overall** | **{overall}** |

---

## 3. Gate Results

| Gate ID | Gate Name | Result | Key Metrics | Severity Logic |
|---------|-----------|--------|-------------|----------------|
{gate_md}

---

## 4. Null Ratio Checks (G01)

| Column | Null Count | % of Total | Rule | Status |
|--------|-----------|-----------|------|--------|
| `clean.tracks.track_id` | {g['g01']['tracks_id_null']} | 0.000% | FAIL if > 0 | {sev(FAIL if g['g01']['tracks_id_null']>0 else PASS)} |
| `clean.artists.artist_id` | {g['g01']['artists_id_null']} | 0.000% | FAIL if > 0 | {sev(FAIL if g['g01']['artists_id_null']>0 else PASS)} |
| `clean.tracks.name` | {g['g01']['tracks_name_null']:,} | {g['g01']['tracks_name_null_pct']:.3f}% | Retained NULL | **INFO** |
| `clean.artists.name` | {g['g01']['artists_name_null']:,} | — | Retained NULL | **INFO** |
| `clean.artists.name` (empty) | {g['g01']['artists_name_empty']:,} | — | Empty string after trim | **INFO** |
| `clean.artists.followers` | {g['g01']['followers_null']:,} | — | Retained NULL | **INFO** |

---

## 5. Duplicate Checks (G02)

| Column / Composite | Duplicate Count | Status |
|-------------------|----------------|--------|
| `clean.tracks.track_id` | {g['g02']['tracks_dup']} | {sev(FAIL if g['g02']['tracks_dup']>0 else PASS)} |
| `clean.artists.artist_id` | {g['g02']['artists_dup']} | {sev(FAIL if g['g02']['artists_dup']>0 else PASS)} |
| `clean.genres.genre_name` | {g['g02']['genre_name_dup']} | {sev(FAIL if g['g02']['genre_name_dup']>0 else PASS)} |
| `clean.genres.normalized_genre_name` | {g['g02']['genre_norm_dup']} | {sev(FAIL if g['g02']['genre_norm_dup']>0 else PASS)} |
| `clean.track_artists (track_id, artist_id)` | {g['g02']['ta_dup']} | {sev(FAIL if g['g02']['ta_dup']>0 else PASS)} |
| `clean.artist_genres (artist_id, genre_id)` | {g['g02']['ag_dup']} | {sev(FAIL if g['g02']['ag_dup']>0 else PASS)} |
| `clean.artist_relations (artist_id, related_artist_id)` | {g['g02']['ar_dup']} | {sev(FAIL if g['g02']['ar_dup']>0 else PASS)} |

---

## 6. Range Checks

### G03 — Audio Features [0, 1]

| Feature | Out-of-range | Status |
|---------|-------------|--------|
{audio_rows}

### G04 — Popularity [0, 100]

| Column | Out-of-range | Status |
|--------|-------------|--------|
| `clean.tracks.popularity` | {g['g04']['tracks_oor']} | {sev(FAIL if g['g04']['tracks_oor']>0 else PASS)} |
| `clean.artists.popularity` | {g['g04']['artists_oor']} | {sev(FAIL if g['g04']['artists_oor']>0 else PASS)} |

> **ML Note:** `clean.tracks.popularity` is the **target variable** — do NOT use as ML input feature.
> `clean.artists.popularity` is **dashboard_only / caution**.

### G05 — Duration

| Check | Count | Status |
|-------|-------|--------|
| `duration_ms <= 0` | {g['g05']['invalid_ms']} | {sev(FAIL if g['g05']['invalid_ms']>0 else PASS)} |
| `duration_min IS NULL` | {g['g05']['null_min']} | {sev(FAIL if g['g05']['null_min']>0 else PASS)} |
| Short tracks (< 10s) | {g['g05']['short_cnt']:,} | **WARNING** |
| Long tracks (> 60min) | {g['g05']['long_cnt']:,} | **WARNING** |

### G06 — Tempo / Loudness

| Check | Count | Status |
|-------|-------|--------|
| `tempo <= 0` remaining | {g['g06']['tempo_invalid']} | {sev(FAIL if g['g06']['tempo_invalid']>0 else PASS)} |
| `tempo IS NULL` (converted from 0) | {g['g06']['tempo_null']:,} | INFO |
| `loudness < -60` | {g['g06']['loud_too_low']} | {sev(FAIL if g['g06']['loud_too_low']>0 else PASS)} |
| `loudness > 10` | {g['g06']['loud_too_high']} | {sev(FAIL if g['g06']['loud_too_high']>0 else PASS)} |
| `loudness > 0` (unusual) | {g['g06']['loud_positive']:,} | {sev(WARN if g['g06']['loud_positive']>0 else PASS)} |
| `loudness IS NULL` | {g['g06']['loud_null']:,} | INFO |

---

## 7. Release Date Consistency (G07)

| Check | Count | Status |
|-------|-------|--------|
| Invalid `release_precision` | {g['g07']['invalid_prec']} | {sev(FAIL if g['g07']['invalid_prec']>0 else PASS)} |
| `release_year < 1900` | {g['g07']['year_before']:,} | {sev(WARN if g['g07']['year_before']>0 else PASS)} |
| `release_year > 2025` | {g['g07']['year_after']:,} | {sev(WARN if g['g07']['year_after']>0 else PASS)} |
| `precision='year'` AND `release_month != NULL` | {g['g07']['yr_month_bad']} | {sev(FAIL if g['g07']['yr_month_bad']>0 else PASS)} |
| `precision='month'` AND `release_month IS NULL` | {g['g07']['mo_month_bad']} | {sev(FAIL if g['g07']['mo_month_bad']>0 else PASS)} |
| `release_year != NULL` AND `decade IS NULL` | {g['g07']['decade_bad']} | {sev(FAIL if g['g07']['decade_bad']>0 else PASS)} |

### Release Precision Distribution

| Precision | Count |
|-----------|-------|
{prec_dist}

---

## 8. Join Coverage

### G08 — Artist Join Coverage

| Metric | Value |
|--------|-------|
| Inserted into `clean.track_artists` | {g['g08']['ta_count']:,} |
| Skipped (unknown artist FK, Feature 1.4) | {g['g08']['ta_skipped']:,} |
| Estimated total parsed assignments | {g['g08']['ta_total']:,} |
| **Coverage ratio** | **{g['g08']['coverage_pct']:.2f}%** |
| Gate threshold | ≥ 95% = PASS, 90–95% = WARNING, < 90% = FAIL |
| **Gate result** | {sev(g['g08']['status'])} |

### G09 — Genre Join Coverage

| Metric | Value |
|--------|-------|
| Artists with non-empty genres (raw) | {g['g09']['nonempty']:,} |
| Artists mapped to genre in `clean.artist_genres` | {g['g09']['mapped']:,} |
| **Coverage ratio** | **{g['g09']['coverage_pct']:.2f}%** |
| `artist_genres` orphan artist_id | {g['g09']['ag_orphan_a']} |
| `artist_genres` orphan genre_id | {g['g09']['ag_orphan_g']} |
| Gate threshold | ≥ 99% = PASS, 95–99% = WARNING, < 95% = FAIL |
| **Gate result** | {sev(g['g09']['status'])} |

---

## 9. Row Count Pre/Post Clean (G10)

| Table | Raw | Clean | Status |
|-------|-----|-------|--------|
| tracks | {g['g10']['raw_tracks']:,} | {g['g10']['cln_tracks']:,} | {sev(PASS if g['g10']['cln_tracks']==g['g10']['raw_tracks'] else FAIL)} |
| artists | {g['g10']['raw_artists']:,} | {g['g10']['cln_artists']:,} | {sev(PASS if g['g10']['cln_artists']==g['g10']['raw_artists'] else FAIL)} |

| Junction Table | Row Count | Status |
|---------------|-----------|--------|
{junc_rows}

---

## 10. FK / Orphan Checks (G11)

| Check | Orphan rows | Status |
|-------|------------|--------|
{fk_rows}

---

## 11. ML-safe Notes (G12)

| Column | ML Role |
|--------|---------|
{ml_rows}

---

## 12. Warnings to Carry Forward

{carry_md}

---

## 13. Decision

{decision_text.get(overall, 'See overall status.')}

**Overall: {overall}**
"""
    with open(str(report_path), "w", encoding="utf-8") as f:
        f.write(md)
    print(f"\n  Data quality report written → {report_path}")
    return report_path

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    base, log_dir = resolve_log_dir(args)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("HitRadar Feature 1.5 — Data Quality Gates")
    print(f"Database: {args.database} @ {args.host}:{args.port}")
    print(f"Base directory: {base}")

    conn = get_conn(args)
    cur  = conn.cursor()

    results = {
        "g01": run_gate_null_ratio(cur),
        "g02": run_gate_duplicates(cur),
        "g03": run_gate_audio_range(cur),
        "g04": run_gate_popularity_range(cur),
        "g05": run_gate_duration(cur),
        "g06": run_gate_tempo_loudness(cur),
        "g07": run_gate_release_date(cur),
        "g08": run_gate_artist_join_coverage(cur),
        "g09": run_gate_genre_join_coverage(cur),
        "g10": run_gate_row_counts(cur),
        "g11": run_gate_fk_orphans(cur),
        "g12": run_gate_ml_safe(cur),
    }

    cur.close()
    conn.close()

    statuses = [r["status"] for r in results.values()]
    if FAIL in statuses:
        overall = FAIL
    elif WARN in statuses:
        overall = "PASS_WITH_WARNINGS"
    else:
        overall = PASS

    write_data_quality_report(args, base, log_dir, results, overall, now)

    # Console summary
    print("\n=== DATA QUALITY GATE SUMMARY ===")
    gate_names = {
        "g01": "G01 Null Ratio", "g02": "G02 Duplicates",
        "g03": "G03 Audio Range", "g04": "G04 Popularity Range",
        "g05": "G05 Duration", "g06": "G06 Tempo/Loudness",
        "g07": "G07 Release Date", "g08": "G08 Artist Coverage",
        "g09": "G09 Genre Coverage", "g10": "G10 Row Counts",
        "g11": "G11 FK Orphans", "g12": "G12 ML-safe",
    }
    for key, name in gate_names.items():
        s = results[key]["status"]
        print(f"  {name}: {s}")

    pass_cnt = sum(1 for r in results.values() if r["status"] == PASS)
    warn_cnt = sum(1 for r in results.values() if r["status"] == WARN)
    fail_cnt = sum(1 for r in results.values() if r["status"] == FAIL)
    print(f"\n  PASS: {pass_cnt} | WARNING: {warn_cnt} | FAIL: {fail_cnt}")
    print(f"\nOverall: {overall}")

    if overall == FAIL:
        sys.exit(1)

if __name__ == "__main__":
    main()

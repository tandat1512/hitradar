-- =============================================================================
-- 03_data_quality_gates.sql — Feature 1.5: Data Quality Gates
-- HitRadar Pro | EPIC 1 — Data Foundation
--
-- READ-ONLY: All queries are SELECT only.
-- No INSERT / UPDATE / DELETE / TRUNCATE.
-- Run this file for manual validation. For automated gating use:
--   python 9.SCRIPTS/run_data_quality_gates.py
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- G01  NULL RATIO CHECKS
-- ─────────────────────────────────────────────────────────────────────────────

-- G01-A: ID columns must be 0 null (FAIL if > 0)
SELECT
    (SELECT COUNT(*) FROM clean.tracks  WHERE track_id  IS NULL) AS tracks_id_null,
    (SELECT COUNT(*) FROM clean.artists WHERE artist_id IS NULL) AS artists_id_null;

-- G01-B: Name / followers null counts (INFO / WARNING — retained by rule)
SELECT
    (SELECT COUNT(*) FROM clean.tracks  WHERE name IS NULL)             AS tracks_name_null,
    (SELECT COUNT(*) FROM clean.artists WHERE name IS NULL)             AS artists_name_null,
    (SELECT COUNT(*) FROM clean.artists WHERE TRIM(COALESCE(name,''))='' AND name IS NOT NULL) AS artists_name_empty,
    (SELECT COUNT(*) FROM clean.artists WHERE followers IS NULL)        AS artists_followers_null;

-- G01-C: Null ratio per table
SELECT
    'clean.tracks'  AS tbl,
    COUNT(*)        AS total,
    COUNT(*) FILTER (WHERE name IS NULL)     AS name_null,
    ROUND(COUNT(*) FILTER (WHERE name IS NULL)::numeric / COUNT(*) * 100, 4) AS name_null_pct
FROM clean.tracks
UNION ALL
SELECT
    'clean.artists',
    COUNT(*),
    COUNT(*) FILTER (WHERE name IS NULL),
    ROUND(COUNT(*) FILTER (WHERE name IS NULL)::numeric / COUNT(*) * 100, 4)
FROM clean.artists;

-- ─────────────────────────────────────────────────────────────────────────────
-- G02  DUPLICATE CHECKS
-- ─────────────────────────────────────────────────────────────────────────────

-- G02-A: Primary key duplicates (FAIL if > 0)
SELECT
    (SELECT COUNT(*) - COUNT(DISTINCT track_id)  FROM clean.tracks)  AS tracks_id_dup,
    (SELECT COUNT(*) - COUNT(DISTINCT artist_id) FROM clean.artists) AS artists_id_dup;

-- G02-B: Genre name duplicates
SELECT
    (SELECT COUNT(*) - COUNT(DISTINCT genre_name)            FROM clean.genres) AS genre_name_dup,
    (SELECT COUNT(*) - COUNT(DISTINCT normalized_genre_name) FROM clean.genres) AS genre_norm_dup;

-- G02-C: Junction table composite key duplicates (FAIL if > 0)
SELECT
    (
        SELECT COUNT(*) - COUNT(DISTINCT (track_id, artist_id)::text)
        FROM clean.track_artists
    ) AS track_artists_dup,
    (
        SELECT COUNT(*) - COUNT(DISTINCT (artist_id, genre_id)::text)
        FROM clean.artist_genres
    ) AS artist_genres_dup,
    (
        SELECT COUNT(*) - COUNT(DISTINCT (artist_id, related_artist_id)::text)
        FROM clean.artist_relations
    ) AS artist_relations_dup;

-- ─────────────────────────────────────────────────────────────────────────────
-- G03  AUDIO FEATURE RANGE [0, 1]
-- ─────────────────────────────────────────────────────────────────────────────

-- G03: Count out-of-range per audio feature (FAIL if any > 0)
SELECT
    (SELECT COUNT(*) FROM clean.tracks WHERE danceability     < 0 OR danceability     > 1) AS danceability_oor,
    (SELECT COUNT(*) FROM clean.tracks WHERE energy           < 0 OR energy           > 1) AS energy_oor,
    (SELECT COUNT(*) FROM clean.tracks WHERE speechiness      < 0 OR speechiness      > 1) AS speechiness_oor,
    (SELECT COUNT(*) FROM clean.tracks WHERE acousticness     < 0 OR acousticness     > 1) AS acousticness_oor,
    (SELECT COUNT(*) FROM clean.tracks WHERE instrumentalness < 0 OR instrumentalness > 1) AS instrumentalness_oor,
    (SELECT COUNT(*) FROM clean.tracks WHERE liveness         < 0 OR liveness         > 1) AS liveness_oor,
    (SELECT COUNT(*) FROM clean.tracks WHERE valence          < 0 OR valence          > 1) AS valence_oor;

-- ─────────────────────────────────────────────────────────────────────────────
-- G04  POPULARITY RANGE [0, 100]
-- ─────────────────────────────────────────────────────────────────────────────

-- G04: Out-of-range popularity (FAIL if any > 0)
SELECT
    (SELECT COUNT(*) FROM clean.tracks  WHERE popularity NOT BETWEEN 0 AND 100) AS tracks_pop_oor,
    (SELECT COUNT(*) FROM clean.artists WHERE popularity NOT BETWEEN 0 AND 100) AS artists_pop_oor;

-- G04-B: Distribution snapshot (INFO)
SELECT
    MIN(popularity) AS min_pop,
    MAX(popularity) AS max_pop,
    ROUND(AVG(popularity), 2) AS avg_pop,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY popularity) AS median_pop
FROM clean.tracks;

-- ─────────────────────────────────────────────────────────────────────────────
-- G05  DURATION VALIDITY
-- ─────────────────────────────────────────────────────────────────────────────

-- G05-A: Critical checks (FAIL if > 0)
SELECT
    (SELECT COUNT(*) FROM clean.tracks WHERE duration_ms  <= 0)          AS dur_ms_invalid,
    (SELECT COUNT(*) FROM clean.tracks WHERE duration_min IS NULL)        AS dur_min_null;

-- G05-B: Outlier counts (WARNING)
SELECT
    (SELECT COUNT(*) FROM clean.tracks WHERE duration_ms < 10000)   AS short_tracks,
    (SELECT COUNT(*) FROM clean.tracks WHERE duration_ms > 3600000) AS long_tracks;

-- ─────────────────────────────────────────────────────────────────────────────
-- G06  TEMPO / LOUDNESS
-- ─────────────────────────────────────────────────────────────────────────────

-- G06-A: Tempo checks
SELECT
    (SELECT COUNT(*) FROM clean.tracks WHERE tempo <= 0)  AS tempo_invalid,
    (SELECT COUNT(*) FROM clean.tracks WHERE tempo IS NULL) AS tempo_null;

-- G06-B: Loudness range checks (FAIL if out of [-60, 10])
SELECT
    (SELECT COUNT(*) FROM clean.tracks WHERE loudness < -60)              AS loudness_too_low,
    (SELECT COUNT(*) FROM clean.tracks WHERE loudness > 10)               AS loudness_too_high,
    (SELECT COUNT(*) FROM clean.tracks WHERE loudness > 0)                AS loudness_positive,  -- WARNING
    (SELECT COUNT(*) FROM clean.tracks WHERE loudness IS NULL)            AS loudness_null;

-- G06-C: Loudness distribution snapshot
SELECT
    MIN(loudness)  AS min_loudness,
    MAX(loudness)  AS max_loudness,
    ROUND(AVG(loudness), 2) AS avg_loudness
FROM clean.tracks;

-- ─────────────────────────────────────────────────────────────────────────────
-- G07  RELEASE DATE / YEAR CONSISTENCY
-- ─────────────────────────────────────────────────────────────────────────────

-- G07-A: Invalid precision (FAIL if > 0)
SELECT COUNT(*) AS invalid_precision
FROM clean.tracks
WHERE release_precision NOT IN ('day', 'month', 'year', 'unknown')
   OR release_precision IS NULL;

-- G07-B: Release year out of expected range (WARNING)
SELECT
    (SELECT COUNT(*) FROM clean.tracks WHERE release_year < 1900 AND release_year IS NOT NULL) AS year_before_1900,
    (SELECT COUNT(*) FROM clean.tracks WHERE release_year > 2025 AND release_year IS NOT NULL) AS year_after_2025;

-- G07-C: Derived column consistency (FAIL if any > 0)
SELECT
    (SELECT COUNT(*) FROM clean.tracks WHERE release_precision='year'  AND release_month IS NOT NULL) AS year_prec_month_nonnull,
    (SELECT COUNT(*) FROM clean.tracks WHERE release_precision='month' AND release_month IS NULL)      AS month_prec_month_null,
    (SELECT COUNT(*) FROM clean.tracks WHERE release_year IS NOT NULL  AND decade IS NULL)             AS year_ok_decade_null;

-- G07-D: Precision distribution
SELECT release_precision, COUNT(*) AS cnt
FROM clean.tracks
GROUP BY release_precision
ORDER BY cnt DESC;

-- ─────────────────────────────────────────────────────────────────────────────
-- G08  ARTIST JOIN COVERAGE
-- ─────────────────────────────────────────────────────────────────────────────

-- G08: Coverage ratio using Feature 1.4 baseline (skipped = 26,224)
SELECT
    COUNT(*)          AS ta_inserted,
    26224             AS ta_skipped,
    COUNT(*) + 26224  AS ta_estimated_total,
    ROUND(COUNT(*)::numeric / (COUNT(*) + 26224) * 100, 2) AS coverage_pct
FROM clean.track_artists;

-- ─────────────────────────────────────────────────────────────────────────────
-- G09  GENRE JOIN COVERAGE
-- ─────────────────────────────────────────────────────────────────────────────

-- G09-A: Artists with non-empty genres in raw
SELECT COUNT(*) AS artists_with_nonempty_genres
FROM raw.raw_artists
WHERE genres IS NOT NULL AND TRIM(genres) <> '[]' AND TRIM(genres) <> '';

-- G09-B: Artists mapped to genre in clean
SELECT COUNT(DISTINCT artist_id) AS artists_mapped_to_genre
FROM clean.artist_genres;

-- G09-C: Coverage calculation
WITH nonempty AS (
    SELECT COUNT(*) AS cnt
    FROM raw.raw_artists
    WHERE genres IS NOT NULL AND TRIM(genres) <> '[]' AND TRIM(genres) <> ''
),
mapped AS (
    SELECT COUNT(DISTINCT artist_id) AS cnt FROM clean.artist_genres
)
SELECT
    nonempty.cnt  AS artists_with_genres,
    mapped.cnt    AS artists_mapped,
    ROUND(mapped.cnt::numeric / NULLIF(nonempty.cnt, 0) * 100, 2) AS coverage_pct
FROM nonempty, mapped;

-- G09-D: FK orphan checks for genre tables
SELECT
    (SELECT COUNT(*) FROM clean.artist_genres ag WHERE NOT EXISTS
        (SELECT 1 FROM clean.artists a WHERE a.artist_id = ag.artist_id)) AS ag_orphan_artists,
    (SELECT COUNT(*) FROM clean.artist_genres ag WHERE NOT EXISTS
        (SELECT 1 FROM clean.genres g WHERE g.genre_id = ag.genre_id))   AS ag_orphan_genres;

-- ─────────────────────────────────────────────────────────────────────────────
-- G10  ROW COUNT PRE/POST CLEAN
-- ─────────────────────────────────────────────────────────────────────────────

-- G10: Raw vs clean comparison (FAIL if mismatch)
SELECT
    (SELECT COUNT(*) FROM raw.raw_tracks)   AS raw_tracks,
    (SELECT COUNT(*) FROM clean.tracks)     AS clean_tracks,
    (SELECT COUNT(*) FROM raw.raw_artists)  AS raw_artists,
    (SELECT COUNT(*) FROM clean.artists)    AS clean_artists,
    (SELECT COUNT(*) FROM clean.genres)          AS clean_genres,
    (SELECT COUNT(*) FROM clean.track_artists)   AS clean_track_artists,
    (SELECT COUNT(*) FROM clean.artist_genres)   AS clean_artist_genres,
    (SELECT COUNT(*) FROM clean.artist_relations) AS clean_artist_relations;

-- ─────────────────────────────────────────────────────────────────────────────
-- G11  FK / ORPHAN CHECKS
-- ─────────────────────────────────────────────────────────────────────────────

-- G11: All orphan counts (FAIL if any > 0)
SELECT
    (SELECT COUNT(*) FROM clean.track_artists ta
        WHERE NOT EXISTS (SELECT 1 FROM clean.tracks t WHERE t.track_id = ta.track_id))
        AS ta_orphan_tracks,
    (SELECT COUNT(*) FROM clean.track_artists ta
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ta.artist_id))
        AS ta_orphan_artists,
    (SELECT COUNT(*) FROM clean.artist_genres ag
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ag.artist_id))
        AS ag_orphan_artists,
    (SELECT COUNT(*) FROM clean.artist_genres ag
        WHERE NOT EXISTS (SELECT 1 FROM clean.genres g WHERE g.genre_id = ag.genre_id))
        AS ag_orphan_genres,
    (SELECT COUNT(*) FROM clean.artist_relations ar
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ar.artist_id))
        AS ar_orphan_src,
    (SELECT COUNT(*) FROM clean.artist_relations ar
        WHERE NOT EXISTS (SELECT 1 FROM clean.artists a WHERE a.artist_id = ar.related_artist_id))
        AS ar_orphan_tgt;

-- ─────────────────────────────────────────────────────────────────────────────
-- G12  ML-SAFE NOTES (informational queries only)
-- ─────────────────────────────────────────────────────────────────────────────

-- G12-A: Tracks popularity as target variable
SELECT
    'target_variable'  AS ml_role,
    'clean.tracks.popularity' AS column_ref,
    MIN(popularity) AS min_val,
    MAX(popularity) AS max_val,
    ROUND(AVG(popularity), 2) AS avg_val,
    COUNT(*) FILTER (WHERE popularity IS NULL) AS null_count
FROM clean.tracks;

-- G12-B: Artists popularity as dashboard-only
SELECT
    'dashboard_only' AS ml_role,
    'clean.artists.popularity' AS column_ref,
    MIN(popularity) AS min_val,
    MAX(popularity) AS max_val,
    ROUND(AVG(popularity), 2) AS avg_val,
    COUNT(*) FILTER (WHERE popularity IS NULL) AS null_count
FROM clean.artists;

-- G12-C: Artists followers caution
SELECT
    'caution'         AS ml_role,
    'clean.artists.followers' AS column_ref,
    MIN(followers)    AS min_val,
    MAX(followers)    AS max_val,
    COUNT(*) FILTER (WHERE followers IS NULL) AS null_count
FROM clean.artists;

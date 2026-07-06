-- =============================================================
-- 02_cleaning_checks.sql
-- HitRadar — Post-cleaning validation queries
-- Feature 1.4 — Data Cleaning & Normalization
-- =============================================================

-- -----------------------------------------------------------
-- 1. Row counts clean tables
-- -----------------------------------------------------------
SELECT
    'clean.tracks'           AS tbl, COUNT(*) AS row_count FROM clean.tracks
UNION ALL SELECT 'clean.artists',          COUNT(*) FROM clean.artists
UNION ALL SELECT 'clean.genres',           COUNT(*) FROM clean.genres
UNION ALL SELECT 'clean.track_artists',    COUNT(*) FROM clean.track_artists
UNION ALL SELECT 'clean.artist_genres',    COUNT(*) FROM clean.artist_genres
UNION ALL SELECT 'clean.artist_relations', COUNT(*) FROM clean.artist_relations
ORDER BY tbl;

-- -----------------------------------------------------------
-- 2. Raw vs Clean row count comparison
-- -----------------------------------------------------------
SELECT
    'raw.raw_tracks'    AS src, COUNT(*) AS raw_cnt FROM raw.raw_tracks
UNION ALL
SELECT 'clean.tracks',          COUNT(*) FROM clean.tracks;

SELECT
    'raw.raw_artists'   AS src, COUNT(*) AS raw_cnt FROM raw.raw_artists
UNION ALL
SELECT 'clean.artists',         COUNT(*) FROM clean.artists;

-- -----------------------------------------------------------
-- 3. NULL ID checks
-- -----------------------------------------------------------
SELECT 'clean.tracks.track_id NULL'     AS check_name, COUNT(*) AS bad_count
FROM clean.tracks WHERE track_id IS NULL
UNION ALL
SELECT 'clean.artists.artist_id NULL',    COUNT(*)
FROM clean.artists WHERE artist_id IS NULL;

-- -----------------------------------------------------------
-- 4. Duplicate ID checks
-- -----------------------------------------------------------
SELECT 'clean.tracks duplicate track_id' AS check_name,
       COUNT(*) - COUNT(DISTINCT track_id) AS duplicates
FROM clean.tracks
UNION ALL
SELECT 'clean.artists duplicate artist_id',
       COUNT(*) - COUNT(DISTINCT artist_id)
FROM clean.artists;

-- -----------------------------------------------------------
-- 5. Invalid release_precision
-- -----------------------------------------------------------
SELECT release_precision, COUNT(*) AS cnt
FROM clean.tracks
GROUP BY release_precision
ORDER BY cnt DESC;

SELECT COUNT(*) AS invalid_precision_count
FROM clean.tracks
WHERE release_precision NOT IN ('day', 'month', 'year', 'unknown')
   OR release_precision IS NULL;

-- -----------------------------------------------------------
-- 6. Tempo issues (should be 0 after cleaning)
-- -----------------------------------------------------------
SELECT 'tempo <= 0 remaining' AS check_name, COUNT(*) AS cnt
FROM clean.tracks
WHERE tempo <= 0;

SELECT 'tempo IS NULL' AS check_name, COUNT(*) AS cnt
FROM clean.tracks
WHERE tempo IS NULL;

-- -----------------------------------------------------------
-- 7. time_signature issues
-- -----------------------------------------------------------
SELECT 'time_signature = 0 remaining' AS check_name, COUNT(*) AS cnt
FROM clean.tracks
WHERE time_signature = 0;

SELECT 'time_signature IS NULL' AS check_name, COUNT(*) AS cnt
FROM clean.tracks
WHERE time_signature IS NULL;

-- -----------------------------------------------------------
-- 8. duration_min check
-- -----------------------------------------------------------
SELECT
    MIN(duration_min) AS min_dur_min,
    MAX(duration_min) AS max_dur_min,
    AVG(duration_min)::NUMERIC(8,4) AS avg_dur_min,
    COUNT(*) FILTER (WHERE duration_min IS NULL) AS null_dur_min,
    COUNT(*) FILTER (WHERE duration_ms < 10000) AS short_tracks,
    COUNT(*) FILTER (WHERE duration_ms > 3600000) AS long_tracks
FROM clean.tracks;

-- -----------------------------------------------------------
-- 9. release_date vs release_precision consistency
-- -----------------------------------------------------------
SELECT
    release_precision,
    MIN(release_date) AS min_date,
    MAX(release_date) AS max_date,
    COUNT(*) AS cnt
FROM clean.tracks
GROUP BY release_precision
ORDER BY release_precision;

-- -----------------------------------------------------------
-- 10. Sample: clean.track_artists
-- -----------------------------------------------------------
SELECT ta.track_id, ta.artist_id, ta.artist_order, ta.is_main_artist,
       t.name AS track_name, a.name AS artist_name
FROM clean.track_artists ta
JOIN clean.tracks  t ON t.track_id  = ta.track_id
JOIN clean.artists a ON a.artist_id = ta.artist_id
LIMIT 10;

-- -----------------------------------------------------------
-- 11. Sample: clean.artist_genres
-- -----------------------------------------------------------
SELECT ag.artist_id, a.name, g.genre_name
FROM clean.artist_genres ag
JOIN clean.artists a ON a.artist_id = ag.artist_id
JOIN clean.genres  g ON g.genre_id  = ag.genre_id
LIMIT 10;

-- -----------------------------------------------------------
-- 12. Sample: clean.artist_relations
-- -----------------------------------------------------------
SELECT ar.artist_id, a1.name AS artist,
       ar.related_artist_id, a2.name AS related,
       ar.relation_order
FROM clean.artist_relations ar
JOIN clean.artists a1 ON a1.artist_id = ar.artist_id
JOIN clean.artists a2 ON a2.artist_id = ar.related_artist_id
LIMIT 10;

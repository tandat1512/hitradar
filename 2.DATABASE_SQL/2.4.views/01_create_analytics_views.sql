-- =============================================================================
-- 01_create_analytics_views.sql — Feature 1.6: Analytics Views
-- HitRadar Pro | EPIC 1 — Data Foundation
--
-- CREATE OR REPLACE VIEW: idempotent, safe to re-run.
-- All views are READ-ONLY projections over the clean layer.
-- No INSERT / UPDATE / DELETE / TRUNCATE.
-- All views reside in the analytics schema.
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Drop existing views first (column schema changes require DROP + recreate)
-- Only drops analytics views — never touches raw or clean tables.
-- ─────────────────────────────────────────────────────────────────────────────
DROP VIEW IF EXISTS analytics.vw_ml_training_dataset   CASCADE;
DROP VIEW IF EXISTS analytics.vw_data_quality_report   CASCADE;
DROP VIEW IF EXISTS analytics.vw_duration_trends       CASCADE;
DROP VIEW IF EXISTS analytics.vw_explicit_by_decade    CASCADE;
DROP VIEW IF EXISTS analytics.vw_genre_trends          CASCADE;
DROP VIEW IF EXISTS analytics.vw_top_artists           CASCADE;
DROP VIEW IF EXISTS analytics.vw_popularity_stats      CASCADE;
DROP VIEW IF EXISTS analytics.vw_audio_trends          CASCADE;
DROP VIEW IF EXISTS analytics.vw_tracks_by_decade      CASCADE;
DROP VIEW IF EXISTS analytics.vw_tracks_overview       CASCADE;

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 1  vw_tracks_overview
-- Purpose : Full track snapshot for EDA / dashboard
-- Source  : clean.tracks
-- Rows    : = clean.tracks (586,672)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_tracks_overview AS
SELECT
    track_id,
    name,
    popularity,
    duration_ms,
    duration_min,
    explicit,
    release_date,
    release_year,
    release_month,
    decade,
    release_precision,
    danceability,
    energy,
    key,
    loudness,
    mode,
    speechiness,
    acousticness,
    instrumentalness,
    liveness,
    valence,
    tempo,
    time_signature
FROM clean.tracks;

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 2  vw_tracks_by_decade
-- Purpose : Aggregate track metrics per decade
-- Source  : clean.tracks
-- Rows    : one per distinct non-null decade
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_tracks_by_decade AS
SELECT
    decade,
    COUNT(*)                                         AS track_count,
    ROUND(AVG(popularity)::numeric, 2)               AS avg_popularity,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY popularity)
                                                     AS median_popularity,
    ROUND(AVG(duration_min)::numeric, 2)             AS avg_duration_min,
    ROUND(AVG(danceability)::numeric, 4)             AS avg_danceability,
    ROUND(AVG(energy)::numeric, 4)                   AS avg_energy,
    ROUND(AVG(valence)::numeric, 4)                  AS avg_valence,
    ROUND(AVG(tempo)::numeric, 2)                    AS avg_tempo,
    ROUND(AVG(loudness)::numeric, 2)                 AS avg_loudness,
    COUNT(*) FILTER (WHERE explicit = TRUE)          AS explicit_count,
    ROUND(
        COUNT(*) FILTER (WHERE explicit = TRUE)::numeric
        / NULLIF(COUNT(*), 0)
    , 4)                                             AS explicit_ratio
FROM clean.tracks
WHERE decade IS NOT NULL
GROUP BY decade
ORDER BY decade;

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 3  vw_audio_trends
-- Purpose : Audio feature evolution per release year
-- Source  : clean.tracks
-- Rows    : one per distinct release_year (non-null)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_audio_trends AS
SELECT
    release_year,
    COUNT(*)                                    AS track_count,
    ROUND(AVG(danceability)::numeric,    4)     AS avg_danceability,
    ROUND(AVG(energy)::numeric,          4)     AS avg_energy,
    ROUND(AVG(speechiness)::numeric,     4)     AS avg_speechiness,
    ROUND(AVG(acousticness)::numeric,    4)     AS avg_acousticness,
    ROUND(AVG(instrumentalness)::numeric,4)     AS avg_instrumentalness,
    ROUND(AVG(liveness)::numeric,        4)     AS avg_liveness,
    ROUND(AVG(valence)::numeric,         4)     AS avg_valence,
    ROUND(AVG(tempo)::numeric,           2)     AS avg_tempo,
    ROUND(AVG(loudness)::numeric,        2)     AS avg_loudness
FROM clean.tracks
WHERE release_year IS NOT NULL
GROUP BY release_year
ORDER BY release_year;

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 4  vw_popularity_stats
-- Purpose : Track distribution across popularity buckets
-- Source  : clean.tracks
-- Note    : clean.tracks.popularity is the TARGET VARIABLE — not an ML input.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_popularity_stats AS
SELECT
    CASE
        WHEN popularity BETWEEN 0  AND 20  THEN '0–20'
        WHEN popularity BETWEEN 21 AND 40  THEN '21–40'
        WHEN popularity BETWEEN 41 AND 60  THEN '41–60'
        WHEN popularity BETWEEN 61 AND 80  THEN '61–80'
        WHEN popularity BETWEEN 81 AND 100 THEN '81–100'
        ELSE 'unknown'
    END                                             AS popularity_bucket,
    COUNT(*)                                        AS track_count,
    MIN(popularity)                                 AS min_popularity,
    MAX(popularity)                                 AS max_popularity,
    ROUND(AVG(popularity)::numeric, 2)              AS avg_popularity,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY popularity)
                                                    AS median_popularity
FROM clean.tracks
GROUP BY popularity_bucket
ORDER BY MIN(popularity);

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 5  vw_top_artists
-- Purpose : Artist ranking by track count and avg track popularity
-- Source  : clean.artists, clean.track_artists, clean.tracks
-- Note    : Only artists with at least one track are included.
--           artist_popularity_dashboard_only = clean.artists.popularity
--           — DO NOT use as ML input feature.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_top_artists AS
SELECT
    a.artist_id,
    a.name                                          AS artist_name,
    COUNT(DISTINCT ta.track_id)                     AS track_count,
    ROUND(AVG(t.popularity)::numeric, 2)            AS avg_track_popularity,
    MAX(t.popularity)                               AS max_track_popularity,
    a.followers,
    a.popularity                                    AS artist_popularity_dashboard_only
FROM clean.artists  a
JOIN clean.track_artists ta ON a.artist_id = ta.artist_id
JOIN clean.tracks        t  ON ta.track_id = t.track_id
GROUP BY a.artist_id, a.name, a.followers, a.popularity
ORDER BY track_count DESC, avg_track_popularity DESC;

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 6  vw_genre_trends
-- Purpose : Genre performance per decade
-- Source  : clean.genres, clean.artist_genres, clean.track_artists, clean.tracks
-- Anti-dup: CTE uses DISTINCT (track_id, genre_id, decade) before aggregation
--           to prevent duplicate-weighting when a track has multiple artists
--           sharing the same genre.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_genre_trends AS
WITH track_genres AS (
    -- One row per unique (track, genre, decade) — eliminates multi-artist inflate
    SELECT DISTINCT
        t.track_id,
        g.genre_id,
        g.genre_name,
        g.normalized_genre_name,
        t.decade,
        t.popularity,
        t.danceability,
        t.energy,
        t.valence,
        t.duration_min
    FROM clean.tracks        t
    JOIN clean.track_artists ta ON t.track_id  = ta.track_id
    JOIN clean.artist_genres ag ON ta.artist_id = ag.artist_id
    JOIN clean.genres         g ON ag.genre_id  = g.genre_id
    WHERE t.decade IS NOT NULL
)
SELECT
    genre_id,
    genre_name,
    normalized_genre_name,
    decade,
    COUNT(DISTINCT track_id)                AS track_count,
    ROUND(AVG(popularity)::numeric,    2)   AS avg_popularity,
    ROUND(AVG(danceability)::numeric,  4)   AS avg_danceability,
    ROUND(AVG(energy)::numeric,        4)   AS avg_energy,
    ROUND(AVG(valence)::numeric,       4)   AS avg_valence,
    ROUND(AVG(duration_min)::numeric,  2)   AS avg_duration_min
FROM track_genres
GROUP BY genre_id, genre_name, normalized_genre_name, decade
ORDER BY decade, COUNT(DISTINCT track_id) DESC;

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 7  vw_explicit_by_decade
-- Purpose : Explicit content ratio per decade
-- Source  : clean.tracks
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_explicit_by_decade AS
SELECT
    decade,
    COUNT(*)                                                AS track_count,
    COUNT(*) FILTER (WHERE explicit = TRUE)                 AS explicit_count,
    COUNT(*) FILTER (WHERE explicit = FALSE OR explicit IS NULL) AS non_explicit_count,
    ROUND(
        COUNT(*) FILTER (WHERE explicit = TRUE)::numeric
        / NULLIF(COUNT(*), 0)
    , 4)                                                    AS explicit_ratio
FROM clean.tracks
WHERE decade IS NOT NULL
GROUP BY decade
ORDER BY decade;

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 8  vw_duration_trends
-- Purpose : Duration distribution per year/decade; carry F1.5 outlier warnings
-- Source  : clean.tracks
-- Note    : Outliers (short/long) are flagged, NOT removed.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_duration_trends AS
SELECT
    release_year,
    decade,
    COUNT(*)                                                    AS track_count,
    ROUND(AVG(duration_min)::numeric, 2)                        AS avg_duration_min,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_min)   AS median_duration_min,
    ROUND(MIN(duration_min)::numeric, 3)                        AS min_duration_min,
    ROUND(MAX(duration_min)::numeric, 3)                        AS max_duration_min,
    COUNT(*) FILTER (WHERE duration_ms < 10000)                 AS short_track_count,
    COUNT(*) FILTER (WHERE duration_ms > 3600000)               AS long_track_count
FROM clean.tracks
WHERE release_year IS NOT NULL
GROUP BY release_year, decade
ORDER BY release_year;

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 9  vw_data_quality_report
-- Purpose : Expose Feature 1.5 quality metrics as a queryable view
-- Source  : clean tables (live counts) + F1.4 literal constants
-- Note    : Literals (skipped=26224, ar_diff=1) come from Feature 1.4 cleaning
--           log and cannot be recomputed without re-running the cleaning script.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_data_quality_report AS
-- Live counts from DB
SELECT 'clean_tracks_row_count'          AS metric_name,
       COUNT(*)::text                    AS metric_value,
       'INFO'                            AS severity,
       'From clean.tracks'               AS note
FROM clean.tracks
UNION ALL
SELECT 'clean_artists_row_count',
       COUNT(*)::text, 'INFO', 'From clean.artists'
FROM clean.artists
UNION ALL
SELECT 'clean_genres_row_count',
       COUNT(*)::text, 'INFO', 'From clean.genres'
FROM clean.genres
UNION ALL
SELECT 'clean_track_artists_row_count',
       COUNT(*)::text, 'INFO', 'From clean.track_artists'
FROM clean.track_artists
UNION ALL
SELECT 'clean_artist_genres_row_count',
       COUNT(*)::text, 'INFO', 'From clean.artist_genres'
FROM clean.artist_genres
UNION ALL
SELECT 'clean_artist_relations_row_count',
       COUNT(*)::text, 'INFO', 'From clean.artist_relations'
FROM clean.artist_relations
UNION ALL
-- Derived quality metrics from DB
SELECT 'duration_short_count',
       COUNT(*)::text, 'WARNING',
       'Tracks with duration_ms < 10000 ms — kept per F1.4 rule'
FROM clean.tracks WHERE duration_ms < 10000
UNION ALL
SELECT 'duration_long_count',
       COUNT(*)::text, 'WARNING',
       'Tracks with duration_ms > 3600000 ms — kept per F1.4 rule'
FROM clean.tracks WHERE duration_ms > 3600000
UNION ALL
SELECT 'loudness_positive_count',
       COUNT(*)::text, 'WARNING',
       'Tracks with loudness > 0 dB — unusual but valid'
FROM clean.tracks WHERE loudness > 0
UNION ALL
SELECT 'tracks_name_null_count',
       COUNT(*)::text, 'INFO',
       'clean.tracks.name IS NULL — retained by F1.4 rule'
FROM clean.tracks WHERE name IS NULL
UNION ALL
SELECT 'artists_followers_null_count',
       COUNT(*)::text, 'INFO',
       'clean.artists.followers IS NULL — retained by F1.4 rule'
FROM clean.artists WHERE followers IS NULL
UNION ALL
-- Literal constants from Feature 1.4 cleaning log (cannot recompute without re-run)
SELECT 'track_artists_skipped',
       '26224', 'WARNING',
       'Artist FK not found in artists.csv — F1.4 cleaning log literal'
UNION ALL
SELECT 'track_artists_coverage_pct',
       '96.54', 'WARNING',
       '730946 / 757170 — F1.4 cleaning log baseline'
UNION ALL
SELECT 'genre_join_coverage_pct',
       '100.00', 'PASS',
       '305595 / 305595 — F1.5 gate G09'
UNION ALL
SELECT 'artist_relations_diff',
       '1', 'WARNING',
       'ON CONFLICT collapsed 1 duplicate (artist_id, related_artist_id) pair'
UNION ALL
SELECT 'data_quality_status',
       'PASS_WITH_WARNINGS', 'WARNING',
       'Feature 1.5 overall gate result — G05 duration + G06 loudness warnings';

-- ─────────────────────────────────────────────────────────────────────────────
-- VIEW 10  vw_ml_training_dataset
-- Purpose : ML handoff candidate for EPIC 2 (read-only, no train/test split)
-- Source  : clean.tracks
-- CRITICAL ML RULES:
--   - target_popularity = clean.tracks.popularity  → LABEL, not an input feature
--   - NO artists.popularity (dashboard_only / caution)
--   - NO aggregate popularity by artist or genre
--   - NO popularity_bucket as input feature
--   - NO train/test split here
--   - NO imputation / label encoding here
--   - NULL rows are kept (EPIC 2 decides imputation strategy)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW analytics.vw_ml_training_dataset AS
SELECT
    track_id,
    -- TARGET: popularity is the prediction label — DO NOT use as input feature
    popularity                  AS target_popularity,
    duration_min,
    explicit,
    release_year,
    release_month,
    decade,
    release_precision,
    -- Audio features (input features for ML)
    danceability,
    energy,
    key,
    loudness,
    mode,
    speechiness,
    acousticness,
    instrumentalness,
    liveness,
    valence,
    tempo,
    time_signature
FROM clean.tracks;

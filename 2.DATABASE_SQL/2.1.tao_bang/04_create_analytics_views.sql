-- =============================================================
-- 04_create_analytics_views.sql
-- HitRadar — analytics layer views
-- Feature 1.2 — Database Architecture
-- Skeleton: views chưa validate bằng data thật (chờ Feature 1.6)
--
-- FIX (SQL review):
--   - ROUND(AVG(<double precision>)) → ROUND(AVG(col)::numeric, n)
--   - vw_genre_trends: dùng CTE DISTINCT để tránh duplicate weighting
--   - percentile_cont: cast kết quả sang ::numeric trước ROUND
-- =============================================================

-- -------------------------------------------------------------
-- vw_tracks_overview — tổng quan tất cả track
-- Không có aggregate — không cần cast
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_tracks_overview AS
SELECT
    t.track_id,
    t.name,
    t.popularity,
    t.duration_min,
    t.explicit,
    t.release_year,
    t.decade,
    t.danceability,
    t.energy,
    t.valence,
    t.tempo,
    t.loudness,
    t.acousticness,
    t.speechiness,
    t.instrumentalness
FROM clean.tracks t;

-- -------------------------------------------------------------
-- vw_tracks_by_decade — thống kê theo thập kỷ
-- FIX: AVG(double precision) → ::numeric trước ROUND
-- popularity là SMALLINT → AVG trả về NUMERIC → không cần cast
-- duration_min là NUMERIC  → AVG trả về NUMERIC → không cần cast
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_tracks_by_decade AS
SELECT
    t.decade,
    COUNT(*)                                    AS track_count,
    ROUND(AVG(t.popularity), 2)                 AS avg_popularity,
    ROUND(AVG(t.danceability)::numeric, 4)      AS avg_danceability,
    ROUND(AVG(t.energy)::numeric, 4)            AS avg_energy,
    ROUND(AVG(t.valence)::numeric, 4)           AS avg_valence,
    ROUND(AVG(t.tempo)::numeric, 2)             AS avg_tempo,
    ROUND(AVG(t.loudness)::numeric, 2)          AS avg_loudness,
    ROUND(AVG(t.acousticness)::numeric, 4)      AS avg_acousticness,
    ROUND(AVG(t.duration_min), 2)               AS avg_duration_min
FROM clean.tracks t
WHERE t.decade IS NOT NULL
GROUP BY t.decade
ORDER BY t.decade;

-- -------------------------------------------------------------
-- vw_audio_trends — xu hướng audio features theo năm
-- FIX: AVG(double precision) → ::numeric trước ROUND
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_audio_trends AS
SELECT
    t.release_year,
    COUNT(*)                                        AS track_count,
    ROUND(AVG(t.danceability)::numeric, 4)          AS avg_danceability,
    ROUND(AVG(t.energy)::numeric, 4)                AS avg_energy,
    ROUND(AVG(t.valence)::numeric, 4)               AS avg_valence,
    ROUND(AVG(t.acousticness)::numeric, 4)          AS avg_acousticness,
    ROUND(AVG(t.instrumentalness)::numeric, 4)      AS avg_instrumentalness,
    ROUND(AVG(t.speechiness)::numeric, 4)           AS avg_speechiness,
    ROUND(AVG(t.tempo)::numeric, 2)                 AS avg_tempo
FROM clean.tracks t
WHERE t.release_year IS NOT NULL
GROUP BY t.release_year
ORDER BY t.release_year;

-- -------------------------------------------------------------
-- vw_popularity_stats — phân phối popularity (target analysis)
-- LƯU Ý: View này chỉ dùng cho EDA — không dùng để train model
-- popularity là SMALLINT → tính toán trên INTEGER/BIGINT, không cần cast
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_popularity_stats AS
SELECT
    CASE
        WHEN popularity BETWEEN 0  AND 9   THEN '0-9'
        WHEN popularity BETWEEN 10 AND 19  THEN '10-19'
        WHEN popularity BETWEEN 20 AND 29  THEN '20-29'
        WHEN popularity BETWEEN 30 AND 39  THEN '30-39'
        WHEN popularity BETWEEN 40 AND 49  THEN '40-49'
        WHEN popularity BETWEEN 50 AND 59  THEN '50-59'
        WHEN popularity BETWEEN 60 AND 69  THEN '60-69'
        WHEN popularity BETWEEN 70 AND 79  THEN '70-79'
        WHEN popularity BETWEEN 80 AND 89  THEN '80-89'
        WHEN popularity BETWEEN 90 AND 100 THEN '90-100'
    END                                                     AS popularity_bucket,
    COUNT(*)                                                AS track_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)     AS pct_of_total
FROM clean.tracks
GROUP BY 1
ORDER BY 1;

-- -------------------------------------------------------------
-- vw_top_artists — top nghệ sĩ theo số track và popularity
-- popularity là SMALLINT → AVG = NUMERIC → không cần cast
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_top_artists AS
SELECT
    a.artist_id,
    a.name                              AS artist_name,
    COUNT(DISTINCT ta.track_id)         AS track_count,
    ROUND(AVG(t.popularity), 2)         AS avg_track_popularity,
    a.followers
FROM clean.artists a
JOIN clean.track_artists ta ON a.artist_id = ta.artist_id
JOIN clean.tracks t         ON ta.track_id = t.track_id
GROUP BY a.artist_id, a.name, a.followers
ORDER BY track_count DESC, avg_track_popularity DESC;

-- -------------------------------------------------------------
-- vw_genre_trends — xu hướng genre theo thập kỷ
-- FIX: dùng CTE DISTINCT (track_id, genre_id) để tránh duplicate
--      weighting khi một track có nhiều artist cùng genre
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_genre_trends AS
WITH track_genres AS (
    -- Mỗi (track_id, genre_id) chỉ xuất hiện 1 lần
    -- dù track có nhiều artist cùng thuộc genre đó
    SELECT DISTINCT
        t.track_id,
        g.genre_id,
        g.genre_name,
        t.decade,
        t.popularity
    FROM clean.tracks          t
    JOIN clean.track_artists   ta  ON t.track_id   = ta.track_id
    JOIN clean.artist_genres   ag  ON ta.artist_id  = ag.artist_id
    JOIN clean.genres          g   ON ag.genre_id   = g.genre_id
    WHERE t.decade IS NOT NULL
)
SELECT
    genre_name,
    decade,
    COUNT(DISTINCT track_id)            AS track_count,
    ROUND(AVG(popularity)::numeric, 2)  AS avg_popularity
FROM track_genres
GROUP BY genre_name, decade
ORDER BY decade, track_count DESC;

-- -------------------------------------------------------------
-- vw_explicit_by_decade — tỷ lệ explicit content theo thập kỷ
-- Không có DOUBLE PRECISION aggregate — không cần cast
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_explicit_by_decade AS
SELECT
    decade,
    COUNT(*)                                                    AS total_tracks,
    SUM(CASE WHEN explicit THEN 1 ELSE 0 END)                   AS explicit_count,
    ROUND(SUM(CASE WHEN explicit THEN 1 ELSE 0 END) * 100.0
          / COUNT(*), 2)                                        AS explicit_pct
FROM clean.tracks
WHERE decade IS NOT NULL
GROUP BY decade
ORDER BY decade;

-- -------------------------------------------------------------
-- vw_duration_trends — xu hướng thời lượng theo năm
-- duration_min là NUMERIC(8,4) → AVG/MIN/MAX = NUMERIC → ROUND OK
-- FIX: PERCENTILE_CONT trả về input type; cast rõ ràng sang ::numeric
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_duration_trends AS
SELECT
    release_year,
    ROUND(AVG(duration_min), 4)                                 AS avg_duration_min,
    ROUND(
        (PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_min))::numeric,
        4
    )                                                           AS median_duration_min,
    ROUND(MIN(duration_min), 4)                                 AS min_duration_min,
    ROUND(MAX(duration_min), 4)                                 AS max_duration_min,
    COUNT(*)                                                    AS track_count
FROM clean.tracks
WHERE release_year IS NOT NULL
  AND duration_min IS NOT NULL
GROUP BY release_year
ORDER BY release_year;

-- -------------------------------------------------------------
-- vw_ml_training_dataset — ML-ready candidate dataset
-- Bàn giao EPIC 2 — EPIC 2 thực hiện split train/test
--
-- LEAKAGE PROTECTION:
--   - artists.popularity KHÔNG có ở đây
--   - artists.followers  KHÔNG có ở đây
--   - Không có aggregate từ toàn dataset
-- Không có DOUBLE PRECISION ROUND ở đây — không cần cast
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW analytics.vw_ml_training_dataset AS
SELECT
    t.track_id,
    -- ─── TARGET (label, không dùng làm input feature) ───
    t.popularity,
    -- ─── Input features ──────────────────────────────────
    t.duration_ms,
    t.duration_min,
    t.explicit::INTEGER             AS explicit_int,   -- 0/1 cho sklearn
    t.release_year,
    t.decade,
    t.danceability,
    t.energy,
    t.key,
    t.loudness,
    t.mode,
    t.speechiness,
    t.acousticness,
    t.instrumentalness,
    t.liveness,
    t.valence,
    t.tempo,
    t.time_signature,
    -- ─── Derived feature ─────────────────────────────────
    COUNT(ta.artist_id)             AS n_artists        -- số nghệ sĩ trong track
FROM clean.tracks t
LEFT JOIN clean.track_artists ta ON t.track_id = ta.track_id
GROUP BY
    t.track_id, t.popularity, t.duration_ms, t.duration_min, t.explicit,
    t.release_year, t.decade, t.danceability, t.energy, t.key, t.loudness,
    t.mode, t.speechiness, t.acousticness, t.instrumentalness, t.liveness,
    t.valence, t.tempo, t.time_signature;

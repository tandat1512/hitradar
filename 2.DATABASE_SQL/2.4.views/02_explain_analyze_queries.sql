-- =============================================================================
-- 02_explain_analyze_queries.sql — Feature 1.6: EXPLAIN ANALYZE
-- HitRadar Pro | EPIC 1 — Data Foundation
--
-- Run EXPLAIN ANALYZE on key analytics view queries to assess performance.
-- All queries are read-only SELECT — no data modification.
-- =============================================================================

-- 1. vw_tracks_overview (simple projection, expected fast)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_tracks_overview LIMIT 100;

-- 2. vw_tracks_by_decade (GROUP BY + PERCENTILE, expected moderate)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_tracks_by_decade;

-- 3. vw_audio_trends (GROUP BY release_year, expected moderate)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_audio_trends LIMIT 100;

-- 4. vw_popularity_stats (CASE + GROUP BY, expected fast)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_popularity_stats;

-- 5. vw_top_artists (3-table JOIN + GROUP BY, expected moderate-heavy)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_top_artists LIMIT 100;

-- 6. vw_genre_trends (4-table JOIN + CTE DISTINCT, expected heavy)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_genre_trends LIMIT 100;

-- 7. vw_explicit_by_decade (GROUP BY + FILTER, expected fast)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_explicit_by_decade;

-- 8. vw_duration_trends (GROUP BY + PERCENTILE, expected moderate)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_duration_trends LIMIT 100;

-- 9. vw_data_quality_report (UNION ALL with subquery counts, expected moderate)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_data_quality_report;

-- 10. vw_ml_training_dataset (simple projection, expected fast)
EXPLAIN ANALYZE
SELECT * FROM analytics.vw_ml_training_dataset LIMIT 100;

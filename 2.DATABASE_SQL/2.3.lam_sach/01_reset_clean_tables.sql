-- =============================================================
-- 01_reset_clean_tables.sql
-- HitRadar — Truncate clean layer theo đúng thứ tự FK
-- Feature 1.4 — Data Cleaning & Normalization
-- =============================================================
-- Thứ tự TRUNCATE: từ table phụ thuộc → table nền
-- clean.artist_relations và clean.artist_genres phụ thuộc clean.artists
-- clean.track_artists phụ thuộc clean.tracks + clean.artists
-- clean.artist_genres phụ thuộc clean.genres
-- =============================================================

TRUNCATE TABLE
    clean.artist_relations,
    clean.artist_genres,
    clean.track_artists,
    clean.genres,
    clean.tracks,
    clean.artists
RESTART IDENTITY;

-- Xác nhận sau truncate
SELECT
    'clean.artist_relations' AS tbl, COUNT(*) FROM clean.artist_relations
UNION ALL SELECT 'clean.artist_genres',  COUNT(*) FROM clean.artist_genres
UNION ALL SELECT 'clean.track_artists',  COUNT(*) FROM clean.track_artists
UNION ALL SELECT 'clean.genres',         COUNT(*) FROM clean.genres
UNION ALL SELECT 'clean.tracks',         COUNT(*) FROM clean.tracks
UNION ALL SELECT 'clean.artists',        COUNT(*) FROM clean.artists;

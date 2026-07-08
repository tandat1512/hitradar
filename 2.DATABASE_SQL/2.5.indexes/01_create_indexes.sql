-- =============================================================================
-- 01_create_indexes.sql — Feature 1.6: Performance Indexes
-- HitRadar Pro | EPIC 1 — Data Foundation
--
-- CREATE INDEX IF NOT EXISTS: idempotent, safe to re-run.
-- Indexes on clean schema tables to support analytics view queries.
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- clean.tracks
-- ─────────────────────────────────────────────────────────────────────────────

-- Primary key already indexed by tracks_pkey
-- Additional lookup columns:

CREATE INDEX IF NOT EXISTS idx_clean_tracks_release_year
    ON clean.tracks (release_year);

CREATE INDEX IF NOT EXISTS idx_clean_tracks_decade
    ON clean.tracks (decade);

CREATE INDEX IF NOT EXISTS idx_clean_tracks_popularity
    ON clean.tracks (popularity);

CREATE INDEX IF NOT EXISTS idx_clean_tracks_explicit
    ON clean.tracks (explicit);

CREATE INDEX IF NOT EXISTS idx_clean_tracks_release_precision
    ON clean.tracks (release_precision);

-- Composite: typical filter for analytics (year + popularity)
CREATE INDEX IF NOT EXISTS idx_clean_tracks_year_popularity
    ON clean.tracks (release_year, popularity);

-- Composite: decade + explicit for vw_explicit_by_decade, vw_tracks_by_decade
CREATE INDEX IF NOT EXISTS idx_clean_tracks_decade_explicit
    ON clean.tracks (decade, explicit);

-- Duration outlier filter
CREATE INDEX IF NOT EXISTS idx_clean_tracks_duration_ms
    ON clean.tracks (duration_ms);

-- Loudness filter
CREATE INDEX IF NOT EXISTS idx_clean_tracks_loudness
    ON clean.tracks (loudness);

-- ─────────────────────────────────────────────────────────────────────────────
-- clean.track_artists
-- ─────────────────────────────────────────────────────────────────────────────

-- Primary key: (track_id, artist_id, artist_order) — already indexed

CREATE INDEX IF NOT EXISTS idx_clean_track_artists_track_id
    ON clean.track_artists (track_id);

CREATE INDEX IF NOT EXISTS idx_clean_track_artists_artist_id
    ON clean.track_artists (artist_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- clean.artists
-- ─────────────────────────────────────────────────────────────────────────────

-- Primary key: artist_id — already indexed by artists_pkey

CREATE INDEX IF NOT EXISTS idx_clean_artists_name
    ON clean.artists (name);

CREATE INDEX IF NOT EXISTS idx_clean_artists_popularity
    ON clean.artists (popularity);

CREATE INDEX IF NOT EXISTS idx_clean_artists_followers
    ON clean.artists (followers);

-- ─────────────────────────────────────────────────────────────────────────────
-- clean.genres
-- ─────────────────────────────────────────────────────────────────────────────

-- Primary key: genre_id — already indexed by genres_pkey
-- Unique constraint on genre_name already indexed

CREATE INDEX IF NOT EXISTS idx_clean_genres_genre_name
    ON clean.genres (genre_name);

CREATE INDEX IF NOT EXISTS idx_clean_genres_normalized
    ON clean.genres (normalized_genre_name);

-- ─────────────────────────────────────────────────────────────────────────────
-- clean.artist_genres
-- ─────────────────────────────────────────────────────────────────────────────

-- PK: (artist_id, genre_id) — already indexed by artist_genres_pkey

CREATE INDEX IF NOT EXISTS idx_clean_artist_genres_artist_id
    ON clean.artist_genres (artist_id);

CREATE INDEX IF NOT EXISTS idx_clean_artist_genres_genre_id
    ON clean.artist_genres (genre_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- clean.artist_relations
-- ─────────────────────────────────────────────────────────────────────────────

-- PK: (artist_id, related_artist_id) — already indexed

CREATE INDEX IF NOT EXISTS idx_clean_artist_relations_artist_id
    ON clean.artist_relations (artist_id);

CREATE INDEX IF NOT EXISTS idx_clean_artist_relations_related
    ON clean.artist_relations (related_artist_id);

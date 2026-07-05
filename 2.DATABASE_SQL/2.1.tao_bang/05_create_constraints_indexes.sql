-- =============================================================
-- 05_create_constraints_indexes.sql
-- HitRadar — indexes và additional constraints
-- Feature 1.2 — Database Architecture
-- Chạy sau 02, 03 — raw tables không cần indexes nặng ở giai đoạn này
-- =============================================================

-- =============================================================
-- INDEXES — Raw Layer (tối giản, chỉ cần lookup khi import)
-- =============================================================
CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_tracks_id
    ON raw.raw_tracks (id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_artists_id
    ON raw.raw_artists (id);

-- =============================================================
-- INDEXES — Clean Layer
-- =============================================================

-- tracks
CREATE INDEX IF NOT EXISTS idx_clean_tracks_release_year
    ON clean.tracks (release_year);

CREATE INDEX IF NOT EXISTS idx_clean_tracks_decade
    ON clean.tracks (decade);

CREATE INDEX IF NOT EXISTS idx_clean_tracks_popularity
    ON clean.tracks (popularity);

CREATE INDEX IF NOT EXISTS idx_clean_tracks_explicit
    ON clean.tracks (explicit);

-- artists
CREATE INDEX IF NOT EXISTS idx_clean_artists_name
    ON clean.artists (name);

-- track_artists: join optimization
CREATE INDEX IF NOT EXISTS idx_clean_track_artists_artist_id
    ON clean.track_artists (artist_id);

CREATE INDEX IF NOT EXISTS idx_clean_track_artists_is_main
    ON clean.track_artists (is_main_artist);

-- artist_genres: join optimization
CREATE INDEX IF NOT EXISTS idx_clean_artist_genres_genre_id
    ON clean.artist_genres (genre_id);

-- genres: lookup by name
CREATE INDEX IF NOT EXISTS idx_clean_genres_normalized
    ON clean.genres (normalized_genre_name);

-- artist_relations: lookup related artists
CREATE INDEX IF NOT EXISTS idx_clean_artist_relations_related
    ON clean.artist_relations (related_artist_id);

-- =============================================================
-- UNIQUE CONSTRAINTS (bổ sung sau CREATE TABLE)
-- =============================================================

-- Đảm bảo không import duplicate track IDs
ALTER TABLE raw.raw_tracks
    ADD CONSTRAINT IF NOT EXISTS uq_raw_tracks_id UNIQUE (id);

-- Đảm bảo không import duplicate artist IDs
ALTER TABLE raw.raw_artists
    ADD CONSTRAINT IF NOT EXISTS uq_raw_artists_id UNIQUE (id);

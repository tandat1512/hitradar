-- =============================================================
-- 03_create_clean_tables.sql
-- HitRadar — clean layer tables
-- Feature 1.2 — Database Architecture
-- Constraints đặt ở clean layer sau khi Feature 1.4 xử lý dữ liệu bẩn
-- =============================================================

-- -------------------------------------------------------------
-- clean.tracks
-- Derived from raw.raw_tracks — sau khi parse, normalize, clean
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clean.tracks (
    track_id            TEXT            NOT NULL,
    name                TEXT,
    -- TARGET: chỉ dùng làm y (label), không dùng làm input feature
    popularity          SMALLINT        NOT NULL
                            CONSTRAINT chk_track_popularity
                            CHECK (popularity BETWEEN 0 AND 100),
    duration_ms         INTEGER         NOT NULL
                            CONSTRAINT chk_duration_ms
                            CHECK (duration_ms > 0),
    duration_min        NUMERIC(8,4),                   -- derived: duration_ms / 60000.0
    explicit            BOOLEAN         NOT NULL,        -- cast từ 0/1
    release_date        DATE,                            -- normalized DATE
    release_year        SMALLINT
                            CONSTRAINT chk_release_year
                            CHECK (release_year BETWEEN 1900 AND 2030),
    release_month       SMALLINT
                            CONSTRAINT chk_release_month
                            CHECK (release_month BETWEEN 1 AND 12),
    decade              SMALLINT,                        -- (release_year / 10) * 10
    -- release_precision: ghi lại độ chi tiết của raw release_date
    -- day   = raw có YYYY-MM-DD
    -- month = raw có YYYY-MM
    -- year  = raw chỉ có YYYY
    -- unknown = không parse được hoặc chưa xác định
    release_precision   TEXT
                            CONSTRAINT chk_release_precision
                            CHECK (release_precision IN ('day', 'month', 'year', 'unknown')),
    danceability        DOUBLE PRECISION
                            CONSTRAINT chk_danceability
                            CHECK (danceability BETWEEN 0 AND 1),
    energy              DOUBLE PRECISION
                            CONSTRAINT chk_energy
                            CHECK (energy BETWEEN 0 AND 1),
    key                 SMALLINT
                            CONSTRAINT chk_key
                            CHECK (key BETWEEN 0 AND 11),
    loudness            DOUBLE PRECISION,
    mode                SMALLINT
                            CONSTRAINT chk_mode
                            CHECK (mode IN (0, 1)),
    speechiness         DOUBLE PRECISION
                            CONSTRAINT chk_speechiness
                            CHECK (speechiness BETWEEN 0 AND 1),
    acousticness        DOUBLE PRECISION
                            CONSTRAINT chk_acousticness
                            CHECK (acousticness BETWEEN 0 AND 1),
    instrumentalness    DOUBLE PRECISION
                            CONSTRAINT chk_instrumentalness
                            CHECK (instrumentalness BETWEEN 0 AND 1),
    liveness            DOUBLE PRECISION
                            CONSTRAINT chk_liveness
                            CHECK (liveness BETWEEN 0 AND 1),
    valence             DOUBLE PRECISION
                            CONSTRAINT chk_valence
                            CHECK (valence BETWEEN 0 AND 1),
    -- tempo = 0 phải được xử lý trước khi insert vào clean layer
    tempo               DOUBLE PRECISION
                            CONSTRAINT chk_tempo
                            CHECK (tempo > 0),
    -- time_signature = 0 phải được xử lý trước khi insert
    time_signature      SMALLINT
                            CONSTRAINT chk_time_signature
                            CHECK (time_signature BETWEEN 1 AND 5),
    _clean_ts           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    PRIMARY KEY (track_id)
);

-- -------------------------------------------------------------
-- clean.artists
-- Derived from raw.raw_artists
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clean.artists (
    artist_id   TEXT        NOT NULL,
    name        TEXT,
    followers   BIGINT
                    CONSTRAINT chk_followers
                    CHECK (followers >= 0),         -- NULL nếu missing
    -- dashboard_only: KHÔNG dùng trực tiếp làm ML feature
    popularity  SMALLINT
                    CONSTRAINT chk_artist_popularity
                    CHECK (popularity BETWEEN 0 AND 100),
    _clean_ts   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (artist_id)
);

-- -------------------------------------------------------------
-- clean.genres
-- Derived từ artists.csv.genres (parse list-string)
-- KHÔNG từ dict_artists.json (đã xác minh là RELATED_ARTIST_GRAPH)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clean.genres (
    genre_id                SERIAL      NOT NULL,
    genre_name              TEXT        NOT NULL,       -- original từ artists.csv
    normalized_genre_name   TEXT,                       -- lowercase, trim
    PRIMARY KEY (genre_id),
    UNIQUE (genre_name)
);

-- -------------------------------------------------------------
-- clean.track_artists
-- Junction table: tracks ↔ artists
-- Derived: explode id_artists từ raw.raw_tracks
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clean.track_artists (
    track_id        TEXT        NOT NULL,
    artist_id       TEXT        NOT NULL,
    artist_order    SMALLINT    NOT NULL DEFAULT 0,     -- 0 = main artist
    is_main_artist  BOOLEAN     NOT NULL DEFAULT FALSE,
    PRIMARY KEY (track_id, artist_id),
    FOREIGN KEY (track_id)  REFERENCES clean.tracks(track_id),
    FOREIGN KEY (artist_id) REFERENCES clean.artists(artist_id)
);

-- -------------------------------------------------------------
-- clean.artist_genres
-- Junction table: artists ↔ genres
-- Source: artists.csv.genres ONLY
-- Không dùng dict_artists.json
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clean.artist_genres (
    artist_id   TEXT    NOT NULL,
    genre_id    INTEGER NOT NULL,
    source      TEXT    NOT NULL DEFAULT 'artists_csv',
    PRIMARY KEY (artist_id, genre_id),
    FOREIGN KEY (artist_id) REFERENCES clean.artists(artist_id),
    FOREIGN KEY (genre_id)  REFERENCES clean.genres(genre_id)
);

-- -------------------------------------------------------------
-- clean.artist_relations
-- Related artist graph từ dict_artists.json
-- CONFIRMED RELATED_ARTIST_GRAPH (overlap 100% với artists.csv.id)
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clean.artist_relations (
    artist_id           TEXT        NOT NULL,
    related_artist_id   TEXT        NOT NULL,
    relation_order      SMALLINT,
    source              TEXT        NOT NULL DEFAULT 'dict_artists_json',
    PRIMARY KEY (artist_id, related_artist_id),
    FOREIGN KEY (artist_id)         REFERENCES clean.artists(artist_id),
    FOREIGN KEY (related_artist_id) REFERENCES clean.artists(artist_id)
);

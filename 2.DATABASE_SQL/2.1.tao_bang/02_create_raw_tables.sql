-- =============================================================
-- 02_create_raw_tables.sql
-- HitRadar — raw layer tables
-- Feature 1.2 — Database Architecture
-- Không có constraints nghiêm ngặt — raw layer giữ dữ liệu nguyên bản
-- =============================================================

-- -------------------------------------------------------------
-- raw.raw_tracks
-- Source: 1.DỮ_LIỆU/1.1.raw/tracks.csv
-- 586,672 rows · 20 columns
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw.raw_tracks (
    id                  TEXT NOT NULL,  -- Spotify track ID (candidate PK)
    name                TEXT,           -- 71 missing (0.01%)
    popularity          SMALLINT,       -- 0–100; nhiều giá trị = 0
    duration_ms         INTEGER,        -- min 3,344 · max 5,621,218
    explicit            SMALLINT,       -- 0/1 từ CSV
    artists             TEXT,           -- list-string ['Name A', 'Name B']
    id_artists          TEXT,           -- list-string ['id1', 'id2']
    release_date        TEXT,           -- mixed: YYYY-MM-DD / YYYY-MM / YYYY
    danceability        DOUBLE PRECISION,
    energy              DOUBLE PRECISION,
    key                 SMALLINT,       -- 0–11
    loudness            DOUBLE PRECISION,
    mode                SMALLINT,       -- 0/1
    speechiness         DOUBLE PRECISION,
    acousticness        DOUBLE PRECISION,
    instrumentalness    DOUBLE PRECISION,
    liveness            DOUBLE PRECISION,
    valence             DOUBLE PRECISION,
    tempo               DOUBLE PRECISION, -- 328 giá trị = 0
    time_signature      SMALLINT,         -- 337 giá trị = 0
    _import_ts          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -------------------------------------------------------------
-- raw.raw_artists
-- Source: 1.DỮ_LIỆU/1.1.raw/artists.csv
-- 1,162,095 rows · 5 columns
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw.raw_artists (
    id          TEXT NOT NULL,      -- Spotify artist ID (candidate PK)
    followers   DOUBLE PRECISION,   -- 11 missing; DOUBLE vì NaN trong CSV
    genres      TEXT,               -- list-string ['pop', 'rock']
    name        TEXT,               -- 3 missing (0.0003%)
    popularity  SMALLINT,           -- 0–100; dashboard_only; leakage risk ML
    _import_ts  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- -------------------------------------------------------------
-- raw.raw_artist_json
-- Source: 1.DỮ_LIỆU/1.1.raw/dict_artists.json
-- 573,856 keys
-- CONFIRMED: RELATED_ARTIST_GRAPH (overlap 100% với artists.csv.id)
-- Không phải genre source.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw.raw_artist_json (
    artist_id       TEXT NOT NULL,          -- key từ dict_artists.json
    raw_values      JSONB,                  -- original list as JSONB array
    value_count     INTEGER,                -- số phần tử trong list
    semantic_status TEXT NOT NULL DEFAULT 'RELATED_ARTIST_GRAPH',
    source_file     TEXT NOT NULL DEFAULT 'dict_artists.json',
    _import_ts      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (artist_id)
);

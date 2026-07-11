# DATABASE SCHEMA — HITRADAR PRO EPIC 1

**Project:** HitRadar Pro  
**EPIC:** 1 — Data Foundation & Data Understanding  
**Owner:** Đạt  
**Status:** Final (Feature 1.9)  
**Last updated:** 2026-07-11  
**Sources:** Feature 1.2 DDL, Feature 1.6 views, Feature 1.8 handoff

---

## 1. Purpose

Mô tả kiến trúc database PostgreSQL 3-layer (raw / clean / analytics) + ML-ready handoff view cho EPIC 1. Schema này là căn cứ cho import (F1.3), cleaning (F1.4), quality gates (F1.5), analytics (F1.6), EDA (F1.7), và ML handoff (F1.8).

---

## 2. Schema Overview

```
tracks.csv ──────────────┐
artists.csv ─────────────┼──► RAW (raw.*)
dict_artists.json ───────┘         │
                                   │ Feature 1.4: parse, normalize, FK
                                   ▼
                            CLEAN (clean.*)
                                   │
                                   │ Feature 1.6: aggregate, join, derive
                                   ▼
                         ANALYTICS (analytics.*)
                                   │
                                   │ Feature 1.8: ML-safe projection
                                   ▼
                    ML-READY HANDOFF (vw_ml_ready_dataset)
                                   │
                                   ▼
                    Export: CSV / Parquet → EPIC 2
```

| Layer | Schema | Objects | Mutability |
|-------|--------|---------|------------|
| Raw | `raw` | 3 tables | Import only (F1.3) |
| Clean | `clean` | 6 tables | Cleaning script (F1.4) |
| Analytics | `analytics` | 11 views | SQL CREATE OR REPLACE (F1.6, F1.8) |

---

## 3. Raw Schema

### `raw.raw_tracks` — 586,672 rows

| Column | Type | Notes |
|--------|------|-------|
| `id` | TEXT | PK candidate — Spotify track ID |
| `name` | TEXT | 71 NULL |
| `popularity` | SMALLINT | 0–100 |
| `duration_ms` | INTEGER | |
| `explicit` | SMALLINT | 0/1 |
| `artists`, `id_artists` | TEXT | List-strings |
| `release_date` | TEXT | Mixed formats |
| Audio features (12 cols) | DOUBLE/SMALLINT | Includes tempo, time_signature |
| `_import_ts` | TIMESTAMPTZ | Import metadata |

**Source:** `tracks.csv`

### `raw.raw_artists` — 1,162,095 rows

| Column | Type | Notes |
|--------|------|-------|
| `id` | TEXT | PK candidate |
| `followers` | DOUBLE PRECISION | 11 NULL |
| `genres` | TEXT | List-string — genre source |
| `name` | TEXT | |
| `popularity` | SMALLINT | Dashboard only |
| `_import_ts` | TIMESTAMPTZ | |

**Source:** `artists.csv`

### `raw.raw_artist_json` — 573,856 rows

| Column | Type | Notes |
|--------|------|-------|
| `artist_id` | TEXT | JSON key |
| `raw_values` | JSONB | Related artist ID list |
| `value_count` | INTEGER | |
| `semantic_status` | TEXT | `RELATED_ARTIST_GRAPH` |
| `source_file` | TEXT | `dict_artists.json` |
| `_import_ts` | TIMESTAMPTZ | |

**Source:** `dict_artists.json` — **not genre source**

---

## 4. Clean Schema

| Table | PK | Rows | Purpose |
|-------|-----|------|---------|
| `clean.tracks` | `track_id` | 586,672 | Track fact — target, audio, release |
| `clean.artists` | `artist_id` | 1,162,095 | Artist dimension |
| `clean.genres` | `genre_id` (SERIAL) | 5,366 | Genre vocabulary |
| `clean.track_artists` | `(track_id, artist_id)` | 730,946 | Track-artist M:N |
| `clean.artist_genres` | `(artist_id, genre_id)` | 468,680 | Artist-genre M:N |
| `clean.artist_relations` | `(artist_id, related_artist_id)` | 8,864,471 | Related artist graph |

### Key `clean.tracks` columns

`popularity` (target), `duration_min`, `explicit` (BOOLEAN), `release_year` (observed 1921–2021), `release_month`, `decade`, `release_precision`, audio features, `tempo` (328 NULL), `time_signature` (337 NULL).

### Constraints (clean layer)

- Audio features ∈ [0, 1]
- `popularity` ∈ [0, 100]
- `duration_ms > 0`
- `tempo > 0` OR NULL
- `time_signature` ∈ [1, 5] OR NULL
- `release_precision` ∈ {day, month, year, unknown}

---

## 5. Analytics Schema

### Feature 1.6 — 10 analytics views

| View | Rows | Source | Use |
|------|------|--------|-----|
| `vw_tracks_overview` | 586,672 | `clean.tracks` | EDA, dashboard |
| `vw_tracks_by_decade` | 12 | `clean.tracks` | Decade trends |
| `vw_audio_trends` | 101 | `clean.tracks` | Audio by year |
| `vw_popularity_stats` | 5 | `clean.tracks` | Target distribution |
| `vw_top_artists` | 81,776 | artists + track_artists + tracks | Artist analytics |
| `vw_genre_trends` | 19,103 | genres + joins | Genre trends |
| `vw_explicit_by_decade` | 12 | `clean.tracks` | Explicit ratio |
| `vw_duration_trends` | 101 | `clean.tracks` | Duration trends |
| `vw_data_quality_report` | 16 | Live metrics | Quality monitoring |
| `vw_ml_training_dataset` | 586,672 | `clean.tracks` | ML candidate base |

### Feature 1.8 — ML-ready handoff

| View | Rows | Columns | Source |
|------|------|---------|--------|
| `vw_ml_ready_dataset` | 586,672 | 20 | `vw_ml_training_dataset` |

**20 columns:** track_id, target_popularity, duration_min, explicit, release_year, release_month, decade, release_precision, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature.

**No leakage columns.** No imputed/scaled/encoded columns. No train/test split column.

---

## 6. Relationship Map

```
tracks.csv ──► raw.raw_tracks ──► clean.tracks ──┬──► analytics views
                                                  │
artists.csv ──► raw.raw_artists ──► clean.artists ┼──► clean.track_artists ◄──┐
                     │                            │         │                  │
                     ├──► clean.artist_genres ────┼──► clean.genres           │
                     │                            │                            │
dict_artists.json ──► raw.raw_artist_json        └──► clean.artist_relations │
                                                  │                            │
                                                  └──► vw_ml_training_dataset  │
                                                            │                  │
                                                            ▼                  │
                                                   vw_ml_ready_dataset ───────┘
                                                            │
                                                            ▼
                                              5.DATA/processed/ml_ready_dataset.*
```

**Join paths:**
- tracks → track_artists → artists
- artists → artist_genres → genres
- artists → artist_relations → artists (self-join)
- clean.tracks → analytics views → vw_ml_training_dataset → vw_ml_ready_dataset

---

## 7. Index Summary

**Feature 1.6 created 20 indexes** (11 new + 9 pre-existing IF NOT EXISTS).

| Category | Indexes |
|----------|---------|
| **Release/time** | `idx_clean_tracks_release_year`, `release_precision`, `decade`, `year_popularity`, `decade_explicit` |
| **Target/features** | `idx_clean_tracks_popularity`, `explicit`, `duration_ms`, `loudness` |
| **Join keys** | `idx_clean_track_artists_track_id`, `track_artists_artist_id`, `artist_genres_artist_id`, `artist_genres_genre_id`, `artist_relations_artist_id`, `artist_relations_related` |
| **Lookup** | `idx_clean_artists_name`, `popularity`, `followers`, `idx_clean_genres_normalized`, `genre_name` |

---

## 8. Important Design Decisions

| Decision | Rationale |
|----------|-----------|
| Không dùng old 5 CSV aggregate files | Scope lock F1.0 — actual dataset = tracks + artists + dict_artists |
| `dict_artists.json` = related artist graph | Semantic check F1.2 — 100% overlap with artist IDs |
| Genre từ `artists.csv.genres` only | dict_artists không chứa genre names |
| Clean layer giữ outliers | short=26, long=83, loudness>0=219 — flag/report, không drop |
| Analytics views read-only | No INSERT/UPDATE/DELETE on views |
| `vw_ml_ready_dataset` no leakage | No artists.popularity, no aggregates, no split columns |
| EPIC 1 không fit scaler/imputer | Preprocessing deferred to EPIC 2 train-only fit |
| `target_popularity` isolated as label | Renamed from popularity in ML views |

---

*Feature 1.9 — Documentation & Epic Review | HitRadar Pro*

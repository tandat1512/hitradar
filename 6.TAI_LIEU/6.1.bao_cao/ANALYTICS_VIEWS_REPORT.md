# ANALYTICS VIEWS REPORT — FEATURE 1.6

## 1. Purpose

Feature 1.6 tạo analytics views từ clean layer (Feature 1.4) trên schema `analytics`, phục vụ:
- **EDA & Data Understanding** (Feature 1.7)
- **Dashboard/BI** queries
- **ML Handoff** (Feature 1.8 / EPIC 2)

Script SQL: `2.DATABASE_SQL/2.4.views/01_create_analytics_views.sql`
Indexes:    `2.DATABASE_SQL/2.5.indexes/01_create_indexes.sql`

---

## 2. Source Tables

| Table | Rows |
|-------|------|
| `clean.tracks` | 586,672 |
| `clean.artists` | 1,162,095 |
| `clean.genres` | 5,366 |
| `clean.track_artists` | 730,946 |
| `clean.artist_genres` | 468,680 |
| `clean.artist_relations` | 8,864,471 |

---

## 3. Views Created

| View | Purpose | Source Tables | Row Behavior | Main Use Case |
|------|---------|--------------|--------------|--------------|
| `vw_tracks_overview` | Full track snapshot | `clean.tracks` | = clean.tracks (586,672) | EDA, dashboard |
| `vw_tracks_by_decade` | Aggregate per decade | `clean.tracks` | 1 row/decade (12 decades) | Trend analysis |
| `vw_audio_trends` | Audio features by year | `clean.tracks` | 1 row/year (101 years) | Audio evolution |
| `vw_popularity_stats` | Popularity buckets | `clean.tracks` | 5 bucket rows | Distribution |
| `vw_top_artists` | Artist ranking | `clean.artists`, `clean.track_artists`, `clean.tracks` | 81,776 artists with tracks | Artist analytics |
| `vw_genre_trends` | Genre per decade | `clean.genres`, `clean.artist_genres`, `clean.track_artists`, `clean.tracks` | 19,103 genre-decade rows | Genre analysis |
| `vw_explicit_by_decade` | Explicit ratio | `clean.tracks` | 1 row/decade | Content analysis |
| `vw_duration_trends` | Duration by year | `clean.tracks` | 1 row/year | Duration trends |
| `vw_data_quality_report` | Quality metrics | Live DB + literals | 16 metric rows | Quality monitoring |
| `vw_ml_training_dataset` | ML candidate | `clean.tracks` | = clean.tracks (586,672) | ML handoff (EPIC 2) |

---

## 4. View Details

### vw_tracks_overview
- **Purpose:** Complete track feature set for EDA and dashboard display.
- **Key columns:** All 23 track attributes including `release_date`, `release_precision`, all 7 audio features, `key`, `mode`, `time_signature`.
- **Important logic:** Simple projection — no joins, no grouping. Row count = clean.tracks.
- **Known warnings:** 71 tracks with `name IS NULL` (retained by F1.4 rule).

### vw_tracks_by_decade
- **Purpose:** Decade-level statistical summary.
- **Key columns:** `track_count`, `avg_popularity`, `median_popularity`, `avg_danceability/energy/valence/tempo`, `explicit_count`, `explicit_ratio`.
- **Important logic:** `decade IS NULL` rows excluded from aggregation. `NULLIF` prevents division-by-zero in `explicit_ratio`. All ROUND uses `::numeric` cast.
- **Known warnings:** 12 distinct decades covered.

### vw_audio_trends
- **Purpose:** Year-over-year audio feature evolution.
- **Key columns:** `avg_danceability`, `avg_energy`, `avg_speechiness`, `avg_acousticness`, `avg_instrumentalness`, `avg_liveness`, `avg_valence`, `avg_tempo`, `avg_loudness`.
- **Important logic:** `release_year IS NOT NULL` filter. NULL audio values are skipped by AVG automatically.

### vw_popularity_stats
- **Purpose:** Popularity bucket distribution.
- **Key columns:** `popularity_bucket` (0–20, 21–40, 41–60, 61–80, 81–100), `track_count`, `min/max/avg/median_popularity`.
- **Important logic:** `popularity` must be in [0,100] (validated in F1.5 G04).
- **ML note:** `clean.tracks.popularity` is the **target variable** — NOT an input feature.

### vw_top_artists
- **Purpose:** Rank artists by track count and average track popularity.
- **Key columns:** `artist_id`, `artist_name`, `track_count`, `avg_track_popularity`, `max_track_popularity`, `followers`, `artist_popularity_dashboard_only`.
- **Important logic:** Only artists with at least one track in `clean.track_artists` are included (81,776 of 1,162,095 artists = 7.0% have tracks).
- **Known warnings:** `artist_popularity_dashboard_only` = `clean.artists.popularity` — labeled explicitly to prevent misuse as ML feature.

### vw_genre_trends
- **Purpose:** Genre performance across decades.
- **Key columns:** `genre_id`, `genre_name`, `normalized_genre_name`, `decade`, `track_count`, `avg_popularity`, `avg_danceability`, `avg_energy`, `avg_valence`, `avg_duration_min`.
- **Important logic (critical):** Uses a CTE `track_genres` with `SELECT DISTINCT (track_id, genre_id, decade, ...)` to eliminate duplicate-weighting. Without DISTINCT, a track with 3 artists sharing genre "pop" would be counted 3×. After dedup, `COUNT(DISTINCT track_id)` confirms.

### vw_explicit_by_decade
- **Purpose:** Explicit content ratio trend by decade.
- **Key columns:** `decade`, `track_count`, `explicit_count`, `non_explicit_count`, `explicit_ratio`.
- **Important logic:** `NULLIF(COUNT(*), 0)` prevents division-by-zero.

### vw_duration_trends
- **Purpose:** Duration statistics by release year, with outlier flagging.
- **Key columns:** `release_year`, `decade`, `avg/median/min/max_duration_min`, `short_track_count`, `long_track_count`.
- **Important logic:** Outliers (short < 10s, long > 60min) are FLAGGED not removed, per F1.4 rule.

### vw_data_quality_report
- **Purpose:** Expose Feature 1.5 quality metrics as a queryable view for dashboards.
- **Key columns:** `metric_name`, `metric_value`, `severity`, `note`.
- **Important logic:** Live DB counts for most metrics. Literals from F1.4 cleaning log for `track_artists_skipped` (26,224) and `track_artists_coverage_pct` (96.54) — cannot be recomputed without re-running the cleaning script.
- **Metrics (16):** All 5 required DQ metrics present; `data_quality_status = PASS_WITH_WARNINGS`.

### vw_ml_training_dataset
- **Purpose:** ML candidate view for EPIC 2 — Feature Engineering & Modeling.
- **Key columns:** `track_id`, `target_popularity`, `duration_min`, `explicit`, `release_year`, `release_month`, `decade`, `release_precision`, 7 audio features, `key`, `loudness`, `mode`, `time_signature`.
- **Row count:** 586,672 (= clean.tracks, no rows dropped).
- **ML safety verified:** No leakage columns. See section 5.

---

## 5. ML-safe View Notes

| Rule | Status |
|------|--------|
| `target_popularity` = `clean.tracks.popularity` (label) | Confirmed |
| `target_popularity` NOT used as input feature | Confirmed — column is labeled |
| `artists.popularity` NOT in ML view | Confirmed — absent from `vw_ml_training_dataset` |
| Aggregate popularity (by artist/genre) NOT in ML view | Confirmed — none present |
| Train/test split | NOT done — EPIC 2 scope |
| Label encoding | NOT done — EPIC 2 scope |
| NULL imputation | NOT done — EPIC 2 scope |

**Validated columns in `vw_ml_training_dataset` (20 columns):**
`acousticness`, `danceability`, `decade`, `duration_min`, `energy`, `explicit`,
`instrumentalness`, `key`, `liveness`, `loudness`, `mode`, `release_month`,
`release_precision`, `release_year`, `speechiness`, `target_popularity`, `tempo`,
`time_signature`, `track_id`, `valence`

---

## 6. Index Summary

| Index | Table | Column(s) | Status |
|-------|-------|-----------|--------|
| `idx_clean_tracks_release_year` | `clean.tracks` | `release_year` | Pre-existing |
| `idx_clean_tracks_decade` | `clean.tracks` | `decade` | Pre-existing |
| `idx_clean_tracks_popularity` | `clean.tracks` | `popularity` | Pre-existing |
| `idx_clean_tracks_explicit` | `clean.tracks` | `explicit` | Pre-existing |
| `idx_clean_tracks_release_precision` | `clean.tracks` | `release_precision` | Created |
| `idx_clean_tracks_year_popularity` | `clean.tracks` | `(release_year, popularity)` | Created |
| `idx_clean_tracks_decade_explicit` | `clean.tracks` | `(decade, explicit)` | Created |
| `idx_clean_tracks_duration_ms` | `clean.tracks` | `duration_ms` | Created |
| `idx_clean_tracks_loudness` | `clean.tracks` | `loudness` | Created |
| `idx_clean_track_artists_track_id` | `clean.track_artists` | `track_id` | Created |
| `idx_clean_track_artists_artist_id` | `clean.track_artists` | `artist_id` | Pre-existing |
| `idx_clean_artists_name` | `clean.artists` | `name` | Pre-existing |
| `idx_clean_artists_popularity` | `clean.artists` | `popularity` | Created |
| `idx_clean_artists_followers` | `clean.artists` | `followers` | Created |
| `idx_clean_genres_genre_name` | `clean.genres` | `genre_name` | Created |
| `idx_clean_genres_normalized` | `clean.genres` | `normalized_genre_name` | Pre-existing |
| `idx_clean_artist_genres_artist_id` | `clean.artist_genres` | `artist_id` | Created |
| `idx_clean_artist_genres_genre_id` | `clean.artist_genres` | `genre_id` | Pre-existing |
| `idx_clean_artist_relations_artist_id` | `clean.artist_relations` | `artist_id` | Created |
| `idx_clean_artist_relations_related` | `clean.artist_relations` | `related_artist_id` | Pre-existing |

---

## 7. EXPLAIN ANALYZE Summary

| View | Execution Time | Status |
|------|---------------|--------|
| `vw_tracks_by_decade` | ~314 ms | PASS |
| `vw_top_artists` (LIMIT 100) | ~2,264 ms | PASS |
| `vw_genre_trends` (LIMIT 100) | ~585 ms | PASS |
| `vw_ml_training_dataset` (LIMIT 100) | ~0.1 ms | PASS |

> `vw_top_artists` is the heaviest view (~2.3s) due to a 3-table JOIN + GROUP BY over 730,946 rows.
> For dashboard use, consider materialization or pagination. Threshold for WARNING: > 10,000 ms.

---

## 8. Carry-Forward Warnings from Feature 1.5

| Warning | Value | Action |
|---------|-------|--------|
| Duration short (<10s) | 26 tracks | `vw_duration_trends.short_track_count` |
| Duration long (>60min) | 83 tracks | `vw_duration_trends.long_track_count` |
| Loudness > 0 dB | 219 tracks | `vw_data_quality_report` |
| track_artists coverage | 96.54% (skipped 26,224) | `vw_data_quality_report` |
| artist_relations diff | 1 pair (ON CONFLICT) | `vw_data_quality_report` |

---

## 9. Status

**PASS**

All 10 views created, all validation checks pass, ML view is leakage-free.
Sẵn sàng chuyển sang Feature 1.7 — EDA & Data Understanding Notebooks.

# ANALYTICS VIEW VALIDATION REPORT — FEATURE 1.6

## 1. Metadata

| Field | Value |
|-------|-------|
| Feature | 1.6 — Analytics Views & Indexes |
| Owner | Đạt |
| Database | `hitradar` @ `localhost:5432` |
| User | `postgres` |
| Date/Time | 2026-07-08 05:58 UTC |
| Script | `9.SCRIPTS/validate_analytics_views.py` |
| **Overall** | **PASS** |

---

## 2. View Existence (10 views required)

| View | Exists | Status |
|------|--------|--------|
| `analytics.vw_tracks_overview` | ✓ | **PASS** |
| `analytics.vw_tracks_by_decade` | ✓ | **PASS** |
| `analytics.vw_audio_trends` | ✓ | **PASS** |
| `analytics.vw_popularity_stats` | ✓ | **PASS** |
| `analytics.vw_top_artists` | ✓ | **PASS** |
| `analytics.vw_genre_trends` | ✓ | **PASS** |
| `analytics.vw_explicit_by_decade` | ✓ | **PASS** |
| `analytics.vw_duration_trends` | ✓ | **PASS** |
| `analytics.vw_data_quality_report` | ✓ | **PASS** |
| `analytics.vw_ml_training_dataset` | ✓ | **PASS** |

---

## 3. Query Smoke Test

| View | Result | Status |
|------|--------|--------|
| `analytics.vw_tracks_overview` | 5 rows returned, 23 columns | **PASS** |
| `analytics.vw_tracks_by_decade` | 5 rows returned, 12 columns | **PASS** |
| `analytics.vw_audio_trends` | 5 rows returned, 11 columns | **PASS** |
| `analytics.vw_popularity_stats` | 5 rows returned, 6 columns | **PASS** |
| `analytics.vw_top_artists` | 5 rows returned, 7 columns | **PASS** |
| `analytics.vw_genre_trends` | 5 rows returned, 10 columns | **PASS** |
| `analytics.vw_explicit_by_decade` | 5 rows returned, 5 columns | **PASS** |
| `analytics.vw_duration_trends` | 5 rows returned, 9 columns | **PASS** |
| `analytics.vw_data_quality_report` | 5 rows returned, 4 columns | **PASS** |
| `analytics.vw_ml_training_dataset` | 5 rows returned, 20 columns | **PASS** |

---

## 4. Row Count Sanity

| View | Count | Status |
|------|-------|--------|
| `analytics.vw_tracks_overview` | 586,672 = 586,672 | **PASS** |
| `analytics.vw_ml_training_dataset` | 586,672 = 586,672 | **PASS** |
| `analytics.vw_tracks_by_decade` | 12 rows | **PASS** |
| `analytics.vw_audio_trends` | 101 rows | **PASS** |
| `analytics.vw_top_artists` | 81,776 rows | **PASS** |
| `analytics.vw_genre_trends` | 19,103 rows | **PASS** |
| `analytics.vw_data_quality_report` | 16 rows | **PASS** |

---

## 5. ML-safe Column Audit — vw_ml_training_dataset

| Check | Result | Status |
|-------|--------|--------|
| `target_popularity` present | Yes | **PASS** |
| Leakage columns found | None | **PASS** |
| **Overall** | | **PASS** |

**All columns in view:**
`acousticness`, `danceability`, `decade`, `duration_min`, `energy`, `explicit`, `instrumentalness`, `key`, `liveness`, `loudness`, `mode`, `release_month`, `release_precision`, `release_year`, `speechiness`, `target_popularity`, `tempo`, `time_signature`, `track_id`, `valence`

---

## 6. Genre Duplicate-Weighting Confirmation — vw_genre_trends

| Check | Result | Status |
|-------|--------|--------|
| CTE DISTINCT confirmed in SQL source | Yes | **PASS** |
| Row count > 0 | 19,103 | **PASS** |
| **Overall** | | **PASS** |

> SQL uses `WITH track_genres AS (SELECT DISTINCT t.track_id, g.genre_id, ...)` to prevent
> duplicate-weighting when a track has multiple artists sharing the same genre.

---

## 7. Data Quality Carry-Forward — vw_data_quality_report

| Metric | Value | Severity |
|--------|-------|---------|
| `artist_relations_diff` | 1 | WARNING |
| `artists_followers_null_count` | 11 | INFO |
| `clean_artist_genres_row_count` | 468680 | INFO |
| `clean_artist_relations_row_count` | 8864471 | INFO |
| `clean_artists_row_count` | 1162095 | INFO |
| `clean_genres_row_count` | 5366 | INFO |
| `clean_track_artists_row_count` | 730946 | INFO |
| `clean_tracks_row_count` | 586672 | INFO |
| `data_quality_status` | PASS_WITH_WARNINGS | WARNING |
| `duration_long_count` | 83 | WARNING |
| `duration_short_count` | 26 | WARNING |
| `genre_join_coverage_pct` | 100.00 | PASS |
| `loudness_positive_count` | 219 | WARNING |
| `track_artists_coverage_pct` | 96.54 | WARNING |
| `track_artists_skipped` | 26224 | WARNING |
| `tracks_name_null_count` | 71 | INFO |

Missing required metrics: None

**Overall:** **PASS**

---

## 8. EXPLAIN ANALYZE Summary

| View | Timing / Note | Status |
|------|--------------|--------|
| `vw_tracks_by_decade` | 315 ms total | Execution Time: 313.801 ms | **PASS** |
| `vw_top_artists` | 2266 ms total | Execution Time: 2264.360 ms | **PASS** |
| `vw_genre_trends` | 587 ms total | Execution Time: 585.335 ms | **PASS** |
| `vw_ml_training_dataset` | 0 ms total | Execution Time: 0.126 ms | **PASS** |

> Threshold: > 10,000 ms = WARNING. Views on large tables without filters may be slow.

---

## 9. Overall Decision

**PASS**

All checks PASS. Proceed to Feature 1.7.

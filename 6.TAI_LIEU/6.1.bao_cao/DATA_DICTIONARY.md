# DATA DICTIONARY — HITRADAR PRO EPIC 1

**Project:** HitRadar Pro  
**EPIC:** 1 — Data Foundation & Data Understanding  
**Owner:** Đạt  
**Status:** Final (Feature 1.9)  
**Last updated:** 2026-07-11

---

## 1. Purpose

Tài liệu chính thức mô tả toàn bộ dữ liệu EPIC 1 — từ raw files đến ML-ready handoff. Dùng để:

- Onboard thành viên mới và reviewer Sprint Review
- Tra cứu ý nghĩa cột, layer, và quan hệ giữa các bảng/view
- Xác nhận ML-safe boundaries trước khi vào EPIC 2
- Làm căn cứ audit khi có thay đổi schema hoặc pipeline

**Nguồn evidence:** Feature 1.1–1.8 completion reports, validation reports, EDA_INSIGHTS_REPORT.md

---

## 2. Dataset Sources

| File | Path | Rows/Keys | Role |
|------|------|-----------|------|
| `tracks.csv` | `1.DỮ_LIỆU/1.1.raw/tracks.csv` | 586,672 | **Track-level data** — audio features, popularity, release date |
| `artists.csv` | `1.DỮ_LIỆU/1.1.raw/artists.csv` | 1,162,095 | **Artist-level data** — name, followers, popularity, genres |
| `dict_artists.json` | `1.DỮ_LIỆU/1.1.raw/dict_artists.json` | 573,856 keys | **Related artist graph** — KHÔNG phải genre source |

### Important clarifications

- **tracks.csv** là nguồn fact chính cho ML baseline (mỗi row = 1 track).
- **artists.csv** cung cấp metadata artist và **genres** (list-string).
- **dict_artists.json** đã xác minh (Feature 1.2): `artist_id → [related_artist_ids]`. **Không dùng làm nguồn genre.**
- **Genres** được parse từ `artists.csv.genres` only → `clean.genres`, `clean.artist_genres`.

> EPIC 1 **không** dùng old 5 CSV aggregate files làm raw source (scope lock Feature 1.0).

---

## 3. Raw Layer Dictionary

### `raw.raw_tracks`

| Property | Value |
|----------|-------|
| **Purpose** | Import nguyên bản tracks.csv — không transform |
| **Source file** | `tracks.csv` |
| **Row count** | 586,672 |
| **Primary key** | `id` (TEXT, unique) |

**Key columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | TEXT | Spotify track ID |
| `name` | TEXT | 71 NULL |
| `popularity` | SMALLINT | 0–100 — becomes ML target in clean layer |
| `duration_ms` | INTEGER | Always > 0 in clean |
| `explicit` | SMALLINT | 0/1 in raw |
| `artists`, `id_artists` | TEXT | Python list-strings — parse in F1.4 |
| `release_date` | TEXT | Mixed: YYYY-MM-DD / YYYY-MM / YYYY |
| Audio features | DOUBLE/SMALLINT | danceability…time_signature |
| `tempo` | DOUBLE | 328 values = 0 in raw |
| `time_signature` | SMALLINT | 337 values = 0 in raw |

**Known issues:** list-string fields need parsing; release_date mixed formats; tempo/time_signature sentinel zeros.

---

### `raw.raw_artists`

| Property | Value |
|----------|-------|
| **Purpose** | Import nguyên bản artists.csv |
| **Source file** | `artists.csv` |
| **Row count** | 1,162,095 |
| **Primary key** | `id` (TEXT, unique) |

**Key columns:**

| Column | Type | Notes |
|--------|------|-------|
| `id` | TEXT | Spotify artist ID |
| `name` | TEXT | 3 NULL in raw; 0 NULL in clean |
| `followers` | DOUBLE | 11 NULL — cast to BIGINT in clean |
| `genres` | TEXT | List-string — **sole genre source** |
| `popularity` | SMALLINT | Dashboard only — leakage risk as ML input |

**Known issues:** `popularity` leakage risk; `genres` requires parsing; extreme followers skew.

---

### `raw.raw_artist_json`

| Property | Value |
|----------|-------|
| **Purpose** | Store related artist graph from dict_artists.json |
| **Source file** | `dict_artists.json` |
| **Row count** | 573,856 keys |
| **Semantic** | `RELATED_ARTIST_GRAPH` (confirmed Feature 1.2) |

**Key columns:**

| Column | Type | Notes |
|--------|------|-------|
| `artist_id` | TEXT | Key from JSON |
| `raw_values` | JSONB | Original list of related artist IDs |
| `value_count` | INTEGER | List length; 126,904 empty lists (22.11%) |
| `semantic_status` | TEXT | `RELATED_ARTIST_GRAPH` |

**Known issues:** 22.11% empty lists; not a genre source.

---

## 4. Clean Layer Dictionary

### `clean.tracks`

| Property | Value |
|----------|-------|
| **Purpose** | Normalized track fact table |
| **PK** | `track_id` |
| **Row count** | 586,672 (= raw) |
| **Relationships** | Parent of `track_artists`; source for analytics views |

**Important columns:** `popularity` (target), `duration_min`, `explicit` (BOOLEAN), `release_year` (observed 1921–2021), `release_month`, `decade`, `release_precision`, 12 audio features.

**Cleaning notes:** tempo=0→NULL (328); time_signature=0→NULL (337); duration outliers kept (short=26, long=83); name NULL=71 retained.

---

### `clean.artists`

| Property | Value |
|----------|-------|
| **Purpose** | Normalized artist dimension |
| **PK** | `artist_id` |
| **Row count** | 1,162,095 (= raw) |

**Important columns:** `name`, `followers` (11 NULL), `popularity` (dashboard only).

**Cleaning notes:** followers cast FLOAT→BIGINT; negative→NULL.

---

### `clean.genres`

| Property | Value |
|----------|-------|
| **Purpose** | Unique genre vocabulary |
| **PK** | `genre_id` (SERIAL) |
| **Row count** | 5,366 |

**Important columns:** `genre_name`, `normalized_genre_name` (lower/strip/collapse spaces).

**Cleaning notes:** Parsed from `artists.csv.genres` only.

---

### `clean.track_artists`

| Property | Value |
|----------|-------|
| **Purpose** | Many-to-many track ↔ artist |
| **PK** | `(track_id, artist_id)` |
| **Row count** | 730,946 |
| **Coverage** | 96.54% (26,224 FK-skipped) |

**Important columns:** `artist_order`, `is_main_artist`.

**Cleaning notes:** FK-validated pairs only; unknown artist IDs skipped.

---

### `clean.artist_genres`

| Property | Value |
|----------|-------|
| **Purpose** | Many-to-many artist ↔ genre |
| **PK** | `(artist_id, genre_id)` |
| **Row count** | 468,680 |
| **Source** | `artists_csv` only |

---

### `clean.artist_relations`

| Property | Value |
|----------|-------|
| **Purpose** | Related artist graph edges |
| **PK** | `(artist_id, related_artist_id)` |
| **Row count** | 8,864,471 |
| **Source** | `dict_artists_json` |

**Known issues:** 1-row diff vs raw total assignments (EDA carry-forward) — not a blocker.

---

## 5. Analytics Layer Dictionary

| View | Rows | Purpose | Source | Use case | Warning |
|------|------|---------|--------|----------|---------|
| `vw_tracks_overview` | 586,672 | Full track snapshot | `clean.tracks` | EDA, dashboard | name NULL=71 |
| `vw_tracks_by_decade` | 12 | Decade aggregates | `clean.tracks` | Trend analysis | — |
| `vw_audio_trends` | 101 | Audio by year | `clean.tracks` | Audio evolution | release_year NOT NULL filter |
| `vw_popularity_stats` | 5 | Popularity buckets | `clean.tracks` | Target distribution | popularity = label |
| `vw_top_artists` | 81,776 | Artist ranking | artists + track_artists + tracks | Artist analytics | `artist_popularity_dashboard_only` — no ML input |
| `vw_genre_trends` | 19,103 | Genre per decade | genres + artist_genres + track_artists + tracks | Genre analysis | CTE DISTINCT prevents double-count |
| `vw_explicit_by_decade` | 12 | Explicit ratio | `clean.tracks` | Content analysis | — |
| `vw_duration_trends` | 101 | Duration by year | `clean.tracks` | Duration trends | short/long flags |
| `vw_data_quality_report` | 16 | Quality metrics | Live DB + literals | Quality monitoring | Carry-forward from F1.5 |
| `vw_ml_training_dataset` | 586,672 | ML candidate | `clean.tracks` | ML handoff base | `target_popularity` aliased; 0 leakage cols |

---

## 6. ML-Ready Dataset Dictionary

### `analytics.vw_ml_ready_dataset` (Feature 1.8)

| Property | Value |
|----------|-------|
| **Source** | `analytics.vw_ml_training_dataset` (read-only projection) |
| **Rows** | 586,672 |
| **Columns** | 20 |
| **Label** | `target_popularity` |
| **Non-training** | `track_id` (identifier) |
| **Allowed input features** | 18 baseline columns |

**20 columns:**

| Column | Role |
|--------|------|
| `track_id` | identifier — do NOT train |
| `target_popularity` | label — do NOT train |
| `duration_min`, `explicit`, `release_year`, `release_month`, `decade`, `release_precision` | input |
| `danceability`, `energy`, `key`, `loudness`, `mode`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`, `time_signature` | input |

**Exports:** `5.DATA/processed/ml_ready_dataset.csv`, `ml_ready_dataset.parquet`

**Validation:** PASS_WITH_WARNINGS (ML_READY_DATASET_VALIDATION_REPORT.md)

See also: `feature_dictionary.md`, `handoff_to_epic2.md`, `ml_excluded_columns.md`

---

## 7. Important Definitions

| Term | Definition |
|------|------------|
| **track** | Một bài hát Spotify — row trong `clean.tracks` / `tracks.csv` |
| **artist** | Nghệ sĩ Spotify — row trong `clean.artists`; liên kết track qua `track_artists` |
| **genre** | Thể loại từ `artists.csv.genres` — 5,366 total; 4,672 track-linked |
| **popularity** | Spotify score 0–100 trong `clean.tracks.popularity` |
| **target_popularity** | Alias của popularity trong ML views — **label only** |
| **audio features** | 7 features [0,1] + key, mode, loudness, tempo, time_signature từ Spotify API |
| **release_precision** | `day` / `month` / `year` / `unknown` — độ chi tiết release_date |
| **related artist graph** | `dict_artists.json` → `clean.artist_relations` — không phải genre |
| **leakage** | Dùng thông tin không có tại thời điểm dự đoán (target, popularity proxy, post-split stats) |
| **ML-ready dataset** | `vw_ml_ready_dataset` — 20 cols, no leakage, no imputation/scaling in EPIC 1 |

---

## 8. Known Warnings

| Warning | Value | Source |
|---------|-------|--------|
| tracks.name NULL | 71 | F1.4 / F1.5 |
| artists.followers NULL | 11 | F1.1 audit |
| duration short (<10s) | 26 | F1.5 G05 |
| duration long (>60min) | 83 | F1.5 G05 |
| loudness > 0 | 219 | F1.5 G06 |
| tempo NULL | 328 | F1.4 / ML validation |
| time_signature NULL | 337 | F1.4 / ML validation |
| release_month NULL | 136,489 | ML validation (year-precision releases) |
| track_artists coverage | 96.54% | F1.4 / F1.5 G08 |
| artist_relations diff | 1 | EDA_INSIGHTS_REPORT |
| popularity imbalance | ~75% tracks ≤ 40 | EDA / F1.7 |
| target_popularity = 0 | 44,690 (~7.6%) | ML validation |

---

*Feature 1.9 — Documentation & Epic Review | HitRadar Pro*

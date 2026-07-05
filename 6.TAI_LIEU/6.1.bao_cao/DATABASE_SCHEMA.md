# DATABASE SCHEMA — FEATURE 1.2

> **Dự án:** HitRadar Pro | **EPIC:** EPIC 1 — Data Foundation & Data Understanding
> **Người thiết kế:** Đạt | **Ngày:** 2026-07-05
> **Dựa trên:** `DATASET_AUDIT_REPORT.md`, `DATA_DICTIONARY_DRAFT.md`, `DICT_ARTISTS_SEMANTIC_CHECK.md`

---

## 1. Purpose

Thiết kế kiến trúc PostgreSQL 3 tầng (raw / clean / analytics) cho EPIC 1 HitRadar.
Schema này là căn cứ để Feature 1.3 thực hiện import dữ liệu và Feature 1.4 thực hiện cleaning.

**Quyết định thiết kế quan trọng:**
- `dict_artists.json` đã xác minh là **related artist graph** (overlap 100% với `artists.csv.id`).
  Không dùng làm nguồn genre. Genre duy nhất từ `artists.csv.genres`.
- `clean.artist_relations` được thiết kế thay vì `clean.artist_genres` từ dict_artists.json.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  RAW LAYER (schema: raw)                                         │
│  Import nguyên bản từ CSV/JSON, không transform, không validate  │
│  raw_tracks · raw_artists · raw_artist_json                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │ Feature 1.4: Parse, clean, normalize
┌───────────────────────▼─────────────────────────────────────────┐
│  CLEAN LAYER (schema: clean)                                     │
│  Dữ liệu đã chuẩn hoá, enforce constraints, explode list fields  │
│  tracks · artists · genres · track_artists                       │
│  artist_genres · artist_relations                                │
└───────────────────────┬─────────────────────────────────────────┘
                        │ Feature 1.6: Aggregate, join, derive
┌───────────────────────▼─────────────────────────────────────────┐
│  ANALYTICS LAYER (schema: analytics)                             │
│  Views / marts phục vụ EDA, dashboard, ML handoff               │
│  vw_tracks_overview · vw_tracks_by_decade · vw_audio_trends     │
│  vw_popularity_stats · vw_top_artists · vw_genre_trends          │
│  vw_explicit_by_decade · vw_duration_trends · vw_ml_training_dataset │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1 — Raw Layer

### `raw.raw_tracks`

| Trường | Purpose |
|--------|---------|
| **Source file** | `1.DỮ_LIỆU/1.1.raw/tracks.csv` |
| **Mục đích** | Import nguyên bản 586,672 track records — không transform |
| **Primary key** | `id` (TEXT, Spotify track ID, unique confirmed) |

| Column | PostgreSQL Type | Nullable | Ghi chú |
|--------|----------------|----------|---------|
| `id` | TEXT | NOT NULL | PK candidate — 586,672 unique |
| `name` | TEXT | NULL | 71 missing (0.01%) |
| `popularity` | SMALLINT | NULL | 0–100; nhiều giá trị = 0 |
| `duration_ms` | INTEGER | NULL | min 3,344 · max 5,621,218 |
| `explicit` | SMALLINT | NULL | 0 / 1 ở raw — đổi thành BOOLEAN ở clean |
| `artists` | TEXT | NULL | Python list-string `['Name']` — parse ở Feature 1.4 |
| `id_artists` | TEXT | NULL | Python list-string `['id']` — explode ở Feature 1.4 |
| `release_date` | TEXT | NULL | Mixed: YYYY-MM-DD / YYYY-MM / YYYY |
| `danceability` | DOUBLE PRECISION | NULL | |
| `energy` | DOUBLE PRECISION | NULL | |
| `key` | SMALLINT | NULL | 0–11 (pitch class) |
| `loudness` | DOUBLE PRECISION | NULL | thường âm; max +5.376 |
| `mode` | SMALLINT | NULL | 0 / 1 |
| `speechiness` | DOUBLE PRECISION | NULL | |
| `acousticness` | DOUBLE PRECISION | NULL | |
| `instrumentalness` | DOUBLE PRECISION | NULL | |
| `liveness` | DOUBLE PRECISION | NULL | |
| `valence` | DOUBLE PRECISION | NULL | |
| `tempo` | DOUBLE PRECISION | NULL | 328 giá trị = 0 — giữ nguyên ở raw |
| `time_signature` | SMALLINT | NULL | 337 giá trị = 0 — giữ nguyên ở raw |
| `_import_ts` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Metadata: thời điểm import |

---

### `raw.raw_artists`

| Trường | Purpose |
|--------|---------|
| **Source file** | `1.DỮ_LIỆU/1.1.raw/artists.csv` |
| **Mục đích** | Import nguyên bản 1,162,095 artist records |
| **Primary key** | `id` (TEXT, Spotify artist ID, unique confirmed) |

| Column | PostgreSQL Type | Nullable | Ghi chú |
|--------|----------------|----------|---------|
| `id` | TEXT | NOT NULL | PK candidate — 1,162,095 unique |
| `followers` | DOUBLE PRECISION | NULL | 11 missing; phân bố cực lệch; DOUBLE vì NaN trong CSV |
| `genres` | TEXT | NULL | Python list-string `['pop', 'rock']` — parse ở Feature 1.4 |
| `name` | TEXT | NULL | 3 missing (0.0003%) |
| `popularity` | SMALLINT | NULL | 0–100; dashboard_only, leakage risk nếu dùng ML |
| `_import_ts` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | Metadata |

---

### `raw.raw_artist_json`

| Trường | Purpose |
|--------|---------|
| **Source file** | `1.DỮ_LIỆU/1.1.raw/dict_artists.json` |
| **Mục đích** | Lưu raw related artist graph — xác nhận là RELATED_ARTIST_GRAPH, không phải genre source |
| **Primary key** | `artist_id` |

| Column | PostgreSQL Type | Nullable | Ghi chú |
|--------|----------------|----------|---------|
| `artist_id` | TEXT | NOT NULL | Key từ dict_artists.json — 573,856 keys |
| `raw_values` | JSONB | NULL | Original list as JSONB array |
| `value_count` | INTEGER | NULL | Số phần tử trong list (0 nếu rỗng) |
| `semantic_status` | TEXT | NOT NULL DEFAULT 'RELATED_ARTIST_GRAPH' | Kết quả từ task 1.2.0 |
| `source_file` | TEXT | NOT NULL DEFAULT 'dict_artists.json' | |
| `_import_ts` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |

---

## 4. Layer 2 — Clean Layer

### `clean.tracks`

| Column | PostgreSQL Type | Nullable | Derived from | Ghi chú |
|--------|----------------|----------|--------------|---------|
| `track_id` | TEXT | NOT NULL | `raw_tracks.id` | PK |
| `name` | TEXT | NULL | `raw_tracks.name` | |
| `popularity` | SMALLINT | NOT NULL | `raw_tracks.popularity` | **TARGET — không dùng làm input feature** |
| `duration_ms` | INTEGER | NOT NULL | `raw_tracks.duration_ms` | |
| `duration_min` | NUMERIC(8,4) | NULL | `duration_ms / 60000.0` | Derived |
| `explicit` | BOOLEAN | NOT NULL | `raw_tracks.explicit` | 0→FALSE, 1→TRUE |
| `release_date` | DATE | NULL | parsed from `raw_tracks.release_date` | YYYY-MM / YYYY → day=01 |
| `release_year` | SMALLINT | NULL | extracted | |
| `release_month` | SMALLINT | NULL | extracted | NULL nếu chỉ có YYYY |
| `decade` | SMALLINT | NULL | `(release_year / 10) * 10` | 1920, 1930…2020 |
| `release_precision` | TEXT | NULL | ghi lại độ chi tiết của raw release_date | `CHECK (IN ('day','month','year','unknown'))` |
| `danceability` | DOUBLE PRECISION | NULL | | |
| `energy` | DOUBLE PRECISION | NULL | | |
| `key` | SMALLINT | NULL | | 0–11 |
| `loudness` | DOUBLE PRECISION | NULL | | |
| `mode` | SMALLINT | NULL | | 0/1 |
| `speechiness` | DOUBLE PRECISION | NULL | | |
| `acousticness` | DOUBLE PRECISION | NULL | | |
| `instrumentalness` | DOUBLE PRECISION | NULL | | |
| `liveness` | DOUBLE PRECISION | NULL | | |
| `valence` | DOUBLE PRECISION | NULL | | |
| `tempo` | DOUBLE PRECISION | NULL | | tempo=0 → NULL hoặc flag ở Feature 1.4 |
| `time_signature` | SMALLINT | NULL | | time_signature=0 → NULL ở Feature 1.4 |
| `_clean_ts` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | | |

---

### `clean.artists`

| Column | PostgreSQL Type | Nullable | Ghi chú |
|--------|----------------|----------|---------|
| `artist_id` | TEXT | NOT NULL | PK |
| `name` | TEXT | NULL | 3 missing |
| `followers` | BIGINT | NULL | 11 missing; log-transform khi dùng ML |
| `popularity` | SMALLINT | NULL | dashboard_only |
| `_clean_ts` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |

---

### `clean.genres`

| Column | PostgreSQL Type | Nullable | Ghi chú |
|--------|----------------|----------|---------|
| `genre_id` | SERIAL | NOT NULL | PK (auto-increment) |
| `genre_name` | TEXT | NOT NULL | Original từ artists.csv.genres |
| `normalized_genre_name` | TEXT | NULL | lowercase, trim, xử lý hyphen — Feature 1.4 |

---

### `clean.track_artists`

| Column | PostgreSQL Type | Nullable | Ghi chú |
|--------|----------------|----------|---------|
| `track_id` | TEXT | NOT NULL | FK → clean.tracks.track_id |
| `artist_id` | TEXT | NOT NULL | FK → clean.artists.artist_id |
| `artist_order` | SMALLINT | NOT NULL DEFAULT 0 | 0 = main artist |
| `is_main_artist` | BOOLEAN | NOT NULL DEFAULT FALSE | TRUE nếu artist_order = 0 |

*Composite PK: `(track_id, artist_id)`*

---

### `clean.artist_genres`

| Column | PostgreSQL Type | Nullable | Ghi chú |
|--------|----------------|----------|---------|
| `artist_id` | TEXT | NOT NULL | FK → clean.artists.artist_id |
| `genre_id` | INTEGER | NOT NULL | FK → clean.genres.genre_id |
| `source` | TEXT | NOT NULL DEFAULT 'artists_csv' | Nguồn: chỉ `artists_csv` — dict_artists.json đã xác minh là related artist graph |

*Composite PK: `(artist_id, genre_id)`*

---

### `clean.artist_relations`

> Bảng này thiết kế từ `dict_artists.json` (confirmed RELATED_ARTIST_GRAPH, overlap 100%)

| Column | PostgreSQL Type | Nullable | Ghi chú |
|--------|----------------|----------|---------|
| `artist_id` | TEXT | NOT NULL | FK → clean.artists.artist_id |
| `related_artist_id` | TEXT | NOT NULL | FK → clean.artists.artist_id |
| `relation_order` | SMALLINT | NULL | Vị trí trong list |
| `source` | TEXT | NOT NULL DEFAULT 'dict_artists_json' | |

*Composite PK: `(artist_id, related_artist_id)`*

---

## 5. Layer 3 — Analytics / Mart Layer

### `analytics.vw_tracks_overview`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | Bức tranh tổng quan về tất cả track |
| **Input tables** | `clean.tracks` |
| **Output columns** | track_id, name, popularity, duration_min, explicit, release_year, decade, danceability, energy, valence, tempo |
| **Used for** | EDA · Dashboard |

### `analytics.vw_tracks_by_decade`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | Thống kê theo thập kỷ: số track, trung bình audio features, popularity |
| **Input tables** | `clean.tracks` |
| **Output columns** | decade, track_count, avg_popularity, avg_danceability, avg_energy, avg_valence, avg_tempo, avg_loudness |
| **Used for** | EDA · Dashboard |

### `analytics.vw_audio_trends`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | Xu hướng audio features theo năm |
| **Input tables** | `clean.tracks` |
| **Output columns** | release_year, avg_danceability, avg_energy, avg_valence, avg_acousticness, avg_instrumentalness, avg_speechiness |
| **Used for** | EDA · Dashboard |

### `analytics.vw_popularity_stats`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | Phân phối popularity tracks — phân tích target variable |
| **Input tables** | `clean.tracks` |
| **Output columns** | popularity_bucket, track_count, pct_of_total |
| **Used for** | EDA · **Target analysis — không dùng để train** |

### `analytics.vw_top_artists`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | Top artists theo số track và avg popularity |
| **Input tables** | `clean.tracks`, `clean.track_artists`, `clean.artists` |
| **Output columns** | artist_id, artist_name, track_count, avg_track_popularity, followers |
| **Used for** | EDA · Dashboard |

### `analytics.vw_genre_trends`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | Xu hướng genre theo năm/thập kỷ |
| **Input tables** | `clean.tracks`, `clean.track_artists`, `clean.artist_genres`, `clean.genres` |
| **Output columns** | genre_name, decade, track_count, avg_popularity |
| **Used for** | EDA · Dashboard |

### `analytics.vw_explicit_by_decade`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | Tỷ lệ explicit content theo thập kỷ |
| **Input tables** | `clean.tracks` |
| **Output columns** | decade, total_tracks, explicit_count, explicit_pct |
| **Used for** | EDA · Dashboard |

### `analytics.vw_duration_trends`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | Xu hướng thời lượng bài hát theo năm |
| **Input tables** | `clean.tracks` |
| **Output columns** | release_year, avg_duration_min, median_duration_min, min_duration_min, max_duration_min |
| **Used for** | EDA · Dashboard |

### `analytics.vw_ml_training_dataset`
| Trường | Chi tiết |
|--------|---------|
| **Purpose** | ML-ready candidate dataset — bàn giao EPIC 2 |
| **Input tables** | `clean.tracks`, `clean.track_artists`, `clean.artists` (join có kiểm soát) |
| **Output columns** | track_id, popularity *(target)*, duration_ms, duration_min, explicit, release_year, decade, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature, n_artists |
| **Used for** | **ML handoff — EPIC 2 split train/test từ view này** |
| **Lưu ý leakage** | Không bao gồm artists.popularity, artists.followers; không bao gồm aggregate popularity |

---

## 6. Keys and Relationships

| Relationship | Type | Detail |
|-------------|------|--------|
| `raw.raw_tracks.id` | Candidate PK | TEXT, NOT NULL, unique trong raw |
| `raw.raw_artists.id` | Candidate PK | TEXT, NOT NULL, unique trong raw |
| `clean.tracks.track_id` | **PK** | TEXT, NOT NULL |
| `clean.artists.artist_id` | **PK** | TEXT, NOT NULL |
| `clean.genres.genre_id` | **PK** | SERIAL |
| `clean.track_artists` | Composite PK | `(track_id, artist_id)` |
| `clean.artist_genres` | Composite PK | `(artist_id, genre_id)` |
| `clean.artist_relations` | Composite PK | `(artist_id, related_artist_id)` |
| `clean.track_artists.track_id` | **FK** | → `clean.tracks.track_id` |
| `clean.track_artists.artist_id` | **FK** | → `clean.artists.artist_id` |
| `clean.artist_genres.artist_id` | **FK** | → `clean.artists.artist_id` |
| `clean.artist_genres.genre_id` | **FK** | → `clean.genres.genre_id` |
| `clean.artist_relations.artist_id` | **FK** | → `clean.artists.artist_id` |
| `clean.artist_relations.related_artist_id` | **FK** | → `clean.artists.artist_id` |

---

## 7. Data Types

| Loại dữ liệu | PostgreSQL Type | Lý do |
|-------------|----------------|-------|
| Spotify IDs | `TEXT` | 22-char alphanumeric, không cần số học |
| Tên / text | `TEXT` | Không cố định độ dài |
| `popularity` | `SMALLINT` | 0–100, tiết kiệm bộ nhớ |
| `duration_ms` | `INTEGER` | Max ~5.6M ms — nằm trong INTEGER range |
| `duration_min` | `NUMERIC(8,4)` | Precision cần thiết cho phút |
| Audio features (0–1) | `DOUBLE PRECISION` | Consistency với pandas float64 |
| `key`, `mode`, `time_signature` | `SMALLINT` | Giá trị nhỏ |
| `explicit` raw | `SMALLINT` | Giữ nguyên 0/1 từ CSV |
| `explicit` clean | `BOOLEAN` | Sau khi cast |
| `release_date` raw | `TEXT` | Mixed format — không ép kiểu ở raw |
| `release_date` clean | `DATE` | Sau khi normalize |
| `release_year`, `release_month`, `decade` | `SMALLINT` | |
| `followers` raw | `DOUBLE PRECISION` | Có NaN trong CSV — dùng float |
| `followers` clean | `BIGINT` | Sau khi cast, NULL nếu missing |
| JSON values | `JSONB` | Indexable, queryable |
| Timestamps | `TIMESTAMPTZ` | Luôn có timezone |

---

## 8. Constraints

> Raw layer: **không có constraints nghiêm ngặt** để tránh lỗi import dữ liệu bẩn.
> Clean layer: enforce đầy đủ constraints sau khi cleaning ở Feature 1.4.

| Column | Constraint | Layer | Ghi chú |
|--------|-----------|-------|---------|
| `popularity` | `CHECK (popularity BETWEEN 0 AND 100)` | clean | |
| `danceability` | `CHECK (danceability BETWEEN 0 AND 1)` | clean | |
| `energy` | `CHECK (energy BETWEEN 0 AND 1)` | clean | |
| `speechiness` | `CHECK (speechiness BETWEEN 0 AND 1)` | clean | |
| `acousticness` | `CHECK (acousticness BETWEEN 0 AND 1)` | clean | |
| `instrumentalness` | `CHECK (instrumentalness BETWEEN 0 AND 1)` | clean | |
| `liveness` | `CHECK (liveness BETWEEN 0 AND 1)` | clean | |
| `valence` | `CHECK (valence BETWEEN 0 AND 1)` | clean | |
| `duration_ms` | `CHECK (duration_ms > 0)` | clean | |
| `tempo` | `CHECK (tempo > 0)` | clean | tempo=0 đã được xử lý trước đó |
| `time_signature` | `CHECK (time_signature BETWEEN 1 AND 5)` | clean | |
| `release_year` | `CHECK (release_year BETWEEN 1900 AND 2030)` | clean | |
| `followers` | `CHECK (followers >= 0)` | clean | |
| `key` | `CHECK (key BETWEEN 0 AND 11)` | clean | |
| `mode` | `CHECK (mode IN (0, 1))` | clean | |

---

## 9. Index Strategy

| Index | Table | Column(s) | Lý do |
|-------|-------|-----------|-------|
| PK | `clean.tracks` | `track_id` | Primary |
| PK | `clean.artists` | `artist_id` | Primary |
| PK | `clean.genres` | `genre_id` | Primary |
| PK | `clean.track_artists` | `(track_id, artist_id)` | Composite |
| PK | `clean.artist_genres` | `(artist_id, genre_id)` | Composite |
| PK | `clean.artist_relations` | `(artist_id, related_artist_id)` | Composite |
| IDX | `clean.tracks` | `release_year` | Aggregate queries |
| IDX | `clean.tracks` | `decade` | Group by decade |
| IDX | `clean.tracks` | `popularity` | Target distribution |
| IDX | `clean.track_artists` | `artist_id` | Join optimization |
| IDX | `clean.genres` | `normalized_genre_name` | Genre lookup |
| IDX | `raw.raw_tracks` | `id` | Import lookup |
| IDX | `raw.raw_artists` | `id` | Import lookup |

---

## 10. ML-Safe Design Notes

| Rule | Chi tiết |
|------|---------|
| **Target isolation** | `tracks.popularity` chỉ xuất hiện trong `vw_ml_training_dataset` như target column, không dùng làm feature |
| **Artist popularity** | `artists.popularity` chỉ trong views EDA/dashboard, **không xuất hiện** trong `vw_ml_training_dataset` |
| **Followers leakage** | `artists.followers` không có trong `vw_ml_training_dataset` mặc định; nếu cần thì EPIC 2 phải tính riêng trên train set |
| **Aggregate protection** | Không tính `avg_artist_popularity`, `avg_genre_popularity` trên toàn dataset rồi join vào ML features |
| **Train/test split** | `vw_ml_training_dataset` là candidate dataset — EPIC 2 thực hiện split, không EPIC 1 |
| **Related artist graph** | `clean.artist_relations` là relational data, không dùng trực tiếp làm ML feature mà chưa qua encoding |

---

## 11. Open Questions

| # | Câu hỏi | Xử lý ở |
|---|---------|---------|
| Q1 | Rule xử lý `tempo = 0` (328 rows): NULL hay loại bỏ? | Feature 1.4 |
| Q2 | Rule xử lý `time_signature = 0` (337 rows): NULL hay loại bỏ? | Feature 1.4 |
| Q3 | Rule xử lý duration outliers (< 10s: 26 rows, > 60min: 83 rows)? | Feature 1.4 |
| Q4 | Rule xử lý `artists.followers = NULL` (11 rows): impute hay NULL? | Feature 1.4 |
| Q5 | `artist_relations` có dùng cho ML (e.g. graph features) hay chỉ EDA? | EPIC 2 |
| Q6 | Normalization rule cho genre strings (e.g. "hip hop" vs "hip-hop")? | Feature 1.4 |

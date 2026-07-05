# DATASET AUDIT REPORT — FEATURE 1.1

## 1. Audit Metadata

| Trường | Thông tin |
|--------|-----------|
| **Người phụ trách** | Đạt |
| **Feature** | 1.1 — Dataset Audit & Data Dictionary |
| **Ngày chạy audit** | 2026-07-05 12:48 (UTC+7) |
| **Script** | `9.SCRIPTS/audit_raw_data.py` |
| **Raw input contract** | `tracks.csv`, `artists.csv`, `dict_artists.json` |
| **Sanity: PASS** | 12 |
| **Sanity: WARNING** | 5 |
| **Sanity: FAIL** | 0 |
| **Trạng thái audit** | **PASS** |

---

## 2. File Inventory

| File | Path | Format | Size | Rows / Keys | Columns | Status |
|------|------|--------|------|-------------|---------|--------|
| `tracks.csv` | `1.DỮ_LIỆU/1.1.raw/tracks.csv` | CSV | 106.21 MB | 586,672 rows | 20 | **OK** |
| `artists.csv` | `1.DỮ_LIỆU/1.1.raw/artists.csv` | CSV | 61.89 MB | 1,162,095 rows | 5 | **OK** |
| `dict_artists.json` | `1.DỮ_LIỆU/1.1.raw/dict_artists.json` | JSON | 317.17 MB | 573,856 keys | — | **OK** |

---

## 3. Schema Summary — tracks.csv

**20 columns · 586,672 rows · 0 duplicates · id unique: YES**

| Column | Data Type | Non-null | Missing | Missing % | Unique |
|--------|-----------|----------|---------|-----------|--------|
| `id` | object | 586,672 | 0 | 0.00% | 586,672 |
| `name` | object | 586,601 | 71 | 0.01% | 446,474 |
| `popularity` | int64 | 586,672 | 0 | 0.00% | 101 |
| `duration_ms` | int64 | 586,672 | 0 | 0.00% | 123,122 |
| `explicit` | int64 | 586,672 | 0 | 0.00% | 2 |
| `artists` | object | 586,672 | 0 | 0.00% | 114,030 |
| `id_artists` | object | 586,672 | 0 | 0.00% | 115,062 |
| `release_date` | object | 586,672 | 0 | 0.00% | 19,700 |
| `danceability` | float64 | 586,672 | 0 | 0.00% | 1,285 |
| `energy` | float64 | 586,672 | 0 | 0.00% | 2,571 |
| `key` | int64 | 586,672 | 0 | 0.00% | 12 |
| `loudness` | float64 | 586,672 | 0 | 0.00% | 29,196 |
| `mode` | int64 | 586,672 | 0 | 0.00% | 2 |
| `speechiness` | float64 | 586,672 | 0 | 0.00% | 1,655 |
| `acousticness` | float64 | 586,672 | 0 | 0.00% | 5,217 |
| `instrumentalness` | float64 | 586,672 | 0 | 0.00% | 5,402 |
| `liveness` | float64 | 586,672 | 0 | 0.00% | 1,782 |
| `valence` | float64 | 586,672 | 0 | 0.00% | 1,805 |
| `tempo` | float64 | 586,672 | 0 | 0.00% | 122,706 |
| `time_signature` | int64 | 586,672 | 0 | 0.00% | 5 |

> **Ghi chú:** tracks.csv **không có cột `year`**. Năm phát hành phải được parse từ `release_date` trong Feature 1.4.

---

## 4. Schema Summary — artists.csv

**5 columns · 1,162,095 rows · 0 duplicates · id unique: YES**

| Column | Data Type | Non-null | Missing | Missing % | Unique |
|--------|-----------|----------|---------|-----------|--------|
| `id` | object | 1,162,095 | 0 | 0.00% | 1,162,095 |
| `followers` | float64 | 1,162,084 | 11 | 0.00% | 51,998 |
| `genres` | object | 1,162,095 | 0 | 0.00% | 49,155 |
| `name` | object | 1,162,092 | 3 | 0.00% | 1,134,429 |
| `popularity` | int64 | 1,162,095 | 0 | 0.00% | 99 |

> **Ghi chú:** `genres` là list-string dạng `[]` hoặc `['pop', 'rock']` — cần parse trong Feature 1.4. Mặc dù non-null count = 1,162,095, nhiều giá trị thực tế là list rỗng `[]`.

---

## 5. JSON Summary — dict_artists.json

| Trường | Thông tin |
|--------|-----------|
| Load status | **OK** |
| File size | 317.17 MB |
| Số keys | 573,856 |
| Key type | `str` (Spotify artist ID) |
| Value type | `list` (genre strings) |
| Empty list ratio | **50.82%** — khoảng 291,688 artist có list genre rỗng |
| Unique genres | 1,079,349 |

**Sample records:**
```
"0DheY5irMjBUeLybbCUEZ2" → []
"0DlhY15l3wsrnlfGio2bjU" → []
"0DmRESX2JknGPQyO15yxg7" → []
```

> **Rủi ro parse:**
> - 50.82% keys có value là list rỗng → sẽ cho NULL trong bảng artist_genres
> - Cần `explode` + join qua `id_artists` trong `tracks.csv`
> - Kích thước 317 MB → nên dùng streaming parse trong Feature 1.4

---

## 6. Duplicate Report

| File | Duplicate rows | Duplicate ratio | ID unique |
|------|---------------|-----------------|-----------|
| `tracks.csv` | **0** | 0.00% | **YES** |
| `artists.csv` | **0** | 0.00% | **YES** |

Không có duplicate. Cả hai file đều có `id` làm khóa chính hợp lệ.

---

## 7. Numeric Statistics

### tracks.csv

| Column | Min | Max | Mean | Median | Std |
|--------|-----|-----|------|--------|-----|
| `popularity` | 0 | 100 | 27.57 | 27.0 | 18.37 |
| `duration_ms` | 3,344 | 5,621,218 | 230,051 | 214,893 | 126,526 |
| `danceability` | 0.000 | 0.991 | 0.564 | 0.577 | 0.166 |
| `energy` | 0.000 | 1.000 | 0.542 | 0.549 | 0.252 |
| `key` | 0 | 11 | 5.22 | 5.0 | 3.52 |
| `loudness` | -60.0 | 5.376 | -10.21 | -9.24 | 5.09 |
| `mode` | 0 | 1 | 0.66 | 1.0 | 0.47 |
| `speechiness` | 0.000 | 0.971 | 0.105 | 0.044 | 0.180 |
| `acousticness` | 0.000 | 0.996 | 0.450 | 0.422 | 0.349 |
| `instrumentalness` | 0.000 | 1.000 | 0.113 | 0.000 | 0.267 |
| `liveness` | 0.000 | 1.000 | 0.214 | 0.139 | 0.184 |
| `valence` | 0.000 | 1.000 | 0.552 | 0.564 | 0.258 |
| `tempo` | 0.0 | 246.381 | 118.46 | 117.38 | 29.76 |
| `time_signature` | 0 | 5 | 3.87 | 4.0 | 0.47 |
| `explicit` | 0 | 1 | 0.044 | 0.0 | 0.205 |

### artists.csv

| Column | Min | Max | Mean | Median | Std |
|--------|-----|-----|------|--------|-----|
| `followers` | 0 | 78,900,234 | 10,220.7 | 57.0 | 254,399.5 |
| `popularity` | 0 | 100 | 8.80 | 2.0 | 13.56 |

> **Insight quan trọng:**
> - `popularity` trong tracks.csv: mean = 27.57, median = 27 — **phân bố lệch nhẹ**, nhiều bài có popularity thấp.
> - `popularity` trong artists.csv: mean = 8.80, median = 2 — **phân bố lệch mạnh**, đa số nghệ sĩ rất ít nổi tiếng.
> - `followers` max = 78.9M, median = 57 — **phân bố cực kỳ lệch phải** (long-tail).
> - `instrumentalness` median ≈ 0 — đa số bài có vocal.
> - `duration_ms` max = 5.6M ms (~93 phút) — cần kiểm tra outlier ở Feature 1.4.

---

## 8. Basic Sanity Checks

| Check | Status | Detail |
|-------|--------|--------|
| `tracks.popularity` range [0-100] | **PASS** | All values in [0-100] |
| `tracks.danceability` range [0-1] | **PASS** | All values in [0-1] |
| `tracks.energy` range [0-1] | **PASS** | All values in [0-1] |
| `tracks.speechiness` range [0-1] | **PASS** | All values in [0-1] |
| `tracks.acousticness` range [0-1] | **PASS** | All values in [0-1] |
| `tracks.instrumentalness` range [0-1] | **PASS** | All values in [0-1] |
| `tracks.liveness` range [0-1] | **PASS** | All values in [0-1] |
| `tracks.valence` range [0-1] | **PASS** | All values in [0-1] |
| `tracks.duration_ms > 0` | **PASS** | All positive |
| `tracks.tempo > 0` | **WARNING** | 328 non-positive values (0.056% of rows) |
| `tracks.release_date` parsability | **WARNING** | Mixed formats: `YYYY-MM-DD` và `YYYY` — manual parse cần thiết |
| `tracks.artists` list-string format | **WARNING** | List-string dạng `['Artist Name']` — cần parse trong Feature 1.4 |
| `artists.popularity` range [0-100] | **PASS** | All values in [0-100] |
| `artists.followers >= 0` | **PASS** | All non-negative |
| `artists.id` uniqueness | **PASS** | All IDs unique |
| `artists.genres` list-string format | **WARNING** | List-string format — cần parse; nhiều giá trị là `[]` |
| `artists.name` missing count | **WARNING** | 3 missing names (0.0003%) — không đáng kể |

**Tóm tắt: 12 PASS · 5 WARNING · 0 FAIL**

---

## 9. Initial Data Risks

| # | Risk | Mức độ | File | Xử lý ở |
|---|------|--------|------|---------|
| R1 | `artists` trong tracks.csv là list-string `['Name']` — cần parse thành bảng riêng | **Cao** | tracks.csv | Feature 1.4 |
| R2 | `genres` trong artists.csv là list-string — nhiều giá trị rỗng `[]` | **Cao** | artists.csv | Feature 1.4 |
| R3 | `dict_artists.json` có 50.82% empty genre list — join sẽ cho nhiều NULL | **Cao** | dict_artists.json | Feature 1.4 |
| R4 | `release_date` có 2 format: `YYYY-MM-DD` và `YYYY` — cần normalize | **Trung bình** | tracks.csv | Feature 1.4 |
| R5 | Không có cột `year` sẵn — phải parse từ `release_date` | **Trung bình** | tracks.csv | Feature 1.4 |
| R6 | `tempo` có 328 giá trị = 0 (0.056%) — có thể là lỗi dữ liệu hoặc track đặc biệt | **Thấp** | tracks.csv | Feature 1.4 / 1.5 |
| R7 | `duration_ms` max = 5,621,218 ms (~93 phút) — có thể là outlier cần lọc | **Thấp** | tracks.csv | Feature 1.4 / 1.5 |
| R8 | `popularity` (tracks) phân bố lệch — mean ≠ median, nhiều bài có popularity = 0 | **Trung bình** | tracks.csv | Feature 1.7 EDA |
| R9 | `followers` (artists) phân bố cực kỳ lệch phải — cần log-transform nếu dùng làm feature | **Trung bình** | artists.csv | Feature 1.8 / EPIC 2 |
| R10 | `popularity` của artists.csv **không được dùng trực tiếp làm ML feature** — leakage risk | **Cao** | artists.csv | Feature 1.8 / EPIC 2 |
| R11 | `id_artists` trong tracks.csv là list-string các Spotify ID → khớp với `artists.id` qua explode | **Trung bình** | tracks.csv | Feature 1.4 |
| R12 | `dict_artists.json` kích thước 317 MB — cần streaming parse trong Feature 1.4 | **Thấp** | dict_artists.json | Feature 1.4 |

---

## 10. Recommendation for Feature 1.2

Dựa trên kết quả audit, Feature 1.2 nên thiết kế schema với ít nhất 3 bảng raw:

| Bảng raw | Nguồn | Ghi chú |
|----------|-------|---------|
| `raw_tracks` | `tracks.csv` | Import nguyên bản, giữ `artists` và `id_artists` dạng text |
| `raw_artists` | `artists.csv` | Import nguyên bản, giữ `genres` dạng text |
| `raw_artist_genres_json` | `dict_artists.json` | Lưu dạng JSONB hoặc text — parse thành bảng riêng ở Feature 1.4 |

> **Feature 1.2 sẽ thiết kế raw/clean/analytics layers dựa trên kết quả audit này.**

---

## 11. Next Step

**Feature 1.2 — Database Architecture:**

- Thiết kế raw schema (raw_tracks, raw_artists, raw_artist_genres_json)
- Thiết kế clean schema (clean_tracks, clean_artists, clean_genres, clean_track_artists, clean_artist_genres)
- Thiết kế analytics views/marts (vw_tracks_by_decade, vw_audio_trends, vw_ml_training_dataset…)
- Định nghĩa primary keys, foreign keys, data types, constraints
- Chuẩn bị ERD
- Chuẩn bị SQL scripts cho Feature 1.3 (import)

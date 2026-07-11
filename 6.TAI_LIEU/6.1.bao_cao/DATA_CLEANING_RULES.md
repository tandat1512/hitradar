# DATA CLEANING RULES — HITRADAR PRO EPIC 1

**Project:** HitRadar Pro  
**Feature:** 1.4 (original rules) + 1.9 (final documentation)  
**Owner:** Đạt  
**Status:** Final — PASS_WITH_WARNINGS  
**Last updated:** 2026-07-11  

**Evidence sources:**
- `FEATURE_1_4_COMPLETION_REPORT.md`
- `CLEANING_LOG.md`
- `CLEAN_TABLE_VALIDATION_REPORT.md`
- `DATA_QUALITY_REPORT.md`
- `DATA_DICTIONARY.md`
- `DATABASE_SCHEMA.md`

> **Note:** File này là **DATA_CLEANING_RULES.md** (raw → clean).  
> Không nhầm với `DATA_QUALITY_RULES.md` (Feature 1.5 quality gate registry).

---

## 1. Purpose

File này mô tả các quy tắc cleaning chính thức từ **raw layer** sang **clean layer** trong EPIC 1 HitRadar Pro.

Mục tiêu:
- Chuẩn hóa dữ liệu để EDA, analytics views, và ML handoff
- Giữ audit trail / reproducibility
- Phân biệt rõ **data cleaning (EPIC 1)** vs **ML preprocessing (EPIC 2)**

**Scripts:**
- `9.SCRIPTS/clean_raw_to_clean.py`
- `9.SCRIPTS/validate_clean_tables.py`
- `2.DATABASE_SQL/2.3.lam_sach/`

---

## 2. Cleaning Philosophy

| # | Principle | Rule |
|---|-----------|------|
| 1 | Không drop row nếu không có lý do mạnh | Track/artist rows giữ 1:1 với raw |
| 2 | Giữ outliers nhưng flag/report | Duration short/long, loudness > 0 |
| 3 | Không impute trong EPIC 1 nếu thuộc ML preprocessing | NULL được giữ cho EPIC 2 |
| 4 | Không tạo leakage | Không thêm popularity-derived input features |
| 5 | Không dùng popularity-derived features làm input | `artists.popularity` dashboard only |
| 6 | Không sửa raw tables | Chỉ ghi vào clean layer |
| 7 | Reproducible | Script + SQL checks có thể chạy lại |

---

## 3. Raw to Clean Transformations

| Source | Destination | Transformation |
|--------|-------------|----------------|
| `raw.raw_tracks` | `clean.tracks` | 1:1 copy + normalize release/duration/explicit/tempo/time_signature |
| `raw.raw_artists` | `clean.artists` | 1:1 copy + cast followers, trim name |
| `raw.raw_artists.genres` | `clean.genres` + `clean.artist_genres` | Parse list-string → unique genres + M:N links |
| `raw.raw_tracks.id_artists` | `clean.track_artists` | Parse list-string → FK-valid pairs only |
| `raw.raw_artist_json` | `clean.artist_relations` | RELATED_ARTIST_GRAPH → distinct pairs |

### `raw.raw_tracks` → `clean.tracks`

- Row count: **586,672 = 586,672**
- `explicit`: 0 → FALSE, 1 → TRUE
- `duration_min = duration_ms / 60000.0`
- Parse `release_date` → `release_date`, `release_year`, `release_month`, `decade`, `release_precision`
- `tempo = 0` → NULL
- `time_signature = 0` → NULL
- `name` NULL retained (71)

### `raw.raw_artists` → `clean.artists`

- Row count: **1,162,095 = 1,162,095**
- `followers`: FLOAT → BIGINT; NULL/negative → NULL
- `name`: trim; NULL retained if missing
- `popularity`: giữ nguyên — **dashboard only**, không dùng làm ML input mặc định

### `raw.raw_artists.genres` → `clean.genres` + `clean.artist_genres`

- Parser: `ast.literal_eval` (safe list-string parse)
- `normalized_genre_name`: lower / strip / collapse spaces
- Unique genres: **5,366**
- `clean.artist_genres`: **468,680** rows, `source = 'artists_csv'`

### `raw.raw_tracks.id_artists` → `clean.track_artists`

- Parser: `ast.literal_eval`
- Chỉ insert nếu `artist_id` tồn tại trong `clean.artists`
- Skipped unknown artist FK: **26,224**
- Inserted: **730,946**
- Coverage: **96.54%**

### `raw.raw_artist_json` → `clean.artist_relations`

- Semantic: **RELATED_ARTIST_GRAPH** (không phải genre)
- Inserted distinct pairs: **8,864,471**
- Raw assignments: **8,864,472** → diff = 1 (duplicate pair collapsed)

---

## 4. Release Date Rules

| Raw format | `release_precision` | Normalized `release_date` | `release_year` | `release_month` |
|------------|---------------------|---------------------------|----------------|-----------------|
| `YYYY-MM-DD` | `day` | Giữ nguyên | YYYY | MM |
| `YYYY-MM` | `month` | `YYYY-MM-01` | YYYY | MM |
| `YYYY` | `year` | `YYYY-01-01` | YYYY | **NULL** |
| Unparseable | `unknown` | NULL | NULL | NULL |

- `decade = (release_year / 10) * 10`
- **Observed release_year range:** **1921–2021** (EDA evidence)
- `release_month NULL = 136,489` vì year-only releases (precision = year)

**Observed precision distribution (Feature 1.4/1.5):**
- day = 448,081
- month = 2,102
- year = 136,489
- invalid = 0

---

## 5. Audio Feature Rules

| Feature / Rule | Detail |
|----------------|--------|
| `danceability`, `energy`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence` | Phải trong **[0, 1]** — 0 out-of-range ở clean (G03 PASS) |
| `tempo = 0` | → **NULL** (sentinel, không phải BPM thật) → **328 NULL** |
| `time_signature = 0` hoặc ngoài range hợp lệ `[1, 5]` | → **NULL** → **337 NULL** |
| `loudness > 0` | **Giữ lại** nhưng WARNING — **219 tracks** |
| Scaling / normalization | **Không** thực hiện trong EPIC 1 |

---

## 6. Duration Rules

| Rule | Detail |
|------|--------|
| `duration_ms > 0` | Required — 0 invalid rows |
| `duration_min` | `duration_ms / 60000` — 0 NULL |
| Short tracks `< 10s` | **26** — giữ lại, flag |
| Long tracks `> 60min` | **83** — giữ lại, flag |
| Outliers | **Không drop** — report ở Feature 1.5 |

---

## 7. Artist and Genre Rules

| Rule | Detail |
|------|--------|
| `id_artists` | List-string — parse bằng safe parser (`ast.literal_eval`) |
| Genre source duy nhất | `artists.csv.genres` / `raw.raw_artists.genres` |
| `dict_artists.json` | **Không phải genre source** |
| `clean.track_artists` | Chỉ giữ FK-valid pairs |
| Skipped unknown artist FK | **26,224** |
| track_artists coverage | **96.54%** (730,946 / 757,170) |
| `clean.genres` | **5,366** |
| Track-linked genres | **4,672** (EDA / genre trends) |
| Populate order | tracks → artists → genres → track_artists → artist_genres → artist_relations |

---

## 8. Related Artist Graph Rules

| Rule | Detail |
|------|--------|
| Semantic | `dict_artists.json` = **RELATED_ARTIST_GRAPH** (Feature 1.2 confirmed) |
| Destination | `clean.artist_relations` |
| Empty lists | Giữ là thông tin hợp lệ (~22% empty lists ở raw) |
| FK | Cả `artist_id` và `related_artist_id` phải tồn tại trong `clean.artists` |
| Raw assignments | 8,864,472 |
| Inserted distinct pairs | 8,864,471 |
| **artist_relations diff = 1** | Do **duplicate pair collapsed** — WARNING, không phải data loss blocker |

---

## 9. Missing Value Rules

| Column / case | Count | Rule |
|---------------|-------|------|
| `tracks.name` NULL | **71** | Giữ lại — không drop row |
| `artists.followers` NULL | **11** | Giữ lại — không impute |
| `tempo` NULL | **328** | Từ tempo=0 → NULL; impute ở EPIC 2 |
| `time_signature` NULL | **337** | Từ 0/out-of-range → NULL; impute ở EPIC 2 |
| `release_month` NULL | **136,489** | Year-only releases; xử lý ở EPIC 2 |
| Imputation trong EPIC 1 | — | **Không impute** |

---

## 10. ML-Safe Rules

| Rule | Detail |
|------|--------|
| `target_popularity` | **Label** — không dùng làm input |
| `track_id` | **Identifier** — không dùng để train |
| Không dùng `target_popularity` làm input | Target leakage |
| Không dùng `artists.popularity` mặc định | Popularity proxy leakage |
| Không dùng aggregate popularity | avg_artist / avg_genre / avg_track popularity excluded |
| Không fit scaler / imputer / encoder trong EPIC 1 | Tránh leakage thống kê |
| EPIC 2 | Fit preprocessing **trên train only** |

---

## 11. Validation Evidence

| Table | Row count | Status |
|-------|-----------|--------|
| `clean.tracks` | **586,672** | PASS |
| `clean.artists` | **1,162,095** | PASS |
| `clean.genres` | **5,366** | PASS |
| `clean.track_artists` | **730,946** | PASS + WARNING (coverage 96.54%) |
| `clean.artist_genres` | **468,680** | PASS |
| `clean.artist_relations` | **8,864,471** | PASS + WARNING (diff=1) |

**Clean layer validation status:** **PASS_WITH_WARNINGS**

**Evidence files:**
- `CLEANING_LOG.md`
- `CLEAN_TABLE_VALIDATION_REPORT.md`
- `FEATURE_1_4_COMPLETION_REPORT.md`
- `DATA_QUALITY_REPORT.md` (gates G01–G12)

---

## 12. Decision

**Cleaning rules final cho EPIC 1.**

| Field | Value |
|-------|-------|
| **Status** | **PASS_WITH_WARNINGS** |
| Blockers | None |
| Warnings carry-forward sang EPIC 2 | tempo NULL=328; time_signature NULL=337; release_month NULL=136,489; track_artists coverage 96.54%; artist_relations diff=1; duration outliers short=26 / long=83; loudness>0=219 |

EPIC 1 cleaning hoàn tất. ML imputation / scaling / encoding / train-test split thuộc **EPIC 2**.

---

*Feature 1.9 — Documentation & Epic Review | HitRadar Pro*

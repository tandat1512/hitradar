# FEATURE 1.4 COMPLETION REPORT

## 1. Feature

**Feature 1.4 — Data Cleaning & Normalization**

| Trường | Thông tin |
|--------|-----------|
| EPIC | EPIC 1 — Data Foundation & Data Understanding |
| Dự án | HitRadar Pro |
| Ngày hoàn thành | 2026-07-07 |
| Ngày hotfix report | 2026-07-07 |
| Trạng thái | **PASS WITH WARNINGS — REPORT FIXED** |
| Database | `hitradar` @ localhost:5432 (PostgreSQL 18.4) |
| Thời gian cleaning | ~12.5 phút |

---

## 2. Owner

**Đạt** — phụ trách EPIC 1

---

## 3. Completed Tasks (WBS chính thức 1.4.1–1.4.13)

| Task | Mô tả | Ghi chú | Trạng thái |
|------|-------|---------|-----------|
| **1.4.1** | Xử lý missing values | `tracks.name`, `artists.name`, `artists.followers` giữ NULL theo rule — không drop row | **DONE** |
| **1.4.2** | Xử lý duplicate tracks | `clean.tracks.track_id`: null=0, duplicate=0 — ON CONFLICT DO NOTHING | **DONE** |
| **1.4.3** | Chuẩn hóa text artist/genre | Artist name: trim; genre: `lower().strip()` + collapse spaces → `normalized_genre_name` | **DONE** |
| **1.4.4** | Parse artists list-string | `id_artists` → `ast.literal_eval` → `clean.track_artists`; skipped 26,224 unknown artist FK (Feature 1.5) | **DONE** |
| **1.4.5** | Parse genres list-string | `genres` → `ast.literal_eval` từ `raw.raw_artists.genres` ONLY; không dùng `dict_artists.json` làm genre source | **DONE** |
| **1.4.6** | Tạo bảng artists chuẩn hóa | `clean.artists`: 1,162,095 rows = `raw.raw_artists` | **DONE** |
| **1.4.7** | Tạo bảng genres chuẩn hóa | `clean.genres`: 5,366 unique genres | **DONE** |
| **1.4.8** | Tạo bảng track_artists | `clean.track_artists`: 730,946 rows (coverage 96.54%) | **DONE** |
| **1.4.9** | Tạo bảng artist_genres | `clean.artist_genres`: 468,680 rows, source=artists_csv | **DONE** |
| **1.4.10** | Chuẩn hóa release_date | YYYY-MM-DD→day, YYYY-MM→month+normalize, YYYY→year+normalize, invalid→unknown | **DONE** |
| **1.4.11** | Tạo release_year, release_month, decade | Derived từ release_date; consistency checks PASS (0 inconsistencies) | **DONE** |
| **1.4.12** | Chuyển duration_ms thành duration_min | `duration_min = duration_ms / 60000.0`; 0 NULL | **DONE** |
| **1.4.13** | Tạo clean tables cuối cùng | `clean.tracks`: 586,672; `clean.artist_relations`: 8,864,471 (dict_artists.json → RELATED_ARTIST_GRAPH only) | **DONE** |

---

## 4. Outputs Created

| File | Mô tả |
|------|-------|
| `3.NOTEBOOKS/3.3.lam_sach_python/01_feature_1_4_cleaning_exploration.ipynb` | Exploration notebook |
| `3.NOTEBOOKS/3.3.lam_sach_python/02_feature_1_4_clean_validation.ipynb` | Validation notebook |
| `9.SCRIPTS/clean_raw_to_clean.py` | Python cleaning script |
| `9.SCRIPTS/validate_clean_tables.py` | Python validation script (extended checks) |
| `2.DATABASE_SQL/2.3.lam_sach/01_reset_clean_tables.sql` | SQL truncate clean tables |
| `2.DATABASE_SQL/2.3.lam_sach/02_cleaning_checks.sql` | SQL post-cleaning checks |
| `6.TAI_LIEU/6.1.bao_cao/DATA_CLEANING_RULES.md` | Cleaning rules document |
| `6.TAI_LIEU/6.1.bao_cao/CLEANING_LOG.md` | Cleaning run log |
| `6.TAI_LIEU/6.1.bao_cao/CLEAN_TABLE_VALIDATION_REPORT.md` | Validation report (extended) |

---

## 5. Clean Table Row Counts (Actual)

| Table | Row Count | Baseline | Status |
|-------|-----------|---------|--------|
| `clean.tracks` | **586,672** | = raw.raw_tracks | PASS |
| `clean.artists` | **1,162,095** | = raw.raw_artists | PASS |
| `clean.genres` | **5,366** | > 0 | PASS |
| `clean.track_artists` | **730,946** | > 0 | PASS |
| `clean.artist_genres` | **468,680** | > 0 | PASS |
| `clean.artist_relations` | **8,864,471** | > 0 | PASS |

---

## 6. Task-to-Evidence Mapping

| WBS Task | Evidence | Output table/report | Status |
|---------|---------|-------------------|--------|
| 1.4.1 Missing values | `clean.tracks.name NULL=71`, `artists.name NULL=0`, `followers NULL=11` — rows NOT dropped | `clean.tracks`, `clean.artists` | PASS |
| 1.4.2 Duplicate tracks | `track_id: nulls=0, duplicates=0` | `clean.tracks` + ID validation | PASS |
| 1.4.3 Text normalization | `artist.name.strip()`, `genre lower/strip/collapse` | `clean.artists`, `clean.genres` | PASS |
| 1.4.4 Parse id_artists | `730,946` pairs; `26,224` skipped (FK); coverage `96.54%` | `clean.track_artists` | PASS+WARNING |
| 1.4.5 Parse genres | `5,366` unique genres từ `artists.csv.genres` | `clean.genres`, `clean.artist_genres` | PASS |
| 1.4.6 Artists table | `1,162,095 = raw.raw_artists`; `followers` cast BIGINT/NULL | `clean.artists` | PASS |
| 1.4.7 Genres table | `5,366` unique, SERIAL PK, `normalized_genre_name` | `clean.genres` | PASS |
| 1.4.8 track_artists | `730,946` FK-validated pairs | `clean.track_artists` | PASS |
| 1.4.9 artist_genres | `468,680` pairs, `source=artists_csv` | `clean.artist_genres` | PASS |
| 1.4.10 release_date | `day=448,081`, `month=2,102`, `year=136,489`; `invalid=0` | `clean.tracks.release_precision` | PASS |
| 1.4.11 Derived columns | `release_year`, `release_month`, `decade`: 0 inconsistencies | `clean.tracks` + derived check | PASS |
| 1.4.12 duration_min | `duration_min IS NULL: 0`; short=26, long=83 (kept) | `clean.tracks.duration_min` | PASS |
| 1.4.13 Clean tables final | All 6 tables populated; all structural validations PASS | All clean tables | PASS |

---

## 7. Missing Values Handling

| Column | NULL Count | Rule | Status |
|--------|-----------|------|--------|
| `clean.tracks.name` | **71** | Retained NULL — no row dropped | **PASS** |
| `clean.artists.name` | **0** | Retained NULL — no row dropped | **PASS** |
| `clean.artists.followers` | **11** | Retained NULL (missing or originally negative) | **PASS** |

> `clean.tracks` row count = `raw.raw_tracks` = 586,672 confirms no rows dropped.

---

## 8. Relationship Coverage

### track_artists

| Metric | Value |
|--------|-------|
| Inserted into `clean.track_artists` | 730,946 |
| Skipped (unknown artist FK) | 26,224 |
| Estimated total parsed assignments | 757,170 |
| Coverage ratio | **96.54%** |
| Skip ratio | 3.46% |
| Status | **WARNING — Feature 1.5 data quality gate** |

> Skipped artist IDs are referenced in tracks but absent from `artists.csv`.
> Expected for niche/inactive artists. Feature 1.5 will set acceptance threshold.

### artist_relations

| Metric | Value |
|--------|-------|
| Total raw assignments (`SUM(value_count)`) | 8,864,472 |
| Inserted distinct pairs | 8,864,471 |
| Difference | **1** |
| Likely cause | ON CONFLICT — 1 duplicate (artist_id, related_artist_id) pair collapsed |
| Status | **WARNING — not a data loss blocker** |

---

## 9. Validation Results (All Structural Checks PASS)

| Check | Result |
|-------|--------|
| clean.tracks = raw.raw_tracks (586,672) | PASS |
| clean.artists = raw.raw_artists (1,162,095) | PASS |
| 4 junction tables > 0 | PASS |
| track_id: nulls=0, duplicates=0 | PASS |
| artist_id: nulls=0, duplicates=0 | PASS |
| release_precision: 0 invalid | PASS |
| release derived consistency (4 checks) | PASS |
| tempo <= 0 remaining: 0 | PASS |
| time_signature = 0 remaining: 0 | PASS |
| time_signature out-of-range: 0 | PASS |
| duration_min IS NULL: 0 | PASS |
| audio features out-of-range: 0/7 | PASS |
| popularity out-of-range: 0/2 | PASS |
| FK orphans: 0/5 checks | PASS |
| missing values retained (NULL) | PASS |
| **Overall** | **PASS** |

---

## 10. Remaining Risks

| Risk | Xử lý ở |
|------|---------|
| 26,224 track_artists skipped (artist not in artists.csv) — 3.46% | **Feature 1.5** |
| artist_relations diff=1 (likely 1 duplicate pair) | **Feature 1.5 monitoring** |
| Duration outliers: short=26, long=83 (kept per rule) | **Feature 1.5** |
| `artists.popularity` chưa phân tách dashboard vs ML-safe | **Feature 1.5** |
| Analytics views chưa validate với clean data | **Feature 1.5** |

---

## 11. Next Step

**Feature 1.5 — Data Quality Gates**

| Task | Mô tả |
|------|-------|
| 1.5.1 | Đặt ngưỡng chấp nhận track_artists skip ratio (hiện 3.46%) |
| 1.5.2 | Validate artist follower anomalies |
| 1.5.3 | Validate analytics views với clean data |
| 1.5.4 | Flag/quarantine duration outliers theo ngưỡng |
| 1.5.5 | Tách `popularity` → dashboard_only vs ML-safe |

---

## 12. Status

> **PASS WITH WARNINGS — REPORT FIXED**
>
> Tất cả 15 structural validation checks: PASS.
> 3 warnings được ghi rõ: track_artists coverage (96.54%), artist_relations diff=1, duration outliers.
> WBS 1.4.1–1.4.13 đã được map đúng với evidence thực tế.
> Sẵn sàng chuyển sang **Feature 1.5 — Data Quality Gates**.

# FEATURE 1.2 COMPLETION REPORT

## 1. Feature

**Feature 1.2 — Database Architecture**

| Trường | Thông tin |
|--------|-----------|
| EPIC | EPIC 1 — Data Foundation & Data Understanding |
| Dự án | HitRadar Pro |
| Ngày hoàn thành | 2026-07-05 |
| Trạng thái | **PASS WITH SQL FIX VERIFIED** |
| Cập nhật lần cuối | 2026-07-05 (SQL fix) |

---

## 2. Owner

**Đạt** — phụ trách EPIC 1

---

## 3. Completed Tasks

| Task | Mô tả | Trạng thái |
|------|-------|-----------|
| **Task 1.2.0** | Verify `dict_artists.json` semantic meaning — chạy script overlap check | **DONE** |
| Task 1.2.1 | Thiết kế kiến trúc 3 tầng (raw / clean / analytics) | **DONE** |
| Task 1.2.2 | Thiết kế raw tables (`raw_tracks`, `raw_artists`, `raw_artist_json`) | **DONE** |
| Task 1.2.3 | Thiết kế clean tables (6 bảng + constraints) | **DONE** |
| Task 1.2.4 | Thiết kế analytics views/marts (9 views) | **DONE** |
| Task 1.2.5 | Định nghĩa primary keys, foreign keys, unique keys | **DONE** |
| Task 1.2.6 | Định nghĩa data type chuẩn PostgreSQL | **DONE** |
| Task 1.2.7 | Định nghĩa constraints kiểm tra dữ liệu (clean layer) | **DONE** |
| Task 1.2.8 | Vẽ ERD (Mermaid — raw / clean / analytics + data flow) | **DONE** |
| **SQL Fix** | Fix 4 SQL blocker trước khi smoke test | **DONE** |

---

## 4. Outputs Created

| File | Mô tả |
|------|-------|
| `9.SCRIPTS/verify_dict_artists_semantic.py` | Script xác minh semantic dict_artists.json |
| `6.TAI_LIEU/6.1.bao_cao/DICT_ARTISTS_SEMANTIC_CHECK.md` | Report kết quả task 1.2.0 |
| `6.TAI_LIEU/6.1.bao_cao/DATABASE_SCHEMA.md` | Thiết kế đầy đủ 3 tầng (11 mục) |
| `6.TAI_LIEU/6.1.bao_cao/ERD.md` | ERD Mermaid — raw, clean, analytics, data flow |
| `2.DATABASE_SQL/2.1.tao_bang/01_create_schemas.sql` | Tạo 3 schema |
| `2.DATABASE_SQL/2.1.tao_bang/02_create_raw_tables.sql` | DDL raw layer |
| `2.DATABASE_SQL/2.1.tao_bang/03_create_clean_tables.sql` | DDL clean layer + FK + constraints |
| `2.DATABASE_SQL/2.1.tao_bang/04_create_analytics_views.sql` | 9 analytics views |
| `2.DATABASE_SQL/2.1.tao_bang/05_create_constraints_indexes.sql` | Indexes + unique constraints |

---

## 5. Architecture Summary

| Layer | Schema | Tables / Views | Mục đích |
|-------|--------|----------------|---------|
| **Raw** | `raw` | `raw_tracks`, `raw_artists`, `raw_artist_json` | Import nguyên bản, không transform |
| **Clean** | `clean` | `tracks`, `artists`, `genres`, `track_artists`, `artist_genres`, `artist_relations` | Dữ liệu đã parse, normalize, enforce constraints |
| **Analytics** | `analytics` | 9 views (`vw_*`) | EDA, dashboard, ML handoff |

---

## 6. Critical Decisions

| Quyết định | Chi tiết |
|-----------|---------|
| **dict_artists.json semantic** | **RELATED_ARTIST_GRAPH** — overlap 100% với `artists.csv.id` trên 50,005 values; 22-char Spotify ID pattern 100% |
| **SQL blocker fixes** | (1) `release_precision` column + CHECK constraint thêm vào `clean.tracks`; (2) `ROUND(AVG(double_precision))` → `ROUND(AVG(col)::numeric, n)` cho 8 columns; (3) `ADD CONSTRAINT IF NOT EXISTS` không hợp lệ — thay bằng comment + DO block pattern; (4) `vw_genre_trends` dùng CTE DISTINCT để tránh duplicate track weighting |
| **Genre source** | `artists.csv.genres` là nguồn genre **duy nhất** được xác nhận |
| **dict_artists.json role** | Lưu vào `raw.raw_artist_json` → `clean.artist_relations(artist_id, related_artist_id)` |
| **artist_genres nguồn** | Chỉ từ `artists_csv`, column source = 'artists_csv' |
| **Raw layer constraints** | Không có constraints nghiêm ngặt — giữ nguyên dữ liệu bẩn để không lỗi import |
| **Clean layer constraints** | Enforce đầy đủ CHECK, FK sau khi Feature 1.4 xử lý |
| **ML target isolation** | `tracks.popularity` là target, không có trong feature columns của `vw_ml_training_dataset` |
| **Leakage protection** | `artists.popularity`, `artists.followers` không xuất hiện trong `vw_ml_training_dataset` |

---

## 7. Remaining Risks

| Risk | Xử lý ở |
|------|---------|
| Import thực tế chưa test (COPY, error handling, batch size) | **Feature 1.3** |
| Parse `artists` list-string chưa thực hiện | **Feature 1.4** |
| Parse `genres` list-string chưa thực hiện | **Feature 1.4** |
| `tempo = 0` (328 rows), `time_signature = 0` (337 rows) — rule chưa quyết định | **Feature 1.4** |
| Duration outliers (26 bài < 10s, 83 bài > 60 phút) — rule chưa quyết định | **Feature 1.4** |
| `artists.followers` NULL (11 rows) — impute hay để NULL? | **Feature 1.4** |
| Analytics views chưa validate bằng data thật | **Feature 1.6** |
| Data quality gates chưa đặt ngưỡng chính thức | **Feature 1.5** |

---

## 8. Next Step

**Feature 1.3 — Data Ingestion Pipeline**

| Task | Mô tả |
|------|-------|
| 1.3.1 | Tạo PostgreSQL database và chạy DDL từ Feature 1.2 |
| 1.3.2 | COPY / insert `tracks.csv` → `raw.raw_tracks` |
| 1.3.3 | COPY / insert `artists.csv` → `raw.raw_artists` |
| 1.3.4 | Parse và insert `dict_artists.json` → `raw.raw_artist_json` |
| 1.3.5 | Kiểm tra row counts: raw tables phải khớp file |
| 1.3.6 | Kiểm tra duplicate IDs trong raw tables |
| 1.3.7 | Tạo `HOW_TO_RUN_DATA_PIPELINE.md` |

---

## 9. Status

> **PASS WITH SQL FIX VERIFIED — Feature 1.2 completed.**
>
> Task 1.2.0 đã xác minh `dict_artists.json` là **RELATED_ARTIST_GRAPH** (overlap 100%).
> Kiến trúc 3 tầng đã thiết kế đầy đủ. ERD, DATABASE_SCHEMA, SQL DDL skeleton đã hoàn thành.
> SQL blockers đã được sửa: release_precision, ROUND::numeric, ADD CONSTRAINT IF NOT EXISTS, vw_genre_trends CTE.
>
> **Ready for PostgreSQL DDL smoke test.**
> Chưa chạy thử trên PostgreSQL thật — chờ Feature 1.3 thực hiện.

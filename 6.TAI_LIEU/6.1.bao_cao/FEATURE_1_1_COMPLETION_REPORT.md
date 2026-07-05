# FEATURE 1.1 COMPLETION REPORT

## 1. Feature

**Feature 1.1 — Dataset Audit & Data Dictionary**

| Trường | Thông tin |
|--------|-----------|
| EPIC | EPIC 1 — Data Foundation & Data Understanding |
| Dự án | HitRadar Pro |
| Ngày hoàn thành | 2026-07-05 |
| Trạng thái | **PASS WITH WARNINGS** |

---

## 2. Owner

**Đạt** — phụ trách EPIC 1

---

## 3. Completed Tasks

| Task | Mô tả | Trạng thái |
|------|-------|-----------|
| Task 1.1.1 | Kiểm tra raw input thực tế: `tracks.csv`, `artists.csv`, `dict_artists.json` | **DONE** |
| Task 1.1.2 | Ghi nhận số dòng, số cột, dung lượng từng file | **DONE** |
| Task 1.1.3 | Lập data dictionary draft cho từng cột (25 columns) | **DONE** |
| Task 1.1.4 | Phân loại cột theo vai trò (ID / target / audio_feature / time / …) | **DONE** |
| Task 1.1.5 | Gắn nhãn cột dùng cho EDA / ML / dashboard | **DONE** |
| Task 1.1.6 | Xác định rủi ro dữ liệu ban đầu (14 risks, bao gồm outlier và release_date formats) | **DONE** |

---

## 4. Outputs Created

| File | Mô tả |
|------|-------|
| `9.SCRIPTS/audit_raw_data.py` | Script audit tự động — có thể chạy lại bất kỳ lúc nào |
| `9.SCRIPTS/_audit_results.json` | Raw audit numbers (không commit) |
| `6.TAI_LIEU/6.1.bao_cao/DATASET_AUDIT_REPORT.md` | Báo cáo audit đầy đủ 11 mục |
| `6.TAI_LIEU/6.1.bao_cao/DATA_DICTIONARY_DRAFT.md` | Data dictionary bản nháp 25 cột + feature engineering candidates |

---

## 5. Key Findings

| Hạng mục | Kết quả |
|----------|---------|
| tracks.csv rows | **586,672** |
| tracks.csv columns | **20** |
| artists.csv rows | **1,162,095** |
| artists.csv columns | **5** |
| dict_artists.json keys | **573,856** |
| Duplicate tracks | **0** (sạch) |
| Duplicate artists | **0** (sạch) |
| tracks.id unique | **YES** |
| artists.id unique | **YES** |
| Missing values | Gần như 0 — chỉ 71 track name và 3 artist name bị thiếu |
| Audio features range | **Tất cả trong range chuẩn** |
| Sanity PASS / WARN / FAIL | **12 / 5 / 0** |

**Rủi ro dữ liệu lớn nhất:**

| # | Rủi ro | Mức |
|---|--------|-----|
| 1 | `artists` và `id_artists` trong tracks.csv là list-string — cần parse thành bảng riêng | **Cao** |
| 2 | `dict_artists.json` values có thể là related artist IDs, không phải genre names — cần xác minh | **Rất cao** |
| 3 | `popularity` của artists.csv có leakage risk nếu dùng làm ML feature trực tiếp | **Cao** |
| 4 | `release_date` có 3 format: `YYYY-MM-DD` (76.4%), `YYYY` (23.3%), `YYYY-MM` (0.4%) | **Trung bình** |
| 5 | Outlier: 328 tempo=0, 337 time_signature=0, 26 tracks dưới 10s, 83 tracks trên 60 phút | **Thấp** |

**Missing values (đã xác nhận chính xác):**

| File | Column | Missing count |
|------|--------|--------------|
| tracks.csv | `name` | 71 (0.01%) |
| artists.csv | `name` | 3 (0.0003%) |
| artists.csv | `followers` | 11 (0.001%) |

**Active warnings — sẽ xử lý ở Feature 1.4 / 1.5:**

| Warning | Xử lý ở |
|---------|---------|
| `dict_artists.json` values chưa xác minh là genre hay related artist | Feature 1.2 |
| 328 tracks có `tempo = 0` | Feature 1.4 |
| 337 tracks có `time_signature = 0` | Feature 1.4 |
| 26 tracks `duration_ms < 10s`, 83 tracks `> 60 phút` | Feature 1.4 |
| `genres` trong artists.csv: nhiều giá trị là list rỗng `[]` | Feature 1.4 |
| `loudness` max = +5.376 dB | Feature 1.5 |

---

## 6. Columns Requiring Processing in Feature 1.4

| Column | File | Vấn đề | Xử lý |
|--------|------|--------|-------|
| `artists` | tracks.csv | List-string — cần tách tên nghệ sĩ | Parse → `clean_track_artists` |
| `id_artists` | tracks.csv | List-string — cần explode để join | Parse → `clean_track_artists` |
| `release_date` | tracks.csv | Mixed format | Parse → `release_year`, `release_month`, `decade` |
| `duration_ms` | tracks.csv | Cần đơn vị phút | Convert → `duration_min` |
| `tempo` | tracks.csv | 328 giá trị = 0 | Kiểm tra, xử lý outlier |
| `genres` | artists.csv | List-string, nhiều empty | Parse → `clean_artist_genres` |
| `dict_artists.json` | — | Values cần xác minh (genre hay related artist?), 317MB | Xác minh ở Feature 1.2, streaming parse ở Feature 1.4 |

---

## 7. Remaining Risks

| Risk | Xử lý ở |
|------|---------|
| Thiết kế schema PostgreSQL 3 tầng chưa có | **Feature 1.2** |
| Chưa kiểm tra import PostgreSQL | **Feature 1.3** |
| Parse artists/genres/dates chưa thực hiện | **Feature 1.4** |
| Data quality gates chưa đặt ngưỡng chính thức | **Feature 1.5** |
| Analytics views chưa có | **Feature 1.6** |
| EDA notebooks chưa có | **Feature 1.7** |

---

## 8. Next Step

**Feature 1.2 — Database Architecture**

> **Lưu ý bắt buộc:** Feature 1.2 phải xác minh semantic của `dict_artists.json` (task 1.2.0) trước khi thiết kế genre pipeline.

| Task | Việc cần làm | Output |
|------|-------------|--------|
| **1.2.0** | **Verify `dict_artists.json` semantic meaning** — đọc 10 cặp key-value, đối chiếu với `artists.csv`, xác định values là genre names hay related artist IDs | Ghi chú vào `DATABASE_SCHEMA.md` |
| 1.2.1 | Thiết kế raw schema | `raw_tracks`, `raw_artists`, `raw_artist_json` |
| 1.2.2 | Thiết kế clean schema | `clean_tracks`, `clean_artists`, `clean_genres`, `clean_track_artists`, `clean_artist_genres` |
| 1.2.3 | Thiết kế analytics views | `vw_tracks_by_decade`, `vw_audio_trends`, `vw_popularity_stats`, `vw_top_artists`, `vw_genre_trends`, `vw_ml_training_dataset`... |
| 1.2.4 | Định nghĩa keys, types, constraints | PKs, FKs, NOT NULL, CHECK |
| 1.2.5 | Vẽ ERD | `DATABASE_SCHEMA.md` + ERD diagram |

---

## 9. Status

> **PASS WITH WARNINGS — Feature 1.1 hotfix completed.**
>
> Tất cả mâu thuẫn tài liệu đã được giải quyết:
> - `dict_artists.json` value không còn gọi là "genre" — đánh dấu `unknown_need_review`.
> - `artists.popularity` chỉ nằm ở `dashboard_only`, không còn xuất hiện đồng thời ở `caution`.
> - `release_date` ghi đủ 3 format + normalize rule.
> - `genre_list` chỉ lấy từ `artists.csv.genres`.
> - Next Step Feature 1.2 dùng tên `raw_artist_json` và có task bắt buộc 1.2.0 xác minh dict_artists.json.
>
> **Được phép chuyển sang Feature 1.2 — Database Architecture.**

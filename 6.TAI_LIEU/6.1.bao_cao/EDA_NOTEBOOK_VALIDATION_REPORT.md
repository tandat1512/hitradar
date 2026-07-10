# EDA NOTEBOOK VALIDATION REPORT — FEATURE 1.7
**Project:** HitRadar Pro  
**Generated:** 2026-07-04  
**Validator:** Manual static check (notebook structure audit)

---

## Danh sách Notebooks

| # | File | Path |
|---|------|------|
| 01 | `01_dataset_overview.ipynb` | `3.NOTEBOOKS/3.4.eda/` |
| 02 | `02_popularity_analysis.ipynb` | `3.NOTEBOOKS/3.4.eda/` |
| 03 | `03_audio_features_distribution.ipynb` | `3.NOTEBOOKS/3.4.eda/` |
| 04 | `04_time_decade_trends.ipynb` | `3.NOTEBOOKS/3.4.eda/` |
| 05 | `05_artist_genre_analysis.ipynb` | `3.NOTEBOOKS/3.4.eda/` |
| 06 | `06_correlation_outlier_analysis.ipynb` | `3.NOTEBOOKS/3.4.eda/` |

---

## Chi tiết Validation

### Notebook 01 — Dataset Overview

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| Markdown mục tiêu | ✅ PASS |
| Kết nối DB (không hardcode password) | ✅ PASS — dùng `os.environ.get('PGPASSWORD')` |
| Query danh sách analytics views | ✅ PASS |
| Query row counts | ✅ PASS |
| Sample từ vw_ml_training_dataset | ✅ PASS |
| Sample từ vw_data_quality_report | ✅ PASS |
| Tóm tắt dataset (tracks/artists/genres/years/decades) | ✅ PASS |
| Biểu đồ track count by decade | ✅ PASS |
| Data quality warnings carry-forward | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 02 — Popularity Analysis

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| Markdown mục tiêu + cảnh báo label | ✅ PASS |
| Query vw_popularity_stats | ✅ PASS |
| Query vw_tracks_by_decade | ✅ PASS |
| Biểu đồ bar chart popularity buckets | ✅ PASS |
| Biểu đồ line chart avg/median by decade | ✅ PASS |
| Biểu đồ distribution histogram | ✅ PASS |
| Nhận xét: skew, imbalance, decade trend | ✅ PASS |
| Ghi rõ target_popularity là label | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 03 — Audio Features Distribution

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| Markdown mục tiêu | ✅ PASS |
| Query aggregate stats 7 features | ✅ PASS |
| Bảng summary (mean/median/min/max/null) | ✅ PASS |
| Biểu đồ mean vs median bar chart | ✅ PASS |
| Biểu đồ trend theo year (2x2 panel) | ✅ PASS |
| Kiểm tra NULL tempo/time_signature | ✅ PASS |
| Nhận xét: skew, trend, đề xuất transform | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 04 — Time & Decade Trends

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| Markdown mục tiêu | ✅ PASS |
| Query vw_tracks_by_decade | ✅ PASS |
| Query vw_explicit_by_decade | ✅ PASS |
| Query vw_duration_trends | ✅ PASS |
| Biểu đồ track count by decade | ✅ PASS |
| Biểu đồ duration by decade | ✅ PASS |
| Biểu đồ explicit count + ratio | ✅ PASS |
| Biểu đồ duration outliers by year | ✅ PASS |
| Nhận xét: mất cân bằng, explicit trend, duration | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 05 — Artist & Genre Analysis

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| Markdown mục tiêu | ✅ PASS |
| Query vw_top_artists (top 20 by count) | ✅ PASS |
| Query vw_top_artists (top 15 by avg popularity) | ✅ PASS |
| Query vw_genre_trends (top 20 genres) | ✅ PASS |
| Query genre trend top 5 by decade | ✅ PASS |
| Biểu đồ horizontal bar top 20 artists | ✅ PASS |
| Biểu đồ horizontal bar top 15 artists by popularity | ✅ PASS |
| Biểu đồ horizontal bar top 20 genres | ✅ PASS |
| Biểu đồ line chart genre trend by decade | ✅ PASS |
| Coverage warning check (96.54%) | ✅ PASS |
| Ghi rõ artist_popularity_dashboard_only | ✅ PASS |
| Nhận xét: bias, coverage, đề xuất ML | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 06 — Correlation & Outlier Analysis

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| Markdown mục tiêu + cảnh báo label | ✅ PASS |
| Query CORR() từ vw_ml_training_dataset | ✅ PASS |
| Không dùng target_popularity làm input | ✅ PASS |
| Biểu đồ correlation bar chart | ✅ PASS |
| Biểu đồ scatter binned (3 panels) | ✅ PASS |
| Bảng outlier analysis | ✅ PASS |
| Biểu đồ duration outliers by year | ✅ PASS |
| Nhận xét correlation table chi tiết | ✅ PASS |
| Nhận xét outlier risks | ✅ PASS |
| Đề xuất cho Feature 1.8 / EPIC 2 | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

## Tổng kết

| Notebook | Status |
|---------|--------|
| 01 — Dataset Overview | ✅ PASS |
| 02 — Popularity Analysis | ✅ PASS |
| 03 — Audio Features Distribution | ✅ PASS |
| 04 — Time & Decade Trends | ✅ PASS |
| 05 — Artist & Genre Analysis | ✅ PASS |
| 06 — Correlation & Outlier Analysis | ✅ PASS |

**Kết quả: 6/6 PASS**

## Ghi chú Validation

- Validation là **static check** (cấu trúc notebook) — không chạy kernel thực tế.
- Để xác nhận notebooks chạy hoàn toàn đúng, cần chạy `jupyter notebook` và execute từng cell.
- Tất cả queries dùng aggregate hoặc LIMIT — không in raw 586K rows.
- Password đọc từ `PGPASSWORD` env var — không hardcode.
- `target_popularity` được đánh dấu là LABEL trong tất cả notebooks có dùng.

**Overall Feature 1.7 Notebook Validation: PASS**

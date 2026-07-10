# EDA NOTEBOOK VALIDATION REPORT — FEATURE 1.7
**Project:** HitRadar Pro  
**Generated:** 2026-07-10  
**Validator:** Executed notebook validation via `nbconvert --execute`  
**Execution tool:** `python -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300`

---

## Execution Summary

| Notebook | Code cells | Executed | Errors | Images | Outputs | Size | Status |
|---------|-----------|---------|--------|--------|---------|------|--------|
| 01_dataset_overview | 8 | 8 | 0 | 1 | 14 | 62 KB | ✅ PASS |
| 02_popularity_analysis | 7 | 7 | 0 | 3 | 8 | 132 KB | ✅ PASS |
| 03_audio_features_distribution | 6 | 6 | 0 | 2 | 6 | 208 KB | ✅ PASS |
| 04_time_decade_trends | 6 | 6 | 0 | 3 | 8 | 208 KB | ✅ PASS |
| 05_artist_genre_analysis | 8 | 8 | 0 | 4 | 9 | 319 KB | ✅ PASS |
| 06_correlation_outlier_analysis | 7 | 7 | 0 | 3 | 8 | 257 KB | ✅ PASS |
| **TOTAL** | **42** | **42** | **0** | **16** | **53** | **1,186 KB** | **✅ PASS** |

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
| execution_count set (không null) | ✅ PASS — 8/8 cells |
| Không có traceback/error output | ✅ PASS — 0 errors |
| Kết nối DB (RuntimeError nếu không set PGPASSWORD) | ✅ PASS — không hardcode |
| Query danh sách analytics views | ✅ PASS |
| Query row counts | ✅ PASS |
| Sample từ vw_tracks_overview (có cột name) | ✅ PASS |
| Sample từ vw_ml_training_dataset (không có name) | ✅ PASS |
| Sample từ vw_data_quality_report | ✅ PASS |
| Tóm tắt dataset (tracks/artists/genres/years/decades) | ✅ PASS |
| Biểu đồ track count by decade (image/png) | ✅ PASS — 1 image |
| Data quality warnings carry-forward | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 02 — Popularity Analysis

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| execution_count set | ✅ PASS — 7/7 cells |
| Không có traceback/error output | ✅ PASS — 0 errors |
| Markdown mục tiêu + cảnh báo label | ✅ PASS |
| Query vw_popularity_stats | ✅ PASS |
| Query vw_tracks_by_decade | ✅ PASS |
| Biểu đồ bar popularity buckets (×2 panel) | ✅ PASS — 1 image |
| Biểu đồ line avg/median by decade | ✅ PASS — 1 image |
| Biểu đồ distribution histogram | ✅ PASS — 1 image |
| Ghi rõ target_popularity là label | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 03 — Audio Features Distribution

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| execution_count set | ✅ PASS — 6/6 cells |
| Không có traceback/error output | ✅ PASS — 0 errors |
| Query aggregate stats 7 features | ✅ PASS |
| Bảng summary (mean/median/min/max/null) | ✅ PASS |
| Biểu đồ mean vs median | ✅ PASS — 1 image |
| Biểu đồ trend theo year (2×2 panel) | ✅ PASS — 1 image |
| Kiểm tra NULL tempo/time_signature | ✅ PASS |
| Nhận xét: skew, trend, đề xuất transform | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 04 — Time & Decade Trends

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| execution_count set | ✅ PASS — 6/6 cells |
| Không có traceback/error output | ✅ PASS — 0 errors |
| Query vw_tracks_by_decade | ✅ PASS |
| Query vw_explicit_by_decade | ✅ PASS |
| Query vw_duration_trends | ✅ PASS |
| Biểu đồ track count + duration by decade | ✅ PASS — 1 image |
| Biểu đồ explicit count + ratio | ✅ PASS — 1 image |
| Biểu đồ duration outliers by year | ✅ PASS — 1 image |
| Nhận xét: mất cân bằng, explicit trend, duration | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

### Notebook 05 — Artist & Genre Analysis

| Check | Result |
|-------|--------|
| File tồn tại | ✅ PASS |
| execution_count set | ✅ PASS — 8/8 cells |
| Không có traceback/error output | ✅ PASS — 0 errors |
| Query vw_top_artists (top 20 by count) | ✅ PASS |
| Query vw_top_artists (top 15 by avg popularity) | ✅ PASS |
| Query vw_genre_trends (top 20 genres) | ✅ PASS |
| Query genre trend top 5 by decade | ✅ PASS |
| Biểu đồ top 20 artists by count | ✅ PASS — 1 image |
| Biểu đồ top 15 artists by popularity | ✅ PASS — 1 image |
| Biểu đồ top 20 genres | ✅ PASS — 1 image |
| Biểu đồ genre trend by decade | ✅ PASS — 1 image |
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
| execution_count set | ✅ PASS — 7/7 cells |
| Không có traceback/error output | ✅ PASS — 0 errors |
| Markdown mục tiêu + cảnh báo label | ✅ PASS |
| Query CORR() từ vw_ml_training_dataset | ✅ PASS |
| Không dùng target_popularity làm input | ✅ PASS |
| Biểu đồ correlation bar chart | ✅ PASS — 1 image |
| Biểu đồ scatter binned (3 panels) | ✅ PASS — 1 image |
| Bảng outlier analysis | ✅ PASS |
| Biểu đồ duration outliers by year | ✅ PASS — 1 image |
| Nhận xét correlation + outlier risks | ✅ PASS |
| Đề xuất cho Feature 1.8 / EPIC 2 | ✅ PASS |
| Kết luận | ✅ PASS |
| **Status** | **✅ PASS** |

---

## Tổng kết

| Notebook | Code cells | Errors | Images | Status |
|---------|-----------|--------|--------|--------|
| 01 — Dataset Overview | 8 | 0 | 1 | ✅ PASS |
| 02 — Popularity Analysis | 7 | 0 | 3 | ✅ PASS |
| 03 — Audio Features Distribution | 6 | 0 | 2 | ✅ PASS |
| 04 — Time & Decade Trends | 6 | 0 | 3 | ✅ PASS |
| 05 — Artist & Genre Analysis | 8 | 0 | 4 | ✅ PASS |
| 06 — Correlation & Outlier Analysis | 7 | 0 | 3 | ✅ PASS |

**Kết quả: 6/6 PASS — EXECUTED**

## Ghi chú Validation

- Validation là **executed notebook validation** — chạy thật bằng `nbconvert --execute`, không phải static check.
- 42/42 code cells có `execution_count` hợp lệ (không null).
- 0 traceback/error trong tất cả outputs.
- 16 biểu đồ (image/png) được tạo ra.
- Password: dùng `os.environ.get("PGPASSWORD")` với `RuntimeError` nếu không set — không hardcode.
- Tổng kích thước notebooks sau execution: ~1,186 KB.

**Overall Feature 1.7 Notebook Validation: ✅ PASS — EXECUTED**

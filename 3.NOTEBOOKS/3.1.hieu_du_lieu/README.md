# Data Understanding Guide — HitRadar Pro

**Vị trí:** `3.NOTEBOOKS/3.1.hieu_du_lieu/`

## Folder này là gì?

Đây là bộ tài liệu **hỗ trợ hiểu dữ liệu** cho dự án HitRadar Pro.  
Mục đích duy nhất: giúp người mới (hoặc người quay lại sau thời gian) đọc và hiểu nhanh dataset, các bảng/views, notebooks EDA, và những insight quan trọng.

> **Folder này KHÔNG phải WBS task mới.**  
> Không có pipeline. Không ảnh hưởng database hay reports chính thức.

### Đọc trực quan (khuyến nghị)

Mở **`01_data_understanding.ipynb`** → Run All → xem bảng + **13 biểu đồ** (histogram, dumbbell, pie...) trong một file duy nhất.

```powershell
$env:PGPASSWORD = "your_password"
jupyter notebook "3.NOTEBOOKS/3.1.hieu_du_lieu/01_data_understanding.ipynb"
```

---

## Tài liệu chính thức (không nằm ở đây)

| Loại | Vị trí |
|------|--------|
| 6 EDA Notebooks | `3.NOTEBOOKS/3.4.eda/` |
| EDA Insights Report | `6.TAI_LIEU/6.1.bao_cao/EDA_INSIGHTS_REPORT.md` |
| Notebook Validation | `6.TAI_LIEU/6.1.bao_cao/EDA_NOTEBOOK_VALIDATION_REPORT.md` |
| Feature 1.7 Completion | `6.TAI_LIEU/6.1.bao_cao/FEATURE_1_7_COMPLETION_REPORT.md` |
| Analytics Views Report | `6.TAI_LIEU/6.1.bao_cao/ANALYTICS_VIEWS_REPORT.md` |
| Analytics View Validation | `6.TAI_LIEU/6.1.bao_cao/ANALYTICS_VIEW_VALIDATION_REPORT.md` |
| Pipeline Guide | `6.TAI_LIEU/6.1.bao_cao/HOW_TO_RUN_DATA_PIPELINE.md` |

---

## 6 EDA Notebooks (đọc theo thứ tự)

| # | File | Câu hỏi trả lời |
|---|------|----------------|
| 01 | `01_dataset_overview.ipynb` | Dataset có gì? Bao nhiêu tracks/artists/genres? |
| 02 | `02_popularity_analysis.ipynb` | Popularity (label ML) phân bố như thế nào? |
| 03 | `03_audio_features_distribution.ipynb` | 7 audio features phân bố và thay đổi thế nào? |
| 04 | `04_time_decade_trends.ipynb` | Dataset lệch thời gian ra sao? Explicit tăng thế nào? |
| 05 | `05_artist_genre_analysis.ipynb` | Ai nhiều bài nhất? Genre nào chiếm ưu thế? |
| 06 | `06_correlation_outlier_analysis.ipynb` | Feature nào liên quan đến popularity? Outlier nào cần xử lý? |

---

## Nội dung folder này

| File | Mô tả | Đọc khi nào |
|------|-------|------------|
| `README.md` | File này | Luôn đọc trước |
| **`01_data_understanding.ipynb`** | **Guide trực quan — text + bảng + 13 biểu đồ (có histogram audio)** | **Bắt đầu ở đây (khuyến nghị)** |
| `INDEX.md` | Mục lục và lộ trình đọc | Xem trước khi chọn file |
| `01_tong_quan_du_lieu.md` | Dataset có gì, số liệu tổng quan | Bắt đầu ở đây |
| `02_giai_thich_bang_va_views.md` | Giải thích từng bảng và analytics view | Khi cần hiểu cấu trúc |
| `03_cach_doc_eda_notebooks.md` | Hướng dẫn đọc 6 notebooks | Trước khi mở Jupyter |
| `04_giai_thich_genres_artists_tracks.md` | Track/Artist/Genre là gì, tại sao lại phức tạp | Khi bị rối về genre |
| `05_giai_thich_popularity_audio_features.md` | Popularity và 10 audio features | Trước khi làm ML |
| `06_cau_hoi_tu_kiem_tra_hieu_du_lieu.md` | 15 câu hỏi tự kiểm tra + đáp án | Sau khi đọc xong |
| `07_tom_tat_insight_cho_epic_2.md` | Checklist Must/Should/Risk cho EPIC 2 | Trước khi bắt đầu EPIC 2 |

---

## Hướng dẫn đọc theo mục tiêu

**Mới vào dự án lần đầu:**  
**`01_data_understanding.ipynb`** (Run All) → `01_tong_quan_du_lieu.md` → `02_giai_thich_bang_va_views.md`

**Cần hiểu dữ liệu để làm ML:**  
`04_giai_thich_genres_artists_tracks.md` → `05_giai_thich_popularity_audio_features.md` → `07_tom_tat_insight_cho_epic_2.md`

**Tự kiểm tra đã hiểu chưa:**  
`06_cau_hoi_tu_kiem_tra_hieu_du_lieu.md`

**Chuẩn bị Feature 1.8:**  
`07_tom_tat_insight_cho_epic_2.md`

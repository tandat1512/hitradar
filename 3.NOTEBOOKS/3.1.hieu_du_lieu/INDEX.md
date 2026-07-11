# INDEX — Data Understanding Guide

**Dự án:** HitRadar Pro | **EPIC 1** — Data Foundation & Data Understanding  
**Cập nhật:** 2026-07-10  
**Nguồn số liệu:** `EDA_INSIGHTS_REPORT.md`, `FEATURE_1_7_COMPLETION_REPORT.md`

---

## Đọc nhanh trong 10 phút

**Cách nhanh nhất:** Mở `01_data_understanding.ipynb` → Run All (có bảng + 8 biểu đồ).

Hoặc đọc 3 file markdown:

1. **`01_data_understanding.ipynb`** — 5 phút: guide trực quan (khuyến nghị)
2. **`05_giai_thich_popularity_audio_features.md`** — 3 phút: popularity và audio features
3. **`07_tom_tat_insight_cho_epic_2.md`** — 2 phút: EPIC 2 checklist

---

## Đọc đầy đủ trong 45 phút

| Thứ tự | File | Thời gian ước tính |
|--------|------|--------------------|
| 0 | **`01_data_understanding.ipynb`** | **10 phút (Run All)** |
| 1 | `README.md` | 2 phút |
| 2 | `01_tong_quan_du_lieu.md` | 5 phút |
| 3 | `02_giai_thich_bang_va_views.md` | 10 phút |
| 4 | `03_cach_doc_eda_notebooks.md` | 8 phút |
| 5 | `04_giai_thich_genres_artists_tracks.md` | 5 phút |
| 6 | `05_giai_thich_popularity_audio_features.md` | 7 phút |
| 7 | `06_cau_hoi_tu_kiem_tra_hieu_du_lieu.md` | 5 phút |
| 8 | `07_tom_tat_insight_cho_epic_2.md` | 3 phút |

---

## Đọc để chuẩn bị Feature 1.8

Feature 1.8 là ML-safe Dataset Handoff — xuất dataset sẵn sàng cho EPIC 2.  
Đọc theo thứ tự:

1. `05_giai_thich_popularity_audio_features.md` — hiểu label và features
2. `04_giai_thich_genres_artists_tracks.md` — hiểu genre encoding
3. `07_tom_tat_insight_cho_epic_2.md` — checklist handoff

---

## Đọc để chuẩn bị EPIC 2

EPIC 2 là Feature Engineering & Modeling. Đọc toàn bộ theo thứ tự đầy đủ, đặc biệt chú ý:

- `05_giai_thich_popularity_audio_features.md` — rủi ro từng feature
- `06_cau_hoi_tu_kiem_tra_hieu_du_lieu.md` — câu hỏi mức 3 (khó)
- `07_tom_tat_insight_cho_epic_2.md` — Must / Should / Risk

---

## Số liệu quan trọng cần nhớ

| Chỉ số | Giá trị | Nguồn |
|--------|---------|-------|
| Tổng tracks | 586,672 | `NB01 executed output` |
| Artists có track | 81,776 | `NB01 executed output` |
| Genres (clean.genres) | 5,366 | `EDA_INSIGHTS_REPORT.md` |
| Genres (track-linked) | 4,672 | `EDA_INSIGHTS_REPORT.md` |
| Năm phát hành | 1921–2021 (101 năm) | `NB01 executed output` |
| Popularity = 0 | 44,690 tracks (7.6%) | `NB06 executed output` |
| Correlation mạnh nhất | release_year = +0.591 | `NB06 executed output` |
| Tempo NULL | 328 tracks | `NB03 executed output` |
| Time_signature NULL | 337 tracks | `NB03 executed output` |
| track_artists coverage | 96.54% | `vw_data_quality_report` |

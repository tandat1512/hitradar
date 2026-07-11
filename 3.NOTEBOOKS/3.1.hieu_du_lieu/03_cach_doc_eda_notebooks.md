# 03 — Cách đọc 6 EDA Notebooks

> Nguồn: `EDA_NOTEBOOK_VALIDATION_REPORT.md`, `EDA_INSIGHTS_REPORT.md`  
> Notebooks: `3.NOTEBOOKS/3.4.eda/` — đã execute thật (42/42 cells, 0 errors)

---

## Trước khi mở Jupyter

1. Set password: `$env:PGPASSWORD = "your_password"` (PowerShell)
2. Mở folder: `3.NOTEBOOKS/3.4.eda/`
3. Đọc theo thứ tự **01 → 06** — mỗi notebook xây dựng trên insight của notebook trước

---

## Notebook 01 — Dataset Overview

**File:** `01_dataset_overview.ipynb`

| | |
|---|---|
| **Mục tiêu** | Kiểm tra dataset tồn tại, đủ lớn, views hoạt động, warnings được ghi nhận |
| **Views dùng** | Tất cả 10 analytics views, `vw_tracks_overview`, `vw_data_quality_report`, `vw_ml_training_dataset` |
| **Biểu đồ chính** | Bar chart: số tracks theo thập kỷ |
| **Insight cần nhớ** | 586,672 tracks, 81,776 artists, 4,672 track-linked genres, status PASS_WITH_WARNINGS |
| **Câu hỏi tự kiểm tra** | View nào có 12 rows? Tại sao không phải lỗi? Data quality status là gì? |

---

## Notebook 02 — Popularity Analysis

**File:** `02_popularity_analysis.ipynb`

| | |
|---|---|
| **Mục tiêu** | Hiểu phân bố `target_popularity` — đây là **label ML**, không phải input |
| **Views dùng** | `vw_popularity_stats`, `vw_tracks_by_decade`, `vw_ml_training_dataset` |
| **Biểu đồ chính** | Bar chart buckets, line chart popularity theo thập kỷ, histogram 0–100 |
| **Insight cần nhớ** | 75% bài có popularity ≤ 40; chỉ 0.1% (736 bài) > 80; 44,690 bài có popularity = 0 (7.6%); popularity tăng theo thời gian do Spotify time bias |
| **Câu hỏi tự kiểm tra** | Popularity là input hay target? Tại sao nhạc 2020s có avg cao hơn 1920s? |

---

## Notebook 03 — Audio Features Distribution

**File:** `03_audio_features_distribution.ipynb`

| | |
|---|---|
| **Mục tiêu** | Phân bố 7 audio features và xu hướng theo năm |
| **Views dùng** | `vw_tracks_overview`, `vw_audio_trends` |
| **Biểu đồ chính** | Bar chart mean/median 7 features; 2×2 panel trends theo year |
| **Insight cần nhớ** | Speechiness và instrumentalness lệch phải nặng (median ≈ 0); acousticness giảm mạnh theo thời gian; tempo NULL=328, time_signature NULL=337 |
| **Câu hỏi tự kiểm tra** | Feature nào cần log-transform? Feature nào có NULL cần impute? |

---

## Notebook 04 — Time & Decade Trends

**File:** `04_time_decade_trends.ipynb`

| | |
|---|---|
| **Mục tiêu** | Phân bố dataset theo thời gian, explicit trend, duration trend |
| **Views dùng** | `vw_tracks_by_decade`, `vw_explicit_by_decade`, `vw_duration_trends`, `vw_audio_trends` |
| **Biểu đồ chính** | Track count + duration by decade; explicit count + ratio; duration outliers by year |
| **Insight cần nhớ** | 1990s (108,875) + 2010s (105,245) chiếm ~36%; explicit tăng từ <0.2% (trước 1980s) → 23.1% (2020s); duration ổn định ~3–4 phút |
| **Câu hỏi tự kiểm tra** | Dataset có mất cân bằng thời gian không? Explicit có xu hướng tăng không? |

---

## Notebook 05 — Artist & Genre Analysis

**File:** `05_artist_genre_analysis.ipynb`

| | |
|---|---|
| **Mục tiêu** | Top artists, top genres, genre trend, coverage warning |
| **Views dùng** | `vw_top_artists`, `vw_genre_trends`, `vw_data_quality_report` |
| **Biểu đồ chính** | Top 20 artists (count), top 15 artists (popularity), top 20 genres, genre trend top 5 |
| **Insight cần nhớ** | Top artist: Die drei ??? (audio drama Đức); top genre: rock (32,026); track_artists coverage = 96.54%; không one-hot 4,672 genres |
| **Câu hỏi tự kiểm tra** | Tại sao top artist không phải Taylor Swift? Genre lấy từ đâu? Coverage 96.54% ảnh hưởng gì? |

---

## Notebook 06 — Correlation & Outlier Analysis

**File:** `06_correlation_outlier_analysis.ipynb`

| | |
|---|---|
| **Mục tiêu** | Feature nào liên quan đến popularity? Outlier nào cần xử lý trước ML? |
| **Views dùng** | `vw_ml_training_dataset`, `vw_tracks_overview`, `vw_duration_trends`, `vw_data_quality_report` |
| **Biểu đồ chính** | Correlation bar chart; 3 scatter binned panels; duration outlier chart |
| **Insight cần nhớ** | release_year corr=+0.59 (mạnh nhất, time bias); acousticness=-0.37; valence≈0; 44,690 bài popularity=0 cần quyết định xử lý |
| **Câu hỏi tự kiểm tra** | Feature nào có correlation mạnh nhất? Tại sao đó là "bẫy"? Outlier nào ảnh hưởng ML nhất? |

---

## Lộ trình đọc theo mục tiêu

| Mục tiêu | Đọc notebooks |
|----------|--------------|
| Hiểu dataset tổng quan | 01 |
| Hiểu label ML | 02 → 06 |
| Hiểu input features | 03 → 06 |
| Hiểu bias thời gian | 04 → 02 |
| Chuẩn bị EPIC 2 | 02 → 03 → 05 → 06 |

---

## Sau khi đọc xong 6 notebooks

Đọc tiếp reports chính thức để đối chiếu:
- `6.TAI_LIEU/6.1.bao_cao/EDA_INSIGHTS_REPORT.md`
- `6.TAI_LIEU/6.1.bao_cao/FEATURE_1_7_COMPLETION_REPORT.md`

Rồi tự kiểm tra bằng: `06_cau_hoi_tu_kiem_tra_hieu_du_lieu.md`

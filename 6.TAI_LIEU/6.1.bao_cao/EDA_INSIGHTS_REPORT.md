# EDA INSIGHTS REPORT — FEATURE 1.7
**Project:** HitRadar Pro  
**Owner:** Đạt  
**Date:** 2026-07-04  
**Status:** PASS_WITH_WARNINGS

---

## 1. Purpose

Phân tích khám phá dữ liệu (EDA) cho dataset Spotify/HitRadar từ analytics views.  
Mục tiêu:
- Hiểu phân bố và đặc điểm của 586,672 tracks.
- Xác định tình trạng dữ liệu, outliers, và data quality issues.
- Cung cấp thông tin nền tảng cho Feature 1.8 ML-safe handoff và EPIC 2 Feature Engineering.

---

## 2. Data Sources

| View | Dùng trong |
|------|-----------|
| `analytics.vw_tracks_overview` | NB 01, 03 |
| `analytics.vw_tracks_by_decade` | NB 01, 02, 04 |
| `analytics.vw_audio_trends` | NB 03, 04 |
| `analytics.vw_popularity_stats` | NB 02 |
| `analytics.vw_top_artists` | NB 05 |
| `analytics.vw_genre_trends` | NB 05 |
| `analytics.vw_explicit_by_decade` | NB 04 |
| `analytics.vw_duration_trends` | NB 04, 06 |
| `analytics.vw_data_quality_report` | NB 01, 05 |
| `analytics.vw_ml_training_dataset` | NB 01, 02, 06 |

---

## 3. Dataset Overview

| Metric | Giá trị |
|--------|---------|
| Tổng tracks | **586,672** |
| Artists có track | **81,776** |
| Unique genres | **4,672** |
| Số năm phát hành | **101** (1921–2021) |
| Số thập kỷ | **12** (1900–2020) |
| Thập kỷ nhiều tracks nhất | **1990s** (108,875) |

---

## 4. Popularity Insights

- **Phân bố rất lệch về thấp (heavy low tail):**
  - 0–20: 37.5% (219,988 tracks)
  - 21–40: 37.3% (219,003 tracks)
  - 41–60: 20.9% (122,813 tracks)
  - 61–80: 4.1% (24,132 tracks)
  - 81–100: 0.1% (736 tracks)
- **44,690 tracks** có `target_popularity = 0` (~7.6%) — inactive/unlisted, không phải lỗi dữ liệu.
- **Popularity tăng theo thời gian:** 1920s avg ≈ 1 → 2020s avg ≈ 42.
  - Nguyên nhân: Spotify tính popularity dựa trên streams gần đây — tracks mới có lợi thế hơn tracks cũ.
- **Implication cho ML:** class imbalance nghiêm trọng — cần xem xét log-transform, class binning, hoặc sampling strategy ở EPIC 2.

---

## 5. Audio Feature Insights

| Feature | Mean | Đặc điểm phân bố |
|---------|------|-----------------|
| danceability | 0.564 | Phân bố đều, ít lệch |
| energy | 0.542 | Phân bố rộng, phù hợp ML |
| speechiness | 0.105 | **Rất lệch phải** — zero-inflated, cần log-transform |
| acousticness | 0.450 | **Bimodal** — acoustic vs non-acoustic |
| instrumentalness | 0.114 | **Rất lệch phải** — zero-inflated |
| liveness | 0.214 | Lệch phải — hầu hết studio recordings |
| valence | 0.552 | Phân bố tương đối đều |

**Xu hướng theo thời gian:**
- Acousticness giảm mạnh: ~0.90 (1920s) → ~0.28 (2020s) — nhạc điện tử tăng.
- Danceability và energy tăng dần từ 1950s đến 2020s.
- Valence không có xu hướng rõ ràng.
- **NULL:** tempo=328, time_signature=337 — cần impute ở EPIC 2.

---

## 6. Time & Decade Insights

- **Dataset mất cân bằng thời gian:** 1990s (108,875) và 2010s (105,245) chiếm ~36% tổng.
  - 1920s chỉ có 7,610 tracks (~1.3%) — sparse historical data.
- **Explicit content tăng rõ rệt:**
  - 1980s: 1.1% → 1990s: 3.1% → 2000s: 4.9% → 2010s: 11.8% → **2020s: 23.1%**
- **Duration ổn định:** ~3.3–4.2 phút qua các thời kỳ, không có xu hướng mạnh.
  - Duration outliers: short=26 (<10s), long=83 (>60min) — giữ theo rule F1.4.

---

## 7. Artist & Genre Insights

- **Artist bias:** Top artist là "Die drei ???\" (3,856 tracks — German radio drama), Lata Mangeshkar (2,605 — Indian).
  - Dataset có bias đa quốc tế và long-tail distribution (phần lớn artists có rất ít tracks).
- **Genre bias:** Top genres: rock (32,026), adult standards (26,688), classic rock (23,808), filmi (19,557), classical (18,995).
  - Dataset thiên về rock và nhạc cổ điển — đa dạng nhưng có bias.
- **Coverage warning:** track_artists = 96.54% — 26,224 tracks thiếu artist info.
- **Genre join coverage = 100%** — sạch, không ảnh hưởng phân tích.
- **Đề xuất:** Sử dụng genre như categorical feature trong ML nhưng cần embedding hoặc top-N truncation (4,672 genres quá nhiều cho one-hot).

---

## 8. Correlation & Outlier Insights

**Correlation với `target_popularity` (label):**

| Feature | Correlation | Nhận xét |
|---------|------------|---------|
| `release_year` | **+0.5909** | Mạnh nhất — time bias của Spotify |
| `loudness` | **+0.3270** | Trung bình dương |
| `energy` | **+0.3023** | Trung bình dương |
| `danceability` | **+0.1870** | Yếu dương |
| `tempo` | **+0.0720** | Rất yếu |
| `duration_min` | **+0.0277** | Gần 0 |
| `valence` | **+0.0046** | Gần 0 |
| `speechiness` | **−0.0474** | Rất yếu âm |
| `liveness` | **−0.0487** | Rất yếu âm |
| `instrumentalness` | **−0.2365** | Yếu âm |
| `acousticness` | **−0.3709** | Trung bình âm — nhạc acoustic ~ ít phổ biến |

**Outlier summary:**

| Loại | Số lượng | % |
|------|----------|---|
| Duration short (<10s) | 26 | 0.004% |
| Duration long (>60min) | 83 | 0.014% |
| Loudness > 0 dB | 219 | 0.037% |
| Tempo NULL | 328 | 0.056% |
| Time_signature NULL | 337 | 0.057% |
| target_popularity = 0 | 44,690 | 7.62% |

---

## 9. Data Quality Warnings Carried Forward

Những warning sau được carry-forward từ Feature 1.5 và cần được xử lý ở EPIC 2:

| Warning | Giá trị | Action cần ở EPIC 2 |
|---------|---------|---------------------|
| Duration short (<10s) | **26 tracks** | Filter hoặc giữ tùy ML strategy |
| Duration long (>60min) | **83 tracks** | Filter hoặc giữ tùy ML strategy |
| Loudness > 0 dB | **219 tracks** | Clip hoặc investigate |
| track_artists coverage | **96.54%** | Xử lý NULL artist khi dùng artist features |
| artist_relations diff | **1** | Không ảnh hưởng analysis |
| tracks.name NULL | **71** | Không dùng name làm feature |
| artists.followers NULL | **11** | Impute nếu dùng followers |
| Tempo NULL | **328** | Impute (median/mean) trước khi train |
| Time_signature NULL | **337** | Impute (mode) trước khi train |

---

## 10. ML Handoff Notes

- **`target_popularity`** là label ML — KHÔNG dùng làm input feature.
- **`artists.popularity`** (chỉ có trong `vw_top_artists.artist_popularity_dashboard_only`) — KHÔNG dùng làm input feature mặc định do data leakage risk.
- **`release_year`** có tương quan cao nhất (+0.59) — cần đánh giá kỹ risk data leakage về thời gian khi split train/test.
- **Cần ở EPIC 2:**
  - Scale/normalize tất cả numeric features.
  - Log-transform `speechiness`, `instrumentalness`.
  - Impute `tempo` (328 NULL), `time_signature` (337 NULL).
  - Quyết định xử lý 44,690 tracks với `popularity = 0`.
  - Encode genre (top-N hoặc embedding).
  - Train/test split theo thời gian (temporal split) để tránh leakage.

---

## 11. Conclusion

Dataset HitRadar (586,672 tracks, 101 năm, 4,672 genres) đã qua pipeline F1.1–F1.6 sạch và sẵn sàng.

**Status: PASS_WITH_WARNINGS**

- ✅ Không có lỗi cấu trúc dữ liệu.
- ✅ 10 analytics views hoạt động đúng.
- ✅ 6 EDA notebooks đã tạo và chứa insight có bằng chứng từ actual data.
- ⚠️ Các warnings về outliers và coverage được ghi nhận đầy đủ.
- ⚠️ Class imbalance (popularity) và time bias (release_year) cần chiến lược ML phù hợp ở EPIC 2.

**Dataset sẵn sàng cho Feature 1.8 — ML-safe Dataset Handoff.**

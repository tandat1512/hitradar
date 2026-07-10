# FEATURE 1.7 COMPLETION REPORT
**Project:** HitRadar Pro  
**Feature:** 1.7 — EDA & Data Understanding Notebooks  
**Owner:** Đạt  
**Completed:** 2026-07-10  
**Status:** ✅ PASS_WITH_WARNINGS — EXECUTED

---

## 1. Feature

**Feature 1.7 — EDA & Data Understanding Notebooks**  
Thuộc EPIC 1: Data Foundation & Data Understanding

**Mục tiêu:** Tạo 6 EDA notebooks chính thức để phân tích dữ liệu Spotify/HitRadar từ analytics views, trực quan hóa kết quả, rút insight từ dữ liệu thực, và tạo báo cáo EDA phục vụ Feature 1.8 ML-safe handoff.

---

## 2. Owner

**Đạt** — EPIC 1 Lead

---

## 3. Completed Tasks (WBS)

| WBS | Task | Status |
|-----|------|--------|
| 1.7.1 | Notebook 01 — Dataset Overview | ✅ DONE — Executed |
| 1.7.2 | Notebook 02 — Popularity Analysis | ✅ DONE — Executed |
| 1.7.3 | Notebook 03 — Audio Features Distribution | ✅ DONE — Executed |
| 1.7.4 | Notebook 04 — Time & Decade Trends | ✅ DONE — Executed |
| 1.7.5 | Notebook 05 — Artist & Genre Analysis | ✅ DONE — Executed |
| 1.7.6 | Notebook 06 — Correlation & Outlier Analysis | ✅ DONE — Executed |

---

## 4. Outputs Created

### Notebooks (6 files — Executed)
```
3.NOTEBOOKS/3.4.eda/
├── 01_dataset_overview.ipynb            (executed, 8 cells, 1 chart, 62 KB)
├── 02_popularity_analysis.ipynb         (executed, 7 cells, 3 charts, 132 KB)
├── 03_audio_features_distribution.ipynb (executed, 6 cells, 2 charts, 208 KB)
├── 04_time_decade_trends.ipynb          (executed, 6 cells, 3 charts, 208 KB)
├── 05_artist_genre_analysis.ipynb       (executed, 8 cells, 4 charts, 319 KB)
└── 06_correlation_outlier_analysis.ipynb(executed, 7 cells, 3 charts, 257 KB)
```

### Reports/Documents (không gán WBS vì không có trong tracker chính thức)
```
6.TAI_LIEU/6.1.bao_cao/
├── EDA_INSIGHTS_REPORT.md               (EDA summary report)
├── EDA_NOTEBOOK_VALIDATION_REPORT.md    (executed notebook validation)
└── FEATURE_1_7_COMPLETION_REPORT.md     (file này)
```

---

## 5. Key Insights Summary

1. **Dataset scale:** 586,672 tracks, 81,776 artists, 4,672 genres, 101 năm (1921–2021).

2. **Popularity severely imbalanced:** 75% tracks có popularity ≤ 40, chỉ 0.1% có popularity > 80. 44,690 tracks có popularity = 0 (~7.6%).

3. **release_year là predictor mạnh nhất** (corr = +0.59 với target) — do Spotify tính popularity dựa trên streams gần đây. Cần xử lý time bias khi split train/test.

4. **Acousticness giảm mạnh theo thời gian** (~0.90 → 0.28 từ 1920s đến 2020s) — phản ánh sự chuyển dịch từ nhạc acoustic sang điện tử.

5. **Speechiness và instrumentalness rất lệch phải (zero-inflated)** — cần log-transform ở EPIC 2.

6. **Explicit content tăng theo thập kỷ:** 2020s đã đạt 23.1% — tăng từ < 1% ở 1970s.

7. **Dataset mất cân bằng thời gian:** 1990s + 2010s chiếm ~36% tổng. 1920s–1940s rất sparse.

8. **Top genres bias:** rock, classic rock, filmi — dataset thiên về Western rock và Indian film music.

9. **Outliers nhỏ:** duration short=26, long=83, loudness>0=219 — tỷ lệ rất nhỏ (<0.04%).

10. **Tempo (328) và time_signature (337) NULL** — cần impute trước khi train.

---

## 6. Warnings / Limitations

Carry-forward từ Feature 1.5:

| Warning | Giá trị | Ghi chú |
|---------|---------|---------|
| Duration short (<10s) | 26 tracks | Giữ theo rule F1.4 |
| Duration long (>60min) | 83 tracks | Giữ theo rule F1.4 |
| Loudness > 0 dB | 219 tracks | Hiếm, hợp lệ |
| track_artists coverage | 96.54% | 26,224 tracks thiếu artist |
| artist_relations diff | 1 | ON CONFLICT duplicate |
| tracks.name NULL | 71 | Không dùng name làm feature |
| artists.followers NULL | 11 | Impute nếu cần |
| Tempo NULL | 328 | Cần impute EPIC 2 |
| Time_signature NULL | 337 | Cần impute EPIC 2 |

**Giới hạn notebooks:**  
- Validation đã chạy thật bằng nbconvert --execute. 42/42 code cells executed, 0 errors, 16 biểu đồ. Không còn là static check.
- Correlation tính bằng aggregate SQL CORR() — không qua pandas/scipy nhưng kết quả tương đương.
- Không dùng seaborn, không load raw 586K rows vào RAM — thiết kế nhẹ và production-safe.

---

## 7. ML Handoff Notes

Những điểm bắt buộc cho Feature 1.8 và EPIC 2:

- **Label:** `target_popularity` = `clean.tracks.popularity` — KHÔNG dùng làm input feature.
- **Leakage risk cao:** `artists.popularity` (trong vw_top_artists) và `release_year` (corr=0.59) — cần xem xét kỹ trong split strategy.
- **Imputation cần thiết:** tempo (328), time_signature (337), artists.followers (11).
- **Scaling:** Tất cả numeric features cần MinMax hoặc StandardScaler.
- **Transform:** speechiness, instrumentalness cần log-transform (zero-inflated).
- **Genre encoding:** 4,672 genres — dùng top-N hoặc embedding, KHÔNG one-hot toàn bộ.
- **Train/test split:** Temporal split (theo release_year) để tránh future data leakage.
- **Class imbalance:** Cân nhắc class weights, resampling, hoặc regression thay vì classification.

---

## 8. Next Step

**Feature 1.8 — ML-safe Dataset Handoff / Final EPIC 1 Handoff**

Nhiệm vụ:
- Tạo final ML-ready dataset export từ `analytics.vw_ml_training_dataset`.
- Document feature list, dtypes, và null counts chính thức.
- Xác nhận train/test split strategy.
- Tạo EPIC 1 completion summary.

---

## 9. Status

### Feature 1.7 Checklist

- [x] 6 notebooks đã tạo trong `3.NOTEBOOKS/3.4.eda/`
- [x] **6 notebooks đã execute thật** — 42/42 cells, 0 errors, 16 biểu đồ
- [x] Tất cả notebooks có markdown tiếng Việt, mục tiêu, query, bảng, biểu đồ, nhận xét, kết luận
- [x] Không hardcode password — dùng `os.environ.get("PGPASSWORD")` + `RuntimeError` nếu không set
- [x] Không import raw data / không clean lại dữ liệu
- [x] Không train model / không split train/test
- [x] Không tạo fake insight — tất cả có bằng chứng từ executed notebook outputs
- [x] `target_popularity` được đánh dấu là label trong tất cả notebooks
- [x] EDA_INSIGHTS_REPORT.md đã tạo (ngày 2026-07-10)
- [x] EDA_NOTEBOOK_VALIDATION_REPORT.md đã tạo (executed validation)
- [x] Warnings carry-forward được ghi nhận đầy đủ
- [x] Genre discrepancy giải thích rõ: clean.genres=5,366 / vw_genre_trends=4,672 / diff=694

### Final Status: **PASS_WITH_WARNINGS — EXECUTED**

Reason: 6/6 notebooks execute thành công, 0 errors, insight có bằng chứng từ outputs thật. Warnings từ F1.5 đã ghi nhận và không ảnh hưởng chất lượng EDA.

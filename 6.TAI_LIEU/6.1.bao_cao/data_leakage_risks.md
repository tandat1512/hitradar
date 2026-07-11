# DATA LEAKAGE RISKS — FEATURE 1.8

**Feature:** 1.8 — ML-Safe Dataset Handoff  
**Dataset:** `analytics.vw_ml_ready_dataset`  
**Owner:** Đạt  
**Nguồn bằng chứng:** EDA_INSIGHTS_REPORT.md, ANALYTICS_VIEWS_REPORT.md, Feature 1.7 carry-forward

---

## 1. Target Leakage

**Rủi ro:** Dùng `target_popularity` làm input feature khi train.

**Biện pháp EPIC 1:**
- `target_popularity` chỉ xuất hiện với vai trò **label**.
- Validation script FAIL nếu có cột `popularity` raw hoặc alias leakage.

**Khuyến nghị EPIC 2:**
- Tách rõ `X` (features) và `y` (target) trước mọi bước preprocessing.
- Không tạo feature derived từ target (bucket, group, residual) trước split.

---

## 2. Popularity Proxy Leakage

**Rủi ro:** Dùng `artists.popularity` hoặc aggregate popularity theo artist/genre.

**Bằng chứng:**
- `artists.popularity` có correlation cao với track popularity (EDA).
- Aggregate popularity (avg_artist_popularity, avg_genre_popularity) có thể encode target distribution.

**Biện pháp EPIC 1:**
- `vw_ml_ready_dataset` **không** chứa artists.popularity, avg_artist_popularity, avg_genre_popularity.
- Forbidden column check trong validation script.

**Khuyến nghị EPIC 2:**
- Không thêm artist/genre popularity làm default baseline feature.
- Nếu nghiên cứu mở rộng, cần time-aware cutoff (chỉ dùng popularity trước thời điểm release).

---

## 3. Time Leakage

**Rủi ro:** Model học time bias thay vì tín hiệu âm nhạc thật.

**Bằng chứng:**
- `release_year` correlation **+0.5909** với `target_popularity` (EDA_INSIGHTS_REPORT).
- Tracks mới có lợi thế popularity trên Spotify (popularity phụ thuộc streams gần đây).

**Biện pháp EPIC 1:**
- Giữ `release_year`, `release_month`, `decade` như time-sensitive features (không loại bỏ).
- Ghi rõ trong feature_dictionary và handoff doc.

**Khuyến nghị EPIC 2:**
- **Temporal split** theo `release_year` (train = older, test = newer) thay vì random split.
- Hoặc time-aware cross-validation.
- Phân tích error theo decade và release_year.

---

## 4. Post-Outcome Leakage

**Rủi ro:** Dùng feature được tính **sau** thời điểm bài hát phát hành khi mục tiêu là dự đoán trước/đầu vòng đời.

**Ví dụ nguy hiểm:**
- `future_popularity`, stream count sau 30 ngày, playlist adds sau release.
- Global dataset statistics tính sau khi biết toàn bộ popularity.

**Biện pháp EPIC 1:**
- Baseline view chỉ chứa audio features và metadata release tại thời điểm snapshot dataset.
- Không có `future_popularity` column.

---

## 5. Genre Aggregation Leakage

**Rủi ro:** Tính genre popularity / genre statistics trên **toàn dataset** trước train/test split.

**Bằng chứng:**
- 4,672 track-linked genres (Feature 1.7 carry-forward).
- Genre-level aggregates có thể encode target distribution của test set.

**Biện pháp EPIC 1:**
- Genre không nằm trong baseline 20-column handoff view.

**Khuyến nghị EPIC 2:**
- Genre encoding/statistics **fit trên train only**.
- Target encoding, top-N multi-hot, hoặc embedding — không one-hot toàn bộ 4,672 genres mặc định.
- Không tính genre popularity global trước split.

---

## 6. Scaling / Imputation Leakage

**Rủi ro:** Fit imputer hoặc scaler trên toàn bộ data (bao gồm test) → leak thống kê test vào train.

**Biện pháp EPIC 1:**
- EPIC 1 **không** fit scaler/imputer.
- View giữ NULL thật (tempo=328, time_signature=337 NULL).
- Không có cột `imputed_*` hoặc `scaled_*`.

**Khuyến nghị EPIC 2:**
- Pipeline: split trước → fit imputer/scaler/encoder trên **train only** → transform train và test.
- Impute tempo (median), time_signature (mode) — statistics từ train fold.

---

## Validation Guardrails (Feature 1.8)

Validation script `validate_ml_ready_dataset.py` kiểm tra:
- Không có forbidden leakage columns
- `target_popularity` hợp lệ (0–100, no null)
- `track_id` unique, non-null
- Row count = 586,672

---

*Feature 1.8 — ML-Safe Dataset Handoff | HitRadar Pro*

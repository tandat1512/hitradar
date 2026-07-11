# ML EXCLUDED COLUMNS

**Feature:** 1.8 — ML-Safe Dataset Handoff  
**Dataset:** `analytics.vw_ml_ready_dataset`  
**Owner:** Đạt

Các cột hoặc nhóm cột **KHÔNG** được dùng làm input feature khi train model ở EPIC 2.

---

## 1. target_popularity

- **Lý do:** Đây là **label** (biến mục tiêu cần dự đoán), không phải input feature.
- **Rủi ro nếu dùng:** Target leakage — model học trực tiếp đáp án.

---

## 2. track_id

- **Lý do:** Identifier (định danh kỹ thuật), không có ý nghĩa dự đoán âm nhạc.
- **Mục đích hợp lệ:** Trace, debug, join với bảng khác sau inference.
- **Rủi ro nếu dùng:** Overfitting trên ID, không generalize.

---

## 3. artists.popularity / artist_popularity_dashboard_only

- **Lý do:** Leakage risk — popularity của artist là proxy rất mạnh của target_popularity.
- **Trạng thái:** Không có trong `vw_ml_ready_dataset` (đã loại bỏ ở EPIC 1).
- **Nguồn bằng chứng:** EDA_INSIGHTS_REPORT — artists.popularity excluded by design.

---

## 4. avg_artist_popularity / avg_genre_popularity / avg_track_popularity

- **Lý do:** Aggregate popularity có thể leak phân phối target, đặc biệt nếu tính trên toàn dataset trước split.
- **Trạng thái:** Không có trong baseline handoff view.

---

## 5. popularity_bucket / popularity_group

- **Lý do:** Derived từ target_popularity nếu tạo từ popularity — tương đương dùng label làm feature.
- **Trạng thái:** Không có trong handoff view.

---

## 6. train/test split columns (train_split, test_split, split)

- **Lý do:** Metadata quy trình ML, không phải feature âm nhạc.
- **Trạng thái:** EPIC 1 không tạo split columns — thuộc EPIC 2.

---

## 7. raw name / artist name (track name, artist name)

- **Lý do:** Text leakage/noisy, không nằm trong baseline dataset EPIC 1.
- **Ghi chú:** Nếu EPIC 2 muốn dùng text, cần pipeline NLP riêng và đánh giá leakage riêng.

---

## 8. Imputed / scaled / encoded columns (imputed_*, scaled_*, label_encoded)

- **Lý do:** EPIC 1 không fit imputer/scaler/encoder — các cột này chưa tồn tại và không được thêm vào view handoff.
- **Trách nhiệm:** EPIC 2 fit trên train split only.

---

## 9. future_popularity

- **Lý do:** Post-outcome leakage — dữ liệu sau thời điểm dự đoán.
- **Trạng thái:** Không có trong dataset.

---

## Baseline Allowed Input Features (18 columns)

```
duration_min, explicit, release_year, release_month, decade, release_precision,
danceability, energy, key, loudness, mode, speechiness, acousticness,
instrumentalness, liveness, valence, tempo, time_signature
```

---

*Feature 1.8 — ML-Safe Dataset Handoff | HitRadar Pro*

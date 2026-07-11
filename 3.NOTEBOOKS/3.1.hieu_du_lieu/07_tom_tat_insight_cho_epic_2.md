# 07 — Tóm tắt insight cho EPIC 2

> Nguồn: `EDA_INSIGHTS_REPORT.md`, `FEATURE_1_7_COMPLETION_REPORT.md`, `NB06 executed output`  
> Đọc file này trước khi bắt đầu Feature Engineering & Modeling.

---

## Must do — Bắt buộc phải làm

| # | Việc cần làm | Lý do | Nguồn |
|---|-------------|-------|-------|
| 1 | **`target_popularity` là label — KHÔNG dùng làm input** | Target leakage → model vô nghĩa | `ANALYTICS_VIEWS_REPORT.md` |
| 2 | **Temporal split train/test theo `release_year`** | Random split → future data leakage (corr release_year = +0.59) | NB06 |
| 3 | **Impute `tempo` (328 NULL) và `time_signature` (337 NULL)** | Model không xử lý NULL | NB03 |
| 4 | **Scale/normalize tất cả numeric features** | Features có range khác nhau (0–1 vs BPM vs dB) | `FEATURE_1_7_COMPLETION_REPORT.md` |
| 5 | **Quyết định xử lý 44,690 bài `popularity = 0`** | 7.6% dataset — ảnh hưởng lớn đến training | NB06 |
| 6 | **Không dùng `artists.popularity` làm input mặc định** | Data leakage — popularity nghệ sĩ không có khi bài mới ra | `ANALYTICS_VIEWS_REPORT.md` |

---

## Should do — Nên làm

| # | Việc nên làm | Lý do | Nguồn |
|---|-------------|-------|-------|
| 1 | **Log-transform `speechiness` và `instrumentalness`** | Zero-inflated — median ≈ 0, mean > 0 | NB03 |
| 2 | **Genre encoding: top-N hoặc embedding** | 4,672 genres — one-hot không khả thi | NB05, EDA report |
| 3 | **Xử lý class imbalance popularity** | 75% bài ≤ 40, chỉ 0.1% > 80 | NB02 |
| 4 | **Carry-forward warnings vào pipeline** | Duration short=26, long=83, loudness>0=219 | `vw_data_quality_report` |
| 5 | **Document feature list chính thức từ `vw_ml_training_dataset`** | 20 cột, ML-safe, chưa processed | Feature 1.8 scope |
| 6 | **Kiểm tra partial correlation acousticness vs release_year** | acousticness corr=-0.37 có thể confounded | NB06 — *cần xác minh* |

---

## Risk to avoid — Rủi ro cần tránh

| # | Rủi ro | Hậu quả | Cách tránh |
|---|--------|---------|-----------|
| 1 | **Dùng `target_popularity` làm input feature** | Model accuracy 100% nhưng vô nghĩa | Chỉ dùng làm label/y |
| 2 | **Random train/test split** | Metric đẹp giả, model thiên vị nhạc mới | Temporal split |
| 3 | **Dùng `artists.popularity` làm feature** | Leakage — biết trước nghệ sĩ nổi tiếng | Không dùng mặc định |
| 4 | **One-hot 4,672 genres** | Sparse matrix, overfitting, OOM | Top-N hoặc embedding |
| 5 | **Join genre không DISTINCT** | Duplicate-weighting — đếm track nhiều lần | Dùng `COUNT(DISTINCT track_id)` |
| 6 | **Bỏ qua popularity=0** | 7.6% data bị xử lý sai hoặc mất | Quyết định strategy rõ ràng |
| 7 | **Tin correlation release_year = causation** | Model học time bias, không học âm nhạc | Kiểm soát hoặc loại release_year |
| 8 | **Train trên toàn bộ data rồi mới split** | Leakage từ test vào train | Split trước, transform sau |

---

## Checklist nhanh trước khi train model đầu tiên

```
□ Label = target_popularity (không nằm trong X)
□ Split theo release_year (không random)
□ tempo NULL imputed (328)
□ time_signature NULL imputed (337)
□ Numeric features scaled
□ speechiness/instrumentalness transformed
□ popularity=0 strategy quyết định
□ artists.popularity KHÔNG trong feature set
□ Genre encoding strategy quyết định (nếu dùng genre)
□ Warnings carry-forward đã review
```

---

## Liên kết Feature 1.8

Feature 1.8 (ML-safe Dataset Handoff) sẽ:
- Export từ `vw_ml_training_dataset`
- Document 20 cột chính thức + dtypes + null counts
- Xác nhận split strategy
- Tạo EPIC 1 completion summary

File này là **input** cho quyết định đó — không thay thế Feature 1.8.

---

## Số liệu then chốt cần nhớ

| Chỉ số | Giá trị |
|--------|---------|
| Tracks | 586,672 |
| Label | `target_popularity` (0–100) |
| Popularity = 0 | 44,690 (7.6%) |
| Corr mạnh nhất | release_year = +0.59 |
| Corr yếu nhất | valence ≈ 0 |
| Tempo NULL | 328 |
| Time_signature NULL | 337 |
| Genres (track-linked) | 4,672 |
| track_artists coverage | 96.54% |

*Nguồn: notebooks executed output + `EDA_INSIGHTS_REPORT.md`*

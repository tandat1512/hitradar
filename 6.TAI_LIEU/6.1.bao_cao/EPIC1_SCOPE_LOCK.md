# EPIC 1 SCOPE LOCK — HITRADAR

## 1. Owner

| Trường | Thông tin |
|--------|-----------|
| **Owner** | Đạt |
| **EPIC** | EPIC 1 — Data Foundation & Data Understanding |
| **Dự án** | HitRadar Pro |
| **Cập nhật lần cuối** | 2026-07-05 |

---

## 2. EPIC 1 Objective

EPIC 1 chịu trách nhiệm xây nền dữ liệu cho HitRadar, bao gồm:

- Xác nhận input data contract (thực tế 2 CSV + 1 JSON từ Kaggle)
- Audit raw dataset (schema, row count, missing, duplicate, range)
- Thiết kế raw / clean / analytics layers trong PostgreSQL
- Import dữ liệu vào PostgreSQL
- Cleaning và normalization (text, date, duration, artist/genre parsing)
- Data quality gates (null ratio, range check, join coverage, consistency)
- Analytics views (vw_tracks_by_decade, vw_audio_trends, vw_ml_training_dataset…)
- EDA notebooks (01–06)
- ML-safe handoff cho EPIC 2 (ml_ready_dataset, feature_dictionary, handoff doc)

---

## 3. Official Raw Inputs

| Logical Input | Actual File | Path | Format | Role | Note |
|---------------|-------------|------|--------|------|------|
| Track-level dataset | `tracks.csv` | `1.DỮ_LIỆU/1.1.raw/tracks.csv` | CSV | Bảng track chính, thay cho `data.csv` trong contract cũ | Chứa id, name, popularity, audio features, release_date/year, duration_ms, explicit |
| Artist-level dataset | `artists.csv` | `1.DỮ_LIỆU/1.1.raw/artists.csv` | CSV | Bảng artist chính, thay cho `data_by_artist.csv` trong contract cũ | Chứa id, name, followers, popularity, genres field |
| Artist genre dictionary | `dict_artists.json` | `1.DỮ_LIỆU/1.1.raw/dict_artists.json` | JSON | Nguồn bổ sung mapping artist_id → genre list | Dùng để sinh artist_genres hoặc genre bridge table khi parse |

---

## 4. Deprecated / Missing Old Inputs

Các file sau từng được nhắc trong contract cũ nhưng **KHÔNG còn là raw input bắt buộc**:

| File cũ | Lý do không còn là raw input | Thay thế |
|---------|------------------------------|----------|
| `data.csv` | Không tồn tại trong phiên bản Kaggle hiện tại | → `tracks.csv` |
| `data_by_artist.csv` | Không tồn tại trong phiên bản Kaggle hiện tại | → `artists.csv` |
| `data_by_year.csv` | Không tồn tại — là dữ liệu aggregate | → Sinh từ analytics pipeline (Feature 1.6) |
| `data_by_genres.csv` | Không tồn tại — là dữ liệu aggregate | → Sinh từ genre aggregation pipeline (Feature 1.6) |
| `data_w_genres.csv` | Không tồn tại — là output join | → Sinh sau khi normalize/join track-artist-genre (Feature 1.4) |

> **Nghiêm cấm tạo fake CSV để thay thế các file này.**

---

## 5. EPIC 1 Outputs

Output bắt buộc khi EPIC 1 kết thúc:

| Output | Loại | Mô tả |
|--------|------|-------|
| `DATASET_AUDIT_REPORT.md` | Tài liệu | Kết quả audit raw data |
| `DATA_DICTIONARY.md` | Tài liệu | Định nghĩa từng cột |
| `DATABASE_SCHEMA.md` | Tài liệu | Schema PostgreSQL 3 tầng |
| `DATA_CLEANING_RULES.md` | Tài liệu | Quy tắc cleaning |
| `DATA_QUALITY_REPORT.md` | Tài liệu | Báo cáo quality gates |
| `EDA_FINDINGS.md` | Tài liệu | Insight từ EDA |
| `HOW_TO_RUN_DATA_PIPELINE.md` | Tài liệu | Hướng dẫn chạy pipeline |
| `feature_dictionary.md` | Tài liệu | Feature nào train được, không được |
| `handoff_to_epic2.md` | Tài liệu | Bàn giao cho EPIC 2 |
| Raw tables | PostgreSQL | `raw_tracks`, `raw_artists` |
| Clean tables | PostgreSQL | `clean_tracks`, `clean_artists`, `clean_genres`… |
| Analytics views | PostgreSQL | `vw_tracks_by_decade`, `vw_audio_trends`, `vw_ml_training_dataset`… |
| `vw_ml_training_dataset` | PostgreSQL view | View ML-ready candidate |
| `ml_ready_dataset` export | CSV / Parquet | Export cho EPIC 2 nếu cần |

---

## 6. EPIC 1 Does

- Audit `tracks.csv`, `artists.csv`, `dict_artists.json`
- Thiết kế PostgreSQL raw schema (raw / clean / analytics 3 tầng)
- Import raw data vào PostgreSQL
- Parse trường `artists` dạng list-string trong `tracks.csv`
- Parse trường `genres` dạng list-string trong `artists.csv`
- Parse `dict_artists.json` thành bảng artist_genres
- Chuẩn hóa: track, artist, genre, track_artist, artist_genre
- Tạo `release_year`, `release_month`, `decade` từ `release_date`
- Tạo `duration_min` từ `duration_ms`
- Kiểm tra data quality gates (null ratio, range, join coverage, consistency)
- Tạo analytics views phục vụ EDA, dashboard, ML
- Tạo EDA notebooks (01–06)
- Bàn giao ML-ready dataset cho EPIC 2

---

## 7. EPIC 1 Does Not Do

- **Không** train model (bất kỳ loại nào)
- **Không** hyperparameter tuning
- **Không** SHAP / explainability chính thức
- **Không** xây FastAPI
- **Không** xây Streamlit
- **Không** deploy app
- **Không** tự split train/test cuối cùng cho EPIC 2 nếu chưa có contract từ EPIC 2
- **Không** dùng feature có nguy cơ leakage mà chưa ghi rõ trong `feature_dictionary.md`
- **Không** tạo fake CSV để thay thế file thiếu

---

## 8. EPIC 1 / EPIC 2 Boundary

EPIC 1 bàn giao dữ liệu sạch, kiểm định, có dictionary và ML-ready view.

**EPIC 2 chịu trách nhiệm:**

| Nhiệm vụ | Thuộc về |
|----------|----------|
| Split train / validation / test | EPIC 2 |
| Preprocessing train-only (imputer, scaler fit trên train) | EPIC 2 |
| Feature engineering ML nâng cao | EPIC 2 |
| Training model (baseline → XGBoost) | EPIC 2 |
| Evaluation (MAE, RMSE, R²) | EPIC 2 |
| SHAP global / local explanation | EPIC 2 |
| Packaging inference pipeline | EPIC 2 |
| Handoff sang EPIC 3 | EPIC 2 |

---

## 9. Data Leakage Rules

| Rule | Mô tả |
|------|-------|
| `popularity` chỉ là target | Không dùng làm input feature trong bất kỳ bước nào của EPIC 1 |
| Aggregate stats giới hạn cho EDA | `artist_avg_popularity`, `genre_avg_popularity`, `decade_avg_popularity` chỉ dùng EDA/dashboard — **không** đưa vào ML feature nếu chưa tính train-only trong EPIC 2 |
| ID / raw text không làm numeric feature | `id`, `name`, raw artist string — không encode trực tiếp làm numeric ML input nếu chưa có quy trình rõ ràng |
| Train/test split thuộc EPIC 2 | EPIC 1 chỉ tạo ML-ready candidate dataset, không định nghĩa split ranh giới |
| Không đánh giá model | EPIC 1 không tính metric model, không so sánh model |

---

## 10. Definition of Done for Feature 1.0

Feature 1.0 được xem là **hoàn thành** khi:

- [x] Raw input contract đã khớp với dữ liệu thật hiện có (2 CSV + 1 JSON)
- [x] `DATA_SOURCE.md` đã ghi đúng nguồn và file thực tế
- [x] `DATASET_DOWNLOAD_CHECK.md` đã **PASS**
- [x] `EPIC1_SCOPE_LOCK.md` đã cập nhật theo 2 CSV + 1 JSON thực tế
- [x] Mapping từ contract cũ (5 CSV) sang contract mới đã rõ ràng
- [x] Ranh giới EPIC 1 / EPIC 2 đã rõ
- [x] Data leakage rules đã có
- [x] Không còn yêu cầu sai rằng 5 CSV cũ là raw input bắt buộc
- [x] `FEATURE_1_0_COMPLETION_REPORT.md` đã tạo

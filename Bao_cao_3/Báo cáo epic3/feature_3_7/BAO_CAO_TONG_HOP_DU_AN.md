# BÁO CÁO TỔNG HỢP DỰ ÁN
## HitRadar Pro — EPIC 3 Productization, Integration & Defense

**Dự án:** HitRadar Pro — Song Popularity Prediction
**Người thực hiện EPIC 3:** Minh
**Repository:** H:\dự án\DUAN1 github
**Branch:** main
**Commit:** 2a6343f
**Ngày:** 2026-08-09
**Phạm vi:** EPIC 3 — Productization, Integration & Defense

---

## 1. Thông tin dự án

| Trường | Giá trị |
|---|---|
| Tên dự án | HitRadar Pro |
| Mô hình | XGBoost regression — EXP24-XGB-FINAL-001 v1.0.0 |
| Dataset | 586.672 bài hát, 1900–2021, Spotify-derived |
| Thuật toán | XGBoost gradient boosting regressor |
| Task type | Regression |
| Python | 3.13.14 (validated defense environment; minimum ≥3.10) |
| Năm học | 2024–2026 |

---

## 2. Bài toán

**Mục tiêu:** Dự đoán điểm popularity (0–100) của một bài hát từ các đặc trưng âm thanh và metadata.

**Điểm target:** `popularity` — continuous score (0–100), được cung cấp bởi Spotify trong dataset. Đây là một chỉ số dựa trên lượng nghe/engagement trên nền tảng Spotify, **không phải** thước đo chất lượng âm nhạc phổ quát.

**Độ khó:** Điểm popularity phụ thuộc vào rất nhiều yếu tố ngoài âm thanh — marketing, tên nghệ sĩ, thời điểm phát hành, nền tảng phân phối — những yếu tố không có trong dữ liệu âm thanh thuần túy.

---

## 3. Dữ liệu

**Nguồn:** Curated Spotify-derived dataset
**Số dòng:** 586.672 bài hát
**Thời gian:** 1900–2021
**Số trường đầu vào:** 18 trường canonical (raw audio + metadata)

Các đặc trưng raw bao gồm: danceability, energy, valence, tempo, loudness, key, mode, speechiness, acousticness, instrumentalness, liveness, duration_min, release_year, release_month, decade, release_precision, explicit, time_signature.

**Lưu ý chất lượng:**
- Dataset là một mẫu curated từ Spotify, không đại diện toàn diện cho ngành công nghiệp âm nhạc toàn cầu.
- Dữ liệu có thể thiên lệch về các thị trường/tiểu văn hóa nhất định.
- Các bài hát thuộc các nghệ sĩ rất nổi tiếng có thể chiếm ưu thế trong tập dữ liệu.

---

## 4. Quá trình xây dựng mô hình (EPIC 2)

Tóm tắt quá trình EPIC 2 (Feature 2.4 – 2.8):

1. **Feature Engineering:** Tạo 13 đặc trưng engineered từ 18 raw features → 31 selected features
2. **Pipeline Transformation:** Áp dụng scaler + one-hot encoding → 49 model matrix columns
3. **Model Selection:** So sánh XGBoost, LightGBM, Random Forest → chọn XGBoost
4. **Hyperparameter Tuning:** Grid search
5. **Training:** Train trên train split
6. **Evaluation:** MAE=17.65, RMSE=21.01, R²=0.070 trên test split (85,876 dòng)
7. **SHAP Explainability:** Tính toán SHAP values với TreeExplainer (1,000 background samples)
8. **Packaging:** Đóng gói thành artifacts/epic2/ với full_inference_pipeline.joblib

---

## 5. Mô hình cuối cùng

| Trường | Giá trị |
|---|---|
| Model ID | EXP24-XGB-FINAL-001 |
| Version | 1.0.0 |
| Algorithm | XGBoost Gradient Boosting Regressor |
| Feature set | FS23-SELECTED |
| Pipeline artifact | artifacts/epic2/pipeline/full_inference_pipeline.joblib |
| SHA-256 | 7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99 |

---

## 6. Kết quả đánh giá

| Metric | Giá trị | Đơn vị | Nguồn |
|---|---|---|---|
| MAE | 17.65 | popularity points | champion_test_metrics.json |
| RMSE | 21.01 | popularity points | champion_test_metrics.json |
| R² | 0.070 | coefficient of determination | champion_test_metrics.json |
| Median AE | 16.29 | popularity points | champion_test_metrics.json |
| Mean Residual | +4.86 | popularity points | residual_statistics.json |
| Underprediction Rate | 67.8% | proportion | champion_test_metrics.json |
| Test split | 85,876 | rows | champion_test_metrics.json |

**Phân tích:**
- MAE ≈ 17.6 điểm trên thang 0–100 có nghĩa là dự đoán của mô hình thường chênh lệch khoảng 18 điểm popularity.
- R² = 0.07 có nghĩa mô hình giải thích được ~7% phương sai của popularity. Con số này **thấp** và phản ánh độ khó của bài toán.
- Mean residual dương (+4.86) cho thấy mô hình **có xu hướng đoán thấp hơn** thực tế.
- 67.8% predictions là underprediction.

---

## 7. Explainability (SHAP)

Mô hình sử dụng **SHAP TreeExplainer** để giải thích từng dự đoán.

| Thành phần | Chi tiết |
|---|---|
| Explainer | shap.TreeExplainer |
| Background samples | 1,000 |
| Model matrix width | 49 columns |
| SHAP additivity validation | 100% pass |
| SHAP values per prediction | 49 entries (→ mapped to 31 selected features) |
| Top features displayed | Top 5 by absolute SHAP magnitude |

**Lưu ý quan trọng:** SHAP values mô tả **hành vi của mô hình** với input đó — không thiết lập mối quan hệ nhân quả. Một SHAP value dương cho danceability không có nghĩa là "tăng danceability sẽ làm tăng popularity thực tế."

---

## 8. What-If Simulator

Cho phép so sánh hai dự đoán: input gốc và input đã được thay đổi.

| Trường | Mô tả |
|---|---|
| Đầu vào | base_features (18 trường) + changed_features (≥1 trường thay đổi) |
| Output | prediction_before, prediction_after, delta |
| Delta | prediction_after − prediction_before (clipped values) |

**Lưu ý:** Delta mô tả sự thay đổi trong **output của mô hình**, không phải hiệu ứng thực tế. Một delta dương không chứng minh rằng thay đổi trong thế giới thực sẽ làm tăng popularity.

---

## 9. Productization — EPIC 3

### Feature 3.1: Artifact Intake & Validation
- Xác nhận 18 required artifacts đều present
- Validate model loads đúng
- Verify 113 tests pass
- Check no refit (zero fit/fit_transform calls)
- SHA-256 unchanged sau validation
- **Result:** ✅ PASS — artifact gate closed

### Feature 3.2: FastAPI Backend
- Xây dựng FastAPI backend với 6 endpoints
- Pydantic schema validation (422 on invalid)
- Eager model loading at startup
- SHAP explainability backend-side
- CORS enabled cho Streamlit
- **Result:** ✅ Implemented

### Feature 3.3: Streamlit Frontend
- 7 pages: Home, Predict, Explain, What-If, Trends, Model Info, Limitations
- HitRadarAPIClient (httpx)
- Session state management
- Error states + loading
- **Result:** ✅ Implemented

### Feature 3.4: Dashboard (Music Trends)
- Đọc CSV trực tiếp từ local filesystem
- @st.cache_data for aggregation
- Charts: songs by year, audio feature trends, correlation heatmap, model error by year
- Backend NOT required cho dashboard page
- **Result:** ✅ Implemented

### Feature 3.5: E2E Testing
- Canonical E2E fixture: prediction_display = 46
- Health validation
- Model info validation
- Backend unavailable graceful degradation
- Timeout handling
- **Result:** ✅ All E2E tests pass

### Feature 3.6: Performance & Reliability
- run_all.py: poll-based health check (no fixed sleep)
- Port conflict detection
- Graceful shutdown
- Offline Demo Mode: precomputed fallback
- Performance benchmark: model load 928ms, warm inference 15.6ms
- **Result:** ✅ Implemented

### Feature 3.7: Documentation
- README.md (Phase 1)
- HOW_TO_RUN_APP.md (Phase 2)
- USER_MANUAL.md (Phase 2)
- API_DOCUMENTATION.md (Phase 3)
- TECHNICAL_APPENDIX.md (Phase 4)
- Báo cáo tổng hợp (Phase 5)
- **Result:** ✅ All phases PASS

---

## 10. Kiến trúc hệ thống

```
Browser (Streamlit — port 8501)
    │  HTTP via HitRadarAPIClient (httpx)
    ▼
FastAPI Backend (port 8000)
    │  PipelineLoader singleton (loads at startup)
    │  shap.Explainer singleton (cached per session)
    ▼
artifacts/epic2/pipeline/full_inference_pipeline.joblib
    │  HitRadarInferencePipeline
    │  18 raw → 31 selected → 49 transformed → XGBoost
    ▼
Prediction (0–100)

Dashboard (Music Trends — no backend):
Browser → Streamlit → ml_ready_dataset.csv (local)
```

---

## 11. Luồng Predict

```
User enters 18 audio/metadata features (UI form)
    │
    ▼
POST /predict (18 required fields)
    │
    ▼
Pydantic validation (422 on failure)
    │
    ▼
HitRadarInferencePipeline.predict_popularity()
    │
    ▼
PredictResponse
    ├── prediction_raw: float (có thể ngoài [0,100])
    ├── prediction_clipped: float (đã clip)
    └── prediction_display: int (đã làm tròn)
```

---

## 12. Luồng Explain

```
POST /explain (18 fields — same as /predict)
    │
    ▼
PipelineLoader.get_explainer() → shap.TreeExplainer (singleton)
    │
    ▼
shap.TreeExplainer.shap_values() (49 values)
    │
    ▼
Map 49 → 31 selected features
    │
    ▼
Top 5 by absolute SHAP magnitude
    │
    ▼
ExplainResponse (base_value, shap_values dict, top_features)
```

---

## 13. Luồng What-If

```
POST /what-if
{
  base_features: 18 fields,
  changed_features: {field: new_value, ...}
}
    │
    ▼
Validate changed_features keys (422 if invalid)
    │
    ▼
Run pipeline twice:
  base → prediction_before
  merged → prediction_after
    │
    ▼
WhatIfResponse (before, after, delta, changes_applied)
```

---

## 14. Dashboard (Music Trends)

Đọc trực tiếp CSV từ filesystem — không qua backend.

| Data source | Mục đích |
|---|---|
| ml_ready_dataset.csv | Songs by year, audio feature trends, correlation |
| yearly_evaluation.csv | MAE, RMSE, R² by year |

Cache: `@st.cache_data` decorators.

**Phạm vi:** Charts mô tả project dataset (1900–2021), không phải toàn bộ ngành công nghiệp âm nhạc.

---

## 15. E2E Testing

| Test | Kết quả |
|---|---|
| Canonical E2E (example_input.json) | prediction_display = 46 ✅ |
| Health endpoint | healthy + model_loaded=true ✅ |
| Model info | model_id + metrics returned ✅ |
| Backend unavailable | Graceful degradation ✅ |
| Timeout | Timeout triggered correctly ✅ |

---

## 16. Performance

| Thao tác | Mean | Median | Đơn vị |
|---|---|---|---|
| Model load (cold) | 928 | 700 | ms |
| First prediction (cold) | 22.2 | 21.0 | ms |
| Warm single inference | 15.6 | 14.3 | ms |

**Môi trường benchmark gốc:** Local Python 3.13.7; artifacts/epic2/; joblib.load. Môi trường defense được kiểm tra sau đó dùng Python 3.13.14; không dùng hai môi trường này để suy diễn benchmark mới.
**Lưu ý:** Không có SLA. Số liệu này chỉ dùng cho mục đích tham khảo trong môi trường local.

---

## 17. Reliability & Demo Backup

| Tính năng | Mô tả |
|---|---|
| Startup | run_all.py poll /health (no fixed sleep) |
| Port conflicts | Detected and reported before starting |
| Graceful shutdown | Ctrl+C kills only child processes |
| Offline Demo | Precomputed validated fallback |
| Dashboard offline | Available (reads local CSV) |
| SHAP offline | **Không khả dụng** |
| What-If offline | **Không khả dụng** |

---

## 18. Documentation Deliverables

| Document | Mục đích |
|---|---|
| README.md | Project entry point |
| HOW_TO_RUN_APP.md | Detailed setup guide |
| USER_MANUAL.md | End-user guide |
| API_DOCUMENTATION.md | API reference |
| TECHNICAL_APPENDIX.md | Technical deep-dive |
| BÁO_CÁO_TONG_HOP_DU_AN.md | Project synthesis (this doc) |

---

## 19. Limitations

| Hạn chế | Chi tiết |
|---|---|
| R² = 0.07 | Mô hình chỉ giải thích được ~7% phương sai |
| MAE ≈ 17.6 | Predictions thường chênh ~18 điểm |
| Not causal | Prediction không thiết lập quan hệ nhân quả |
| SHAP not causal | SHAP mô tả hành vi mô hình, không phải nguyên nhân |
| What-If not real effect | So sánh output mô hình, không phải hiệu ứng thực tế |
| Dataset 1900–2021 | Không bảo đảm generalize cho releases gần đây hoặc ngoài phân phối |
| Not production | Academic prototype — không phải công cụ production |
| Offline = precomputed | Demo fallback — không phải live inference |

---

## 20. Responsible Use

- **Không** dùng prediction để quyết định kinh doanh mà không có human review.
- **Không** suy luận SHAP values là nguyên nhân thực tế.
- **Không** dùng What-If để lập kế hoạch sản xuất.
- Dashboard chỉ mô tả **available dataset**, không phải toàn bộ ngành âm nhạc.
- Offline mode là **precomputed demonstration**, không phải production backup.

---

## 21. Kết quả đạt được

- ✅ Mô hình XGBoost regression hoàn chỉnh với SHAP explainability
- ✅ FastAPI backend với 6 endpoints, full Pydantic validation
- ✅ Streamlit frontend 7 pages với state management
- ✅ Music Trends dashboard (local CSV, không cần backend)
- ✅ What-If simulator
- ✅ E2E test suite với canonical fixture
- ✅ Startup automation (run_all.py) với health polling
- ✅ Offline Demo Mode
- ✅ Performance benchmark
- ✅ Đầy đủ tài liệu: README, HOW_TO_RUN, USER_MANUAL, API_DOC, TECHNICAL_APPENDIX

---

## 22. Các vấn đề còn lại

| ID | Vấn đề | Mức độ |
|---|---|---|
| F37-B01 | Không có Python environment trong session — clean install và live test không thể thực thi | Blocker (shared with Feature 3.6) |
| F37-W05 | API example values từ E2E fixture, không phải live-tested | Warning |
| F37-W01 | TECHNICAL_APPENDIX.md was Phase 4 placeholder | Resolved |

---

## 23. Hướng phát triển

Các hướng mở rộng tiềm năng (không nằm trong scope hiện tại):

1. **Model improvement:** Thử ensemble methods, deep learning (RNN/Transformer cho sequential audio)
2. **Additional features:** Thêm metadata nghệ sĩ, genre, lyrics embedding
3. **Temporal analysis:** Forecasting popularity trends
4. **A/B testing:** So sánh model versions trong production
5. **Production hardening:** Auth, rate limiting, TLS, monitoring, CI/CD
6. **SHAP global explanations:** Global feature importance dashboard

---

## 24. Kết luận

HitRadar Pro là một ứng dụng web minh họa việc áp dụng XGBoost regression và SHAP explainability cho bài toán dự đoán popularity của bài hát. Dự án hoàn thành đầy đủ vòng đời ML: từ data processing (EPIC 1), training/evaluation (EPIC 2), đến productization và tài liệu (EPIC 3).

**Điểm mạnh:**
- Mô hình được đóng gói rõ ràng, reproducible
- SHAP explainability đầy đủ
- 6 API endpoints với Pydantic validation
- Startup automation với health polling
- Offline Demo Mode cho presentation

**Điểm giới hạn:**
- R² = 0.07 — low explanatory power
- MAE = 17.65 — substantial prediction error
- Dataset 1900–2021 không bảo đảm cover recent hoặc out-of-distribution releases
- Không phải production tool

Dự án minh họa được workflow ML thực tế trong môi trường học tập. Kết quả nên được sử dụng cho mục đích giáo dục, không phải quyết định kinh doanh.

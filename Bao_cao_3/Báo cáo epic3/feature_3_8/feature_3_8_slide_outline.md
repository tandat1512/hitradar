# Feature 3.8 — Slide Outline & Speaker Notes
## HitRadar Pro — Defense Preparation Phase 1

---

## Slide 1: Title

**Title:** HitRadar Pro — Song Popularity Prediction with Explainable ML
**Subtitle:** EPIC 3 — Productization, Integration & Defense
**Presenter:** UNCONFIRMED — human assignment required
**Date:** 2026-08-12

**Speaker notes:**
- HitRadar Pro là một ứng dụng web dự đoán popularity score của bài hát từ các đặc trưng âm thanh
- Dự án thể hiện full ML pipeline: từ data → model → deployed application
- Điểm đặc biệt: có SHAP explainability và honest limitations

---

## Slide 2: Problem & Objective

**Main message:** Can we predict how popular a song is from its audio features alone?

**Bullets:**
- Streaming platforms have large datasets of songs with audio features + popularity scores
- Question: Do audio characteristics predict popularity?
- Project scope: build a complete ML system to explore this question
- Honest goal: understand the limits of this approach

**Speaker notes:**
- Không phải để dự đoán "hit" thương mại
- Đây là bài toán regression: predict popularity score (0-100)
- Scope giới hạn: chỉ dùng audio features, không có artist popularity, marketing, etc.

---

## Slide 3: Dataset Overview

**Main message:** The dataset is a curated Spotify-derived sample — useful but not comprehensive.

**Bullets:**
- 586,672 songs | 1900–2021
- 18 raw audio + metadata features
- Target: popularity score (0–100)
- Source: curated Spotify-derived sample
- Limitation: Not all music globally; Spotify-specific engagement patterns

**Speaker notes:**
- Dataset là một mẫu curated từ Spotify — không đại diện toàn bộ ngành công nghiệp âm nhạc
- Popularity score phản ánh engagement pattern trên Spotify — không phải universal quality metric
- Phạm vi 1900–2021 là phạm vi của ML-ready CSV hiện tại; không đại diện toàn bộ âm nhạc toàn cầu

---

## Slide 4: ML Pipeline

**Main message:** A structured pipeline transforms raw features into a popularity prediction.

```
Raw Input (18 fields)
    → Feature Engineering (+13 engineered features)
    → Feature Selection (31 features retained)
    → Preprocessing (scaler, one-hot encoding)
    → Transformed Model Matrix (49 columns)
    → XGBoost Regression
    → Popularity Score (0–100)
```

**Speaker notes:**
- Từ 18 raw features, tạo thêm 13 engineered features (e.g., danceability × valence)
- Sau preprocessing: 49 columns trong model matrix
- Pipeline hoàn toàn serialized trong full_inference_pipeline.joblib

---

## Slide 5: Model Selection

**Main message:** XGBoost was selected as the champion model based on Epic 2 evaluation.

**Bullets:**
- Champion model: XGBoost Gradient Boosting Regressor
- Model ID: EXP24-XGB-FINAL-001 v1.0.0
- Feature set: FS23-SELECTED (31 features)
- Packaged inference artifact hash matched its manifest during the final smoke
- Zero refit calls confirmed (artifacts unchanged post-training)

**Speaker notes:**
- Registry Epic 2 ghi nhận XGBoost, Random Forest và Ridge; Linear và Dummy là baseline
- XGBoost được chọn làm champion dựa trên evaluation metrics
- Artifacts được validate bởi Feature 3.1 — model load thành công, không có refit

---

## Slide 6: Model Performance — What the Numbers Say

**Main message:** The model achieves moderate error but low explanatory power — typical for this task.

**Metrics table:**

| Metric | Value | Interpretation |
|---|---|---|
| MAE | 17.65 pts | Typical error ≈ 18 points on 0–100 scale |
| RMSE | 21.01 pts | Sensitive to large errors |
| R² | 0.07 | Model explains ~7% of popularity variance |
| Underprediction rate | 67.8% | Model tends to predict lower than actual |

**Test set:** 85,876 songs

**Speaker notes:**
- MAE ~18 điểm trên thang 0-100 — tức là prediction thường chênh ~18 điểm
- R² = 0.07 — thấp, phản ánh độ khó của bài toán
- 67.8% predictions là underprediction — model có xu hướng đoán thấp hơn thực tế
- R² thấp là BÌNH THƯỜNG cho bài toán này — popularity phụ thuộc nhiều yếu tố ngoài audio

---

## Slide 7: SHAP — Why Did the Model Say That?

**Main message:** SHAP tells us which features drove a specific prediction — but does NOT prove causation.

**SHAP explanation for example prediction:**
- Epic 2 explainability artifacts were validated with a 1,000-row train-only background; the current live FastAPI endpoint separately constructs `TreeExplainer(model)` without passing that background artifact
- Computes per-feature contributions (positive or negative)
- Top contributing features displayed

**What SHAP does:**
- Shows which features pushed prediction UP or DOWN for this specific song
- Additivity validated: base + ΣSHAP ≈ prediction (100% pass)

**What SHAP does NOT do:**
- ✗ Prove that changing a feature will change real-world popularity
- ✗ Establish causal relationships

**Speaker notes:**
- SHAP value dương cho energy không có nghĩa là "tăng energy sẽ làm tăng popularity thực tế"
- SHAP chỉ mô tả: trong training data, songs với higher energy thường có higher model-predicted popularity
- Quan hệ correlation không phải causation

---

## Slide 8: What-If Simulator

**Main message:** What-If compares two model predictions — it is a prediction comparison tool, not a causal experiment.

**Canonical measured example (final smoke 2026-08-12):**
- Scenario A: energy = 0.793 → prediction = 46.421062
- Scenario B: same canonical input, energy = 0.95 → prediction = 44.045479
- Delta: −2.375583 points

**Critical note:**
- Delta describes change in **model output**, not real-world effect
- A positive delta does NOT prove that increasing danceability increases real-world popularity
- What-If answers: "what would the model predict if...?"

**Speaker notes:**
- Rất hữu ích để hiểu model behavior
- Không nên dùng để lập kế hoạch sản xuất nhạc
- Giúp stakeholders hiểu model "thấy gì" trong data

---

## Slide 9: System Architecture

**Main message:** HitRadar Pro uses a clean separation between frontend and backend.

```
Browser (Streamlit — port 8501)
    │  HTTP (httpx)
    ▼
FastAPI Backend (port 8000)
    │  PipelineLoader
    │  full_inference_pipeline.joblib
    │  SHAP.TreeExplainer
    ▼
Prediction / Explanation

Dashboard (Music Trends):
Streamlit → ml_ready_dataset.csv (local, no backend)
```

**Key engineering decisions:**
- Frontend NEVER loads model artifacts
- Model loaded eagerly at FastAPI startup
- Pydantic validation on all inputs
- Health endpoint with readiness check

**Speaker notes:**
- Architecture clean separation: frontend gọi API, backend chạy model
- Không có direct model access từ browser
- run_all.py tự động start backend, đợi ready, rồi start frontend

---

## Slide 10: Application — Predict Page

**Main message:** Users enter 18 song features and receive a popularity prediction.

**Flow:**
1. Enter 18 audio/metadata features
2. POST /predict
3. Receive prediction score (0–100)
4. Score saved for SHAP/What-If pages

**Canonical example:** Song features → prediction score = 46

**Speaker notes:**
- 18 required fields: danceability, energy, valence, tempo, loudness, key, mode, etc.
- Backend validates input với Pydantic — invalid input → HTTP 422
- Backend chạy full pipeline: feature engineering → preprocessing → XGBoost → output

---

## Slide 11: Application — SHAP Explanation Page

**Main message:** After a prediction, users can see which features drove that specific prediction.

**Flow:**
1. POST /explain (same 18 fields as /predict)
2. Backend computes SHAP values (TreeExplainer)
3. Frontend displays top contributing features
4. Visual waterfall chart

**Canonical measured output (final smoke 2026-08-12):**
- Base value: 22.879942
- Top contributions by absolute value: release_year (+7.736362), energy_danceability (+5.928582), acousticness (+1.818460), duration_min (+1.395095), danceability (+1.259571)
- Final prediction: 46.421062

**Speaker notes:**
- SHAP computation chạy trên backend — frontend không compute SHAP
- Top 5 features by absolute SHAP value được hiển thị
- SHAP values có thể negative (giảm prediction) hoặc positive (tăng prediction)

---

## Slide 12: Application — What-If Simulator

**Main message:** Users modify one or more features and compare two model predictions.

**Flow:**
1. Load baseline from last prediction
2. Select features to modify
3. POST /what-if
4. Compare: prediction_before vs prediction_after

**Speaker notes:**
- Cho phép explore "what if" scenarios
- Không thay đổi model hay dataset
- Rất tốt để demonstrate model sensitivity

---

## Slide 13: Dashboard — Music Trends

**Main message:** The Music Trends dashboard shows descriptive statistics from the training dataset.

**Charts:**
- Songs per year (1900–2021; 586,672 valid rows)
- Audio feature trends over decades
- Correlation heatmap
- Model error by year

**Scope:** Describes the available dataset only — not all global music.

**Technical note:** Dashboard reads local CSV directly — no backend required.

**Speaker notes:**
- Dashboard không gọi model API — đọc trực tiếp ml_ready_dataset.csv
- Có thể xem dashboard kể cả khi backend không chạy
- Các chart cho thấy patterns trong training data — không phải global trends

---

## Slide 14: Testing — Making It Reliable

**Final technical smoke (2026-08-12):**
- Canonical prediction: 46.421062 ✅
- Health: healthy + model_loaded=true ✅
- Explain: SHAP response returned ✅
- What-if: measured delta −2.375583 ✅
- Model info: correct identity; metrics field is null ⚠
- Frontend health: HTTP 200 ✅
- Automatic offline UI: not validated ⚠

**Speaker notes:**
- Đây là technical smoke, không phải human rehearsal
- Không dùng trạng thái closure lịch sử của Feature 3.5 làm bằng chứng thay cho lần chạy hiện tại
- Các kiểm thử tự động Feature 3.8 được báo cáo riêng trong JUnit XML

---

## Slide 15: Performance & Reliability

**Final smoke observations (local — Python 3.13):**

| Operation | Mean | Median |
|---|---|---|
| Predict API | 86 ms | one measured request |
| What-if API | 38 ms | one measured request |
| Explain API | 400 ms | one measured request |

**Reliability features:**
- run_all.py: automatic startup with health polling
- Port conflict detection
- Graceful shutdown (Ctrl+C)
- Offline fallback: evidence files exist; automatic UI/banner is not validated
- **No SLA defined** — local benchmark only

**Speaker notes:**
- Các số này là một technical smoke cục bộ, không phải benchmark hay production SLA
- Script frontend cần chạy Python UTF-8 trong đường dẫn tiếng Việt để tránh lỗi ghi log CP1252
- Offline chỉ được dùng khi hiển thị disclosure rõ ràng; hiện chưa được xác nhận qua UI

---

## Slide 16: Limitations — Honest Assessment

**Main message:** We clearly communicate what the model cannot do.

| Limitation | Explanation |
|---|---|
| R² = 0.07 | Model explains ~7% of popularity variance — low |
| MAE ≈ 18 pts | Predictions typically off by ~18 points |
| Audio ≠ causation | SHAP/What-If describe model behavior, not real effects |
| Dataset 1900–2021 | Historical, Spotify-derived sample; not all global music |
| Not production-ready | Academic prototype — no auth, rate limiting, or TLS |
| Offline = precomputed | Not live model inference |

**Speaker notes:**
- Không có hidden caveats — limitations được communicate rõ ràng
- Điểm quan trọng: R² thấp là EXPECTED cho bài toán này
- Audio features chỉ là một phần nhỏ của what makes a song popular

---

## Slide 17: Future Work

**Natural next steps (not currently implemented):**

- **Additional features:** artist popularity, genre, lyrics embedding, social media signals
- **Temporal validation:** test model on more recent data
- **Model monitoring:** track prediction drift over time
- **Production hardening:** auth, rate limiting, TLS, CI/CD
- **Ensemble methods:** combine multiple model types
- **User studies:** evaluate real-world utility with actual music professionals

**Speaker notes:**
- Đây là những hướng mở rộng tự nhiên — không phải là bugs hay missing features
- Đặc biệt interesting: thêm artist-level features có thể cải thiện R² đáng kể

---

## Slide 18: Conclusion

**What we built:**
- Full ML pipeline from raw data to deployed model
- SHAP explainability for every prediction
- What-If analysis tool
- Music Trends dashboard
- Full-stack FastAPI + Streamlit application
- Automated testing and startup tooling

**What we learned:**
- Audio features alone explain very little of popularity variance (R² = 0.07)
- This is typical for this task — popularity depends on many factors outside audio
- Explainability (SHAP) adds interpretability but not causal power
- The system is a working demonstration, not a production prediction tool

**Key message:** HitRadar Pro demonstrates the full ML lifecycle with honest limits.

---

## Slide 19: Q&A

**Prepared Q&A areas:**
- Dataset: source, scope, limitations
- Model: selection rationale, metrics interpretation
- SHAP: what it means, what it doesn't mean
- System: architecture, API, testing
- Limitations: honest boundaries

---

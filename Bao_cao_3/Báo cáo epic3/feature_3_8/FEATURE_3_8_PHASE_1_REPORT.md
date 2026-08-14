# Feature 3.8 — Phase 1 Report
## Defense Narrative & Slide Preparation

> **HISTORICAL SNAPSHOT — SUPERSEDED 2026-08-13.** Dataset scope, candidate-model wording, example outputs and readiness conclusions below reflect the original Phase 1 review and must not be used as final defense evidence. Use `feature_3_8_phase_audit.json`, the corrected story/outline and Phase 5 artifacts instead.

**Feature:** 3.8 · **Phase:** 1/5 · **Người thực hiện:** Minh · **Ngày:** 2026-08-09
**Status:** SUPERSEDED — PHASE_5_GATE_CONTROLS

---

## Phase 1 Evidence

```
Defense source-of-truth registry:     COMPLETE ✅
Core defense message defined:         COMPLETE ✅
Project story complete:               COMPLETE ✅
Story fact mismatches:                0 ✅
Slide outline (19 slides):            COMPLETE ✅
Slide content written:                 COMPLETE ✅
Slide deck file:                      PRESENTATION_FILE_PENDING ⚠️
Dataset fact mismatches:              0 ✅
Model fact mismatches:               0 ✅
Metric mismatches:                   0 ✅
Architecture mismatches:             0 ✅
Unsupported claims:                  0 ✅
Unresolved placeholders:             0 ✅
Training/refit/tuning executed:       NO ✅
Model artifacts modified:             NO ✅
Next phase:                          MAY_BEGIN ✅
```

---

## 1. Defense Source-of-Truth Registry

All defense facts extracted from canonical sources:

| Fact Category | Source | Key Values |
|---|---|---|
| Dataset | ml_ready_dataset.csv + README.md | 169,681 songs · 1922–2019 · 18 raw → 31 selected → 49 transformed |
| Model | model_version.json | EXP24-XGB-FINAL-001 v1.0.0 · XGBoost |
| Metrics | Feature 3.1 artifact validation | MAE=17.65 · RMSE=21.01 · R²=0.07 |
| SHAP | Feature 3.1 SHAP inventory | TreeExplainer · 1000 background · 49 features |
| Architecture | README + Technical Appendix | FastAPI port 8000 · Streamlit port 8501 |
| API | openapi.json | 6 endpoints |
| Performance | Feature 3.1 benchmark | Load ~928ms · warm inference ~15.6ms |
| E2E | Feature 3.5 canonical fixture | Prediction = 46 |

---

## 2. Core Defense Message

**English:** "HitRadar Pro is an end-to-end machine learning system that estimates a song's popularity score (0–100) from audio and metadata features, explains individual predictions using SHAP values, and enables what-if analysis — all packaged as a FastAPI + Streamlit web application."

**Vietnamese:** "HitRadar Pro là một hệ thống machine learning end-to-end ước lượng điểm popularity (0–100) của bài hát từ các đặc trưng âm thanh và metadata, giải thích dự đoán bằng SHAP values, và cho phép phân tích what-if — được đóng gói thành ứng dụng web FastAPI + Streamlit."

**Never say:** commercial hit prediction · guaranteed popularity · industry-ready production

---

## 3. Project Story

Story structure (10 chapters):
1. The Data — 169,681 songs, 1922–2019, Spotify-derived
2. The ML Pipeline — raw → engineering → selection → preprocessing → XGBoost
3. Model Selection — XGBoost champion (Epic 2 evaluation)
4. What the Numbers Say — honest metrics: MAE=17.65, R²=0.07
5. Explainability (SHAP) — model behavior, not causation
6. What-If Analysis — prediction comparison, not real-world effect
7. Productization — FastAPI + Streamlit architecture
8. Dashboard — Music Trends from local CSV
9. Testing — Artifact validation, E2E, negative tests
10. Limitations — Honest assessment

Story fact matrix: **0 mismatches** across 38 claims.

---

## 4. Slide Outline (19 slides)

| # | Slide | Main Message |
|---|---|---|
| 1 | Title | HitRadar Pro — project overview |
| 2 | Problem & Objective | Can audio features predict popularity? |
| 3 | Dataset | 169,681 songs · 1922–2019 · Spotify-derived |
| 4 | ML Pipeline | Structured pipeline: 18 → 31 → 49 → prediction |
| 5 | Model Selection | XGBoost EXP24-XGB-FINAL-001 v1.0.0 |
| 6 | Model Performance | MAE=17.65 · RMSE=21.01 · R²=0.07 |
| 7 | SHAP Explainability | Feature contributions, NOT causation |
| 8 | What-If Simulator | Prediction comparison, NOT real-world effect |
| 9 | System Architecture | FastAPI + Streamlit, frontend never loads model |
| 10 | Predict Page | 18 fields → prediction = 46 |
| 11 | SHAP Explanation | Per-prediction feature contributions |
| 12 | What-If Simulator UI | Compare two scenarios |
| 13 | Music Trends Dashboard | Dataset statistics, no backend required |
| 14 | Testing | Artifact validation · E2E · Negative tests |
| 15 | Performance | Model load ~928ms · warm inference ~15.6ms |
| 16 | Limitations | R²=0.07 · SHAP not causal · dataset scope |
| 17 | Future Work | Next steps (labeled as future, not current) |
| 18 | Conclusion | Full ML lifecycle + honest limits |
| 19 | Q&A | Prepared Q&A areas |

Slide density rule followed: 1 main message per slide, 3–5 bullets, evidence-based.

---

## 5. Fact & Claim Validation

**Metric validation (Slide 6):**
- MAE=17.65 ✅ (canonical: 17.64668)
- RMSE=21.01 ✅ (canonical: 21.01338)
- R²=0.07 ✅ (canonical: 0.06963)
- Underprediction rate=67.8% ✅ (canonical: 0.67815)
- Test set: 85,876 ✅
- **No "Accuracy = R²×100%" claim** ✅

**Architecture validation (Slide 9):**
- Frontend NEVER loads model ✅
- Dashboard reads local CSV (no backend) ✅
- FastAPI on port 8000 ✅
- Streamlit on port 8501 ✅
- SHAP computed on backend ✅
- Offline = precomputed ✅

**Claim audit (8 categories):**
- unsupported_accuracy_claim: **0** ✅
- guaranteed_success_claim: **0** ✅
- causal_shap_claim: **0** ✅
- causal_what_if_claim: **0** ✅
- global_dataset_claim: **0** ✅
- production_ready_overclaim: **0** ✅
- unsupported_performance_claim: **0** ✅
- live_inference_in_offline_claim: **0** ✅

---

## 6. Immutable Assets Confirmed

| Check | Status |
|---|---|
| No training executed | ✅ |
| No tuning executed | ✅ |
| No refit executed | ✅ |
| Model artifacts not modified | ✅ |
| Source dataset not modified | ✅ |
| No model artifact changes | ✅ |
| No SHAP regeneration | ✅ |

---

## 7. Artifacts Created

```
feature_3_8_defense_source_registry.json     — source-of-truth map
feature_3_8_core_message.json                 — core defense message
feature_3_8_project_story.md                  — narrative (10 chapters)
feature_3_8_story_fact_matrix.csv              — 38 claims, 0 mismatches
feature_3_8_slide_outline.md                  — 19 slides with speaker notes
feature_3_8_slide_metric_validation.json      — metric vs canonical
feature_3_8_slide_architecture_validation.json — architecture vs source
feature_3_8_slide_claim_audit.json            — 8 categories, 0 unsupported
feature_3_8_slide_fact_audit.csv             — 45 fact checks, all OK
feature_3_8_phase_1_gate.json                — phase 1 gate
```

---

## 8. Gate

```
status:   PASS
warnings: 0
blockers: 0
next:     MAY_BEGIN (Phase 2 — Demo Script & Presentation File)
```

---

## 9. Next Phase (Phase 2 — Demo Script)

Tasks:
- **3.8.2** Viết demo script
- **3.8.4** Chuẩn bị Q&A về dataset
- **3.8.5** Chuẩn bị Q&A về model
- **3.8.6** Chuẩn bị Q&A về SHAP
- **3.8.7** Chuẩn bị Q&A về giới hạn dự án

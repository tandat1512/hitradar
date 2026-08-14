# ARTIFACT VALIDATION REPORT
## Feature 3.1 — Artifact Intake & Validation Gate

---

## 1. Thông tin chung

| Trường | Giá trị |
|---|---|
| Project | HitRadar Pro |
| EPIC | EPIC 3 — Productization, Integration & Defense |
| Feature | 3.1 — Artifact Intake & Validation Gate |
| Người thực hiện | Minh |
| Repository | `<PROJECT_ROOT>` |
| Branch | main |
| Ngày kiểm tra | 2026-08-03 → 2026-08-04 |
| Trạng thái | **PASS_WITH_WARNINGS** |

---

## 2. Mục tiêu Validation Gate

Xác minh toàn bộ artifacts từ EPIC 2 trước khi xây sản phẩm FastAPI + Streamlit (EPIC 3). Đảm bảo model, schema, metrics, SHAP, và example prediction đều hợp lệ, load được, và không bị can thiệp trong quá trình validation.

---

## 3. Handoff từ EPIC 2

| Trường | Giá trị |
|---|---|
| Model ID | `EXP24-XGB-FINAL-001` |
| Model Version | `1.0.0` |
| Package Version | `1.0.0` |
| Data Version | `v1.0` |
| Artifact SHA-256 (model) | `7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99` |
| Artifact Size | 3,982,751 bytes |
| Pipeline Type | `inference_pipeline.HitRadarInferencePipeline` |
| Main API | `predict_popularity()` |

### Cảnh báo từ EPIC 2

- `4.MODELS/4.2.evaluation/model_metrics.json` rỗng (0 bytes) — đã dùng `champion_test_metrics.json` làm workaround.
- Formal handoff document `handoff_to_epic3.md` không tồn tại — đã dùng `MODEL_PACKAGE_README.md` làm workaround.
- `artifact_manifest.json` có stale hash cho `runtime/inference_pipeline.py`.

---

## 4. Required Artifact Checklist

| Artifact role | Declared path | Actual path | Hash | Status |
|---|---|---|---|---|
| Model pipeline | `7.ML/7.10.model_packaging/package/pipeline/full_inference_pipeline.joblib` | ✅ Found | `7ff4b118...` | PASS |
| Input schema | `7.ML/.../schemas/input_schema.json` | ✅ Found | — | PASS |
| Output schema | `7.ML/.../schemas/output_schema.json` | ✅ Found | — | PASS |
| Selected features | `7.ML/.../schemas/selected_features.json` | ✅ Found | — | PASS |
| Feature names | `7.ML/.../schemas/feature_names.json` | ✅ Found | — | PASS |
| Feature mapping | `7.ML/.../schemas/feature_mapping.json` | ✅ Found | — | PASS |
| Example input | `7.ML/.../examples/example_input.json` | ✅ Found | — | PASS |
| Example output | `7.ML/.../examples/example_output.json` | ✅ Found | — | PASS |
| Model metrics | `7.ML/7.8.model_evaluation/metrics/champion_test_metrics.json` | ✅ Found | — | PASS |
| Residual stats | `7.ML/7.8.model_evaluation/residuals/residual_statistics.json` | ✅ Found | — | PASS |
| SHAP values | `7.ML/7.9.explainability/shap_values/shap_values_global.npy` | ✅ Found | — | PASS |
| SHAP background | `7.ML/7.9.explainability/background/shap_background_transformed.npy` | ✅ Found | — | PASS |
| Runtime wrapper | `7.ML/.../runtime/inference_pipeline.py` | ✅ Found | stale hash | WARNING |

---

## 5. Manifest Validation

`artifact_manifest.json` parse được và chứa 18 source artifacts. Known issue: hash của `runtime/inference_pipeline.py` không khớp với actual file (stale, BLK-GLOBAL-002).

---

## 6. Model Artifact

| Property | Value |
|---|---|
| Extension | `.joblib` |
| Loader | `joblib` 1.5.3 |
| Object type | `HitRadarInferencePipeline` |
| Load result | SUCCESS (1849ms) |
| Load duration | 1849ms (cold), ~15ms warm inference |
| No-refit evidence | `fit_call_count=0`, `fit_transform_call_count=0`, `partial_fit_call_count=0` |
| 4 runtime patches required | ✅ Applied and documented |

---

## 7. Runtime Dependencies

| Package | Version | Status |
|---|---|---|
| sklearn | 1.8.0 | ✅ (pipeline pickled with 1.9.0 — WARNING) |
| xgboost | — | ✅ Importable |
| joblib | 1.5.3 | ✅ Importable |
| pandas | — | ✅ Importable |
| numpy | — | ✅ Importable |
| shap | — | ✅ Importable |

---

## 8. Input Schema

| Property | Value |
|---|---|
| Schema ID | `HITRADAR-PREDICTION-INPUT-V1` |
| Field count | 18 |
| Fields | duration_min, explicit, release_year, release_month, decade, release_precision, danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature |
| Target excluded | ✅ `target_popularity` NOT present |
| Identifier excluded | ✅ `track_id` NOT present |
| Additional properties | `IGNORE_WITH_WARNING` |

---

## 9. Output Schema

| Property | Value |
|---|---|
| Schema ID | `HITRADAR-PREDICTION-OUTPUT-V1` |
| Field count | 8 |
| Fields | status, prediction_raw, prediction_clipped, prediction_display, model_id, model_version, warnings, request_id |
| prediction_raw range | Any finite number |
| prediction_clipped range | [0, 100] |

---

## 10. Feature Contracts

| Layer | Count | Status |
|---|---|---|
| RAW_INPUT_FEATURES | 18 | ✅ PASS |
| SELECTED_ENGINEERED_FEATURES | 31 (13 raw + 5 categorical passthrough + 13 engineered) | ✅ PASS |
| TRANSFORMED_MODEL_FEATURES | 49 (26 numeric + 23 OHE) | ✅ PASS |
| All layers distinct | YES | ✅ PASS |
| target/track_id excluded | YES | ✅ PASS |

OHE expansion: 5 categorical fields → 23 one-hot columns (release_precision × 3, key × 12, time_signature × 4, explicit × 2, mode × 2).

---

## 11. Model Metrics

| Metric | Value | Unit | Notes |
|---|---|---|---|
| MAE | 17.647 | popularity points | |
| RMSE | 21.013 | popularity points | |
| R² | 0.0696 | coefficient | Low — challenging task |
| Median AE | 16.292 | popularity points | |
| P80 AE | 28.938 | popularity points | |
| P90 AE | 34.116 | popularity points | |
| P95 AE | 37.102 | popularity points | |
| Mean Residual | +4.857 | popularity points | Underprediction |
| Residual Std | 20.445 | popularity points | |
| Underprediction Rate | 67.8% | proportion | |
| Overprediction Rate | 32.2% | proportion | |

**Evaluation stage:** test split, 85,876 rows. **Cảnh báo:** R² = 0.07 thấp nhưng đây là task khó (predict Spotify popularity 0–100). Feature 3.1 chỉ kiểm artifact, không đánh giá chất lượng model.

---

## 12. Residual Statistics

| Property | Value |
|---|---|
| Convention | `actual - predicted` (inferred from consistency) |
| Mean residual | +4.857 (systematic underprediction) |
| Median residual | +8.830 |
| Residual std | 20.445 |
| Sample rows | 85,876 |
| Min | -53.055 |
| Max | +69.092 |

**Cảnh báo:** Residual convention không được ghi rõ trong artifact — đã suy ra từ metric consistency. Nếu convention bị đảo ngược trong tương lai, interpretation sẽ sai.

---

## 13. SHAP Assets

| Property | Value |
|---|---|
| Total assets found | 16 |
| Required assets | 8 |
| Required all PASS | ✅ Yes |
| SHAP values shape | [5000, 49] |
| SHAP values finite | ✅ Yes, no NaN/Inf |
| Background shape | [1000, 49] |
| Additivity pass rate | 100% (tolerance 0.001) |
| Feature dimension | 49 (matches model matrix) |
| SHAP recomputed | ❌ NO |
| Model version consistent | ✅ `EXP24-XGB-FINAL-001` |
| EPIC 3 requirement | SHAP required for `/explain` endpoint |

---

## 14. Example Prediction

| Item | Expected | Actual | Status |
|---|---|---|---|
| prediction_raw | 46.421062 | 46.421062 | ✅ PASS |
| prediction_clipped | 46.421062 | 46.421062 | ✅ PASS |
| prediction_display | 46 | 46 | ✅ PASS |
| model_id | `EXP24-XGB-FINAL-001` | `EXP24-XGB-FINAL-001` | ✅ PASS |
| model_version | `1.0.0` | `1.0.0` | ✅ PASS |
| NaN/Inf | — | None | ✅ PASS |
| Absolute difference | ≤ 0.001 | 0.0 | ✅ PASS |
| Deterministic | — | YES (3/3 runs = 46.421062) | ✅ PASS |

---

## 15. Prediction Determinism

| Run | Value |
|---|---|
| Run 1 | 46.421062 |
| Run 2 | 46.421062 |
| Run 3 | 46.421062 |
| Max absolute difference | 0.0 |
| Status | **DETERMINISTIC** |

---

## 16. Local Inference Benchmark

> **Lưu ý quan trọng:** Benchmark này đo local inference mechanics, KHÔNG PHẢI production API SLA.

| Measurement | Median | P95 | Notes |
|---|---|---|---|
| Model cold load | 1849ms | — | Single fresh-process measurement |
| First prediction (after load) | ~68ms | — | First call, potential lazy init |
| Warm single inference | ~15ms | — | After warm-up |
| Fit calls during benchmark | 0 | — | No-refit enforced |

---

## 17. Source Immutability

| Artifact | SHA-256 unchanged |
|---|---|
| `full_inference_pipeline.joblib` | ✅ Yes — verified before/after Phase 2-3 |
| All schemas | ✅ Yes |
| Metrics | ✅ Yes |
| SHAP | ✅ Yes — no regeneration |
| Examples | ✅ Yes |

---

## 18. Test Results

| Metric | Value |
|---|---|
| Total tests | 241 |
| Passed | **241** |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Duration | ~15s |

All Phase 2 (113), Phase 3 (88), Phase 4 (37), Phase 5 (3 governance) tests PASS. Total: 241.

---

## 19. Warnings

| ID | Type | Severity | Detail |
|---|---|---|---|
| W1 | MISSING_HANDOFF_DOCUMENT | HIGH | `handoff_to_epic3.md` không tồn tại; workaround: `MODEL_PACKAGE_README.md` |
| W2 | STALE_MANIFEST | MEDIUM | `artifact_manifest.json` hash stale cho `runtime/inference_pipeline.py` |
| W3 | EMPTY_METRIC_FILE | MEDIUM | `4.MODELS/4.2.evaluation/model_metrics.json` rỗng; workaround: `champion_test_metrics.json` |
| W4 | RESIDUAL_CONVENTION_NOT_EXPLICIT | WARNING | Convention suy ra từ consistency, không ghi rõ trong artifact |
| W5 | LOW_R2 | INFO | R² = 0.0696 thấp nhưng không phải validation failure |
| W6 | SKLEARN_VERSION_MISMATCH | WARNING | Pipeline pickled với sklearn 1.9.0, runtime 1.8.0 |

---

## 20. Blockers

| ID | Type | Severity | Resolution |
|---|---|---|---|
| BLK-GLOBAL-001 | MISSING_HANDOFF_DOCUMENT | HIGH | Workaround: dùng MODEL_PACKAGE_README.md |
| BLK-GLOBAL-002 | STALE_MANIFEST | HIGH | Stale hash — non-critical, không block prediction |
| BLK-GLOBAL-003 | EMPTY_METRIC_FILE | MEDIUM | Workaround: dùng champion_test_metrics.json |

**Tất cả blockers đều có workaround và không ảnh hưởng inference correctness.**

---

## 21. Validation Gate Decision

| Criterion | Result |
|---|---|
| Model artifact intact | ✅ PASS |
| Prediction accurate | ✅ PASS |
| Deterministic | ✅ PASS |
| No training/refit | ✅ PASS |
| SHAP assets complete | ✅ PASS |
| Source artifacts unchanged | ✅ PASS |
| All tests pass | ✅ PASS (241/241) |
| **Overall Gate** | **PASS_WITH_WARNINGS** |

---

## 22. Feature 3.2 Readiness

**Decision: MAY_BEGIN**

FastAPI backend (Feature 3.2) có thể bắt đầu với các điều kiện:

1. Model load với 4 runtime patches đã được xác minh và document.
2. `/predict` endpoint dùng `predict_popularity()` — đã test với example input.
3. SHAP assets đầy đủ cho `/explain` endpoint.
4. Input/output schemas đã validate.

**Lưu ý:** sklearn version mismatch (1.9.0 / 1.8.0) cần được ghi nhận trong API error handling.

---

## 23. Evidence Index

| Evidence | Path | SHA-256 (nếu có) |
|---|---|---|
| Model load validation | `epic3/.../validation/feature_3_1_model_load_validation.json` | — |
| Model hash evidence | `epic3/.../validation/feature_3_1_no_refit_validation.json` | `7ff4b118...` |
| Feature contract | `epic3/.../validation/feature_3_1_feature_contract_consistency.json` | — |
| Metrics | `7.ML/7.8.model_evaluation/metrics/champion_test_metrics.json` | — |
| Residual stats | `7.ML/7.8.model_evaluation/residuals/residual_statistics.json` | — |
| SHAP validation | `epic3/.../validation/feature_3_1_shap_asset_validation.json` | — |
| Example prediction | `epic3/.../validation/feature_3_1_example_prediction_result.json` | — |
| Closure gate | `epic3/.../validation/feature_3_1_closure_gate.json` | — |
| Evidence matrix | `epic3/.../validation/feature_3_1_evidence_matrix.csv` | — |
| Test XML | `epic3/.../reports/pytest_feature_3_1.xml` | — |

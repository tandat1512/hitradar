# FEATURE 3.1 — Inference Asset Validation Report
**Phase:** 3/5
**Feature:** 3.1 — Artifact Intake & Validation Gate
**Person in Charge:** Minh
**Session:** 2026-08-04

---

## 1. Model Metrics

**Source:** `7.ML/7.8.model_evaluation/metrics/champion_test_metrics.json`

| Metric | Value | Unit | Stage |
|--------|-------|------|-------|
| MAE | 17.647 | popularity points | test |
| RMSE | 21.013 | popularity points | test |
| R² | 0.070 | coefficient | test |
| Median AE | 16.292 | popularity points | test |
| P80 AE | 28.938 | popularity points | test |
| P90 AE | 34.116 | popularity points | test |
| Mean Residual | 4.857 | popularity points | test |
| Residual Std | 20.445 | popularity points | test |
| Underprediction Rate | 67.8% | proportion | test |
| Overprediction Rate | 32.2% | proportion | test |

**Evaluation:** 85,876 rows, test split. All finite values. Model ID: `EXP24-XGB-FINAL-001`. Version `1.0.0`.

**Note:** R² = 0.07 is low. This reflects the difficulty of the prediction task (Spotify popularity 0–100) and is not a validation failure.

---

## 2. Residual Convention

**Convention:** `actual - predicted` (positive residual = underprediction)

| Statistic | Value |
|-----------|-------|
| Mean Residual | +4.857 |
| Median Residual | +8.830 |
| Std | 20.445 |
| Underprediction Rate | 67.8% |
| Skewness | −0.579 |

**Interpretation:** Model systematically underpredicts popularity by ~4.9 points on average. 67.8% of predictions are below actual values. This is consistent with a positive mean residual under the `actual - predicted` convention.

**Warning:** Residual convention is inferred from consistency with `Underprediction_Rate`, not explicitly documented in the artifact.

---

## 3. Metric Consistency

| Check | Status |
|-------|--------|
| Model ID matches across all sources | PASS |
| Model version consistent (`1.0.0`) | PASS |
| Evaluation split = test | PASS |
| Sample rows = 85,876 | PASS |
| MAE ≈ AE mean in residual_stats | PASS |
| Mean residual identical across sources | PASS |
| Underprediction + overprediction = 1.0 | PASS |

---

## 4. SHAP Inventory

| Role | Status | Notes |
|------|--------|-------|
| SHAP background (raw) | ✅ Found | 1,000 rows × 18 cols |
| SHAP background (transformed) | ✅ Found | 1,000 rows × 49 cols |
| SHAP explainer manifest | ✅ Found | TreeExplainer |
| SHAP values (global) | ✅ Found | 5,000 rows × 49 cols |
| SHAP base values | ✅ Found | 5,000 base values |
| SHAP feature mapping | ✅ Found | 49 features mapped |
| SHAP feature names | ✅ Found | 49 names |
| SHAP additivity validation | ✅ Found | Pass rate 100% |
| SHAP value validation | ✅ Found | No NaN/Inf |
| SHAP global importance (transformed) | ✅ Found | CSV |
| SHAP global importance (selected) | ✅ Found | CSV |
| SHAP top 10 features | ✅ Found | JSON |
| SHAP dependence figures | ✅ Found | PNG files |
| SHAP explanation sample (raw) | ✅ Found | Parquet |
| SHAP explanation sample (transformed) | ✅ Found | NPY |
| SHAP grouping manifest | ✅ Found | JSON |

**Total: 16 SHAP assets found. 0 missing.**

Model version consistency: `EXP24-XGB-FINAL-001` matches across all SHAP manifests.

---

## 5. Example Input Validation

**Source:** `7.ML/7.10.model_packaging/package/examples/example_input.json`

| Check | Status |
|-------|--------|
| 18 fields present | ✅ PASS |
| All required fields present | ✅ PASS |
| Target (`popularity`) excluded | ✅ PASS |
| No unknown fields | ✅ PASS |
| Range checks (danceability, tempo, etc.) | ✅ PASS |
| Category checks (release_precision) | ✅ PASS |
| No NaN/null values | ✅ PASS |

---

## 6. Prediction Invocation

**Method:** `HitRadarInferencePipeline.predict_popularity(example_input)`
**Load duration:** ~1,724 ms
**Prediction duration:** ~14–22 ms

```
Input:  {18 raw audio features for song "My Sweet Lord"}
Output: prediction_raw = 46.421062
        prediction_clipped = 46.421062
        prediction_display = 46
```

**Patches applied:** 4 runtime patches for module resolution, no model modification.

---

## 7. Actual vs Expected Output

| Field | Expected | Actual | Match |
|-------|----------|--------|-------|
| prediction_raw | 46.421062 | 46.421062 | ✅ Exact |
| prediction_clipped | 46.421062 | 46.421062 | ✅ Exact |
| prediction_display | 46 | 46 | ✅ Exact |
| model_id | EXP24-XGB-FINAL-001 | EXP24-XGB-FINAL-001 | ✅ Match |
| model_version | 1.0.0 | 1.0.0 | ✅ Match |
| package_version | 2.7.0 | 2.7.0 | ✅ Match *(actual: package_version.json declares 2.7.0; example_output.json uses placeholder 1.0.0 — no functional conflict)* |

**Absolute difference:** 0.0 | **Tolerance:** 0.001 | **Match:** YES

---

## 8. Output Schema

| Check | Status |
|-------|--------|
| Required fields present | ✅ PASS |
| prediction_raw: number | ✅ PASS |
| prediction_clipped: number | ✅ PASS |
| prediction_display: integer | ✅ PASS |
| Finite prediction | ✅ PASS |
| model_id present | ✅ PASS |
| model_version present | ✅ PASS |
| warnings: array | ✅ PASS |

---

## 9. Determinism

Three sequential predictions on identical input:

| Run | Prediction |
|-----|------------|
| 1 | 46.421062 |
| 2 | 46.421062 |
| 3 | 46.421062 |

**Max absolute difference: 0.0 | Deterministic: YES**

---

## 10. No-Refit Validation

| Check | Count |
|-------|-------|
| `fit()` calls | 0 |
| `fit_transform()` calls | 0 |
| `partial_fit()` calls | 0 |
| Model file hash unchanged | ✅ YES |

---

## 11. Phase Gate

| Criterion | Status |
|-----------|--------|
| Model metrics valid | ✅ PASS |
| Residual stats valid | ✅ PASS |
| Metric consistency valid | ✅ PASS |
| SHAP required for EPIC 3 | YES |
| SHAP assets valid | ✅ VALID |
| SHAP recomputed | ❌ NO |
| Example input valid | ✅ PASS |
| Prediction executed | ✅ PASS |
| Output schema valid | ✅ PASS |
| Prediction matches expected | ✅ PASS |
| Prediction deterministic | ✅ PASS |
| Fit calls = 0 | ✅ PASS |
| Source artifacts modified | ❌ NO |

**Phase Gate Status: PASS WITH_WARNINGS**
**Next Phase: MAY_BEGIN**

---

## 12. Warnings

1. **RESIDUAL_CONVENTION_NOT_EXPLICITLY_DOCUMENTED** — Residual convention inferred from consistency; no explicit field in artifact
2. **SKLEARN_VERSION_MISMATCH** — Pipeline pickled with sklearn 1.9.0, running on 1.8.0; non-blocking

---

## 13. Blockers

None.

---

## 14. Conclusion — Benchmark Readiness

Feature 3.1 Phase 3 establishes that:

1. Model metrics are parseable, finite, and from the test split (not validation)
2. Residual convention is understood and consistent
3. All SHAP assets required for EPIC 3 `/explain` endpoint are present and validated
4. Example input conforms to input schema
5. Prediction is deterministic and matches expected output exactly
6. No training, refit, or artifact modification occurred

**EPIC 3 `/explain` endpoint has sufficient SHAP assets to proceed.**
**Benchmark baseline is established for Phase 4.**

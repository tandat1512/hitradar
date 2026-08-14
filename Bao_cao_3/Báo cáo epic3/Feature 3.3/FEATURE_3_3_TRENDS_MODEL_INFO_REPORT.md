# Feature 3.3 — Trends & Model Info Report
## Phase 5 — Music Trends + Model Info

**Feature:** 3.3 — Streamlit Frontend
**Phase:** 5 / 7
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. Music Trends Page

**File:** `pages/4_Trends.py`

### Data Sources

| Source | Content | Purpose |
|---|---|---|
| `5.DATA/processed/ml_ready_dataset.csv` | Raw track data with audio features | Audio feature trends |
| `7.ML/.../yearly_evaluation.csv` | Model evaluation by year | Prediction vs actual, error metrics |

Both are read-only artifacts — no mutation.

### Actual Data Range

- **Dataset:** ~1922–2019 (based on `year_distribution.csv` evidence)
- **Evaluation:** 2014–2021 (8 years, from `yearly_evaluation.csv`)
- Page title reflects actual coverage (`1922–2019`); no data fabricated for missing years

### Aggregation

`mean` per `release_year` for audio features. No imputation for missing years.

### Charts (4 total)

1. **Songs per Year** — bar chart, track count by release year
2. **Audio Feature Trends** — line chart, dropdown: danceability/energy/speechiness/acousticness/instrumentalness/liveness/valence/tempo/loudness
3. **Popularity Trend** — line chart, actual vs predicted mean by year (2014–2021)
4. **Model Error by Year** — line chart, dropdown: MAE/RMSE/R²/actual_mean/predicted_mean

### Hard Rules

| Rule | Status |
|---|---|
| Data source: ml_ready_dataset.csv | ✅ |
| Data source: yearly_evaluation.csv | ✅ |
| No training / refit | ✅ |
| No dataset mutation | ✅ |
| `st.cache_data` for data loading | ✅ |
| Causal disclaimer present | ✅ |
| Limitation warning | ✅ |
| Path relative to repo root (not hardcoded absolute) | ✅ |

### Attribution

> "Historical trends describe the available dataset and should not be interpreted as causal relationships."

---

## 2. Model Info Page

**File:** `pages/5_Model_Info.py`

### API Integration

`GET /model-info` → `ModelInfoResponse`

### Metrics Contract (corrected)

```python
ModelInfoResponse:
  model_id, model_version, model_family,
  package_version, data_version, feature_set,
  training_date, metrics (MAE/RMSE/R2), timestamp
```

`metrics` is a nested object from backend — `MAE`, `RMSE`, `R2` (float or None).

Frontend `api/models.py` updated to match: added `._Metrics` class, `metrics` attribute, `timestamp` field.

### Display

- Model Identity: ID, Family, Version
- Version Info: Data Version, Package Version, API Timestamp
- Training Data: Feature Set
- Evaluation Metrics: MAE / RMSE / R² (from API, not hardcoded)
- Explainability availability
- Model Limitations warning

### Hard Rules

| Rule | Status |
|---|---|
| GET /model-info integration | ✅ |
| No hardcoded model metadata | ✅ |
| Metrics from API response | ✅ |
| "Not accuracy" disclaimer | ✅ |
| No "accuracy" mislabel | ✅ |
| Regression model labeled | ✅ |
| Limitation warning | ✅ |
| Offline-safe (render_error) | ✅ |

---

## 3. API Model Contract Fix

`api/models.py` — `ModelInfoResponse` updated to match backend:

```python
# BEFORE (wrong)
request_id: str | None = data.get("request_id")

# AFTER (correct)
metrics = _Metrics(data.get("metrics", {}))
timestamp: str = data.get("timestamp", "")   # from backend
request_id: str | None = data.get("request_id")  # backward compat
```

---

## 4. Phase Gate

| Check | Status |
|---|---|
| Music Trends source resolved | ✅ |
| Trends page complete | ✅ |
| Source data not modified | ✅ |
| No causal claim | ✅ |
| Model Info page complete | ✅ |
| GET /model-info integration | ✅ |
| Regression metrics labeled correctly | ✅ |
| No accuracy mislabel | ✅ |
| No direct model access | ✅ |

**Status: PASS — MAY BEGIN Phase 6**

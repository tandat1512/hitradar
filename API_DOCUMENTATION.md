# HitRadar Pro API Documentation

**Version:** 1.0.0 · **Base URL:** `http://localhost:8000`
**OpenAPI:** `http://localhost:8000/openapi.json`

---

## 1. Overview

The HitRadar Pro API is a REST service that provides:
- Song popularity prediction from audio features
- SHAP-based feature attribution
- What-if comparison under modified inputs
- Model metadata and feature schema

**No authentication** is required for the local academic/demo application.

**API prefix:** none. Routes are at the root level (`/health`, `/predict`, etc.).

---

## 2. Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 3. Common Behavior

**Content-Type:** All requests and responses use `application/json`.

**Request IDs:** All responses include an optional `request_id` field (nullable). If set, it can be used for tracing.

**Timeouts:**
- Backend read timeout: 30 seconds (default)
- Request timeout: 35 seconds (default)
- Override with `BACKEND_READ_TIMEOUT` / `BACKEND_REQUEST_TIMEOUT` environment variables.

**Model readiness:** Most endpoints return `503` if the model is not yet loaded. The backend must complete model loading before these endpoints are fully available.

---

## 4. GET /health

Health check endpoint — liveness and readiness probe.

**Request:** No parameters.

**Success response (200):**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_ready": true,
  "service_name": "HitRadar Pro API",
  "api_version": "1.0.0",
  "explain_service_available": true,
  "what_if_available": true,
  "model_version": "1.0.0",
  "timestamp": "2026-08-05T10:00:00Z"
}
```

**Status values:**

| status | meaning |
|---|---|
| `healthy` | Backend up and model loaded |
| `degraded` | Backend up but model still loading |
| `unavailable` | Backend not reachable |

**`model_loaded` semantics:**
- `true`: model pipeline is fully loaded → endpoints are ready
- `false`: model loading in progress or failed → `/predict`, `/explain`, `/what-if`, `/model-info`, `/features` return `503`

The `/health` endpoint never runs a full prediction. It only checks whether the `PipelineLoader` singleton has completed loading.

---

## 5. GET /model-info

Return model metadata and evaluation metrics.

**Request:** No parameters.

**Success response (200):**

```json
{
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "model_family": "XGBoost",
  "package_version": "2.7.0",
  "data_version": "1.0.0",
  "feature_set": "FS23-SELECTED",
  "training_date": null,
  "metrics": {
    "MAE": 17.65,
    "RMSE": 21.01,
    "R2": 0.070
  },
  "timestamp": "2026-08-05T10:00:00Z"
}
```

**Error response (503):**
Model not loaded yet. Retry after `/health` returns `model_loaded=true`.

---

## 6. GET /features

Return the canonical input field definitions and selected feature names.

**Request:** No parameters.

**Success response (200):**

```json
{
  "canonical_fields": [
    {
      "name": "danceability",
      "position": 7,
      "data_type": "number",
      "required": true,
      "minimum": 0.0,
      "maximum": 1.0,
      "allowed_categories": null,
      "default_policy": "PIPELINE_IMPUTE"
    }
    // ... 17 more fields
  ],
  "selected_features": [
    "danceability", "energy", "speechiness", "acousticness",
    "instrumentalness", "liveness", "valence", "tempo", "loudness",
    "key", "mode", "time_signature", "duration_min",
    "release_year", "release_month", "decade",
    "explicit", "release_precision"
  ],
  "total_input_fields": 18,
  "total_selected_features": 31,
  "timestamp": "2026-08-05T10:00:00Z"
}
```

The API selects 31 features from the 18 canonical inputs (including engineered features from the pipeline).

**Error response (503):** Model not loaded.

---

## 7. POST /predict

Predict song popularity from 18 audio features.

### Request body

`PredictRequest` — 18 required fields.

```json
{
  "duration_min": 5.1767,
  "explicit": true,
  "release_year": 1992,
  "release_month": 11.0,
  "decade": 1990,
  "release_precision": "day",
  "danceability": 0.785,
  "energy": 0.793,
  "key": 1,
  "loudness": -7.915,
  "mode": 1,
  "speechiness": 0.163,
  "acousticness": 0.22,
  "instrumentalness": 0.718,
  "liveness": 0.124,
  "valence": 0.655,
  "tempo": 88.902,
  "time_signature": 4.0
}
```

**Field constraints:**

| Field | Type | Range / Pattern |
|---|---|---|
| `duration_min` | float | 0.0 – 120.0 |
| `explicit` | boolean | — |
| `release_year` | int | 1900 – 2100 |
| `release_month` | float | 1.0 – 12.0 |
| `decade` | int | 1900 – 2100 |
| `release_precision` | string | `day` \| `month` \| `year` |
| `danceability` | float | 0.0 – 1.0 |
| `energy` | float | 0.0 – 1.0 |
| `key` | int | 0 – 11 |
| `loudness` | float | −60.0 – 0.0 |
| `mode` | int | 0 – 1 |
| `speechiness` | float | 0.0 – 1.0 |
| `acousticness` | float | 0.0 – 1.0 |
| `instrumentalness` | float | 0.0 – 1.0 |
| `liveness` | float | 0.0 – 1.0 |
| `valence` | float | 0.0 – 1.0 |
| `tempo` | float | 0.0 – 300.0 |
| `time_signature` | float | — |

**Extra fields:** `additionalProperties: allow` — extra fields are ignored with a warning.

### Success response (200)

```json
{
  "status": "SUCCESS",
  "prediction_raw": 46.421062,
  "prediction_clipped": 46.421062,
  "prediction_display": 46,
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "package_version": "1.0.0",
  "warnings": [],
  "request_id": "req-abc123",
  "timestamp": "2026-08-05T10:00:00Z"
}
```

**Prediction fields:**

| Field | Description |
|---|---|
| `prediction_raw` | Raw model output — may be outside [0, 100] |
| `prediction_clipped` | Clipped to [0, 100] |
| `prediction_display` | Rounded integer for display |

### Error responses

**422 — Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "danceability"],
      "msg": "ensure float is greater than or equal to 0.0",
      "type": "value_error"
    }
  ]
}
```

**503 — Service Unavailable:** Model not loaded.

---

## 8. POST /explain

Compute SHAP feature attribution for a prediction.

**Uses the same 18-field input as `/predict`.** All 18 fields are required.

### Request body

Same as `PredictRequest` (18 required fields).

### Success response (200)

```json
{
  "status": "SUCCESS",
  "prediction_raw": 46.421062,
  "prediction_clipped": 46.421062,
  "prediction_display": 46,
  "base_value": 42.0,
  "shap_values": {
    "danceability": 1.2,
    "energy": -0.8,
    "speechiness": 0.3,
    "acousticness": 2.1,
    "instrumentalness": -1.5
    // ... 31 total entries (one per selected feature)
  },
  "top_features": [
    {
      "name": "danceability",
      "shap_value": 1.2,
      "feature_value": 0.785
    },
    {
      "name": "energy",
      "shap_value": -0.8,
      "feature_value": 0.793
    }
    // ... top 5 by absolute SHAP magnitude
  ],
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "explanation_method": "SHAP_TreeExplainer",
  "request_id": "req-abc123",
  "timestamp": "2026-08-05T10:00:00Z"
}
```

**SHAP semantics:**
- `base_value`: expected (average) model output across the training dataset
- `shap_values`: per-feature contribution (same unit as prediction); positive = pushes score up, negative = pushes down
- `top_features`: top 5 features by absolute SHAP magnitude

**Important:** SHAP values describe how the model weighed the input features. They do **not** establish causal relationships. A positive SHAP value for danceability does not mean "increasing danceability causes popularity to increase."

### Error responses

**422** — validation error. **503** — model not loaded.

---

## 9. POST /what-if

Compare two predictions: original input vs. modified input.

### Request body

```json
{
  "base_features": {
    "duration_min": 5.1767,
    "explicit": true,
    "release_year": 1992,
    "release_month": 11.0,
    "decade": 1990,
    "release_precision": "day",
    "danceability": 0.785,
    "energy": 0.793,
    "key": 1,
    "loudness": -7.915,
    "mode": 1,
    "speechiness": 0.163,
    "acousticness": 0.22,
    "instrumentalness": 0.718,
    "liveness": 0.124,
    "valence": 0.655,
    "tempo": 88.902,
    "time_signature": 4.0
  },
  "changed_features": {
    "energy": 0.95,
    "danceability": 0.9
  }
}
```

**Constraints:**
- `base_features`: full 18-field input (same as `PredictRequest`)
- `changed_features`: at least 1 key; keys must be canonical field names

### Success response (200)

```json
{
  "status": "SUCCESS",
  "prediction_before": {
    "prediction_raw": 46.42,
    "prediction_clipped": 46.42,
    "prediction_display": 46
  },
  "prediction_after": {
    "prediction_raw": 48.15,
    "prediction_clipped": 48.15,
    "prediction_display": 48
  },
  "delta": 1.73,
  "delta_display": 2,
  "changes_applied": {
    "energy": 0.95,
    "danceability": 0.9
  },
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "request_id": "req-abc123",
  "timestamp": "2026-08-05T10:00:00Z"
}
```

**`delta`** = `prediction_after - prediction_before` (clipped values). Positive means the model's predicted score increased.

**Important:** The delta describes how the **model's prediction** changes. It does **not** prove that changing energy or danceability in the real world will increase a song's popularity.

### Error responses

**422 — Validation Error:**
- Empty `changed_features` (must have at least 1 key)
- Unknown field name in `changed_features` (key not in canonical field names)

**503 — Service Unavailable:** Model not loaded.

---

## 10. Error Responses

### 422 — Validation Error

Triggered by: missing required fields, out-of-range values, invalid enum values, unknown field names in `changed_features` (what-if).

```json
{
  "detail": [
    {
      "loc": ["body", "danceability"],
      "msg": "ensure float is greater than or equal to 0.0",
      "type": "value_error",
      "input": -0.5
    }
  ]
}
```

### 503 — Service Unavailable

Triggered by: endpoints that require model loading, before the model is ready.

```json
{
  "error_code": "MODEL_NOT_LOADED",
  "message": "Model is not loaded yet. Wait for /health to report model_loaded=true.",
  "request_id": null,
  "details": [],
  "timestamp": "2026-08-05T10:00:00Z"
}
```

---

## 11. Example Workflow

### Step 1 — Check readiness

```
GET http://localhost:8000/health
```

Wait until response contains `"model_loaded": true`.

### Step 2 — Get feature definitions

```
GET http://localhost:8000/features
```

Returns the 18 input field definitions with ranges and defaults.

### Step 3 — Predict

```
POST http://localhost:8000/predict
Content-Type: application/json

{
  "duration_min": 5.1767,
  "explicit": true,
  "release_year": 1992,
  "release_month": 11.0,
  "decade": 1990,
  "release_precision": "day",
  "danceability": 0.785,
  "energy": 0.793,
  "key": 1,
  "loudness": -7.915,
  "mode": 1,
  "speechiness": 0.163,
  "acousticness": 0.22,
  "instrumentalness": 0.718,
  "liveness": 0.124,
  "valence": 0.655,
  "tempo": 88.902,
  "time_signature": 4.0
}
```

Response: `prediction_display: 46`

### Step 4 — Explain

```
POST http://localhost:8000/explain
Content-Type: application/json

<same body as above>
```

Response: `base_value`, `shap_values` (31 entries), `top_features` (top 5).

### Step 5 — What-If

```
POST http://localhost:8000/what-if
Content-Type: application/json

{
  "base_features": <same 18 fields>,
  "changed_features": { "energy": 0.95 }
}
```

Response: `prediction_before`, `prediction_after`, `delta`.

---

## 12. Limitations

- **Predictions are model outputs, not causal facts.** The model describes patterns in its training data. Do not infer that modifying a feature will causally change real-world popularity.
- **SHAP values describe model behavior.** They show which features the model weighted heavily, not which features causally determine a song's success.
- **What-if compares model outputs.** A positive delta means the model's predicted score increased — not that the song would actually become more popular.
- **Temporal coverage:** model uses 1900–2021 Spotify-derived project data; it may not generalize to recent or out-of-distribution releases.
- **API response times are not guaranteed.** No SLA is defined for the local demo environment.

See [USER_MANUAL.md](USER_MANUAL.md) and [README.md](README.md) for the full limitations section.

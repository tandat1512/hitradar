# Feature 3.3 — Home & Predict Pages Report
## Phase 3 — Home / Project Overview + Complete Predict Popularity Workflow

**Feature:** 3.3 — Streamlit Frontend
**Phase:** 3 / 7
**Person in Charge:** Minh
**Date:** 2026-08-06
**Status:** PASS

---

## 1. Home Page

**File:** `pages/0_Home.py`

### Content

- Project name and tagline
- Short description: what HitRadar Pro does
- **Research disclaimer**: "student research project"
- **No commercial claims**: not described as commercial or production
- **Limitation warning**: ⚠️ prominent warning about demonstration-only predictions
- Navigation guide (3-column): Predict / Explain / What-If
- Model information panel (from session cache, not called on load)
- Backend status indicator with retry button
- **Does NOT call backend on page load** — static content renders without backend

### Backend Dependency

- Static content renders without backend
- Model info panel uses `cached_model_info` from session state (set by Predict page)
- Retry button for reconnection guidance
- No crash if backend is offline

---

## 2. Predict Form Component

**File:** `components/predict_form.py`

### Architecture

- Generates form from `GET /features` canonical field definitions
- Uses `st.form` — **no API call on widget change**
- Submits all fields at once

### 18 Canonical Fields

| Group | Fields |
|---|---|
| Release metadata | release_year, release_month, decade, release_precision |
| Audio | danceability, energy, speechiness, acousticness, instrumentalness, liveness, valence, tempo, loudness |
| Musical | key (C=0 → B=11), mode (Major/Minor), time_signature |
| Other | duration_min, explicit |

### Field Widget Mapping

| Type | Widget |
|---|---|
| Float [0–1] | `st.slider` |
| Float [wide range] | `st.slider` |
| Integer [year] | `st.number_input` |
| Integer [0–11] | `st.selectbox` |
| Enum/category | `st.selectbox` |
| Boolean | `st.checkbox` |
| String | `st.selectbox` |

### Defaults

- Source: feature metadata `default_policy = "PIPELINE_IMPUTE"` → midpoint of min/max
- No dataset mean used
- Fallback: minimum value

### Payload

Only 18 canonical fields sent to `POST /predict`:
- No `target` field
- No `model_version_override`
- No `selected_features`

---

## 3. Predict Page Workflow

**File:** `pages/1_Predict.py`

### Flow

```
Page load
  → GET /features (cached to session)
  → render_predict_form()
  → User fills form → clicks "Predict"
  → guard: block 'target' field
  → POST /predict (with st.spinner)
  → Success: render_prediction_result() + save to session
  → Error: render_error() by type
```

### Session State After Success

| Key | Content |
|---|---|
| `current_prediction_input` | 18-field dict submitted |
| `current_prediction_result` | Full result dict with version |
| `latest_request_id` | Request ID for debug |
| `cached_model_info` | Model metadata (once) |
| `cached_features` | Feature definitions |

### CTAs After Success

- "Navigate to Explain to see feature contributions"
- "Navigate to What-If to compare scenarios"

### Guard

```python
if "target" in payload:
    st.error("Invalid: 'target' field must not be in prediction request.")
    st.stop()
```

---

## 4. Error Handling

| Error Type | Display |
|---|---|
| 422 | Field-level validation errors |
| 503 | "Service temporarily unavailable" |
| Timeout | "Request timed out" |
| Connection | "Cannot connect to backend" |
| 500 | "Backend error" + request ID |
| Contract error | "Unexpected response format" |

---

## 5. Hard Rules Compliance

| Rule | Status |
|---|---|
| No model loading in pages | ✅ |
| No target field in form | ✅ |
| No hardcoded predictions | ✅ |
| No commercial claims | ✅ |
| No causal language | ✅ |
| Backend status safe when offline | ✅ |
| No backend call on widget change | ✅ (st.form) |
| Prediction not labeled as probability | ✅ |
| Terminology: "Predicted Popularity" | ✅ |
| Session state: no model artifacts | ✅ |
| Session state: no API secrets | ✅ |

---

## 6. Tests

| File | Coverage |
|---|---|
| `test_feature_3_3_home.py` | no model import, research disclaimer, limitation warning, offline-safe |
| `test_feature_3_3_predict.py` | form contract, 18 fields, payload, target blocked, defaults, no model import |
| `test_feature_3_3_session.py` | session keys, no artifact storage, no secrets |

---

## 7. Phase Gate

| Check | Status |
|---|---|
| Home page complete | ✅ |
| Home offline-safe | ✅ |
| Home research disclaimer | ✅ |
| Home limitation warning | ✅ |
| Predict form from canonical contract | ✅ |
| Target field excluded | ✅ |
| POST /predict integration | ✅ |
| Session state valid | ✅ |
| No direct model access | ✅ |
| No probability terminology | ✅ |

**Status: PASS — MAY BEGIN Phase 4**

# HitRadar Pro

> Song popularity prediction with explainable machine learning.

**Project type:** Academic / student machine learning project
**Model:** XGBoost regression · version 1.0.0 (EXP24-XGB-FINAL-001)
**Dataset:** 586,672 songs · 1900–2021 · 18 input features → 31 selected features
**Python:** 3.13.14 in the validated defense environment (requires ≥3.10)

---

## Overview

HitRadar Pro is a web application that predicts a song's popularity score (0–100) from audio and metadata features and explains individual predictions using SHAP values. It is designed to demonstrate how gradient-boosted tree models behave on a structured music dataset — not to produce production-grade music recommendation.

**Prediction target:** continuous popularity score (integer 0–100), as modeled in Feature 2.4.

---

## Key Features

| Feature | Description | Status |
|---|---|---|
| Popularity Prediction | POST `/predict` — 18-field input → popularity score | Implemented |
| SHAP Explanation | POST `/explain` — feature contributions for a given prediction | Implemented |
| What-If Simulator | POST `/what-if` — compare predictions under changed inputs | Implemented |
| Music Trends Dashboard | Descriptive statistics and visualizations from the training dataset | Implemented |
| Model Info | `/model-info` — model metadata and training metrics | Implemented |
| Limitations & Responsible Use | Honest limitations and appropriate-use guidance | Implemented |
| Offline Demo Mode | Precomputed validated fallback when live API is unavailable | Design complete; UI implementation pending |

---

## System Architecture

```
Browser (Streamlit UI — port 8501)
    → HTTP REST (httpx)
        → FastAPI Backend (port 8000)
            → ModelService / ExplainService / WhatIfService
                → PipelineLoader
                    → artifacts/epic2/pipeline/full_inference_pipeline.joblib
                    → artifacts/epic2/schemas/
                    → 7.ML/7.4.feature_transformers/ohe_and_scaler.joblib
                        → Song popularity score (0–100)

Music Trends Dashboard (local dataset):
    → 5.DATA/processed/ml_ready_dataset.csv (586,672 rows)
```

**No direct model access from the frontend.** The frontend never loads model artifacts, never computes SHAP values, and never calls the model package directly.

---

## Technology Stack

| Component | Technology |
|---|---|
| Backend | FastAPI ≥ 0.110 · uvicorn ≥ 0.30 |
| Frontend | Streamlit ≥ 1.30 |
| Model | XGBoost ≥ 2.0 · scikit-learn ≥ 1.5 |
| Explainability | SHAP ≥ 0.45 |
| Serialization | joblib ≥ 1.4 |
| HTTP client | httpx ≥ 0.27 |
| Data validation | Pydantic ≥ 2.0 |
| Python | 3.13.14 validated defense environment; requires ≥3.10 |

---

## Quick Start

### 1. Environment

```bash
# Defense environment validated with Python 3.13.14 (requires ≥3.10)
python --version

# Backend dependencies
pip install -r 5.UNG_DUNG/5.1.backend_api/requirements.txt

# Frontend dependencies
pip install -r epic3/feature_3_3/frontend/requirements.txt
```

### 2. Start the application

**Option A — Full stack (recommended):**
```bash
python scripts/run_all.py
```
This starts the backend, waits for it to be ready, then starts the frontend.

**Option B — Individual terminals:**
```bash
# Terminal 1: Backend
python scripts/run_backend.py

# Terminal 2: Frontend
python scripts/run_frontend.py
```

### 3. Open in browser

| Service | URL |
|---|---|
| Frontend (Streamlit) | http://localhost:8501 |
| Backend API | http://127.0.0.1:8000 |
| Backend docs | http://127.0.0.1:8000/docs |

### Demo flow

1. Home
2. **Predict Popularity** — enter song features → popularity score
3. **SHAP Explanation** — see which features drove the prediction
4. **What-If Simulator** — modify features and compare predictions
5. **Music Trends** — dataset statistics and visualizations
6. **Model Info** — model metadata and metrics
7. **Limitations & Responsible Use** — honest limitations

### Troubleshooting

- Backend won't start → check `artifacts/epic2/` is present; see `DEMO_RUNBOOK_FEATURE_3_6.md`
- Frontend can't connect → verify backend is running and `BACKEND_BASE_URL` is correct
- Port in use → override with `BACKEND_PORT=XXXX` / `STREAMLIT_SERVER_PORT=YYYY`. When changing `BACKEND_PORT`, also set `BACKEND_BASE_URL=http://localhost:XXXX` explicitly before `python scripts/run_all.py`; the current launcher does not derive and propagate that frontend URL reliably.

---

## Repository Structure

```
H:\dự án\DUAN1 github\
├── 5.UNG_DUNG/
│   └── 5.1.backend_api/          # FastAPI backend
│       ├── api.py                 # Main entrypoint
│       ├── config.py              # Artifact path configuration
│       ├── pipeline_loader.py      # Model loading
│       ├── models/                # Pydantic request/response schemas
│       └── requirements.txt        # Backend dependencies
│   └── 5.2.frontend/              # Legacy/alternative frontend
│
├── epic3/
│   └── feature_3_3/
│       └── frontend/              # Canonical Streamlit frontend
│           ├── app.py             # Main entrypoint
│           ├── core/              # Config, session, navigation
│           ├── api/               # HTTP client, typed responses
│           ├── components/         # Reusable UI components
│           └── pages/            # 7 Streamlit pages
│
├── artifacts/
│   └── epic2/                    # Model artifacts & metadata
│       ├── pipeline/             # Champion model: full_inference_pipeline.joblib
│       ├── metadata/              # model_version, model_metrics, package_version, data_version
│       ├── schemas/               # Input/output schemas
│       └── examples/             # Canonical E2E example
│
├── 7.ML/                         # ML training artifacts
│   ├── 7.4.feature_transformers/ # ohe_and_scaler.joblib
│   └── 7.9.explainability/       # SHAP artifacts
│
├── 5.DATA/processed/
│   └── ml_ready_dataset.csv       # Locked ML-ready dataset (586,672 rows)
│
├── scripts/                       # Demo startup (Feature 3.6)
│   ├── _common.py                # Shared helpers
│   ├── run_backend.py            # Start backend
│   ├── run_frontend.py           # Start frontend
│   └── run_all.py                # Full stack orchestrator
│
├── demo/                          # Demo assets (Feature 3.6)
│   ├── backup/screenshots/        # Backup screenshots (MANUAL_CAPTURE_REQUIRED)
│   ├── backup/video/              # Backup demo video (MANUAL_RECORDING_REQUIRED)
│   └── offline/evidence/          # Precomputed offline demo evidence
│
├── 6.TAI_LIEU/                   # General project documentation
├── Bao_cao_3/                    # EPIC 3 closure reports and validation
└── README.md                      # This file
```

---

## Documentation

| Document | Purpose |
|---|---|
| [HOW_TO_RUN_APP.md](HOW_TO_RUN_APP.md) | Detailed setup, configuration, and startup instructions |
| [USER_MANUAL.md](USER_MANUAL.md) | End-user guide for all pages and features |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | API reference for all endpoints, schemas, and error codes |
| [TECHNICAL_APPENDIX.md](TECHNICAL_APPENDIX.md) | Model details, metrics, data schema, architecture decisions |

---

## Testing

- Frontend component tests: `epic3/feature_3_3/frontend/tests/`
- API integration tests: Feature 3.5 E2E test artifacts
- Performance benchmark artifacts: Feature 3.6 validation directory

**Live test execution blocked** (no Python environment in current session) — see `Bao_cao_3/Báo cáo epic3/feature_3_6/`.

---

## Model & Data Overview

- **Algorithm:** XGBoost regression
- **Champion model:** `artifacts/epic2/pipeline/full_inference_pipeline.joblib` (model_id: EXP24-XGB-FINAL-001, version: 1.0.0)
- **Feature set:** FS23-SELECTED (31 features from 18 raw inputs)
- **Training data:** `5.DATA/processed/ml_ready_dataset.csv` (586,672 rows, 1900–2021)
- **Full metrics:** see [TECHNICAL_APPENDIX.md](TECHNICAL_APPENDIX.md)

---

## Limitations

This application is built for demonstration and academic purposes. See [USER_MANUAL.md](USER_MANUAL.md) §Limitations and [TECHNICAL_APPENDIX.md](TECHNICAL_APPENDIX.md) for the complete limitations section.

Key points:
- **Predictions describe model behavior, not causal relationships.**
- The model uses historical Spotify-derived data (1900–2021) and may not generalize to recent or out-of-distribution releases.
- The model does not account for artist popularity, marketing, or external factors.

---

## Demo Reliability

For presentation-day preparation, see:
- [demo_reliability_checklist.md](Bao_cao_3/Báo%20cáo%20epic3/feature_3_6/demo_reliability_checklist.md)
- [DEMO_RUNBOOK_FEATURE_3_6.md](Bao_cao_3/Báo%20cáo%20epic3/feature_3_6/DEMO_RUNBOOK_FEATURE_3_6.md)

---

## Academic Context

Developed as part of the EPIC 3 — Productization, Integration & Defense project.

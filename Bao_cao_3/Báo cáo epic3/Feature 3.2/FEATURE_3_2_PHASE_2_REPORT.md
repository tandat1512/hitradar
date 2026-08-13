# Feature 3.2 — FastAPI Backend — Phase 2 Report
**Feature:** 3.2 — FastAPI Backend
**Phase:** 2 / 6
**Person in Charge:** Minh
**Date:** 2026-08-05
**Status:** PASS

---

## 1. Mục tiêu Phase 2

Refactor `api.py` (Phase 1) thành layered architecture:
- **Routers** — thin, chỉ nhận request/response, gọi service
- **Services** — business logic thật
- **Main app** — app factory tách rời, không load model ở import time

Hard rules tuân thủ: không train, không refit, không sửa artifact nguồn.

---

## 2. Deliverables

### 2.1 Backend Structure

```
epic3/feature_3_2/backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  ← App factory + lifespan + middleware
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            ← All config, paths from __file__
│   │   └── exceptions.py         ← BackendError, ModelNotLoadedError, …
│   ├── api/
│   │   ├── __init__.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py         ← GET /health
│   │       ├── model_info.py     ← GET /model-info, GET /features
│   │       ├── predict.py        ← POST /predict
│   │       ├── explain.py        ← POST /explain
│   │       └── whatif.py         ← POST /what-if
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py             ← HealthResponse, ModelInfoResponse, ErrorResponse
│   │   ├── prediction.py         ← PredictRequest, PredictResponse
│   │   ├── explanation.py        ← ExplainRequest, ExplainResponse, TopFeature
│   │   └── what_if.py            ← WhatIfRequest, WhatIfResponse, PredictionShort
│   └── services/
│       ├── __init__.py
│       ├── pipeline_loader.py     ← PipelineLoader singleton + runtime patches
│       ├── model_service.py      ← ModelService: predict(), get_model_info()
│       ├── explain_service.py    ← ExplainService: explain() with SHAP
│       └── whatif_service.py     ← WhatIfService: compare()
└── tests/
    └── __init__.py
```

### 2.2 App Factory Pattern

```python
# main.py
def create_app() -> FastAPI:
    app = FastAPI(
        title=config.APP_NAME,
        lifespan=lifespan,
    )
    app.include_router(health.router)
    ...
    return app
```

- Model loaded **trong lifespan** (server startup), không phải khi import module
- `PipelineLoader.set_instance()` / `clear_instance()` cho singleton pattern
- `lifespan` là asynccontextmanager

### 2.3 Service Classes

| Class | Responsibility |
|---|---|
| `ModelService` | predict(), get_model_info(), get_features(), is_healthy() |
| `ExplainService` | explain() — SHAP TreeExplainer trên XGBoost model |
| `WhatIfService` | compare() — before/after prediction + delta |

Service nhận `PipelineLoader` (dependency injection), không tự khởi tạo.

### 2.4 Router Responsibilities

| Router | What it does |
|---|---|
| `health.py` | GET /health — trả HealthResponse |
| `model_info.py` | GET /model-info + GET /features — gọi ModelService |
| `predict.py` | POST /predict — gọi ModelService.predict() |
| `explain.py` | POST /explain — gọi ExplainService.explain() |
| `whatif.py` | POST /what-if — gọi WhatIfService.compare() |

### 2.5 Path Resolution (config.py)

```
backend/app/core/config.py
  parent[1] → app/core
  parent[2] → app
  parent[3] → backend/
  parent[4] → feature_3_2/
  parent[5] → epic3/
  parent[6] → DUAN1 github/   ← REPO_ROOT
  _REPO_ROOT = parent[6]

ARTIFACTS_PATH = _REPO_ROOT / "artifacts" / "epic2"
PIPELINE_PATH = resolved from config
EPIC2_FE_TRANSFORMERS = _REPO_ROOT / "7.ML" / "7.6.feature_engineering" / "src" / "transformers.py"
```

### 2.6 Pydantic Schemas (Phase 1 reused)

| Schema | File | Fields |
|---|---|---|
| PredictRequest | prediction.py | 18 canonical + extra="allow" |
| PredictResponse | prediction.py | 10 fields |
| ExplainRequest | explanation.py | 18 canonical |
| ExplainResponse | explanation.py | 11 fields + base_value + shap_values + top_features |
| WhatIfRequest | what_if.py | base_features + changed_features (min_length=1) |
| WhatIfResponse | what_if.py | before/after + delta |
| HealthResponse | common.py | 3 fields |
| ModelInfoResponse | common.py | 9 fields + metrics |
| ErrorResponse | common.py | 5 fields |
| FieldDescriptor | common.py | 8 fields |

---

## 3. Architecture Decisions

### 3.1 Router-Service Separation

**Rule:** Router chỉ validate request, gọi service, map response. Không có business logic.

**Why:** Testable independently, service có thể reuse trong CLI/batch scripts.

### 3.2 PipelineLoader Singleton

```
app.startup  → PipelineLoader.set_instance(loader)
              → loader.pipeline  (eager load)
request      → PipelineLoader.get_instance()  (singleton access)
app.shutdown → PipelineLoader.clear_instance()
```

**Why:** Một pipeline instance duy nhất, không tạo mới mỗi request.

### 3.3 ExplainService: XGBoost Model, not Full Pipeline

```python
xgb_model = loader.pipeline.champion_pipeline.named_steps["model"]
self._explainer = shap.TreeExplainer(xgb_model)
```

**Why:** `shap.TreeExplainer` không hỗ trợ sklearn.Pipeline trực tiếp. Truyền XGBoost model step.

### 3.4 WhatIfService: Base + Changes Contract

```python
WhatIfRequest = { base_features: PredictRequest, changed_features: dict }
```

**Why:** Caller chỉ gửi thay đổi, không phải full record. Service merge vào base rồi predict.

---

## 4. Hard Rules Compliance

| Rule | Status |
|---|---|
| Không train | ✅ Không có .fit() |
| Không tuning | ✅ Không có tuning code |
| Không refit | ✅ fit interception patch vẫn active |
| Không thay champion | ✅ Không sửa model artifact |
| Không hardcode paths | ✅ Tất cả paths từ __file__ |
| Không sửa EPIC 2 artifacts | ✅ Không chỉnh sửa nguồn |

---

## 5. E2E Verification

Server: `http://127.0.0.1:8767`, model eager-loaded at startup.

| Endpoint | Method | Status | Response |
|---|---|---|---|
| `/health` | GET | 200 | `model_loaded: true` |
| `/model-info` | GET | 200 | `model_id: EXP24-XGB-FINAL-001` |
| `/features` | GET | 200 | `fields: 18, selected: 31` |
| `/predict` | POST | 200 | `raw: 28.347221, display: 28` |
| `/explain` | POST | 200 | `base_value: 22.879942, top1: release_year` |
| `/what-if` | POST | 200 | `delta: 8.208` (1992→2020) |

**6/6 endpoints 200 OK.**

---

## 6. Warnings

| ID | Type | Severity | Detail |
|---|---|---|---|
| W1 | sklearn version mismatch | INFO | Pipeline pickled with 1.9.0, runtime 1.8.0 — WARNING only, not an error |
| W2 | unused import | HINT | `ModelNotLoadedError` imported but not used in explain_service.py (caught by linter) |

---

## 7. Blockers

None.

---

## 8. Phase 2 Gate

| Criterion | Status |
|---|---|
| Project structure matches spec | ✅ |
| App factory pattern implemented | ✅ |
| No model load at import time | ✅ |
| PipelineLoader singleton | ✅ |
| ModelService thin router | ✅ |
| ExplainService with XGBoost model | ✅ |
| WhatIfService with validation | ✅ |
| 4 runtime patches applied | ✅ |
| 6/6 endpoints 200 OK | ✅ |
| No training/refit | ✅ |
| No source artifact modified | ✅ |
| No hardcoded paths | ✅ |

**Phase 2 Gate: PASS — MAY BEGIN Phase 3**

---

## 9. Next Phase

**Phase 3:** CORS → structured logging → centralized error handling → request ID middleware → GET endpoints refinement.

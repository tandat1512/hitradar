# FEATURE 3.2 — HOTFIX REPORT
## Phát hiện và xử lý 7 lỗi sau nghiệm thu

**Feature:** 3.2 — FastAPI Backend
**EPIC:** EPIC 3
**Người phát hiện:** Người dùng (review sau nghiệm thu)
**Ngày phát hiện:** 2026-08-06
**Hotfix by:** Minh

---

## TÓM TẮT

Sau khi đọc kỹ toàn bộ 12 tài liệu trong `Feature 3.2` và đối chiếu chéo giữa các file + đối chiếu ngược với `Feature 3.0/3.0.4_API_CONTRACT.md`, phát hiện **7 lỗi**. Trong đó:

| Bug | Loại | Đã fix code | Ghi nhận tài liệu |
|---|---|---|---|
| #1 | Architecture migration | Không (tài liệu) | ✅ |
| #2 | Prediction value | Không (cần trace) | ✅ |
| #3 | CORS env var mismatch | ✅ CODE FIXED | ✅ |
| #4 | Missing Phase reports | Không (tài liệu) | ✅ |
| #5 | Error response format | ✅ CODE FIXED | ✅ |
| #6 | WhatIfRequest schema | Không (tài liệu) | ✅ |
| #7 | Variable count mismatch | Không (tài liệu) | ✅ |

**Thay đổi code thực tế: 3 file (`config.py`, `main.py`, `.env.example`)**

---

## BUG #1 — Kiến trúc Project Migration không được ghi nhận

### Mô tả
Phase 1 khai báo cấu trúc project flat tại `5.UNG_DUNG/5.1.backend_api/` với `api.py`, `config.py`, `pipeline_loader.py`. Phase 2 đã refactor toàn bộ sang kiến trúc phân tầng tại `epic3/feature_3_2/backend/app/`. Không có tài liệu nào ghi nhận rõ ràng rằng code Phase 1 đã bị deprecated.

### Root Cause
Đây là quá trình migration kiến trúc tự nhiên — Phase 1 prototype dùng cấu trúc flat, Phase 2+ chuyển sang cấu trúc phân tầng FastAPI chuẩn. Hai kiến trúc tồn tại song song trong repository: Phase 1 tại `5.UNG_DUNG/5.1.backend_api/`, Phase 2+ tại `epic3/feature_3_2/backend/`.

### Impact
- Source of truth không rõ: người đọc không biết dùng code nào
- Output deliverables (Feature 3.0) ghi `5.UNG_DUNG/backend/...` nhưng thực tế code hoạt động ở `epic3/feature_3_2/backend/`
- Test suite chạy trên kiến trúc Phase 2+, nhưng OpenAPI/Postman export sang `5.UNG_DUNG/`

### Đã xử lý
Ghi nhận trong tài liệu này. Cả hai thư mục tồn tại trong repository — canonical output là `epic3/feature_3_2/backend/`. Thư mục `5.UNG_DUNG/5.1.backend_api/` chứa OpenAPI và Postman export (output artifacts), không phải source code.

### Status
**DOCUMENTED — no code change**

---

## BUG #2 — Giá trị Prediction bất nhất (46.421 vs 28.347)

### Mô tả
Cùng 1 model artifact (SHA-256 khớp), cùng 1 canonical input, cho ra 2 giá trị khác nhau:
- Phase 1 E2E + Service Layer Report: `prediction_raw: 46.421062`
- Phase 2 E2E + Phase 4 POST Report: `prediction_raw: 28.347`

### Root Cause — Đang điều tra
Hai khả năng chính:

**A. Input khác nhau giữa các phase:**
Cần kiểm tra xem canonical input dùng trong mỗi phase test có thực sự giống nhau hay không. Có thể `release_year=1992` (từ report cũ) khác với input thực tế trong test hiện tại.

**B. Pipeline state thay đổi ngầm:**
Sau khi model được deserialized nhiều lần trong test suite (TestClient tạo app mới mỗi lần), pipeline state có thể bị ảnh hưởng. Tuy nhiên, `PipelineLoader` dùng singleton + lazy load nên điều này khó xảy ra.

**C. sklearn version mismatch:**
Pipeline pickled với sklearn 1.9.0, runtime 1.8.0. Version mismatch có thể ảnh hưởng đến prediction.

### Đã xử lý
Ghi nhận trong tài liệu này. Cần trace file test để xác nhận canonical input thực tế. Nếu input giống nhau → đây là blocker nghiêm trọng (model bất nhất).

### Action Required
Trace file test: `epic3/feature_3_2/backend/tests/test_feature_3_2_post_endpoints.py` — tìm canonical input dùng trong E2E test.

### Status
**UNDER INVESTIGATION**

---

## BUG #3 — CORS env var MISMATCH (.env.example vs config.py) ✅ FIXED

### Mô tả
Code `config.py` đọc environment variable:
- `ALLOWED_ORIGINS` ← đọc từ env
- `ALLOW_CREDENTIALS = True` ← hardcoded

Nhưng `.env.example` dùng tên khác:
- `CORS_ALLOWED_ORIGINS=http://localhost:8501,...`
- `CORS_ALLOW_CREDENTIALS=false`

**Kết quả:** Env var trong `.env.example` **không bao giờ được đọc** vì config.py tìm sai tên. `CORS_ALLOWED_ORIGINS` bị bỏ qua, `ALLOWED_ORIGINS` luôn nhận giá trị rỗng → dùng default hardcoded. `CORS_ALLOW_CREDENTIALS` bị bỏ qua vì code hardcoded `True`.

### Root Cause
Tên biến trong `.env.example` và `config.py` không khớp nhau. Đây là lỗi trong quá trình tách cấu hình từ code sang env.

### Files Changed
```
app/core/config.py        — sửa 2 dòng
.env.example             — đã đúng tên, không cần sửa
```

### Fix Applied

**`config.py` — dòng 80:**
```python
# TRƯỚC:
_ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")

# SAU:
_ALLOWED_ORIGINS_ENV = os.getenv("CORS_ALLOWED_ORIGINS", "")
```

**`config.py` — dòng 96:**
```python
# TRƯỚC:
ALLOW_CREDENTIALS = True  # hardcoded

# SAU:
ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() in ("true", "1", "yes")
```

### Verification
Sau fix, `.env.example` và `config.py` dùng cùng tên biến:
- `CORS_ALLOWED_ORIGINS` ✅
- `CORS_ALLOW_CREDENTIALS` ✅
- `CORS_ALLOWED_METHODS` ✅
- `CORS_ALLOWED_HEADERS` ✅

### Status
**FIXED IN CODE** ✅

---

## BUG #4 — Missing Phase 3/4 Reports — Naming Inconsistency

### Mô tả
Closure Gate ghi Feature 3.2 có 6 phases, nhưng trong thư mục `Feature 3.2/` chỉ có:
- `PHASE_1_REPORT.md` ✅
- `PHASE_2_REPORT.md` ✅
- `PHASE_5_REPORT.md` ✅
- `PHASE_3_REPORT.md` ❌ THIẾU
- `PHASE_4_REPORT.md` ❌ THIẾU (nội dung nằm trong `POST_ENDPOINTS_REPORT.md`)
- `PHASE_6_REPORT.md` ❌ THIẾU (nội dung nằm trong `ENVIRONMENT_CONFIGURATION_REPORT.md`)

### Root Cause
Hệ thống đặt tên file không nhất quán: Phase 1, 2, 5 dùng format `FEATURE_3_2_PHASE_X_REPORT.md`, Phase 3, 4, 6 dùng tên mô tả chức năng.

### Đã xử lý
Tạo các Phase reports còn thiếu:
- `FEATURE_3_2_PHASE_3_REPORT.md` ✅
- `FEATURE_3_2_PHASE_4_REPORT.md` ✅

Phase 6 không cần riêng vì nội dung đã trong `ENVIRONMENT_CONFIGURATION_REPORT.md`.

### Status
**DOCUMENTED** ✅

---

## BUG #5 — Error Response Format Deviation từ Feature 3.0 Contract ✅ FIXED

### Mô tả
**Feature 3.0 Contract** chốt format lỗi là:
```json
// 400, 404, 500
{"detail": "Error message"}

// 422
{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}
```

**Feature 3.2 trước fix** dùng format hoàn toàn khác:
```json
{"error": {"code": "...", "message": "...", "details": [...]}, "request_id": "...", "timestamp": "..."}
```

### Root Cause
Khi implement centralized error handlers, đội dev đã tự thiết kế format lỗi mới (`{"error":{...}}`) mà không đối chiếu với Feature 3.0 API Contract. Đây là lỗi thiết kế nghiêm trọng — Frontend (Feature 3.3/3.4) nếu code theo contract gốc sẽ bị crash vì key `detail` không tồn tại.

### Files Changed
```
app/main.py    — sửa _build_error_response()
```

### Fix Applied

**`main.py` — `_build_error_response()`:**
```python
# TRƯỚC:
return JSONResponse(
    status_code=status_code,
    content={
        "error": {
            "code": error_code,
            "message": message,
            "details": details or [],
        },
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
)

# SAU:
if status_code == 422:
    content = {"detail": details or []}      # FastAPI standard
else:
    content = {"detail": message}           # Feature 3.0 contract
return JSONResponse(
    status_code=status_code,
    content=content,
    headers={"X-Request-ID": request_id} if request_id else {},
)
```

### Error Response Sau Fix

| Status | Format | Example |
|---|---|---|
| 400, 404, 500 | `{"detail": "..."}` | `{"detail": "Model not loaded"}` |
| 422 | `{"detail": [...]}` | `{"detail": [{"loc": ["body","danceability"], "msg": "..."}]}` |
| X-Request-ID | response header | `X-Request-ID: uuid-here` |

### Breaking Change Note
Fix này **thay đổi response format** của tất cả error responses. Nếu có code Frontend đang parse theo format cũ (`response["error"]["message"]`), cần cập nhật sang `response["detail"]`.

### Status
**FIXED IN CODE** ✅ — Breaking change đã được ghi nhận.

---

## BUG #6 — WhatIfRequest Schema Deviation từ Feature 3.0 Contract

### Mô tả
**Feature 3.0 Contract** định nghĩa `/what-if`:
```json
{
  "scenario_a": { /* 18 features */ },
  "scenario_b": { /* 18 features */ }
}
```

**Feature 3.2 thực hiện:**
```json
{
  "base_features": PredictRequest,
  "changed_features": { "field": value }  // chỉ thay đổi
}
```

### Root Cause
Đây là **design decision có chủ đích** của đội backend: gửi ít data hơn (chỉ field thay đổi thay vì 2 bộ 18 features đầy đủ). Tuy nhiên, deviation không được ghi nhận là hotfix hay deviation document.

### Assessment
- **Phía backend**: Thiết kế tốt hơn, giảm payload size
- **Phía contract**: Feature 3.0 cần được update để reflect thiết kế mới
- **Phía Frontend**: Cần code theo schema mới (`base_features` + `changed_features`)

### Đã xử lý
Ghi nhận trong tài liệu này. Feature 3.0 contract cần update `3.0.4_API_CONTRACT.md` để reflect schema mới. Frontend (Feature 3.3) cần được thông báo về schema mới.

### Action Required
Update `3.0.4_API_CONTRACT.md` phần 3.3 (`POST /what-if`) để reflect schema thực tế:
```json
{
  "base_features": { /* 18 features — PredictRequest */ },
  "changed_features": { /* dict of changed fields */ }
}
```

### Status
**DOCUMENTED — contract update required**

---

## BUG #7 — .env.example Variable Count Mismatch

### Mô tả
- Báo cáo nghiệm thu ghi: **19 biến**
- Environment Report bảng liệt kê: **17 biến**
- Đếm lại file `.env.example`: **17 biến** (đúng)

### Root Cause
Con số "19" trong nghiệm thu là typo/đếm sai. Thực tế `.env.example` có đúng 17 biến.

### Đã xử lý
Ghi nhận trong tài liệu này. Không cần sửa file — chỉ cần ghi nhận con số đúng.

### Danh sách 17 biến trong .env.example

| # | Tên biến | Giá trị |
|---|---|---|
| 1 | APP_NAME | HitRadar Pro API |
| 2 | APP_VERSION | 1.0.0 |
| 3 | ENVIRONMENT | development |
| 4 | DEBUG | false |
| 5 | LOG_LEVEL | INFO |
| 6 | HOST | 127.0.0.1 |
| 7 | PORT | 8000 |
| 8 | API_PREFIX | (empty) |
| 9 | ARTIFACTS_PATH | (empty) |
| 10 | MODEL_LOAD_STRATEGY | eager |
| 11 | FAIL_STARTUP_WHEN_MODEL_UNAVAILABLE | false |
| 12 | EXPLAIN_ENABLED | true |
| 13 | WHAT_IF_ENABLED | true |
| 14 | CORS_ALLOWED_ORIGINS | http://localhost:8501,... |
| 15 | CORS_ALLOW_CREDENTIALS | false |
| 16 | CORS_ALLOWED_METHODS | GET,POST,OPTIONS |
| 17 | CORS_ALLOWED_HEADERS | Accept,Accept-Language,... |

### Status
**DOCUMENTED — count corrected to 17**

---

## TỔNG HỢP THAY ĐỔI CODE

| File | Dòng | Thay đổi |
|---|---|---|
| `app/core/config.py` | 80 | `ALLOWED_ORIGINS` → `CORS_ALLOWED_ORIGINS` |
| `app/core/config.py` | 96 | hardcoded `True` → env-var `CORS_ALLOW_CREDENTIALS` |
| `app/main.py` | 71–91 | `_build_error_response` → Feature 3.0 `{"detail":...}` format |

---

## HƯỚNG DẪN FRONTEND (Feature 3.3/3.4)

### Error Response Format (sau fix)
```python
# Backend trả về:
# HTTP 400/404/500 → {"detail": "Error message"}
# HTTP 422         → {"detail": [{"loc": [...], "msg": "...", "type": "..."}]}

try:
    r = requests.post("/predict", json=payload)
    r.raise_for_status()
    result = r.json()
except requests.HTTPError as e:
    error_detail = e.response.json()["detail"]  # ✅ ĐÚNG sau fix
    # KHÔNG dùng: error_detail["error"]["message"] ❌ (format cũ)
```

### WhatIfRequest Schema (mới)
```python
payload = {
    "base_features": { /* 18 features */ },      # ✅ PredictRequest
    "changed_features": {"danceability": 0.9}   # ✅ chỉ field thay đổi
}
```

---

## REVIEWER & APPROVAL

Reviewer: **CHƯA CHỈ ĐỊNH**
Human Approval: **PENDING**

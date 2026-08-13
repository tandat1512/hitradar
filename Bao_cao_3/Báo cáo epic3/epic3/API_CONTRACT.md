# API CONTRACT — EPIC 3: HitRadar Pro FastAPI Backend
**Ngày chốt:** 2026-07-30
**Phiên:** 2
**Người phụ trách:** Minh
**Nguồn tham chiếu:** `input_schema.json`, `output_schema.json`, `feature_names.json`, `selected_features.json`, `example_input.json`, `example_output.json`, `model_version.json`, `package_version.json`, `data_version.json`, `runtime/inference_pipeline.py` từ `7.ML/7.10.model_packaging/package/`

---

## Tổng quan

**Base URL:** `http://localhost:8000` (mặc định; configurable qua `API_BASE_URL` env var)
**OpenAPI:** `GET /docs` (Swagger UI), `GET /openapi.json` (schema)

### Base Configuration
- **Framework:** FastAPI (uvicorn)
- **CORS:** Enabled cho tất cả origins (`*`) trong development; restrict trong production
- **JSON:** `application/json` cho cả request và response
- **Artifact path:** configurable qua `ARTIFACTS_PATH` env var, không hardcode
- **Model load:** at startup (singleton), không lazy-load per request

### Error Response Format (chung cho tất cả endpoints)
```json
{
  "error": true,
  "code": 400,
  "message": "Human-readable error message",
  "detail": { ... }
}
```

### HTTP Status Codes
| Code | Khi nào | Ví dụ |
|------|---------|-------|
| 200 | Thành công | Response bình thường |
| 400 | Request không đúng JSON | Body không parse được |
| 422 | Sai schema | Thiếu field, sai kiểu, giá trị ngoài range |
| 500 | Lỗi nội bộ | Model chưa load, exception không lường |

---

## GET /health

Kiểm tra trạng thái service và model readiness.

### (a) Request
```
GET /health
Header: Content-Type: application/json
Body: (không có)
```

### (b) Response Schema
| Field | Kiểu | Mô tả |
|-------|------|--------|
| `status` | string | `"healthy"` hoặc `"degraded"` |
| `model_loaded` | boolean | Model đã load thành công chưa |
| `timestamp` | string (ISO 8601) | Thời điểm check |

### (c) Response Examples

**Thành công — model đã load:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-07-30T10:15:00+07:00"
}
```

**Degraded — model chưa load:**
```json
{
  "status": "degraded",
  "model_loaded": false,
  "timestamp": "2026-07-30T10:15:00+07:00"
}
```

### (d) Error Codes
- **500:** Lỗi khi kiểm tra model load (exception không lường trước)

---

## GET /model-info

Trả về thông tin về model đang chạy: tên, version, training date, metrics, feature set.

### (a) Request
```
GET /model-info
Header: Content-Type: application/json
Body: (không có)
```

### (b) Response Schema
| Field | Kiểu | Mô tả |
|-------|------|--------|
| `model_id` | string | Model identifier: `"EXP24-XGB-FINAL-001"` |
| `model_version` | string | Semantic version: `"1.0.0"` |
| `model_family` | string | `"XGBoost"` |
| `package_version` | string | Package version: `"2.7.0"` |
| `data_version` | string | Data version: `"1.0.0"` |
| `feature_set` | string | Feature set ID: `"FS23-SELECTED"` |
| `training_date` | string \| null | Ngày train model (từ `model_metrics.json`); `null` nếu artifact không có |
| `metrics` | object \| null | Performance metrics trên test set |
| `metrics.MAE` | number \| null | Mean Absolute Error |
| `metrics.RMSE` | number \| null | Root Mean Square Error |
| `metrics.R2` | number \| null | R-squared |
| `timestamp` | string (ISO 8601) | |

> **⚠️ Lưu ý:** `training_date` và `metrics` phụ thuộc vào artifact `model_metrics.json` (Nhóm B — **CẦN XÁC NHẬN** từ EPIC 2). Nếu artifact không tồn tại, trả về `null`.

### (c) Response Example
```json
{
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "model_family": "XGBoost",
  "package_version": "2.7.0",
  "data_version": "1.0.0",
  "feature_set": "FS23-SELECTED",
  "training_date": "2026-07-20",
  "metrics": {
    "MAE": 14.23,
    "RMSE": 18.75,
    "R2": 0.41
  },
  "timestamp": "2026-07-30T10:15:00+07:00"
}
```

### (d) Error Codes
- **500:** Lỗi khi load metadata (artifact không đọc được)

---

## GET /features

Trả về danh sách 18 canonical input fields kèm mô tả, kiểu dữ liệu và khoảng giá trị hợp lệ.

### (a) Request
```
GET /features
Header: Content-Type: application/json
Body: (không có)
```

### (b) Response Schema
| Field | Kiểu | Mô tả |
|-------|------|--------|
| `canonical_fields` | array[object] | 18 trường input theo đúng thứ tự contract |
| `canonical_fields[].name` | string | Tên trường |
| `canonical_fields[].position` | integer | Thứ tự (1–18) |
| `canonical_fields[].data_type` | string | `"number"` \| `"integer"` \| `"boolean"` \| `"string"` |
| `canonical_fields[].required` | boolean | Luôn `true` (bắt buộc trong request) |
| `canonical_fields[].minimum` | number \| null | Giá trị nhỏ nhất |
| `canonical_fields[].maximum` | number \| null | Giá trị lớn nhất |
| `canonical_fields[].allowed_categories` | array \| null | Danh sách giá trị hợp lệ (cho enum) |
| `canonical_fields[].default_policy` | string | `"PIPELINE_IMPUTE"` — pipeline tự động impute nếu null |
| `selected_features` | array[string] | 31 features thực sự dùng bởi model (sau FE) |
| `total_input_fields` | integer | `18` |
| `total_selected_features` | integer | `31` |

### (c) Response Example
```json
{
  "canonical_fields": [
    {"name": "duration_min", "position": 1, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 120.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "explicit", "position": 2, "data_type": "boolean", "required": true, "minimum": null, "maximum": null, "allowed_categories": ["False", "True"], "default_policy": "PIPELINE_IMPUTE"},
    {"name": "release_year", "position": 3, "data_type": "integer", "required": true, "minimum": 1900, "maximum": 2100, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "release_month", "position": 4, "data_type": "integer", "required": true, "minimum": 1, "maximum": 12, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "decade", "position": 5, "data_type": "integer", "required": true, "minimum": 1900, "maximum": 2100, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "release_precision", "position": 6, "data_type": "string", "required": true, "minimum": null, "maximum": null, "allowed_categories": ["day", "month", "year"], "default_policy": "PIPELINE_IMPUTE"},
    {"name": "danceability", "position": 7, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 1.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "energy", "position": 8, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 1.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "key", "position": 9, "data_type": "integer", "required": true, "minimum": 0, "maximum": 11, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "loudness", "position": 10, "data_type": "number", "required": true, "minimum": -60.0, "maximum": 0.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "mode", "position": 11, "data_type": "integer", "required": true, "minimum": null, "maximum": null, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "speechiness", "position": 12, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 1.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "acousticness", "position": 13, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 1.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "instrumentalness", "position": 14, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 1.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "liveness", "position": 15, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 1.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "valence", "position": 16, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 1.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "tempo", "position": 17, "data_type": "number", "required": true, "minimum": 0.0, "maximum": 300.0, "allowed_categories": null, "default_policy": "PIPELINE_IMPUTE"},
    {"name": "time_signature", "position": 18, "data_type": "number", "required": true, "minimum": null, "maximum": null, "allowed_categories": ["1.0", "3.0", "4.0", "5.0"], "default_policy": "PIPELINE_IMPUTE"}
  ],
  "selected_features": ["duration_min", "release_year", "danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "release_month", "decade", "release_precision", "key", "time_signature", "explicit", "mode", "release_month_sin", "release_month_cos", "year_in_decade", "duration_log", "duration_squared", "energy_danceability", "energy_valence", "danceability_valence", "acousticness_instrumentalness", "energy_liveness", "speechiness_explicit", "tempo_danceability", "loudness_energy"],
  "total_input_fields": 18,
  "total_selected_features": 31
}
```

### (d) Error Codes
- **500:** Lỗi khi load schema (file không đọc được)

---

## POST /predict

Nhận 18 features, trả về dự đoán popularity.

### (a) Request
```
POST /predict
Header: Content-Type: application/json
Body: JSON object — 18 fields theo đúng thứ tự và tên dưới đây
```

**18 canonical input fields (BẮT BUỘC theo đúng tên và thứ tự):**

| # | Tên field | Kiểu | Min | Max | Ghi chú |
|---|-----------|------|-----|-----|---------|
| 1 | `duration_min` | number | 0.0 | 120.0 | Thời lượng tính bằng phút |
| 2 | `explicit` | boolean | — | — | Có nội dung explicit không |
| 3 | `release_year` | integer | 1900 | 2100 | Năm phát hành |
| 4 | `release_month` | number | 1 | 12 | Tháng phát hành (float hợp lệ) |
| 5 | `decade` | integer | 1900 | 2100 | Thập kỷ (1980, 1990, ...) |
| 6 | `release_precision` | string | — | — | `"day"` \| `"month"` \| `"year"` |
| 7 | `danceability` | number | 0.0 | 1.0 | |
| 8 | `energy` | number | 0.0 | 1.0 | |
| 9 | `key` | integer | 0 | 11 | Cung âm (0=C) |
| 10 | `loudness` | number | -60.0 | 0.0 | dB |
| 11 | `mode` | integer | 0 | 1 | Major=1, Minor=0 |
| 12 | `speechiness` | number | 0.0 | 1.0 | |
| 13 | `acousticness` | number | 0.0 | 1.0 | |
| 14 | `instrumentalness` | number | 0.0 | 1.0 | |
| 15 | `liveness` | number | 0.0 | 1.0 | |
| 16 | `valence` | number | 0.0 | 1.0 | |
| 17 | `tempo` | number | 0.0 | 300.0 | BPM |
| 18 | `time_signature` | number | — | — | `1.0`\|`3.0`\|`4.0`\|`5.0` |

### (b) Response Schema
| Field | Kiểu | Mô tả |
|-------|------|--------|
| `status` | string | `"SUCCESS"` \| `"ERROR"` |
| `prediction_raw` | number | Giá trị thô từ model (có thể ngoài 0–100) |
| `prediction_clipped` | number | Clipped vào [0, 100] |
| `prediction_display` | integer | Làm tròn prediction_clipped |
| `warnings` | array[string] | Danh sách warning (extra fields bị bỏ, giá trị imputed) |
| `model_id` | string | `"EXP24-XGB-FINAL-001"` |
| `model_version` | string | `"1.0.0"` |
| `package_version` | string | `"2.7.0"` |
| `timestamp` | string (ISO 8601) | |

> **Lưu ý:** Pipeline tự động impute giá trị null theo default_policy. `warnings` sẽ thông báo nếu có giá trị imputed.

### (c) Request/Response Examples

**Request:**
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

**Response:**
```json
{
  "status": "SUCCESS",
  "prediction_raw": 46.421062,
  "prediction_clipped": 46.421062,
  "prediction_display": 46,
  "warnings": [],
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "package_version": "2.7.0",
  "timestamp": "2026-07-30T10:15:00+07:00"
}
```

### (d) Error Codes
- **400:** Body không parse được thành JSON
- **422:** Thiếu field bắt buộc, sai kiểu dữ liệu, giá trị ngoài [min, max], `release_precision` không nằm trong `["day","month","year"]`
- **500:** Lỗi nội bộ (model chưa load, exception khi predict)

---

## POST /explain

Nhận 18 features, trả về SHAP values chi tiết cho prediction vừa chạy.

### (a) Request
```
POST /explain
Header: Content-Type: application/json
Body: giống hệt POST /predict (18 fields)
```

### (b) Response Schema
| Field | Kiểu | Mô tả |
|-------|------|--------|
| `status` | string | `"SUCCESS"` \| `"ERROR"` |
| `prediction_raw` | number | Giá trị thô |
| `prediction_clipped` | number | Clipped vào [0, 100] |
| `prediction_display` | integer | Làm tròn |
| `base_value` | number | SHAP base value (giá trị trung bình khi không có feature nào) |
| `shap_values` | object | Dict: feature_name (selected feature sau FE) → SHAP value (float) |
| `top_features` | array[object] | Top 5 features có ảnh hưởng nhất, sắp xếp theo abs(SHAP) giảm dần |
| `top_features[].name` | string | Tên feature |
| `top_features[].shap_value` | number | Giá trị SHAP đóng góp |
| `top_features[].feature_value` | number \| string | Giá trị thực của feature trong request này |
| `model_id` | string | |
| `model_version` | string | |
| `timestamp` | string (ISO 8601) | |

### (c) Request/Response Example

**Request:** (giống POST /predict)

**Response:**
```json
{
  "status": "SUCCESS",
  "prediction_raw": 46.421062,
  "prediction_clipped": 46.421062,
  "prediction_display": 46,
  "base_value": 42.15,
  "shap_values": {
    "release_year": 2.34,
    "energy": 1.87,
    "danceability": -0.92,
    "loudness": 1.21,
    "valence": -0.45,
    "acousticness": -2.10,
    "tempo": 0.33,
    "speechiness": 0.88,
    "instrumentalness": -1.55,
    "liveness": -0.22,
    "release_month_sin": 0.11,
    "release_month_cos": -0.08,
    "year_in_decade": 0.56,
    "duration_log": 1.02,
    "duration_squared": 0.47,
    "energy_danceability": 0.78,
    "energy_valence": -0.31,
    "danceability_valence": 0.19,
    "acousticness_instrumentalness": -0.88,
    "energy_liveness": 0.42,
    "speechiness_explicit": 0.55,
    "tempo_danceability": -0.14,
    "loudness_energy": 0.91
  },
  "top_features": [
    {"name": "acousticness", "shap_value": -2.10, "feature_value": 0.22},
    {"name": "instrumentalness", "shap_value": -1.55, "feature_value": 0.718},
    {"name": "release_year", "shap_value": 2.34, "feature_value": 1992},
    {"name": "energy", "shap_value": 1.87, "feature_value": 0.793},
    {"name": "loudness", "shap_value": 1.21, "feature_value": -7.915}
  ],
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "timestamp": "2026-07-30T10:15:00+07:00"
}
```

### (d) Error Codes
- **400:** Body không parse được JSON
- **422:** Thiếu field, sai kiểu, giá trị ngoài range
- **500:** Lỗi nội bộ (SHAP explainer chưa load, lỗi khi tính SHAP)

---

## POST /what-if

So sánh hai predictions: base input vs. base input với một số features thay đổi.

### (a) Request
```
POST /what-if
Header: Content-Type: application/json
```

| Field | Kiểu | Bắt buộc | Mô tả |
|-------|------|---------|--------|
| `base_features` | object | ✅ | 18 canonical fields — trạng thái gốc |
| `changed_features` | object | ✅ | Object chỉ chứa fields muốn thay đổi (tên field giống bảng 18 fields) |

### (b) Response Schema
| Field | Kiểu | Mô tả |
|-------|------|--------|
| `status` | string | `"SUCCESS"` \| `"ERROR"` |
| `prediction_before` | object | Prediction với base_features |
| `prediction_before.prediction_raw` | number | |
| `prediction_before.prediction_clipped` | number | |
| `prediction_before.prediction_display` | integer | |
| `prediction_after` | object | Prediction với base_features + changed_features merged |
| `prediction_after.prediction_raw` | number | |
| `prediction_after.prediction_clipped` | number | |
| `prediction_after.prediction_display` | number | |
| `delta` | number | `prediction_after.prediction_clipped − prediction_before.prediction_clipped` |
| `delta_display` | integer | Làm tròn delta |
| `changes_applied` | object | Các thay đổi thực sự được áp dụng (key = field name, value = giá trị mới) |
| `model_id` | string | |
| `model_version` | string | |
| `timestamp` | string (ISO 8601) | |

> **Lưu ý:** `changed_features` có thể chứa 1 hoặc nhiều fields. Chỉ fields trong 18 canonical fields mới được chấp nhận. Fields không có trong 18 canonical fields → lỗi 422.

### (c) Request/Response Example

**Request:**
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
    "danceability": 0.3,
    "energy": 0.2,
    "valence": 0.9
  }
}
```

**Response:**
```json
{
  "status": "SUCCESS",
  "prediction_before": {
    "prediction_raw": 46.421062,
    "prediction_clipped": 46.421062,
    "prediction_display": 46
  },
  "prediction_after": {
    "prediction_raw": 38.152300,
    "prediction_clipped": 38.152300,
    "prediction_display": 38
  },
  "delta": -8.268762,
  "delta_display": -8,
  "changes_applied": {
    "danceability": 0.3,
    "energy": 0.2,
    "valence": 0.9
  },
  "model_id": "EXP24-XGB-FINAL-001",
  "model_version": "1.0.0",
  "timestamp": "2026-07-30T10:15:00+07:00"
}
```

### (d) Error Codes
- **400:** Body không parse được JSON
- **422:** `base_features` thiếu field bắt buộc; `changed_features` chứa field không nằm trong 18 canonical fields; giá trị trong `changed_features` ngoài range
- **500:** Lỗi nội bộ

---

## Quy ước lỗi chung

### Error Response Format
```json
{
  "error": true,
  "code": 422,
  "message": "Validation error",
  "detail": {
    "field": "danceability",
    "reason": "Value 1.5 exceeds maximum 1.0",
    "value": 1.5
  }
}
```

### Status Code Reference

| Code | Tên | Trigger | Ví dụ message |
|------|-----|--------|--------------|
| 200 | OK | Thành công | — |
| 400 | Bad Request | Body không parse được JSON | `"Invalid JSON: ..."` |
| 422 | Unprocessable Entity | Thiếu required field; sai kiểu; giá trị ngoài [min, max]; enum không hợp lệ; changed_features chứa field lạ (POST /what-if) | `"Missing required field: release_year"`, `"Value 150 exceeds maximum 120.0"` |
| 500 | Internal Server Error | Model chưa load; exception không lường trước; file artifact không đọc được | `"Model load failed: ..."`, `"Unexpected error: ..."` |

### Validation Rules (áp dụng cho POST /predict, /explain, /what-if)

1. **Thiếu field bắt buộc** → 422
2. **Sai kiểu dữ liệu** (string thay vì number) → 422
3. **Giá trị ngoài [minimum, maximum]** → 422 (áp dụng cho: duration_min, release_year, release_month, decade, danceability, energy, key, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo, time_signature)
4. **release_precision không trong ["day","month","year"]** → 422
5. **changed_features chứa field không nằm trong 18 canonical fields** → 422
6. **Extra fields (field không có trong 18 canonical)** → **IGNORED** với warning trong response (không lỗi)
7. **null values** → **AUTO-IMPUTED** bởi pipeline (không lỗi, có warning)
8. **Infinite values** → 422

### Lưu ý đặc biệt cho /what-if
- `base_features` phải đầy đủ 18 fields như POST /predict
- `changed_features` chỉ cần chứa fields muốn thay đổi (1–17 fields)
- Merge: `changed_features` ghi đè `base_features` ( không thay thế toàn bộ)

---

## Appendix: Field Order & Type Summary

Tất cả endpoints nhận 18 canonical fields theo đúng thứ tự sau:

```
1.  duration_min      number   [0.0, 120.0]
2.  explicit          boolean
3.  release_year      integer  [1900, 2100]
4.  release_month     number   [1, 12]
5.  decade           integer  [1900, 2100]
6.  release_precision string   ["day", "month", "year"]
7.  danceability     number   [0.0, 1.0]
8.  energy           number   [0.0, 1.0]
9.  key              integer  [0, 11]
10. loudness         number   [-60.0, 0.0]
11. mode             integer  [0, 1]
12. speechiness      number   [0.0, 1.0]
13. acousticness     number   [0.0, 1.0]
14. instrumentalness number   [0.0, 1.0]
15. liveness         number   [0.0, 1.0]
16. valence          number   [0.0, 1.0]
17. tempo            number   [0.0, 300.0]
18. time_signature   number   [1.0, 3.0, 4.0, 5.0]
```

> **⚠️ Thứ tự trên là final.** Backend và Frontend phải tuân theo. Không thay đổi tên field hay thứ tự.

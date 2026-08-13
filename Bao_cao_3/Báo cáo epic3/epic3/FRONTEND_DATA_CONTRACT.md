# FRONTEND DATA CONTRACT — EPIC 3: Streamlit Frontend Data Mapping
**Ngày chốt:** 2026-07-30
**Phiên:** 3
**Người phụ trách:** Minh
**Nguồn tham chiếu:** `docs/epic3/API_CONTRACT.md`, `docs/epic3/UI_UX_CONTRACT.md`

> Mỗi trang gọi endpoint nào, lấy field nào, hiển thị ra sao. Đối chiếu chéo với API_CONTRACT.md.

---

## Tổng quan: Pages ↔ Endpoints Mapping

| Trang | Endpoint(s) gọi |
|-------|----------------|
| Home / Overview | `GET /health` (kiểm tra kết nối khi khởi động) |
| Predict Popularity | `POST /predict` |
| SHAP Explanation | `POST /explain` |
| What-If Simulator | `POST /what-if` |
| Music Trends 1921–2020 | *(không gọi model API — dữ liệu static từ Feature 3.4)* |
| Model Info | `GET /model-info` |
| Limitations & Responsible Use | *(không gọi API — nội dung tĩnh)* |

---

## Trang: Home / Project Overview

| # | Field/API response | UI Display | Format | Ghi chú |
|---|------------------|-----------|--------|---------|
| 1 | `GET /health.status` | Banner cảnh báo ở đầu trang | `"⚠️ Model chưa sẵn sàng"` nếu `"degraded"` | Chỉ khi degraded |
| 2 | `GET /health.model_loaded` | Badge trong sidebar | ✅ / ❌ | |
| 3 | KPI: `586,672` | Big number | Số nguyên, có dấu phẩy | Static |
| 4 | KPI: `1921–2020` | Text | `"1921–2020"` | Static |
| 5 | KPI: `1,162,095` | Big number | Số nguyên, có dấu phẩy | Static |
| 6 | `GET /model-info.model_family` | Badge | `"XGBoost"` | Gọi 1 lần khi khởi động |

---

## Trang: Predict Popularity

### Form inputs → API request body
*(18 fields gửi trong POST /predict body, theo đúng thứ tự API contract)*

| # | UI Component | Field name (API) | Type | Validation/Range | Hiển thị mặc định | Ghi chú |
|---|------------|----------------|------|----------------|-------------------|---------|
| 1 | `st.number_input` | `duration_min` | number | [0.0, 120.0] | 3.5 | Phút |
| 2 | `st.checkbox` | `explicit` | boolean | — | False | |
| 3 | `st.number_input` | `release_year` | integer | [1921, 2020] | 2000 | Năm phát hành |
| 4 | `st.number_input` | `release_month` | number | [1, 12] | 6 | Tháng |
| 5 | `st.selectbox` | `decade` | integer | [1920..2020] | 2000 | Thập kỷ |
| 6 | `st.selectbox` | `release_precision` | string | ["day","month","year"] | "day" | |
| 7 | `st.slider` | `danceability` | number | [0.0, 1.0] | 0.5 | |
| 8 | `st.slider` | `energy` | number | [0.0, 1.0] | 0.5 | |
| 9 | `st.selectbox` (0–11) | `key` | integer | [0, 11] | 0 | 12 options |
| 10 | `st.slider` | `loudness` | number | [-60.0, 0.0] | -10.0 | dB |
| 11 | `st.radio` | `mode` | integer | [0, 1] | 1 | |
| 12 | `st.slider` | `speechiness` | number | [0.0, 1.0] | 0.1 | |
| 13 | `st.slider` | `acousticness` | number | [0.0, 1.0] | 0.3 | |
| 14 | `st.slider` | `instrumentalness` | number | [0.0, 1.0] | 0.1 | |
| 15 | `st.slider` | `liveness` | number | [0.0, 1.0] | 0.15 | |
| 16 | `st.slider` | `valence` | number | [0.0, 1.0] | 0.5 | |
| 17 | `st.slider` | `tempo` | number | [0.0, 300.0] | 120.0 | BPM |
| 18 | `st.selectbox` | `time_signature` | number | [1.0,3.0,4.0,5.0] | 4.0 | |

### API response → UI display

| # | Field từ response | UI Component | Display format | Ghi chú |
|---|------------------|------------|---------------|---------|
| 1 | `prediction_display` | Big number + color | Số nguyên + màu theo ngưỡng | Core output |
| 2 | `prediction_clipped` | Chi tiết nhỏ | `"46.42"` (2 decimal) | Secondary |
| 3 | `prediction_raw` | Chi tiết nhỏ | `"46.421062"` (6 decimal) | Debug/technical |
| 4 | `warnings` | `st.warning()` | Danh sách string | Mỗi warning 1 dòng |
| 5 | `model_id` | Footer nhỏ | `"Model: EXP24-XGB-FINAL-001"` | |
| 6 | `model_version` | Footer nhỏ | `"v1.0.0"` | |

> **⚠️ Lưu ý:** `confidence`/`uncertainty` KHÔNG có trong API contract → **không hiển thị**. Nếu EPIC 2 có bổ sung artifact này, cần cập nhật API contract trước.

---

## Trang: SHAP Explanation

### API request body
*(Giống hệt Predict — 18 fields)*

### API response → UI display

| # | Field từ response | UI Component | Display format | Ghi chú |
|---|------------------|------------|---------------|---------|
| 1 | `prediction_display` | Small card | Số nguyên | |
| 2 | `base_value` | Text/breakdown | `"42.15"` (2 decimal) | |
| 3 | `top_features` | Horizontal bar chart | Top 5, màu +/- SHAP | Core output |
| 4 | `top_features[].name` | Bar label | Tên feature | |
| 5 | `top_features[].shap_value` | Bar length + label | `"+2.34"` hoặc `"-0.92"` (2 decimal) | |
| 6 | `top_features[].feature_value` | Tooltip/label | Giá trị thực | |
| 7 | `shap_values` | Dataframe table | Toàn bộ 31 features | |
| 8 | `shap_summary_beeswarm.png` | Image | Render ảnh | Fallback: ẩn nếu không có |

---

## Trang: What-If Simulator

### API request body

| # | Field | Source | Ghi chú |
|---|-------|--------|---------|
| 1 | `base_features` | Form nhập đầy đủ 18 fields | Baseline |
| 2 | `changed_features` | Từ preset selector hoặc enabled sliders | Chỉ fields user chọn thay đổi |

### API response → UI display

| # | Field từ response | UI Component | Display format | Ghi chú |
|---|------------------|------------|---------------|---------|
| 1 | `prediction_before.prediction_display` | Card "Before" | Số nguyên | |
| 2 | `prediction_after.prediction_display` | Card "After" | Số nguyên | |
| 3 | `delta_display` | Card "Thay đổi" | `"+8"` hoặc `"-5"` | Màu xanh/đỏ |
| 4 | `delta` | Bar chart comparison | `"+8.27"` (2 decimal) | |
| 5 | `changes_applied` | Table | Feature \| Baseline \| Mới | |

---

## Trang: Music Trends 1921–2020

*(Không gọi model API — dữ liệu từ Feature 3.4)*

| # | Data source | UI Component | Display format | Ghi chú |
|---|------------|-------------|---------------|---------|
| 1 | Analytics view (DB) | Line chart | Popularity avg by decade | |
| 2 | Analytics view (DB) | Line chart (multi-series) | 5 audio features by decade | |
| 3 | Analytics view (DB) | Bar chart | Explicit ratio by decade | |
| 4 | Analytics view (DB) | Line chart | Avg duration by decade | |
| 5 | Analytics view (DB) | Bar chart (tùy chọn) | Top artists/genres | |

> **⚠️ Lưu ý:** Trang này phụ thuộc vào Feature 3.4 hoàn thành trước. Dữ liệu trends lấy từ `analytics.vw_*` views, không từ model API.

---

## Trang: Model Info

### API request: `GET /model-info` (no body)

### API response → UI display

| # | Field từ response | UI Component | Display format | Ghi chú |
|---|------------------|------------|---------------|---------|
| 1 | `model_id` | Table row | `"EXP24-XGB-FINAL-001"` | |
| 2 | `model_version` | Table row + badge | `"1.0.0"` | |
| 3 | `model_family` | Table row | `"XGBoost"` | |
| 4 | `package_version` | Table row | `"2.7.0"` | |
| 5 | `data_version` | Table row | `"1.0.0"` | |
| 6 | `feature_set` | Table row | `"FS23-SELECTED"` | |
| 7 | `training_date` | Table row | `"2026-07-20"` hoặc `"—"` | Null → hiển thị `"—"` |
| 8 | `metrics.MAE` | KPI card | `"14.23 điểm"` | Null → `"đang cập nhật"` |
| 9 | `metrics.RMSE` | KPI card | `"18.75 điểm"` | Null → `"đang cập nhật"` |
| 10 | `metrics.R2` | KPI card | `"0.41"` (không đơn vị) | Null → `"đang cập nhật"` |
| 11 | `shap_summary_bar_selected.png` | Image | Feature importance chart | |

---

## Trang: Limitations & Responsible Use

*(Không gọi API — nội dung tĩnh, đọc từ model_card.md nếu có)*

| # | Content | UI Component | Ghi chú |
|---|---------|------------|---------|
| 1 | Giới hạn dataset | `st.markdown()` blocks | |
| 2 | Giới hạn model | `st.markdown()` blocks | |
| 3 | Responsible use checklist | `st.markdown()` ✅ / ❌ list | |
| 4 | model_card.md link | `st.markdown("[📄 Model Card](...)")` | Null-safe |

---

## Đối chiếu chéo: Nhu cầu Frontend vs. API Contract hiện tại

### ✅ Đã khớp — không cần thay đổi

| Nhu cầu frontend | Có trong API contract | Field |
|-----------------|----------------------|-------|
| Hiển thị prediction_display | ✅ | `/predict.prediction_display` |
| Hiển thị prediction_clipped | ✅ | `/predict.prediction_clipped` |
| Hiển thị warnings | ✅ | `/predict.warnings` |
| Hiển thị model_id/version | ✅ | `/predict.model_id`, `.model_version` |
| SHAP top_features (name + shap_value + feature_value) | ✅ | `/explain.top_features` |
| SHAP base_value | ✅ | `/explain.base_value` |
| SHAP full values dict | ✅ | `/explain.shap_values` |
| What-if delta | ✅ | `/what-if.delta` |
| What-if delta_display | ✅ | `/what-if.delta_display` |
| What-if prediction_before/after | ✅ | `/what-if.prediction_before/after` |
| What-if changes_applied | ✅ | `/what-if.changes_applied` |
| Model info metadata | ✅ | `/model-info` (tất cả fields) |
| Model metrics MAE/RMSE/R2 | ✅ | `/model-info.metrics` |

### ⚠️ Có trong API contract nhưng CẦN LƯU Ý khi code

| Field | Cảnh báo |
|-------|---------|
| `shap_summary_beeswarm.png` | KHÔNG có trong API contract — trả về từ SHAP assets (file). Cần load từ disk, không phải từ API response |
| `shap_global_importance_selected.png` | Tương tự — load từ `artifacts/epic2/explainability/` |
| Music Trends data | KHÔNG gọi API — lấy từ database analytics views (Feature 3.4) |

### ❌ Thiếu trong API contract — CẦN BỔ SUNG

| # | Nhu cầu frontend | Ảnh hưởng | Đề xuất |
|---|-----------------|-----------|---------|
| 1 | `confidence` / `uncertainty` score cho prediction | Predict page muốn hiển thị "độ tin cậy" nhưng field không có trong API contract | **Tùy chọn.** Nếu EPIC 2 có artifact uncertainty — bổ sung vào API contract. Nếu không: bỏ yêu cầu này, không bịa field |

> **Quyết định:** Bỏ yêu cầu `confidence`/`uncertainty` cho Phiên 3. Nếu EPIC 2 có artifact này, bổ sung sau.

---

## Cấu hình API Client (Frontend)

```python
# config.py hoặc trong mỗi page
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def call_api(method, endpoint, payload=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.request(method, url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            # Parse validation error
            detail = response.json()
            raise ValidationError(detail)
        elif response.status_code == 500:
            raise ServerError("Model error")
        else:
            raise APIError(f"HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Cannot connect to API")
```

---

## Session State Keys

| Key | Type | Lưu trữ | Dùng bởi |
|-----|------|---------|---------|
| `last_prediction_input` | dict (18 fields) | Sau khi gọi `/predict` | SHAP Explanation, What-If |
| `baseline_features` | dict (18 fields) | Khi user click "Dùng làm baseline" | What-If Simulator |
| `last_explain_response` | dict (SHAP response) | Sau khi gọi `/explain` | SHAP Explanation (re-render) |
| `api_base_url` | string | Từ sidebar config | Mọi page gọi API |
| `health_status` | dict | Từ `GET /health` | Sidebar badge, Home banner |

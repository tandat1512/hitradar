# BÁO CÁO NGHIỆM THU — PHIÊN 2: Task 3.0.4 — Chốt API Contract
**Người thực hiện:** Minh
**Ngày:** 2026-07-30
**Dự án:** HitRadar Pro — EPIC 3: Productization, Integration & Defense

---

## 1. Tóm tắt việc đã làm

Đã tạo file `docs/epic3/API_CONTRACT.md` — hợp đồng đầy đủ cho 6 endpoints của FastAPI backend. Tất cả request/response schemas được đối chiếu trực tiếp với 7 artifact thực tế của EPIC 2: `input_schema.json` (18 fields với min/max/type), `output_schema.json`, `feature_names.json` (49 features + 31 selected), `selected_features.json`, `example_input.json`, `example_output.json`, `model_version.json`, `package_version.json`, `data_version.json`, và `runtime/inference_pipeline.py`.

---

## 2. Danh sách 6 endpoint đã chốt

| # | Endpoint | Method | Tóm tắt |
|---|---------|--------|---------|
| 1 | `/health` | GET | Trả về `status`, `model_loaded`, `timestamp` — dùng để Frontend kiểm tra API sống |
| 2 | `/model-info` | GET | Trả về `model_id`, `model_version`, `package_version`, `data_version`, `metrics` (MAE/RMSE/R2), `feature_set` — dùng cho trang Model Info |
| 3 | `/features` | GET | Trả về 18 canonical fields (tên, kiểu, min, max, enum) + 31 selected features — dùng để Frontend validate form và generate sliders |
| 4 | `/predict` | POST | Nhận 18 fields → trả về `prediction_raw`, `prediction_clipped`, `prediction_display`, `warnings`, metadata — endpoint core |
| 5 | `/explain` | POST | Nhận 18 fields → trả về prediction + `base_value`, `shap_values` (31 key → float), `top_features` (top 5) — dùng cho trang SHAP Explanation |
| 6 | `/what-if` | POST | Nhận `base_features` + `changed_features` → trả về so sánh prediction_before/after, `delta`, `changes_applied` — dùng cho What-If Simulator |

---

## 3. Những chỗ còn phụ thuộc artifact chưa xác nhận từ EPIC 2

### ⚠️ Ảnh hưởng đến API contract

| # | Artifact | Vấn đề | Ảnh hưởng |
|---|---------|---------|-----------|
| A | `model_metrics.json` | **Chưa xác nhận** — file tìm thấy tại `4.MODELS/4.2.evaluation/` nhưng rỗng (0 bytes). Chưa rõ tên field chính xác cho metrics (MAE, RMSE, R2) | `/model-info` response metrics fields còn placeholder. Cần EPIC 2 xác nhận tên keys trong JSON (ví dụ `"MAE"` hay `"mae"`?) |
| B | `residual_stats.json` | **Không tìm thấy** — file này không tồn tại trong repo | `/model-info` và trang Model Info **không có residual distribution**. Cần quyết định: bỏ qua field này hay yêu cầu EPIC 2 tạo bổ sung |
| C | `shap_explanation_sample` SHAP values cụ thể cho từng prediction | `runtime/inference_pipeline.py` chỉ có method `predict_popularity`, **không có** method `explain` tích hợp sẵn | `/explain` cần implement mới: load `shap_background_raw.parquet`, `shap_values_grouped_selected.npy`, tính SHAP local bằng `shap.Explainer`. SHAP assets có sẵn nhưng **chưa test end-to-end** với inference_pipeline |

### ℹ️ Không ảnh hưởng đến API contract (đã xác nhận OK)

| # | Artifact | Trạng thái |
|---|---------|-----------|
| ✅ | 18 canonical field names + types + min/max | Xác nhận từ `input_schema.json` — final |
| ✅ | `prediction_raw`, `prediction_clipped`, `prediction_display` | Xác nhận từ `output_schema.json` + `inference_pipeline.py` — final |
| ✅ | `model_id = "EXP24-XGB-FINAL-001"`, `model_version = "1.0.0"`, `package_version = "2.7.0"` | Xác nhận từ `model_version.json` + `package_version.json` |
| ✅ | 31 selected features | Xác nhận từ `selected_features.json` |
| ✅ | 49 feature names (transformed) | Xác nhận từ `feature_names.json` |
| ✅ | Example input/output | Xác nhận từ `examples/example_input.json` + `example_output.json` |

---

## 4. Đề xuất cho Phiên 3

**Task 3.0.5 — Chốt UI/UX Contract + Frontend Data Contract**

Dựa trên API contract vừa chốt, Phiên 3 cần quyết định 5 vấn đề còn lại giữa backend và frontend:

### 4.1. Form field mapping cho trang Predict
- 18 fields cần được mapping sang UI components cụ thể: `st.number_input`, `st.selectbox`, `st.slider`, v.v.
- Gợi ý:
  - Audio features (0.0–1.0): `st.slider` với step=0.01
  - `explicit`: `st.checkbox`
  - `release_precision`: `st.selectbox` với 3 options
  - `time_signature`: `st.selectbox` với 4 options
  - `key`: `st.selectbox` với 12 options (C, C#, D...)
  - Các fields số khác: `st.number_input`

### 4.2. SHAP response format
- `/explain` trả về `shap_values` là dict 31 keys → float (feature_name → SHAP value). Frontend cần quyết định:
  - Hiển thị top 5 (API đã filter `top_features`)
  - Biểu đồ: dùng bar chart từ `shap_summary_bar_selected.png` (global) hay vẽ từ dữ liệu JSON?

### 4.3. What-If UI — cách chọn features thay đổi
- Frontend cần quyết định: dùng pre-set scenarios ("Tăng energy lên 0.9", "Giảm acousticness") hay cho user tự chọn bất kỳ field nào?
- Đề xuất: hybrid — 3-5 preset scenarios + "Custom" tab để user chọn field cụ thể

### 4.4. API base URL configuration
- Frontend Streamlit cần biết backend chạy ở port nào. Quyết định:
  - Default: `http://localhost:8000`
  - Configurable qua `API_BASE_URL` env var hoặc `st.text_input` trong sidebar

### 4.5. Error handling trên UI
- Mỗi endpoint có thể trả 400/422/500. Frontend cần handle:
  - `st.error()` cho user-facing messages
  - Log chi tiết error ra console
  - Fallback: hiển thị cached result hoặc pre-filled example

---

## 5. Ghi chú kỹ thuật cho Feature 3.2 (FastAPI)

- **Model load:** Dùng `inference_pipeline.py` của EPIC 2 — có sẵn method `predict_popularity(input_data: dict)`. Backend chỉ cần wrap, không viết lại logic.
- **Validation:** `input_schema.json` đã định nghĩa đầy đủ. Dùng trực tiếp để generate Pydantic models.
- **SHAP explain:** Cần implement riêng trong `ExplainService` — không có trong `inference_pipeline.py`. Logic:
  1. Load `shap_background_transformed.npy` làm `background`
  2. Load `best_model.joblib` + `full_inference_pipeline.joblib`
  3. Tạo `shap.Explainer(model, background)`
  4. Gọi `explainer.shap_values(transformed_row)`
  5. Map về 31 selected feature names qua `shap_feature_mapping.json`
- **Extra fields:** Backend ignore extra fields (không lỗi), có warning — nhất quán với `inference_pipeline.py:111-113`
- **Config:** `ARTIFACTS_PATH` env var trỏ đến thư mục chứa artifacts (khi chuẩn hoá vào `artifacts/epic2/`)

---

## 6. Hành động cần xác nhận trước Phiên 3

1. **[CẦN XÁC NHẬN GẤP]** `model_metrics.json` — xác nhận tên keys (MAE/RMSE/R2 hay viết khác?), nếu file rỗng thì cần yêu cầu EPIC 2 cung cấp
2. **[CẦN QUYẾT ĐỊNH]** `residual_stats.json` — có hay không? Nếu không có, trang Model Info bỏ qua residual distribution
3. **[CẦN TEST]** SHAP explain integration — artifacts SHAP có sẵn nhưng chưa test end-to-end với `full_inference_pipeline`. Feature 3.2 cần dành effort cho việc này
4. **[CẦN CHUẨN HOÁ]** Copy artifacts vào `artifacts/epic2/` trước khi Feature 3.2 bắt đầu code

# BÁO CÁO NGHIỆM THU — PHIÊN 3: Task 3.0.5 & 3.0.6
**Người thực hiện:** Minh
**Ngày:** 2026-07-30
**Dự án:** HitRadar Pro — EPIC 3: Productization, Integration & Defense

---

## 1. Tóm tắt 7 trang đã thiết kế

| # | Trang | Tóm tắt 1-2 câu |
|---|-------|----------------|
| 1 | **Home / Overview** | Trang giới thiệu tĩnh: hero section, 3 KPIs (586K tracks, 1921–2020, 1.16M artists), workflow 3 bước, navigation cards. Gọi `/health` khi khởi động để hiển thị model status badge. |
| 2 | **Predict Popularity** | Form 18 fields (slider/input/selectbox/radio) → gọi `POST /predict` → hiển thị `prediction_display` lớn với gauge màu theo ngưỡng (0–30 đỏ, 31–60 vàng, 61–100 xanh). Lưu input vào `session_state` để chia sẻ sang SHAP/What-If. |
| 3 | **SHAP Explanation** | Nhận dữ liệu từ Predict hoặc nhập thủ công → gọi `POST /explain` → hiển thị horizontal bar chart top 5 features, table 31 SHAP values, base_value breakdown. |
| 4 | **What-If Simulator** | Nhận baseline từ Predict hoặc nhập mới → chọn preset hoặc bật custom sliders → gọi `POST /what-if` → hiển thị 3 cards (before/after/delta) + bar chart so sánh. |
| 5 | **Music Trends 1921–2020** | Hiển thị 4-5 biểu đồ (line/bar) từ dữ liệu static của Feature 3.4 — không gọi model API. Bộ lọc theo decade/năm. |
| 6 | **Model Info** | Gọi `GET /model-info` → hiển thị metadata card (model_id, version, family), metrics KPI (MAE/RMSE/R2), feature importance bar chart từ SHAP assets. |
| 7 | **Limitations & Responsible Use** | Trang tĩnh: giới hạn dataset, giới hạn model, checklist responsible use ✅/❌, credits. Không gọi API. |

---

## 2. Phát hiện lệch giữa Frontend và API Contract

### ✅ Khớp hoàn toàn — không cần thay đổi

Tất cả fields mà frontend cần đều có sẵn trong API contract:
- `prediction_display` / `prediction_clipped` / `prediction_raw`
- `warnings`
- `model_id` / `model_version`
- `top_features` (name + shap_value + feature_value)
- `base_value`
- `shap_values` (31-key dict)
- `delta` / `delta_display`
- `prediction_before/after` (full objects)
- `changes_applied`
- Tất cả fields của `GET /model-info`

### ⚠️ Cần lưu ý khi code (không phải lỗi contract)

| # | Vấn đề | Cách xử lý |
|---|---------|-----------|
| A | `shap_summary_beeswarm.png` và `shap_global_importance_selected.png` không nằm trong API contract | Load trực tiếp từ `artifacts/epic2/explainability/` (file .png) — không phải từ API response |
| B | Music Trends data không đến từ model API | Lấy từ database analytics views hoặc pre-generated CSV của Feature 3.4 — cần Feature 3.4 hoàn thành trước |
| C | `confidence`/`uncertainty` cho prediction | **BỎ yêu cầu này.** Không có trong API contract và không có artifact từ EPIC 2. Không bịa field. |

### ❌ Thiếu — [CẦN BỔ SUNG Ở API CONTRACT nếu muốn]

| # | Nhu cầu | Ảnh hưởng | Đề xuất |
|---|---------|-----------|---------|
| — | Không có nhu cầu thiếu nào | — | Không cần bổ sung |

> **Kết luận:** API contract v1.0.0 đủ dùng cho frontend. Không có field thiếu nghiêm trọng.

---

## 3. Đề xuất cho Phiên 4

**Task 3.0.7 — Demo Scenario + Definition of Done**

### 3.1. Chốt Demo Scenario chính

Demo là phần quan trọng nhất khi bảo vệ. Phiên 4 nên chốt kịch bản demo theo thứ tự:

```
Demo Scenario: "Dự đoán và giải thích một bài hát giả định"

Bước 1 — Giới thiệu nhanh (30 giây)
  → Mở Home page, giới thiệu dataset + model

Bước 2 — Dự đoán (2 phút)
  → Nhập 18 features cho một bài hát giả định
  → Click "Dự đoán" → kết quả ~46 điểm

Bước 3 — Giải thích SHAP (2 phút)
  → Click "Phân tích SHAP" → bar chart top 5
  → Giải thích: tại sao bài hát này được điểm như vậy

Bước 4 — What-If (2 phút)
  → Tăng Energy từ 0.5 → 0.9 → hiển thị delta +8 điểm
  → Giải thích: thay đổi feature nào ảnh hưởng nhiều nhất

Bước 5 — Xu hướng (1 phút)
  → Chuyển sang Music Trends → chart popularity theo thập kỷ

Bước 6 — Model Info (30 giây)
  → Chỉ metrics MAE/RMSE, giới hạn model

Tổng: ~8 phút
```

### 3.2. Chốt Definition of Done cho EPIC 3

| # | Tiêu chí DONE |
|---|--------------|
| 1 | `POST /predict` trả về `prediction_display` đúng với `example_output.json` (±0.1) |
| 2 | `POST /explain` trả về `base_value` và `top_features` (top 5) |
| 3 | `POST /what-if` trả về `delta` đúng (`after - before`) |
| 4 | Streamlit gọi được `/predict`, `/explain`, `/what-if` khi backend chạy trên `localhost:8000` |
| 5 | Mọi lỗi 422 hiển thị message rõ ràng (không traceback) |
| 6 | App chạy được trên máy sạch với `pip install -r requirements.txt && run_all` |
| 7 | Backup demo (screenshots/video) có sẵn nếu live demo lỗi |

### 3.3. Đề xuất tiếp theo sau Phiên 4

Sau khi Definition of Done rõ ràng → bắt đầu **Feature 3.1** (Artifact Validation Gate) và **Feature 3.2** (FastAPI Backend) song song:

- **Feature 3.1** (Minh): Validate artifacts → `artifact_validation_report.md`
- **Feature 3.2** (Đạt): FastAPI skeleton → 6 endpoints → unit tests

---

## 4. Hành động cần xác nhận trước Phiên 4

1. **[CẦN XÁC NHẬN]** Xác nhận `model_metrics.json` có dữ liệu thực hay không — ảnh hưởng trực tiếp đến Model Info page
2. **[CẦN CHỐT]** Demo scenario trên có hợp lý với nhóm chưa? Nếu cần điều chỉnh → góp ý trước Phiên 4
3. **[CẦN CHUẨN HOÁ]** Copy artifacts vào `artifacts/epic2/` — để Feature 3.2 không phải hardcode đường dẫn dài

---

## 5. Danh sách file đã tạo

| File | Mô tả |
|------|--------|
| `docs/epic3/UI_UX_CONTRACT.md` | Task 3.0.5 — Thiết kế UI/UX cho 7 trang |
| `docs/epic3/FRONTEND_DATA_CONTRACT.md` | Task 3.0.6 — Mapping endpoint → field → display |
| `docs/epic3/session_reports/phien3_report.md` | Báo cáo nghiệm thu Phiên 3 |

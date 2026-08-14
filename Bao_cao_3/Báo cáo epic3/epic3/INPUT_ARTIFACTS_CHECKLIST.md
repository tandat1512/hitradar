# INPUT ARTIFACTS CHECKLIST — EPIC 3 nhận từ EPIC 2
**Ngày lập:** 2026-07-30
**Người phụ trách:** Minh
**Nguồn tham chiếu:** artifact_manifest.json trong `7.ML/7.10.model_packaging/package/metadata/`

> **Lưu ý:** File `handoff_to_epic3.md` **chưa tìm thấy** trong repo tại thời điểm lập checklist này. Danh sách artifact bên dưới được đối chiếu trực tiếp từ `artifact_manifest.json` và `MODEL_PACKAGE_README.md` của Feature 2.7. Các artifact được chia thành 2 nhóm: **đã xác nhận tồn tại trong repo** (`artifacts/epic2/` — vị trí chuẩn hoá đề xuất) và **chưa tìm thấy / cần xác nhận thêm**.

---

## Nhóm A: Artifacts đã xác nhận tồn tại trong repo

| STT | Tên artifact | Định dạng | Mục đích dùng ở EPIC 3 | Đường dẫn thực tế trong repo | Đường dẫn chuẩn đề xuất | Trạng thái |
|-----|-------------|-----------|------------------------|-------------------------------|--------------------------|------------|
| 1 | `full_inference_pipeline` | `.joblib` | Backend load model để predict — load pipeline, gọi `pipe.predict_popularity(dict_record)` | `7.ML/7.10.model_packaging/package/pipeline/full_inference_pipeline.joblib` | `artifacts/epic2/pipeline/full_inference_pipeline.joblib` | ✅ Có |
| 2 | `best_model` | `.joblib` | Backend load model layer (nếu tách riêng khỏi pipeline) | `7.ML/7.10.model_packaging/package/models/best_model.joblib` | `artifacts/epic2/models/best_model.joblib` | ✅ Có |
| 3 | `feature_engineering_pipeline` | `.joblib` | Backend/frontend: transform input features theo đúng logic EPIC 2 | `7.ML/7.10.model_packaging/package/preprocessing/feature_engineering_pipeline.joblib` | `artifacts/epic2/preprocessing/feature_engineering_pipeline.joblib` | ✅ Có |
| 4 | `model_preprocessing_pipeline` | `.joblib` | Backend: preprocessing step trước khi gọi model | `7.ML/7.10.model_packaging/package/preprocessing/model_preprocessing_pipeline.joblib` | `artifacts/epic2/preprocessing/model_preprocessing_pipeline.joblib` | ✅ Có |
| 5 | `inference_pipeline_module` | `.py` | Backend: inference wrapper module đã test, tái sử dụng logic predict/explain | `7.ML/7.10.model_packaging/package/runtime/inference_pipeline.py` | `artifacts/epic2/runtime/inference_pipeline.py` | ✅ Có |
| 6 | `input_schema` | `.json` | Backend: Pydantic validation request body theo 18 trường trong schema | `7.ML/7.10.model_packaging/package/schemas/input_schema.json` | `artifacts/epic2/schemas/input_schema.json` | ✅ Có |
| 7 | `output_schema` | `.json` | Backend: validate response body trả về, Frontend: hiển thị kết quả đúng format | `7.ML/7.10.model_packaging/package/schemas/output_schema.json` | `artifacts/epic2/schemas/output_schema.json` | ✅ Có |
| 8 | `selected_features` | `.json` | Backend/Frontend: biết cột nào model dùng, hiển thị feature importance | `7.ML/7.10.model_packaging/package/schemas/selected_features.json` | `artifacts/epic2/schemas/selected_features.json` | ✅ Có |
| 9 | `feature_names` | `.json` | Frontend: hiển thị danh sách features, SHAP mapping | `7.ML/7.10.model_packaging/package/schemas/feature_names.json` | `artifacts/epic2/schemas/feature_names.json` | ✅ Có |
| 10 | `feature_mapping` | `.json` | Backend: map tên feature gốc → feature transformed, dùng cho SHAP explain | `7.ML/7.10.model_packaging/package/schemas/feature_mapping.json` | `artifacts/epic2/schemas/feature_mapping.json` | ✅ Có |
| 11 | `example_input` | `.json` | Backend: test endpoint `/predict`, Frontend: pre-fill form mẫu | `7.ML/7.10.model_packaging/package/examples/example_input.json` | `artifacts/epic2/examples/example_input.json` | ✅ Có |
| 12 | `example_output` | `.json` | Frontend: hiển thị kết quả mẫu, backend unit test | `7.ML/7.10.model_packaging/package/examples/example_output.json` | `artifacts/epic2/examples/example_output.json` | ✅ Có |
| 13 | `model_version` | `.json` | Backend: trả về trong `/model-info`, Frontend: hiển thị phiên bản | `7.ML/7.10.model_packaging/package/metadata/model_version.json` | `artifacts/epic2/metadata/model_version.json` | ✅ Có |
| 14 | `data_version` | `.json` | Backend: trả về trong `/model-info` | `7.ML/7.10.model_packaging/package/metadata/data_version.json` | `artifacts/epic2/metadata/data_version.json` | ✅ Có |
| 15 | `package_version` | `.json` | Backend: trả về trong `/model-info` | `7.ML/7.10.model_packaging/package/metadata/package_version.json` | `artifacts/epic2/metadata/package_version.json` | ✅ Có |
| 16 | `artifact_manifest` | `.json` | EPIC 3 validate: kiểm tra SHA256, file size, tồn tại của tất cả artifacts | `7.ML/7.10.model_packaging/package/metadata/artifact_manifest.json` | `artifacts/epic2/metadata/artifact_manifest.json` | ✅ Có |
| 17 | `requirements-runtime` | `.txt` | EPIC 3 cài đặt môi trường: `pip install -r requirements-runtime.txt` | `7.ML/7.10.model_packaging/package/requirements-runtime.txt` | `artifacts/epic2/requirements-runtime.txt` | ✅ Có |
| 18 | `requirements-explainability` | `.txt` | EPIC 3 cài SHAP dependencies: `pip install -r requirements-explainability.txt` | `7.ML/7.10.model_packaging/package/requirements-explainability.txt` | `artifacts/epic2/requirements-explainability.txt` | ✅ Có |

---

## Nhóm B: Artifacts đã biết tên nhưng CHƯA tìm thấy trong repo

| STT | Tên artifact | Định dạng | Mục đích dùng ở EPIC 3 | Ghi chú cần xác nhận |
|-----|-------------|-----------|------------------------|---------------------|
| 19 | `model_metrics` | `.json` | Backend/Frontend: hiển thị metrics (MAE, RMSE, R2) trong `/model-info` và trang Model Info | **CẦN XÁC NHẬN:** Tìm thấy `4.MODELS/4.2.evaluation/model_metrics.json` nhưng cần xác nhận đây có phải artifact chính thức từ EPIC 2 bàn giao không. |
| 20 | `residual_stats` | `.json` | Frontend: hiển thị residual distribution, error analysis trong trang Model Info | **CẦN XÁC NHẬN:** File này không tìm thấy trong repo. Có thể EPIC 2 chưa export hoặc đặt tên khác. |
| 21 | `model_card` | `.md` | Frontend: trang Limitations & Responsible Use, slide bảo vệ | **CẦN XÁC NHẬN:** File `model_card.md` không tìm thấy trong repo. Cần xác nhận EPIC 2 đã tạo và đặt ở đâu. |
| 22 | `handoff_to_epic3` | `.md` | EPIC 3 đọc hướng dẫn bàn giao chính thức từ EPIC 2 | **CẦN XÁC NHẬN:** File không tìm thấy trong repo. Đây là tài liệu bắt buộc — EPIC 3 cần có trước khi bắt đầu Feature 3.1. |

---

## Nhóm C: SHAP Assets (đã tìm thấy trong repo, xác nhận tồn tại)

| STT | Tên artifact SHAP | Định dạng | Mục đích dùng ở EPIC 3 | Đường dẫn thực tế | Trạng thái |
|-----|-------------------|-----------|------------------------|-------------------|------------|
| 23 | `shap_background_raw` | `.parquet` | Backend ExplainService: tính SHAP local explanation | `7.ML/7.9.explainability/background/shap_background_raw.parquet` | ✅ Có |
| 24 | `shap_background_transformed` | `.npy` | Backend ExplainService: transformed background sample | `7.ML/7.9.explainability/background/shap_background_transformed.npy` | ✅ Có |
| 25 | `shap_base_values` | `.npy` | Backend: base value cho từng prediction | `7.ML/7.9.explainability/shap_values/shap_base_values.npy` | ✅ Có |
| 26 | `shap_values_global` | `.npy` | Frontend: hiển thị global SHAP summary bar chart | `7.ML/7.9.explainability/shap_values/shap_values_global.npy` | ✅ Có |
| 27 | `shap_values_grouped_selected` | `.npy` | Frontend: SHAP beeswarm plot (selected features) | `7.ML/7.9.explainability/shap_values/shap_values_grouped_selected.npy` | ✅ Có |
| 28 | `shap_feature_names` | `.json` | Backend: map feature index → feature name | `7.ML/7.9.explainability/shap_values/shap_feature_names.json` | ✅ Có |
| 29 | `shap_feature_mapping` | `.json` | Backend: map raw → transformed feature names | `7.ML/7.9.explainability/shap_values/shap_feature_mapping.json` | ✅ Có |
| 30 | `shap_global_importance_selected` | `.csv` | Frontend: feature importance bar chart data | `7.ML/7.9.explainability/global/shap_global_importance_selected.csv` | ✅ Có |
| 31 | `shap_summary_bar_selected` | `.png` | Frontend: global SHAP bar chart image | `7.ML/7.9.explainability/global/shap_summary_bar_selected.png` | ✅ Có |
| 32 | `shap_summary_beeswarm` | `.png` | Frontend: beeswarm plot image | `7.ML/7.9.explainability/global/shap_summary_beeswarm.png` | ✅ Có |
| 33 | `shap_dependence_*.png` | `.png` | Frontend: dependence plots cho từng feature | `7.ML/7.9.explainability/dependence/shap_dependence_*.png` (7 files) | ✅ Có |
| 34 | `shap_explanation_sample_*` | `.parquet` / `.json` | Frontend: ví dụ explanation cụ thể | `7.ML/7.9.explainability/explanation_sample/` | ✅ Có |

---

## Tổng kết trạng thái

| Nhóm | Số artifact | ✅ Có | ⚠️ Cần xác nhận |
|------|-------------|-------|----------------|
| Nhóm A (pipeline, schemas, metadata) | 18 | 18 | 0 |
| Nhóm B (metrics, residual, card, handoff) | 4 | 0 | 4 |
| Nhóm C (SHAP assets) | ~12 | ~12 | 0 |
| **Tổng** | **~34** | **~30** | **4** |

---

## Hành động cần thiết trước Phiên 2

1. **[CẦN XÁC NHẬN GẤP]** Tìm hoặc yêu cầu EPIC 2 tạo lại `handoff_to_epic3.md` — đây là tài liệu bắt buộc cho Feature 3.1.
2. **[CẦN XÁC NHẬN]** Xác nhận `model_metrics.json` tại `4.MODELS/4.2.evaluation/` có phải artifact chính thức bàn giao không, hay cần copy vào `artifacts/epic2/`.
3. **[CẦN XÁC NHẬN]** Tìm hoặc yêu cầu EPIC 2 tạo `residual_stats.json` — dùng cho trang Model Info.
4. **[CẦN XÁC NHẬN]** Tìm hoặc yêu cầu EPIC 2 tạo `model_card.md` — dùng cho trang Limitations & Responsible Use.
5. Chuẩn hoá đường dẫn: copy toàn bộ Nhóm A và C vào `artifacts/epic2/` thống nhất trước khi Feature 3.1 bắt đầu.

---

## Cấu trúc thư mục chuẩn hoá đề xuất cho `artifacts/epic2/`

```
artifacts/epic2/
├── pipeline/
│   └── full_inference_pipeline.joblib
├── models/
│   └── best_model.joblib
├── preprocessing/
│   ├── feature_engineering_pipeline.joblib
│   └── model_preprocessing_pipeline.joblib
├── runtime/
│   └── inference_pipeline.py
├── schemas/
│   ├── input_schema.json
│   ├── output_schema.json
│   ├── selected_features.json
│   ├── feature_names.json
│   └── feature_mapping.json
├── examples/
│   ├── example_input.json
│   └── example_output.json
├── metadata/
│   ├── model_version.json
│   ├── data_version.json
│   ├── package_version.json
│   └── artifact_manifest.json
├── explainability/
│   ├── shap_background_raw.parquet
│   ├── shap_background_transformed.npy
│   ├── shap_base_values.npy
│   ├── shap_values_global.npy
│   ├── shap_values_grouped_selected.npy
│   ├── shap_feature_names.json
│   ├── shap_feature_mapping.json
│   ├── shap_global_importance_selected.csv
│   ├── shap_summary_bar_selected.png
│   ├── shap_summary_beeswarm.png
│   ├── shap_dependence_*.png  (7 files)
│   └── explanation_sample/
│       └── ... (sample configs + parquet)
├── metrics/
│   └── model_metrics.json          [CẦN XÁC NHẬN]
├── evaluation/
│   └── residual_stats.json          [CẦN XÁC NHẬN]
├── docs/
│   ├── model_card.md               [CẦN XÁC NHẬN]
│   └── handoff_to_epic3.md        [CẦN XÁC NHẬN]
└── requirements/
    ├── requirements-runtime.txt
    └── requirements-explainability.txt
```

# HitRadar - Feature Engineering Hard Requirement Review

Ngày đóng gói: 2026-08-13  
Source project: `<PROJECT_ROOT>/hitradar-main`
Review package: `<PROJECT_ROOT>` (flat layout, không có thư mục con)

## 1. Nội dung đã sửa

### Shared feature engineering

- `src/features.py`
  - Tạo 13 engineered features bằng code thật.
  - Implement `FeatureBuilder.fit()` trên train và `transform()` cho train/test/inference.
  - Learned statistics cho duration và period averages không nhìn thấy test.
  - Có validation table: Exists, Dtype, Missing Count, Infinite Count, Status.
- `src/modeling.py`
  - Pipeline dùng chung cho Linear Regression, Random Forest và XGBoost.
  - Category features được encode bằng `OneHotEncoder(handle_unknown="ignore")`.
  - Scaler, imputer, encoder và FeatureBuilder chỉ fit trên train.

### Notebook 05

- Đọc real dataset, không synthetic fallback.
- Time split trước/sau năm 2019.
- Tạo và validate 13 features:
  - `key_sin`, `key_cos`
  - `dance_energy`, `positive_energy`
  - `acoustic_energy_balance`, `dance_valence`
  - `acoustic_instrumental`, `tempo_energy`
  - `energy_vs_period_avg`, `dance_vs_period_avg`
  - `mood_quadrant`, `duration_category`, `tempo_category`
- Save/reload `features_engineered.parquet`.
- 13/13 feature có Status = PASS.

### Notebook 06

- Kiểm tra `MODEL_FEATURES` tồn tại thật từ output NB05.
- Không dùng `cluster` làm regression feature.
- Train lại 6 experiment thật:
  - Baseline + Linear Regression / Random Forest / XGBoost.
  - Engineered + Linear Regression / Random Forest / XGBoost.
- Lưu metrics, predictions, feature importance và final fitted pipeline.

### Notebook 07 và deployment

- FastAPI và Streamlit chỉ dùng raw input; user không nhập engineered features.
- FastAPI load đúng final pipeline từ Notebook 06.
- Sửa mismatch preprocessing cũ và loại bỏ bug `speechiness_log = log1p(instrumentalness)`.
- Test `/health`, `/predict`, invalid range, extra engineered input và API/direct prediction parity.
- Streamlit initial render test không có exception.

## 2. Kết quả model mới

| Experiment | Model | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| Baseline | Linear Regression | 18.6336 | 22.9131 | 0.0828 |
| Engineered | Linear Regression | 18.3039 | 22.6926 | 0.1004 |
| Baseline | Random Forest | 16.5207 | 20.7078 | 0.2509 |
| Engineered | Random Forest | 16.6458 | 20.7770 | 0.2459 |
| Baseline | XGBoost | 16.3132 | 20.5796 | 0.2601 |
| Engineered | XGBoost | 16.2913 | 20.5736 | 0.2606 |

Final model: **Engineered XGBoost**.

Train rows: 554,547  
Test rows: 32,125  
Raw input fields: 17  
Baseline features: 18  
Engineered features: 13  
Total model features trước encoding: 31

## 3. Validation

- Notebook 05: 6/6 code cells executed, 0 error.
- Notebook 06: 8/8 code cells executed, 0 error.
- Notebook 07: 5/5 code cells executed, 0 error.
- 13/13 engineered features: PASS.
- 5 unit/integration tests: PASS.
- FastAPI health/predict/parity: PASS.
- Streamlit initial render: PASS.

## 4. Cấu trúc package

Tất cả file nằm trực tiếp trong `<PROJECT_ROOT>`, không có thư mục con.
Tên file được thêm số thứ tự và tiền tố chức năng để tránh ghi đè các file trùng tên.
Các notebook cũ có tiền tố `BACKUP` để so sánh với notebook mới.

## 5. Lưu ý về Git

Source folder hiện không có `.git`, vì vậy không có `git status` hoặc normal `git diff`.
Bản notebook cũ có tiền tố `BACKUP` để so sánh bằng `git diff --no-index`.
Không có thao tác kết nối GitHub, commit hoặc push.

Thư mục lồng cũ được chuyển ra `<PROJECT_ROOT>` làm bản backup khôi phục được, không nằm trong thư mục review.

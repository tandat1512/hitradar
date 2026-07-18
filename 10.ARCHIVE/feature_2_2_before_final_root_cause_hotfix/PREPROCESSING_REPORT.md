# BÁO CÁO TỔNG QUAN PREPROCESSING
Thời gian tạo: 2026-07-18 10:18:39 UTC

## 1. Môi Trường Dữ Liệu Đầu Vào

- Data Version: ml-ready-2026-07-17-v1
- Split Version: temporal-split-v1
- Số lượng dòng Train: 415524

## 2. Pipeline Ứng Viên (Candidates)

| Pipeline | Mục Tiêu Mô Hình | Chức Năng Chính |
|---|---|---|
| P22-A | Ridge Regression | StandardScaler, Median Imputer, OneHotEncoder |
| P22-B | Ridge Regression (Có Missing Indicator) | Giống P22-A + Missing indicators cho cột tháng/tempo |
| P22-C | Ridge Regression (Chống nhiễu) | RobustScaler, TrainOnlyOutlierClipper, OneHotEncoder |
| P22-D | Tree Models (HistGB, XGBoost) | Passthrough numeric, OrdinalEncoder với unknown_value=-1 |

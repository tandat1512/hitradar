# Preprocessing Report — Feature 2.2

## Summary

Three model-specific preprocessing pipelines have been created, each optimized for its model type.

## Pipeline Comparison

| Aspect | Ridge | HistGradientBoosting | XGBoost |
|--------|-------|---------------------|---------|
| Numeric imputation | median | median | median |
| Categorical imputation | most_frequent | most_frequent | most_frequent |
| Categorical encoding | OneHotEncoder | OrdinalEncoder | OrdinalEncoder |
| Scaling | StandardScaler | none | none |
| Binary handling | passthrough | passthrough | passthrough |

## Ridge Preprocessor

### Configuration
- **Numeric**: SimpleImputer → TrainOnlyOutlierClipper → StandardScaler
- **Categorical**: SimpleImputer → ScaledOneHotEncoder (float32 output)
- **Binary**: passthrough
- **Unknown categories**: ignored

### Output Shape
- Input: 18 features + 2 missing indicators = 20 columns
- Output: ~85 features (one-hot expands categorical columns)

## HistGradientBoosting Preprocessor

### Configuration
- **Numeric**: SimpleImputer only (no scaling)
- **Categorical**: SimpleImputer → OrdinalEncoder (unknown=-1)
- **Binary**: passthrough

### Output Shape
- Input: 18 features + 2 missing indicators = 20 columns
- Output: 20 features (ordinal encoding preserves dimensions)

## XGBoost Preprocessor

### Configuration
- **Numeric**: SimpleImputer only (no scaling)
- **Categorical**: SimpleImputer → OrdinalEncoder (unknown=-1)
- **Binary**: passthrough

### Output Shape
- Input: 18 features + 2 missing indicators = 20 columns
- Output: 20 features (ordinal encoding preserves dimensions)

## Leakage Guarantees

✅ All statistics (median, mode, scaler mean/var, encoder categories) learned from train split only
✅ Preprocessors saved as artifacts with version tracking
✅ Manifest records all configuration and data hashes

## Artifacts

| Artifact | Path |
|----------|------|
| Ridge preprocessor | 7.ML/7.5.preprocessing/preprocessor_ridge.pkl |
| HistGB preprocessor | 7.ML/7.5.preprocessing/preprocessor_histgb.pkl |
| XGB preprocessor | 7.ML/7.5.preprocessing/preprocessor_xgb.pkl |
| Manifest | 7.ML/7.5.preprocessing/preprocessor_manifest.json |
| Column roles | 7.ML/7.5.preprocessing/column_roles.json |
| Feature names (Ridge) | 7.ML/7.5.preprocessing/ridge_feature_names.json |

---
Generated: 2026-07-17

# HitRadar Pro - Model Package (Feature 2.7)
## 1. Package overview
Canonical model inference package for HitRadar Pro.
## 2. Target and model purpose
Predict track popularity (0-100) based on 18 track metadata and audio features.
## 3. Package directory tree
- `models/`: Base XGBoost model
- `preprocessing/`: Feature engineering transformers
- `pipeline/`: Full unified inference pipeline
- `runtime/`: Inference wrapper module
- `schemas/`: Input/Output constraints
- `examples/`: Sample request/response
- `metadata/`: Versioning and hashes
## 4. Runtime prerequisites
Python 3.10+, numpy, pandas, scikit-learn, xgboost, joblib.
## 5. Installation
`pip install -r requirements-runtime.txt`
## 6. Load pipeline
```python
import joblib
pipe = joblib.load('package/pipeline/full_inference_pipeline.joblib')
```
## 7. Input schema
18 canonical fields. (See `schemas/input_schema.json`).
## 8. Single prediction
```python
result = pipe.predict_popularity(dict_record)
```
## 9. Batch prediction
```python
results = pipe.predict_popularity(pandas_dataframe)
```
## 10. Output schema
Dictionary with `status`, `prediction_raw`, `prediction_clipped`, `prediction_display`.
## 11. Explainability
Requires `requirements-explainability.txt`. SHAP logic is in EPIC 3.
## 12. Error handling
Invalid inputs raise `ValueError`.
## 13. Versioning
Model: 1.0.0, Data: 1.0.0, Package: 2.7.0.
## 14. Artifact verification
Check `metadata/artifact_manifest.json`.
## 15. Model limitations
Underpredicts viral tracks. High error rates on specific categories.
## 16. Troubleshooting
Check `warnings` array in the prediction output for silently dropped fields.

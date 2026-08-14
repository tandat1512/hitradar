"""Rebuild Notebooks 05-07 around the canonical shared feature pipeline."""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]


def md(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    return nbf.v4.new_code_cell(text.strip())


def write_notebook(path, cells):
    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    nbf.write(notebook, path)


nb05_cells = [
    md(
        """
# Notebook 05 — Feature Engineering

**Main task:** dự đoán `target_popularity` bằng supervised regression.  
**Input:** `5.DATA/processed/ml_ready_dataset.parquet` (586.672 track thật).  
**Output:** engineered dataset, validation table, feature contract và train-only statistics cho Notebook 06.

Notebook này tạo **13 engineered features bằng code thật**. Clustering không được dùng như một feature của regression. Các thống kê theo thời kỳ và ngưỡng duration chỉ được fit trên train (`release_year < 2019`), sau đó transform train/test/inference bằng cùng statistics.
"""
    ),
    md(
        """
## 1. Mục tiêu và câu hỏi

1. Các giả thuyết từ EDA được chuyển thành column thật như thế nào?
2. 13 feature có tồn tại, đúng dtype, không missing và không infinite không?
3. Feature category sẽ được encoding thật ở bước training như thế nào?
4. Làm sao tránh leakage với `energy_vs_period_avg`, `dance_vs_period_avg` và duration thresholds?
"""
    ),
    code(
        """
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
from IPython.display import display

ROOT = Path.cwd()
if not (ROOT / "src").exists():
    for candidate in Path.cwd().resolve().parents:
        if (candidate / "src").exists() and (candidate / "5.DATA").exists():
            ROOT = candidate
            break
sys.path.insert(0, str(ROOT))

from src.features import (
    BASELINE_MODEL_FEATURES,
    ENGINEERED_CATEGORICAL_FEATURES,
    EXPECTED_ENGINEERED_FEATURES,
    MODEL_FEATURES,
    RAW_INPUT_FEATURES,
    TARGET,
    TEST_START_YEAR,
    FeatureBuilder,
    build_feature_contract,
    validate_engineered_features,
)

DATA_PATH = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
OUTPUT_DIR = ROOT / "5.DATA" / "processed"
FE_OUTPUT_DIR = ROOT / "7.ML" / "7.6.feature_engineering"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Project root: {ROOT}")
print(f"Real dataset: {DATA_PATH}")
"""
    ),
    md("## 2. Đọc dữ liệu thật và time-based split"),
    code(
        """
if not DATA_PATH.exists():
    raise FileNotFoundError(f"Không có real dataset: {DATA_PATH}. Không dùng synthetic fallback.")

df_raw = pd.read_parquet(DATA_PATH)
required = [*RAW_INPUT_FEATURES, TARGET, "track_id"]
missing_raw = [column for column in required if column not in df_raw.columns]
assert not missing_raw, f"Missing source columns: {missing_raw}"

shape_before = df_raw.shape
train_mask = df_raw["release_year"] < TEST_START_YEAR
assert train_mask.any() and (~train_mask).any(), "Time split tạo train/test rỗng."

print(f"Shape trước Feature Engineering: {shape_before}")
print(f"Train (< {TEST_START_YEAR}): {train_mask.sum():,}")
print(f"Test  (>= {TEST_START_YEAR}): {(~train_mask).sum():,}")
display(df_raw[["track_id", TARGET, *RAW_INPUT_FEATURES[:6]]].head())
"""
    ),
    md(
        """
## 3. Fit trên TRAIN → transform toàn bộ dữ liệu

`FeatureBuilder.fit()` học duration quantiles và decade-level means từ train. Target không được truyền vào feature builder. Những decade không xuất hiện trong train sẽ dùng global train mean, không dùng test/future statistics.
"""
    ),
    code(
        """
feature_builder = FeatureBuilder(include_engineered=True)
feature_builder.fit(df_raw.loc[train_mask, RAW_INPUT_FEATURES])

engineered_matrix = feature_builder.transform(df_raw[RAW_INPUT_FEATURES])
df = pd.concat(
    [df_raw[["track_id", TARGET]].reset_index(drop=True), engineered_matrix.reset_index(drop=True)],
    axis=1,
)

shape_after = df.shape
print(f"Shape trước: {shape_before}")
print(f"Shape sau:   {shape_after}")
print(f"Số engineered features: {len(EXPECTED_ENGINEERED_FEATURES)}")
display(df[["track_id", TARGET, *EXPECTED_ENGINEERED_FEATURES]].head(8))
"""
    ),
    md("## 4. Validation bắt buộc"),
    code(
        """
missing_features = [
    feature for feature in EXPECTED_ENGINEERED_FEATURES
    if feature not in df.columns
]

assert len(missing_features) == 0, f"Missing engineered features: {missing_features}"
assert len(EXPECTED_ENGINEERED_FEATURES) >= 12

feature_validation = validate_engineered_features(df)
assert feature_validation["Status"].eq("PASS").all(), feature_validation
display(feature_validation)

print("Engineered columns:")
print(EXPECTED_ENGINEERED_FEATURES)
print()
print("Missing values:")
display(df[EXPECTED_ENGINEERED_FEATURES].isna().sum().to_frame("missing_count"))
"""
    ),
    md(
        """
## 5. Feature contract và encoding contract

Ba cột string/category (`mood_quadrant`, `duration_category`, `tempo_category`) không được đưa raw vào estimator. Notebook 06 dùng `ColumnTransformer` + `OneHotEncoder(handle_unknown='ignore')` được fit trên train. `MODEL_FEATURES` dưới đây chỉ được duyệt sau khi các columns đã được tạo và validation PASS.
"""
    ),
    code(
        """
MODEL_FEATURES_ACTUAL = [feature for feature in MODEL_FEATURES if feature in df.columns]
assert MODEL_FEATURES_ACTUAL == MODEL_FEATURES
assert not set(ENGINEERED_CATEGORICAL_FEATURES).difference(df.columns)

contract = build_feature_contract()
learned_statistics = feature_builder.get_learned_statistics()

print(f"Baseline features: {len(BASELINE_MODEL_FEATURES)}")
print(f"Engineered features: {len(EXPECTED_ENGINEERED_FEATURES)}")
print(f"MODEL_FEATURES: {len(MODEL_FEATURES)}")
display(pd.DataFrame({"MODEL_FEATURES": MODEL_FEATURES}))
display(pd.DataFrame([learned_statistics]).drop(columns=["energy_period_means", "dance_period_means"]))
"""
    ),
    md("## 6. Save output thật cho Notebook 06"),
    code(
        """
ENGINEERED_DATA_PATH = OUTPUT_DIR / "features_engineered.parquet"
VALIDATION_PATH = FE_OUTPUT_DIR / "hard_requirement_feature_validation.csv"
CONTRACT_PATH = FE_OUTPUT_DIR / "hard_requirement_feature_contract.json"
STATS_PATH = FE_OUTPUT_DIR / "hard_requirement_train_statistics.json"

df.to_parquet(ENGINEERED_DATA_PATH, index=False)
feature_validation.to_csv(VALIDATION_PATH, index=False)
CONTRACT_PATH.write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
STATS_PATH.write_text(json.dumps(learned_statistics, indent=2, ensure_ascii=False), encoding="utf-8")

reloaded = pd.read_parquet(ENGINEERED_DATA_PATH)
assert len(reloaded) == len(df)
assert all(feature in reloaded.columns for feature in EXPECTED_ENGINEERED_FEATURES)
assert validate_engineered_features(reloaded)["Status"].eq("PASS").all()

print(f"Saved engineered dataset: {ENGINEERED_DATA_PATH}")
print(f"Saved validation:         {VALIDATION_PATH}")
print(f"Saved contract:           {CONTRACT_PATH}")
print(f"Saved train statistics:   {STATS_PATH}")
print(f"Reloaded shape: {reloaded.shape}")
"""
    ),
    md(
        """
## 7. Key findings, insight và handoff

**Finding:** 13/13 engineered columns được tạo thật và validation PASS; output giữ đúng 586.672 track.  
**Interpretation:** interaction, cyclic key, nonlinear category và period-relative signals đã trở thành dữ liệu executable thay vì danh sách ý tưởng.  
**Impact:** Notebook 06 có thể so sánh baseline với engineered set trên cùng time split, còn deployment có thể tái tạo features từ raw input.  
**Leakage control:** learned statistics chỉ fit trên các track trước 2019.  
**Handoff:** Notebook 06 phải đọc `features_engineered.parquet`, kiểm tra `MODEL_FEATURES`, fit encoder/scaler trên train, chạy Linear/RF/XGBoost và lưu metrics mới.
"""
    ),
]


nb06_cells = [
    md(
        """
# Notebook 06 — Machine Learning

**Input:** output thật của Notebook 05 (`features_engineered.parquet`).  
**Main task:** time-based popularity regression.  
**Experiments:** Baseline và Baseline + 13 Engineered Features; mỗi experiment chạy Linear Regression, Random Forest và XGBoost.  
**Output:** metrics mới, predictions, feature importance và một pipeline hoàn chỉnh dùng cho Notebook 07/FastAPI.
"""
    ),
    code(
        """
from pathlib import Path
import json
import sys
import time

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

ROOT = Path.cwd()
if not (ROOT / "src").exists():
    for candidate in Path.cwd().resolve().parents:
        if (candidate / "src").exists() and (candidate / "5.DATA").exists():
            ROOT = candidate
            break
sys.path.insert(0, str(ROOT))

from src.features import (
    BASELINE_MODEL_FEATURES,
    EXPECTED_ENGINEERED_FEATURES,
    MODEL_FEATURES,
    RAW_INPUT_FEATURES,
    TARGET,
    TEST_START_YEAR,
    validate_engineered_features,
)
from src.modeling import (
    MODEL_NAMES,
    build_model_pipeline,
    regression_metrics,
    transformed_feature_importance,
)

DATA_PATH = ROOT / "5.DATA" / "processed" / "features_engineered.parquet"
ARTIFACT_DIR = ROOT / "4.MODELS" / "hitradar_popularity"
EVALUATION_DIR = ROOT / "4.MODELS" / "4.2.evaluation"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

print(f"Project root: {ROOT}")
"""
    ),
    md("## 1. Load NB05 output và kiểm tra feature contract"),
    code(
        """
if not DATA_PATH.exists():
    raise FileNotFoundError(f"Chưa có output NB05: {DATA_PATH}. Không dùng synthetic fallback.")

df = pd.read_parquet(DATA_PATH)
missing_features = [feature for feature in MODEL_FEATURES if feature not in df.columns]
assert not missing_features, f"MODEL_FEATURES chưa tồn tại: {missing_features}"
assert validate_engineered_features(df)["Status"].eq("PASS").all()
assert "cluster" not in MODEL_FEATURES, "Cluster không được tính vào regression features."

train_df = df[df["release_year"] < TEST_START_YEAR].copy()
test_df = df[df["release_year"] >= TEST_START_YEAR].copy()
assert len(train_df) + len(test_df) == len(df)
assert train_df["release_year"].max() < test_df["release_year"].min()

X_train = train_df[RAW_INPUT_FEATURES]
y_train = train_df[TARGET]
X_test = test_df[RAW_INPUT_FEATURES]
y_test = test_df[TARGET]

print(f"Dataset: {df.shape}")
print(f"Train: {X_train.shape}, years {train_df.release_year.min()}–{train_df.release_year.max()}")
print(f"Test:  {X_test.shape}, years {test_df.release_year.min()}–{test_df.release_year.max()}")
print(f"Baseline feature count: {len(BASELINE_MODEL_FEATURES)}")
print(f"Engineered feature count: {len(EXPECTED_ENGINEERED_FEATURES)}")
print(f"Approved MODEL_FEATURES: {len(MODEL_FEATURES)}")
"""
    ),
    md(
        """
## 2. Leakage-safe training pipeline

Mỗi pipeline thực hiện đúng thứ tự: raw input → `FeatureBuilder.fit(train)` → `ColumnTransformer.fit(train)` → estimator. Category features được one-hot encode thật; scaler, imputer, encoder và period statistics không nhìn thấy test.
"""
    ),
    code(
        """
experiment_specs = [
    ("Baseline", False),
    ("Engineered", True),
]

metrics_rows = []
trained_pipelines = {}
predictions = {}

for experiment, include_engineered in experiment_specs:
    for model_name in MODEL_NAMES:
        print(f"Training {experiment} / {model_name} ...")
        started = time.perf_counter()
        pipeline = build_model_pipeline(model_name, include_engineered=include_engineered)
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        metrics = regression_metrics(y_test, y_pred)
        metrics_rows.append(
            {
                "Experiment": experiment,
                "Model": model_name,
                **metrics,
                "Train Rows": len(X_train),
                "Test Rows": len(X_test),
                "Raw Input Features": len(RAW_INPUT_FEATURES),
                "Engineered Features": len(EXPECTED_ENGINEERED_FEATURES) if include_engineered else 0,
                "Runtime Seconds": time.perf_counter() - started,
            }
        )
        trained_pipelines[(experiment, model_name)] = pipeline
        predictions[(experiment, model_name)] = np.asarray(y_pred)
        print(metrics_rows[-1])

metrics_table = pd.DataFrame(metrics_rows).sort_values(["Experiment", "RMSE"])
display(metrics_table)
"""
    ),
    md("## 3. Baseline vs Feature Engineering"),
    code(
        """
comparison = metrics_table.pivot(index="Model", columns="Experiment", values=["MAE", "RMSE", "R2"])
display(comparison)

effect_rows = []
for model_name in MODEL_NAMES:
    baseline = metrics_table.query("Experiment == 'Baseline' and Model == @model_name").iloc[0]
    engineered = metrics_table.query("Experiment == 'Engineered' and Model == @model_name").iloc[0]
    effect_rows.append({
        "Model": model_name,
        "MAE Change (FE-Baseline)": engineered.MAE - baseline.MAE,
        "RMSE Change (FE-Baseline)": engineered.RMSE - baseline.RMSE,
        "R2 Change (FE-Baseline)": engineered.R2 - baseline.R2,
        "FE Improved RMSE": bool(engineered.RMSE < baseline.RMSE),
    })
feature_effect = pd.DataFrame(effect_rows)
display(feature_effect)
"""
    ),
    md("## 4. Chọn final model bằng metrics mới"),
    code(
        """
engineered_metrics = metrics_table[metrics_table["Experiment"] == "Engineered"].copy()
winner = engineered_metrics.sort_values(["RMSE", "MAE"], ascending=True).iloc[0]
FINAL_MODEL_NAME = str(winner["Model"])
final_pipeline = trained_pipelines[("Engineered", FINAL_MODEL_NAME)]
y_pred_final = predictions[("Engineered", FINAL_MODEL_NAME)]
final_test_metrics = regression_metrics(y_test, y_pred_final)

print(f"Final model: {FINAL_MODEL_NAME}")
print(f"Final metrics: {final_test_metrics}")
assert final_pipeline.named_steps["features"].fit_row_count_ == len(X_train)
assert len(final_pipeline.named_steps["features"].get_feature_names_out()) == len(MODEL_FEATURES)
"""
    ),
    md("## 5. Diagnostics và error by popularity group"),
    code(
        """
diagnostics = test_df[["track_id", "release_year", TARGET]].copy()
diagnostics["prediction"] = y_pred_final
diagnostics["residual"] = diagnostics[TARGET] - diagnostics["prediction"]
diagnostics["absolute_error"] = diagnostics["residual"].abs()
diagnostics["popularity_group"] = pd.cut(
    diagnostics[TARGET],
    bins=[-np.inf, 30, 50, 70, np.inf],
    labels=["low", "emerging", "medium", "high"],
)

error_by_group = diagnostics.groupby("popularity_group", observed=True).agg(
    Rows=("absolute_error", "size"),
    MAE=("absolute_error", "mean"),
    Bias=("residual", "mean"),
).reset_index()
display(error_by_group)

sample = diagnostics.sample(min(5000, len(diagnostics)), random_state=1512)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
axes[0].scatter(sample[TARGET], sample["prediction"], alpha=0.25, s=10)
axes[0].plot([0, 100], [0, 100], "r--")
axes[0].set(title="Actual vs Predicted", xlabel="Actual popularity", ylabel="Predicted popularity")
sns.histplot(diagnostics["residual"], bins=50, kde=True, ax=axes[1])
axes[1].set(title="Residual Distribution", xlabel="Actual - Predicted", ylabel="Count")
axes[2].scatter(sample["prediction"], sample["residual"], alpha=0.25, s=10)
axes[2].axhline(0, color="red", linestyle="--")
axes[2].set(title="Residual vs Prediction", xlabel="Prediction", ylabel="Residual")
plt.tight_layout()
plt.show()
"""
    ),
    md("## 6. Feature importance"),
    code(
        """
feature_importance = transformed_feature_importance(final_pipeline)
display(feature_importance.head(20))

top = feature_importance.head(20).sort_values("Importance")
plt.figure(figsize=(10, 7))
plt.barh(top["Feature"], top["Importance"])
plt.title(f"Top Feature Importance — {FINAL_MODEL_NAME}")
plt.xlabel("Importance")
plt.ylabel("Transformed feature")
plt.tight_layout()
plt.show()
"""
    ),
    md("## 7. Save model, preprocessing, metrics và predictions"),
    code(
        """
PIPELINE_PATH = ARTIFACT_DIR / "popularity_pipeline.joblib"
FEATURE_COLUMNS_PATH = ARTIFACT_DIR / "feature_columns.json"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"
PREDICTIONS_PATH = EVALUATION_DIR / "hard_requirement_test_predictions.parquet"
IMPORTANCE_PATH = EVALUATION_DIR / "feature_importance.json"
METRICS_MIRROR_PATH = EVALUATION_DIR / "model_metrics.json"

metrics_payload = {
    "final_model": FINAL_MODEL_NAME,
    "selection_rule": "lowest engineered test RMSE, tie-break by MAE",
    "test_start_year": TEST_START_YEAR,
    "train_rows": len(X_train),
    "test_rows": len(X_test),
    "raw_input_feature_count": len(RAW_INPUT_FEATURES),
    "model_feature_count": len(MODEL_FEATURES),
    "engineered_feature_count": len(EXPECTED_ENGINEERED_FEATURES),
    "final_test_metrics": final_test_metrics,
    "experiments": metrics_table.to_dict(orient="records"),
    "feature_engineering_effect": feature_effect.to_dict(orient="records"),
    "error_by_popularity_group": error_by_group.to_dict(orient="records"),
}

joblib.dump(final_pipeline, PIPELINE_PATH)
FEATURE_COLUMNS_PATH.write_text(json.dumps({
    "raw_input_features": RAW_INPUT_FEATURES,
    "model_features": MODEL_FEATURES,
    "engineered_features": EXPECTED_ENGINEERED_FEATURES,
    "transformed_feature_names": final_pipeline.named_steps["preprocessing"].get_feature_names_out().tolist(),
}, indent=2, ensure_ascii=False), encoding="utf-8")
METRICS_PATH.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")
METRICS_MIRROR_PATH.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")
diagnostics.to_parquet(PREDICTIONS_PATH, index=False)
IMPORTANCE_PATH.write_text(feature_importance.to_json(orient="records", indent=2), encoding="utf-8")

reloaded_pipeline = joblib.load(PIPELINE_PATH)
reloaded_pred = reloaded_pipeline.predict(X_test.head(5))
np.testing.assert_allclose(reloaded_pred, final_pipeline.predict(X_test.head(5)))

print(f"Pipeline: {PIPELINE_PATH}")
print(f"Metrics: {METRICS_PATH}")
print(f"Predictions: {PREDICTIONS_PATH}")
print(f"Feature columns: {FEATURE_COLUMNS_PATH}")
"""
    ),
    md(
        """
## 8. Insight, limitations và handoff

**Finding:** bảng experiment phía trên là kết quả mới từ 6 lần train thật; không tái sử dụng metric cũ.  
**Interpretation:** hiệu quả của Feature Engineering được kết luận bằng chênh lệch MAE/RMSE/R², không bằng feature importance đơn lẻ.  
**Impact:** final artifact chứa FeatureBuilder + encoder/scaler + estimator trong một pipeline, giảm train/inference mismatch.  
**Limitation:** popularity lịch sử chịu time bias; metric test 2019–2021 không chứng minh quan hệ nhân quả hoặc khả năng dự báo hit tương lai ngoài distribution.  
**Handoff:** Notebook 07 và FastAPI chỉ nhận 17 raw fields, load `popularity_pipeline.joblib`, rồi smoke test toàn luồng RAW INPUT → FEATURES → MODEL → PREDICTION.
"""
    ),
]


nb07_cells = [
    md(
        """
# Notebook 07 — AI Deployment (FastAPI + Streamlit)

Kiến trúc triển khai: **User → Streamlit → FastAPI → Pydantic validation → shared FeatureBuilder → fitted preprocessing → final model → popularity prediction**.

User không nhập engineered features. Notebook này kiểm tra artifact, feature order, `/health`, valid `/predict`, invalid input và parity giữa API với pipeline trực tiếp.
"""
    ),
    code(
        """
from pathlib import Path
import importlib.util
import json
import sys

import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

ROOT = Path.cwd()
if not (ROOT / "src").exists():
    for candidate in Path.cwd().resolve().parents:
        if (candidate / "src").exists() and (candidate / "5.DATA").exists():
            ROOT = candidate
            break
sys.path.insert(0, str(ROOT))

from src.features import (
    EXPECTED_ENGINEERED_FEATURES,
    MODEL_FEATURES,
    RAW_INPUT_FEATURES,
)

ARTIFACT_DIR = ROOT / "4.MODELS" / "hitradar_popularity"
PIPELINE_PATH = ARTIFACT_DIR / "popularity_pipeline.joblib"
FEATURE_COLUMNS_PATH = ARTIFACT_DIR / "feature_columns.json"
API_PATH = ROOT / "5.UNG_DUNG" / "5.1.backend_api" / "api.py"
STREAMLIT_PATH = ROOT / "5.UNG_DUNG" / "5.2.frontend" / "streamlit_app.py"

assert PIPELINE_PATH.exists(), "Chưa có final pipeline từ Notebook 06."
assert API_PATH.exists() and API_PATH.stat().st_size > 0
assert STREAMLIT_PATH.exists() and STREAMLIT_PATH.stat().st_size > 0
print(f"Model artifact: {PIPELINE_PATH}")
print(f"FastAPI source: {API_PATH}")
print(f"Streamlit source: {STREAMLIT_PATH}")
"""
    ),
    md("## 1. Model load và train/inference contract"),
    code(
        """
pipeline = joblib.load(PIPELINE_PATH)
feature_contract = json.loads(FEATURE_COLUMNS_PATH.read_text(encoding="utf-8"))

assert feature_contract["raw_input_features"] == RAW_INPUT_FEATURES
assert feature_contract["model_features"] == MODEL_FEATURES
assert feature_contract["engineered_features"] == EXPECTED_ENGINEERED_FEATURES
assert pipeline.named_steps["features"].get_feature_names_out().tolist() == MODEL_FEATURES

print(f"Raw fields: {len(RAW_INPUT_FEATURES)}")
print(f"Engineered fields generated server-side: {len(EXPECTED_ENGINEERED_FEATURES)}")
print(f"Model features before encoding: {len(MODEL_FEATURES)}")
print(f"Encoded matrix columns: {len(feature_contract['transformed_feature_names'])}")
"""
    ),
    md("## 2. RAW INPUT → FEATURE ENGINEERING → MODEL → PREDICTION"),
    code(
        """
sample_raw = {
    "duration_min": 3.55,
    "explicit": False,
    "release_year": 2020,
    "release_month": 7.0,
    "release_precision": "day",
    "danceability": 0.72,
    "energy": 0.78,
    "key": 5,
    "loudness": -6.5,
    "mode": 1,
    "speechiness": 0.08,
    "acousticness": 0.18,
    "instrumentalness": 0.02,
    "liveness": 0.14,
    "valence": 0.64,
    "tempo": 124.0,
    "time_signature": 4.0,
}
raw_frame = pd.DataFrame([sample_raw])[RAW_INPUT_FEATURES]
engineered_frame = pipeline.named_steps["features"].transform(raw_frame)
missing_features = [feature for feature in MODEL_FEATURES if feature not in engineered_frame.columns]
assert not missing_features
assert np.isfinite(engineered_frame.select_dtypes(include=np.number)).all().all()

direct_prediction = float(np.clip(pipeline.predict(raw_frame)[0], 0, 100))
print(f"RAW shape: {raw_frame.shape}")
print(f"Feature shape before encoding: {engineered_frame.shape}")
print(f"Direct prediction: {direct_prediction:.4f}")
display(engineered_frame[EXPECTED_ENGINEERED_FEATURES])
"""
    ),
    md("## 3. FastAPI /health, /predict và invalid input"),
    code(
        """
spec = importlib.util.spec_from_file_location("hitradar_api", API_PATH)
api_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_module)
client = TestClient(api_module.app)

health_response = client.get("/health")
assert health_response.status_code == 200
health = health_response.json()
assert health["status"] == "ready" and health["model_loaded"] is True

predict_response = client.post("/predict", json=sample_raw)
assert predict_response.status_code == 200, predict_response.text
api_prediction = predict_response.json()
assert abs(api_prediction["predicted_popularity"] - direct_prediction) < 1e-3
assert api_prediction["engineered_feature_count"] == len(EXPECTED_ENGINEERED_FEATURES)
assert api_prediction["feature_count"] == len(MODEL_FEATURES)

invalid_payload = {**sample_raw, "energy": 1.5}
invalid_response = client.post("/predict", json=invalid_payload)
assert invalid_response.status_code == 422

engineered_input_attack = {**sample_raw, "key_sin": 0.5}
extra_field_response = client.post("/predict", json=engineered_input_attack)
assert extra_field_response.status_code == 422

test_results = pd.DataFrame([
    {"Test": "Model load", "Status": "PASS"},
    {"Test": "GET /health", "Status": "PASS"},
    {"Test": "POST /predict valid raw input", "Status": "PASS"},
    {"Test": "Invalid range rejected", "Status": "PASS"},
    {"Test": "Engineered input rejected", "Status": "PASS"},
    {"Test": "Direct/API prediction parity", "Status": "PASS"},
    {"Test": "Feature names and order", "Status": "PASS"},
    {"Test": "Streamlit source present", "Status": "PASS"},
])
display(test_results)
print(api_prediction)
"""
    ),
    md("## 4. Save deployment smoke-test evidence"),
    code(
        """
VALIDATION_DIR = ROOT / "5.UNG_DUNG" / "validation"
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
TEST_RESULT_PATH = VALIDATION_DIR / "hard_requirement_deployment_smoke_test.json"

payload = {
    "all_pass": bool(test_results["Status"].eq("PASS").all()),
    "tests": test_results.to_dict(orient="records"),
    "health": health,
    "valid_prediction": api_prediction,
    "invalid_status_code": invalid_response.status_code,
    "extra_engineered_field_status_code": extra_field_response.status_code,
    "raw_input_features": RAW_INPUT_FEATURES,
    "model_features": MODEL_FEATURES,
}
TEST_RESULT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Saved smoke-test evidence: {TEST_RESULT_PATH}")
"""
    ),
    md(
        """
## 5. Insight, cách chạy và kết luận

**Finding:** model load, health, valid prediction, invalid-input rejection, feature order và direct/API parity đều PASS.  
**Interpretation:** feature engineering ở inference không phải bản copy khác; API load đúng pipeline đã fit tại Notebook 06.  
**Impact:** user chỉ nhập raw audio/time fields; 13 engineered features và encoding được xử lý server-side, loại bỏ mismatch kiểu “train 31 features nhưng API gửi 11”.  
**Limitations:** FastAPI/Streamlit smoke test trong notebook xác nhận logic và contract; kiểm thử tải, authentication và production observability vẫn nằm ngoài phạm vi.

Chạy ứng dụng từ project root:

```powershell
uvicorn api:app --app-dir "5.UNG_DUNG/5.1.backend_api" --host 127.0.0.1 --port 8000
streamlit run "5.UNG_DUNG/5.2.frontend/streamlit_app.py"
```
"""
    ),
]


write_notebook(
    ROOT / "3.NOTEBOOKS" / "3.5.feature_engineering" / "05_feature_engineering.ipynb",
    nb05_cells,
)
write_notebook(
    ROOT / "3.NOTEBOOKS" / "3.6.modeling" / "06_machine_learning.ipynb",
    nb06_cells,
)
write_notebook(
    ROOT / "3.NOTEBOOKS" / "3.7.demo" / "07_ai_deployment.ipynb",
    nb07_cells,
)

print("Rebuilt Notebook 05, 06 and 07.")

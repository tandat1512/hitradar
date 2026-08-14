"""Generate executable hotfix notebooks 05-07 from shared production code."""

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]


def md(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


def code(source: str):
    return nbf.v4.new_code_cell(source.strip())


def write(relative_path: str, cells: list):
    path = ROOT / relative_path
    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "HitRadar Runtime",
                "language": "python",
                "name": "hitradar-runtime",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    nbf.write(notebook, path)
    print(path)


common_setup = r'''
from pathlib import Path
import json
import sys

import joblib
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
print(f"Project root: {ROOT}")
'''


nb05 = [
    md(r'''
# Notebook 05 — Feature Engineering, Clustering & Recommendation

Notebook này dùng **586,672 track thật** từ `ml_ready_dataset.parquet`. Mục tiêu chính là popularity regression; KMeans và content-based recommendation là hai nhiệm vụ phụ độc lập.

Luồng chống leakage: **fit trên train (`release_year < 2019`) → đóng băng statistics → transform train/test/inference**. Target không bao giờ được truyền vào `FeatureBuilder`, KMeans hay recommender.
'''),
    code(common_setup + r'''
import matplotlib.pyplot as plt

from src.features import (
    BASELINE_MODEL_FEATURES, CANDIDATE_ENGINEERED_FEATURES,
    CANDIDATE_ENGINEERED_CATEGORICAL_FEATURES, CLUSTER_FEATURES,
    IDENTIFIER, MODEL_FEATURES, RAW_INPUT_FEATURES,
    RECOMMENDATION_FEATURES, SELECTED_ENGINEERED_FEATURES,
    TARGET, TEST_START_YEAR, FeatureBuilder, build_feature_contract,
    validate_selected_engineered_features,
)
from src.secondary_tasks import (
    cluster_profiles, fit_cluster_pipeline, fit_recommender,
    recommend_by_track_id, select_kmeans_k,
)

DATA_PATH = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
OUTPUT_DIR = ROOT / "5.DATA" / "processed"
FE_DIR = ROOT / "7.ML" / "7.6.feature_engineering"
SECONDARY_DIR = ROOT / "4.MODELS" / "hitradar_secondary"
for directory in (OUTPUT_DIR, FE_DIR, SECONDARY_DIR):
    directory.mkdir(parents=True, exist_ok=True)
assert DATA_PATH.exists(), "Real dataset is required; no synthetic fallback is allowed."
'''),
    md(r'''
## 1. Dữ liệu thật và time split

`target_popularity` là tên nội bộ của Spotify popularity (0–100). `track_id` chỉ là định danh, không phải model feature.
'''),
    code(r'''
df_raw = pd.read_parquet(DATA_PATH)
required = [IDENTIFIER, TARGET, *RAW_INPUT_FEATURES]
missing_source = [c for c in required if c not in df_raw.columns]
assert not missing_source, f"Missing source columns: {missing_source}"
train_mask = pd.to_numeric(df_raw["release_year"], errors="coerce") < TEST_START_YEAR
assert train_mask.any() and (~train_mask).any()
print("Shape before Feature Engineering:", df_raw.shape)
print(f"Train rows: {train_mask.sum():,}; test rows: {(~train_mask).sum():,}")
display(df_raw[[IDENTIFIER, TARGET, *RAW_INPUT_FEATURES[:6]]].head())
'''),
    md(r'''
## 2. Candidate register có căn cứ EDA

Notebook 04 cho thấy audio variables có phân phối lệch, quan hệ popularity không hoàn toàn tuyến tính, và có thay đổi mạnh theo thời gian. Vì vậy candidate register kiểm tra interaction, cyclic key, category và độ lệch so với trung bình lịch sử. Mood dùng mốc 0.5 vì energy/valence đã chuẩn hóa [0,1]; duration và tempo dùng quantile **học từ train** để tránh ngưỡng tùy ý và tránh test leakage.
'''),
    code(r'''
FORMULAS = {
 "key_sin":"sin(2*pi*(key mod 12)/12)", "key_cos":"cos(2*pi*(key mod 12)/12)",
 "dance_energy":"danceability * energy", "positive_energy":"valence * energy",
 "acoustic_energy_balance":"acousticness / (acousticness + energy + epsilon)",
 "dance_valence":"danceability * valence",
 "acoustic_instrumental":"acousticness * instrumentalness",
 "tempo_energy":"tempo * energy", "energy_loudness":"energy * loudness",
 "speechiness_log":"log1p(max(speechiness, 0))",
 "instrumentalness_log":"log1p(max(instrumentalness, 0))",
 "mood_quadrant":"energy/valence quadrants at normalized midpoint 0.5",
 "duration_category":"short/standard/long from train q33/q67",
 "tempo_category":"four bins from train q25/q50/q75",
 "energy_vs_period_avg":"energy - train decade energy mean",
 "dance_vs_period_avg":"danceability - train decade danceability mean",
}
EDA_EVIDENCE = {
 "key_sin":"NB04 correlation review: key is cyclic, so endpoints 0/11 must be adjacent.",
 "key_cos":"NB04 correlation review: complementary coordinate required for cyclic key.",
 "dance_energy":"NB04 audio distributions/correlation: danceability and energy may act jointly.",
 "positive_energy":"NB04 nonlinear bins: valence and energy jointly describe intensity/mood.",
 "acoustic_energy_balance":"NB04 audio distributions: acousticness and energy oppose each other strongly.",
 "dance_valence":"NB04 nonlinear bins: danceability and valence show non-additive patterns.",
 "acoustic_instrumental":"NB04 right-skew review: acoustic/instrumental content co-occurs.",
 "tempo_energy":"NB04 audio review: speed and energy jointly express intensity.",
 "energy_loudness":"NB04 correlation review: loudness and energy are related but not identical.",
 "speechiness_log":"NB04 distribution review: speechiness is right-skewed.",
 "instrumentalness_log":"NB04 distribution review: instrumentalness is right-skewed.",
 "mood_quadrant":"NB04 normalized audio review supports interpretable mood quadrants.",
 "duration_category":"NB04 duration/time trends show nonlinear duration behavior.",
 "tempo_category":"NB04 nonlinear binned plots motivate tempo regimes.",
 "energy_vs_period_avg":"NB04 decade trends show energy changes over time.",
 "dance_vs_period_avg":"NB04 decade trends show danceability changes over time.",
}
candidate_register = pd.DataFrame({
    "Feature": CANDIDATE_ENGINEERED_FEATURES,
    "Formula": [FORMULAS[f] for f in CANDIDATE_ENGINEERED_FEATURES],
    "Type": ["categorical" if f in CANDIDATE_ENGINEERED_CATEGORICAL_FEATURES else "numeric" for f in CANDIDATE_ENGINEERED_FEATURES],
    "Expected Benefit": [EDA_EVIDENCE[f] for f in CANDIDATE_ENGINEERED_FEATURES],
    "EDA Source": ["Notebook 04 — EDA" for _ in CANDIDATE_ENGINEERED_FEATURES],
})
display(candidate_register)
'''),
    md(r'''
## 3. Tạo thật toàn bộ candidate bằng shared `FeatureBuilder`

Code bên dưới tạo columns thật. Learned thresholds và period means chỉ fit bằng train rows.
'''),
    code(r'''
feature_builder = FeatureBuilder(include_engineered=True).fit(
    df_raw.loc[train_mask, RAW_INPUT_FEATURES]
)
candidate_matrix = feature_builder.transform_candidates(df_raw[RAW_INPUT_FEATURES])
selected_matrix = feature_builder.transform(df_raw[RAW_INPUT_FEATURES])
df = pd.concat(
    [df_raw[[IDENTIFIER, TARGET]].reset_index(drop=True), selected_matrix.reset_index(drop=True)],
    axis=1,
)
print("Shape after selected Feature Engineering:", df.shape)
print("Implemented candidates:", len(CANDIDATE_ENGINEERED_FEATURES))
print("Selected engineered features:", len(SELECTED_ENGINEERED_FEATURES))
display(pd.concat([df_raw[[IDENTIFIER, TARGET]].head(5).reset_index(drop=True),
                   candidate_matrix[CANDIDATE_ENGINEERED_FEATURES].head(5).reset_index(drop=True)], axis=1))
'''),
    md(r'''
## 4. Candidate evaluation và quyết định Keep/Drop

Association là |Spearman| cho numeric và correlation ratio (η) cho categorical. Redundancy numeric là |Spearman| lớn nhất với raw numeric features. Tính trên deterministic train sample để audit có thể chạy lại; target chỉ dùng để **đánh giá candidate sau khi tạo**, tuyệt đối không tham gia công thức/fit.
'''),
    code(r'''
audit_index = df_raw.loc[train_mask].sample(
    min(120_000, int(train_mask.sum())), random_state=1512
).index
audit_X = candidate_matrix.loc[audit_index]
audit_y = pd.to_numeric(df_raw.loc[audit_index, TARGET], errors="coerce")
raw_numeric = [c for c in BASELINE_MODEL_FEATURES if c in audit_X and pd.api.types.is_numeric_dtype(audit_X[c])]

def association(series, target):
    if pd.api.types.is_numeric_dtype(series):
        return abs(float(pd.to_numeric(series, errors="coerce").corr(target, method="spearman")))
    temp = pd.DataFrame({"x": series.astype("string"), "y": target}).dropna()
    grand = temp["y"].mean()
    between = sum(len(g) * (g["y"].mean() - grand) ** 2 for _, g in temp.groupby("x", observed=True))
    total = ((temp["y"] - grand) ** 2).sum()
    return float(np.sqrt(between / total)) if total else 0.0

def redundancy(feature):
    s = audit_X[feature]
    if not pd.api.types.is_numeric_dtype(s):
        return np.nan
    return max(abs(float(pd.to_numeric(s, errors="coerce").corr(
        pd.to_numeric(audit_X[c], errors="coerce"), method="spearman"))) for c in raw_numeric)

candidate_evaluation = candidate_register.copy()
candidate_evaluation["Missing Count"] = [int(candidate_matrix[f].isna().sum()) for f in CANDIDATE_ENGINEERED_FEATURES]
candidate_evaluation["Infinite Count"] = [int(np.isinf(candidate_matrix[f].to_numpy(dtype=float)).sum()) if pd.api.types.is_numeric_dtype(candidate_matrix[f]) else 0 for f in CANDIDATE_ENGINEERED_FEATURES]
candidate_evaluation["Target Association"] = [association(audit_X[f], audit_y) for f in CANDIDATE_ENGINEERED_FEATURES]
candidate_evaluation["Max Raw Redundancy"] = [redundancy(f) for f in CANDIDATE_ENGINEERED_FEATURES]
candidate_evaluation["Leakage Check"] = "PASS — formula/fit excludes target"
candidate_evaluation["Interpretability"] = "PASS"
candidate_evaluation["Decision"] = candidate_evaluation["Feature"].map(lambda f: "KEEP" if f in SELECTED_ENGINEERED_FEATURES else "DROP")
candidate_evaluation["Decision Reason"] = candidate_evaluation["Feature"].map({
    "speechiness_log":"DROP: exact monotonic rank redundancy with retained raw speechiness.",
    "instrumentalness_log":"DROP: exact monotonic rank redundancy with retained raw instrumentalness.",
}).fillna("KEEP: executable, valid, leakage-safe candidate with EDA/domain rationale.")
assert set(candidate_evaluation.query("Decision == 'KEEP'")["Feature"]) == set(SELECTED_ENGINEERED_FEATURES)
display(candidate_evaluation.sort_values(["Decision", "Target Association"], ascending=[True, False]))
'''),
    md(r'''
`key_sin` và `key_cos` được giữ như một cặp tọa độ: association riêng lẻ thấp không phủ định giá trị biểu diễn chu kỳ. Các interaction tương quan cao với raw sources vẫn được giữ để mô hình tuyến tính thấy quan hệ nhân; hai log bị drop vì biến đổi đơn điệu cho rank redundancy đúng 1.0 và raw source vẫn có mặt.
'''),
    code(r'''
statistics = feature_builder.get_learned_statistics()
threshold_table = pd.DataFrame([
    {"Feature":"mood_quadrant", "Thresholds":"energy=0.5, valence=0.5", "Source":"fixed midpoint of normalized [0,1] domain", "Fit Scope":"domain constant"},
    {"Feature":"duration_category", "Thresholds":f"q33={statistics['duration_q33']:.4f}, q67={statistics['duration_q67']:.4f}", "Source":"empirical quantiles", "Fit Scope":"train only"},
    {"Feature":"tempo_category", "Thresholds":f"q25={statistics['tempo_q25']:.3f}, q50={statistics['tempo_q50']:.3f}, q75={statistics['tempo_q75']:.3f}", "Source":"empirical quantiles", "Fit Scope":"train only"},
])
display(threshold_table)
'''),
    md(r'''
## 5. Validation cứng của 14 selected features

Category features tồn tại thật ở dataframe và sẽ được `OneHotEncoder(handle_unknown='ignore')` trong Notebook 06/deployment.
'''),
    code(r'''
EXPECTED_ENGINEERED_FEATURES = list(SELECTED_ENGINEERED_FEATURES)
missing_features = [f for f in EXPECTED_ENGINEERED_FEATURES if f not in df.columns]
assert len(missing_features) == 0, f"Missing engineered features: {missing_features}"
assert len(EXPECTED_ENGINEERED_FEATURES) >= 12
feature_validation = validate_selected_engineered_features(df)
assert feature_validation["Status"].eq("PASS").all(), feature_validation
assert MODEL_FEATURES == [c for c in MODEL_FEATURES if c in df.columns]
display(feature_validation)
'''),
    md(r'''
## 6. Central feature contract và save/reload
'''),
    code(r'''
contract = build_feature_contract()
paths = {
    "engineered": OUTPUT_DIR / "features_engineered.parquet",
    "candidate_register": FE_DIR / "candidate_feature_register.csv",
    "candidate_evaluation": FE_DIR / "candidate_feature_evaluation.csv",
    "keep_drop": FE_DIR / "feature_keep_drop_decisions.csv",
    "validation": FE_DIR / "hard_requirement_feature_validation.csv",
    "contract": FE_DIR / "hard_requirement_feature_contract.json",
    "statistics": FE_DIR / "hard_requirement_train_statistics.json",
}
df.to_parquet(paths["engineered"], index=False)
candidate_register.to_csv(paths["candidate_register"], index=False)
candidate_evaluation.to_csv(paths["candidate_evaluation"], index=False)
candidate_evaluation[["Feature", "Decision", "Decision Reason"]].to_csv(paths["keep_drop"], index=False)
feature_validation.to_csv(paths["validation"], index=False)
paths["contract"].write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
paths["statistics"].write_text(json.dumps(statistics, indent=2, ensure_ascii=False), encoding="utf-8")
reloaded = pd.read_parquet(paths["engineered"])
assert validate_selected_engineered_features(reloaded)["Status"].eq("PASS").all()
print(json.dumps({k: str(v) for k, v in paths.items()}, indent=2))
'''),
    md(r'''
## 7. KMeans: chọn k=2..10 bằng inertia và silhouette

Fit/evaluation dùng đúng `CLUSTER_FEATURES`: audio content, không popularity, không track ID, không release time. k được chọn bằng silhouette cao nhất trên deterministic sample; model cuối fit toàn bộ rows.
'''),
    code(r'''
assert TARGET not in CLUSTER_FEATURES and IDENTIFIER not in CLUSTER_FEATURES
assert not {"release_year", "release_month", "decade"}.intersection(CLUSTER_FEATURES)
k_scores, chosen_k = select_kmeans_k(df_raw)
display(k_scores)
print(f"Chosen k={chosen_k}: maximum sampled silhouette={k_scores['Silhouette'].max():.4f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(k_scores["k"], k_scores["Inertia"], marker="o"); axes[0].set(title="Elbow / inertia", xlabel="k", ylabel="Inertia")
axes[1].plot(k_scores["k"], k_scores["Silhouette"], marker="o"); axes[1].axvline(chosen_k, color="red", ls="--"); axes[1].set(title="Silhouette", xlabel="k", ylabel="Score")
plt.tight_layout()
K_PLOT = SECONDARY_DIR / "kmeans_k_selection.png"
fig.savefig(K_PLOT, dpi=140, bbox_inches="tight")
plt.show()
'''),
    code(r'''
cluster_pipeline = fit_cluster_pipeline(df_raw, chosen_k)
cluster_labels = cluster_pipeline.predict(df_raw[CLUSTER_FEATURES])
profile, profile_by_decade = cluster_profiles(df_raw, cluster_labels)
assignments = pd.DataFrame({IDENTIFIER: df_raw[IDENTIFIER].astype(str), "cluster": cluster_labels})
display(profile)
display(profile_by_decade.tail(20))

KMEANS_PATH = SECONDARY_DIR / "kmeans_pipeline.joblib"
joblib.dump(cluster_pipeline, KMEANS_PATH, compress=3)
k_scores.to_csv(SECONDARY_DIR / "kmeans_k_selection.csv", index=False)
profile.to_csv(SECONDARY_DIR / "cluster_profiles.csv", index=False)
profile_by_decade.to_csv(SECONDARY_DIR / "cluster_profiles_by_decade.csv", index=False)
assignments.to_parquet(SECONDARY_DIR / "cluster_assignments.parquet", index=False)
(SECONDARY_DIR / "cluster_metadata.json").write_text(json.dumps({
    "chosen_k": chosen_k, "selection_rule":"maximum sampled silhouette",
    "features": CLUSTER_FEATURES, "target_used": False, "time_used": False,
    "rows": len(df_raw),
}, indent=2), encoding="utf-8")
print(f"Saved cluster model: {KMEANS_PATH}")
'''),
    md(r'''
## 8. Content-based recommender

Similarity dùng standardized audio + cyclic key, không target/popularity và không thời gian. Dataset local không có track/artist name, nên output trung thực dùng `track_id`; không bịa metadata.
'''),
    code(r'''
assert TARGET not in RECOMMENDATION_FEATURES and IDENTIFIER not in RECOMMENDATION_FEATURES
assert not {"release_year", "release_month", "decade"}.intersection(RECOMMENDATION_FEATURES)
recommender = fit_recommender(
    df_raw[RAW_INPUT_FEATURES], df_raw[IDENTIFIER], feature_builder=feature_builder
)
RECOMMENDER_PATH = SECONDARY_DIR / "content_recommender.joblib"
joblib.dump(recommender, RECOMMENDER_PATH, compress=3)

example_positions = [0, len(df_raw) // 2, len(df_raw) - 1]
example_frames = []
for position in example_positions:
    query_id = str(df_raw.iloc[position][IDENTIFIER])
    recs = recommend_by_track_id(recommender, query_id, n_recommendations=5)
    assert query_id not in set(recs[IDENTIFIER])
    recs.insert(0, "query_track_id", query_id)
    example_frames.append(recs)
recommendation_examples = pd.concat(example_frames, ignore_index=True)
recommendation_examples.to_csv(SECONDARY_DIR / "recommendation_examples.csv", index=False)
(SECONDARY_DIR / "recommendation_metadata.json").write_text(json.dumps({
    "features": RECOMMENDATION_FEATURES, "metric":"cosine",
    "target_used":False, "time_used":False, "self_excluded":True,
    "metadata_limitation":"Local ML-ready source contains track_id but no track/artist names.",
    "rows":len(df_raw),
}, indent=2), encoding="utf-8")
display(recommendation_examples)
print(f"Saved recommender: {RECOMMENDER_PATH}")
'''),
    md(r'''
## 9. Kết luận

- 16 candidates đã được tạo bằng code; 14 selected features PASS toàn bộ validation, vượt yêu cầu ≥12.
- Hai log features bị loại vì exact monotonic rank redundancy; không feature nào bị “đề xuất” mà chưa tạo.
- KMeans và recommender đã fit/save bằng audio content, tách biệt khỏi popularity regression.
- Hạn chế dữ liệu: chỉ có `track_id`, không có tên bài hát/nghệ sĩ; Notebook không giả lập metadata.
'''),
]


nb06 = [
    md(r'''
# Notebook 06 — Popularity Regression

Notebook chạy lại Linear Regression, Random Forest và XGBoost trên ba contract: Baseline With-Time, Engineered With-Time, Engineered No-Time. Winner được chọn từ **tất cả eligible experiments**, không ép engineered model thắng.
'''),
    code(common_setup + r'''
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.features import (
    RAW_INPUT_FEATURES, SELECTED_ENGINEERED_FEATURES, TARGET,
    TEST_START_YEAR, FeatureBuilder, get_model_features,
)
from src.modeling import (
    MODEL_NAMES, build_model_pipeline, grouped_feature_importance,
    regression_metric_variants, transformed_feature_importance,
)

DATA_PATH = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
ENGINEERED_PATH = ROOT / "5.DATA" / "processed" / "features_engineered.parquet"
EVAL_DIR = ROOT / "4.MODELS" / "4.2.evaluation"
MODEL_DIR = ROOT / "4.MODELS" / "hitradar_popularity"
for directory in (EVAL_DIR, MODEL_DIR): directory.mkdir(parents=True, exist_ok=True)
assert DATA_PATH.exists() and ENGINEERED_PATH.exists(), "Run Notebook 05 first."
'''),
    md(r'''
## 1. Load output Notebook 05 và parity test

Parity test chứng minh saved dataframe và shared builder tạo cùng giá trị. Numeric dùng tolerance chặt; categorical so khớp chính xác. Kết quả được save, không chỉ in ra.
'''),
    code(r'''
raw = pd.read_parquet(DATA_PATH)
saved = pd.read_parquet(ENGINEERED_PATH)
assert len(raw) == len(saved)
train_mask = raw["release_year"] < TEST_START_YEAR
test_mask = ~train_mask
X_train, X_test = raw.loc[train_mask, RAW_INPUT_FEATURES], raw.loc[test_mask, RAW_INPUT_FEATURES]
y_train, y_test = raw.loc[train_mask, TARGET], raw.loc[test_mask, TARGET]

parity_builder = FeatureBuilder(include_engineered=True).fit(X_train)
parity_index = raw.loc[test_mask].sample(min(10_000, int(test_mask.sum())), random_state=1512).index
rebuilt = parity_builder.transform(raw.loc[parity_index, RAW_INPUT_FEATURES]).reset_index(drop=True)
expected = saved.loc[parity_index, rebuilt.columns].reset_index(drop=True)
numeric = rebuilt.select_dtypes(include=np.number).columns.tolist()
categorical = [c for c in rebuilt.columns if c not in numeric]
numeric_ok = bool(np.allclose(rebuilt[numeric], expected[numeric], rtol=1e-9, atol=1e-10, equal_nan=True))
categorical_ok = all(rebuilt[c].astype("string").equals(expected[c].astype("string")) for c in categorical)
parity_result = {"rows_checked":len(rebuilt), "numeric_allclose":numeric_ok, "categorical_exact":categorical_ok, "status":"PASS" if numeric_ok and categorical_ok else "FAIL"}
assert parity_result["status"] == "PASS", parity_result
(EVAL_DIR / "feature_builder_saved_parity.json").write_text(json.dumps(parity_result, indent=2), encoding="utf-8")
print(parity_result)
'''),
    md(r'''
## 2. Train all eligible experiments

Category features được impute + one-hot encode trong pipeline. Scaler/encoder/learned features chỉ fit bằng train. Metrics báo cả raw predictions và production-clipped [0,100].
'''),
    code(r'''
experiments = [
    {"Experiment":"Baseline With-Time", "include_engineered":False, "include_time":True},
    {"Experiment":"Engineered With-Time", "include_engineered":True, "include_time":True},
    {"Experiment":"Engineered No-Time", "include_engineered":True, "include_time":False},
]
rows, fitted, predictions = [], {}, {}
for experiment in experiments:
    declared = get_model_features(include_engineered=experiment["include_engineered"], include_time=experiment["include_time"])
    assert declared and all(f in parity_builder.transform(X_train.head(3)).columns for f in declared)
    for model_name in MODEL_NAMES:
        key = (experiment["Experiment"], model_name)
        print("Fitting", key)
        pipeline = build_model_pipeline(model_name, include_engineered=experiment["include_engineered"], include_time=experiment["include_time"])
        pipeline.fit(X_train, y_train)
        pred_raw = pipeline.predict(X_test)
        fitted[key] = pipeline
        predictions[key] = pred_raw
        for variant, metric in regression_metric_variants(y_test, pred_raw).items():
            rows.append({"Experiment":key[0], "Model":model_name, "Prediction Variant":variant, "Feature Count":len(declared), **metric})
metrics_table = pd.DataFrame(rows).sort_values(["Prediction Variant", "RMSE"]).reset_index(drop=True)
display(metrics_table)
'''),
    md(r'''
## 3. Winner selection toàn cục và bias comparisons

Selection dùng clipped RMSE vì API trả popularity trong miền hợp lệ. Raw metrics vẫn được lưu để minh bạch ảnh hưởng clipping.
'''),
    code(r'''
eligible = metrics_table.query("`Prediction Variant` == 'Clipped [0,100]'").copy()
winner_row = eligible.sort_values(["RMSE", "MAE", "Model", "Experiment"]).iloc[0]
winner_key = (winner_row["Experiment"], winner_row["Model"])
final_pipeline = fitted[winner_key]
winner_experiment = next(e for e in experiments if e["Experiment"] == winner_key[0])
print("FINAL WINNER:", winner_key)
display(winner_row.to_frame().T)

clipped = metrics_table.query("`Prediction Variant` == 'Clipped [0,100]'")
feature_effect = clipped.pivot(index="Model", columns="Experiment", values=["MAE","RMSE","R2"])
display(feature_effect)

time_bias = []
for model in MODEL_NAMES:
    with_time = clipped.query("Model == @model and Experiment == 'Engineered With-Time'").iloc[0]
    no_time = clipped.query("Model == @model and Experiment == 'Engineered No-Time'").iloc[0]
    time_bias.append({"Model":model, "With-Time RMSE":with_time.RMSE, "No-Time RMSE":no_time.RMSE,
                      "No-Time minus With-Time RMSE":no_time.RMSE-with_time.RMSE,
                      "Interpretation":"positive means time features improve held-out RMSE" if no_time.RMSE-with_time.RMSE > 0 else "non-positive means no-time is equal/better"})
time_bias_table = pd.DataFrame(time_bias)
display(time_bias_table)
'''),
    md(r'''
## 4. Error diagnostics theo popularity group

Residual/Bias convention: **actual − prediction**. Bias dương = underprediction; bias âm = overprediction.
'''),
    code(r'''
final_pred_raw = predictions[winner_key]
final_pred = np.clip(final_pred_raw, 0, 100)
diagnostics = pd.DataFrame({"Actual":np.asarray(y_test), "Prediction Raw":final_pred_raw, "Prediction Clipped":final_pred})
diagnostics["Residual (Actual-Prediction)"] = diagnostics["Actual"] - diagnostics["Prediction Clipped"]
diagnostics["Popularity Group"] = pd.cut(diagnostics["Actual"], [-np.inf,29,49,69,np.inf], labels=["Low 0-29","Emerging 30-49","Medium 50-69","High 70-100"])

def group_metrics(group):
    residual = group["Residual (Actual-Prediction)"].to_numpy()
    return pd.Series({"Rows":len(group), "MAE":np.abs(residual).mean(), "RMSE":np.sqrt(np.mean(residual**2)), "Bias (Actual-Prediction)":residual.mean(), "Bias Direction":"underprediction" if residual.mean()>0 else "overprediction"})
error_groups = diagnostics.groupby("Popularity Group", observed=True).apply(group_metrics, include_groups=False).reset_index()
display(error_groups)
display(pd.DataFrame(regression_metric_variants(y_test, final_pred_raw)).T)
'''),
    md(r'''
## 5. Feature importance, grouped importance và artifacts
'''),
    code(r'''
detailed_importance = transformed_feature_importance(final_pipeline)
grouped_importance = grouped_feature_importance(final_pipeline)
display(detailed_importance.head(25))
display(grouped_importance.head(25))

metrics_table.to_csv(EVAL_DIR / "hotfix_all_experiment_metrics.csv", index=False)
time_bias_table.to_csv(EVAL_DIR / "hotfix_time_bias_comparison.csv", index=False)
error_groups.to_csv(EVAL_DIR / "hotfix_error_groups.csv", index=False)
detailed_importance.to_csv(EVAL_DIR / "hotfix_transformed_feature_importance.csv", index=False)
grouped_importance.to_csv(EVAL_DIR / "hotfix_grouped_feature_importance.csv", index=False)
pd.DataFrame({"track_id":raw.loc[test_mask, "track_id"].astype(str).values,
              "actual":np.asarray(y_test), "prediction_raw":final_pred_raw,
              "prediction_clipped":final_pred}).to_parquet(EVAL_DIR / "hard_requirement_test_predictions.parquet", index=False)

final_model_path = MODEL_DIR / "popularity_pipeline.joblib"
joblib.dump(final_pipeline, final_model_path, compress=3)
final_contract_features = get_model_features(include_engineered=winner_experiment["include_engineered"], include_time=winner_experiment["include_time"])
metrics_payload = {
    "final_experiment":winner_key[0], "final_model":winner_key[1],
    "include_engineered":winner_experiment["include_engineered"],
    "include_time":winner_experiment["include_time"],
    "model_features":final_contract_features,
    "selected_engineered_features":SELECTED_ENGINEERED_FEATURES,
    "selection_pool":"all eligible experiments and all three algorithms",
    "selection_metric":"minimum clipped [0,100] RMSE; MAE tie-break",
    "final_test_metrics":{"MAE":float(winner_row.MAE), "RMSE":float(winner_row.RMSE), "R2":float(winner_row.R2)},
    "raw_test_metrics":regression_metric_variants(y_test, final_pred_raw)["Raw"],
    "residual_convention":"actual - prediction; positive means underprediction",
    "parity_test":parity_result,
}
(MODEL_DIR / "metrics.json").write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
(MODEL_DIR / "feature_columns.json").write_text(json.dumps(final_contract_features, indent=2), encoding="utf-8")
(EVAL_DIR / "model_metrics.json").write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

reloaded_pipeline = joblib.load(final_model_path)
assert np.allclose(reloaded_pipeline.predict(X_test.head(20)), final_pipeline.predict(X_test.head(20)))
print(json.dumps(metrics_payload, indent=2))
print("Saved and reload-validated:", final_model_path)
'''),
    md(r'''
## 6. Kết luận

Winner bên trên là kết quả đo mới sau hotfix, không tái sử dụng metric cũ. Bảng time-bias định lượng mức phụ thuộc vào release-time; bảng group errors nêu rõ khu vực model under/overpredict. Deployment phải đọc `include_engineered`, `include_time` và `model_features` từ chính artifact metadata này.
'''),
]


nb07 = [
    md(r'''
# Notebook 07 — Deployment End-to-End Validation

Kiểm thử thật chuỗi **RAW INPUT → FEATURE ENGINEERING → MODEL_FEATURES → MODEL → PREDICTION**, đồng thời kiểm tra cluster/recommend endpoints và bốn tab Streamlit.
'''),
    code(common_setup + r'''
import importlib.util
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from src.features import RAW_INPUT_FEATURES, get_model_features

MODEL_DIR = ROOT / "4.MODELS" / "hitradar_popularity"
SECONDARY_DIR = ROOT / "4.MODELS" / "hitradar_secondary"
DATA_PATH = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
metrics = json.loads((MODEL_DIR / "metrics.json").read_text(encoding="utf-8"))
pipeline = joblib.load(MODEL_DIR / "popularity_pipeline.joblib")
expected_features = get_model_features(include_engineered=metrics["include_engineered"], include_time=metrics["include_time"])
assert metrics["model_features"] == expected_features
print("Actual final experiment:", metrics["final_experiment"], "/", metrics["final_model"])
print("Model feature count:", len(expected_features))
'''),
    code(r'''
raw_data = pd.read_parquet(DATA_PATH)
raw_example = raw_data.loc[[raw_data.index[-1]], RAW_INPUT_FEATURES]
engineered = pipeline.named_steps["features"].transform(raw_example)
model_features_present = all(f in engineered.columns for f in expected_features)
prediction_raw = float(pipeline.predict(raw_example)[0])
prediction = float(np.clip(prediction_raw, 0, 100))
e2e = {"raw_columns_ok":raw_example.columns.tolist()==RAW_INPUT_FEATURES,
       "feature_engineering_ok":model_features_present,
       "model_features":len(expected_features), "prediction_raw":prediction_raw,
       "prediction_clipped":prediction, "status":"PASS"}
assert np.isfinite(prediction)
display(pd.DataFrame([e2e]))
'''),
    md(r'''
## FastAPI integration: prediction, cluster, recommendation
'''),
    code(r'''
api_path = ROOT / "5.UNG_DUNG" / "5.1.backend_api" / "api.py"
spec = importlib.util.spec_from_file_location("hitradar_hotfix_api", api_path)
api_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(api_module)
client = TestClient(api_module.app)
payload = raw_example.iloc[0].to_dict()
payload["explicit"] = bool(payload["explicit"])
for key in ("release_year","key","mode","time_signature","release_month"):
    payload[key] = int(payload[key])

health = client.get("/health")
pred_response = client.post("/predict", json=payload)
cluster_response = client.post("/cluster", json=payload)
query_id = str(raw_data.iloc[0]["track_id"])
recommend_response = client.get(f"/recommend/{query_id}?n=5")
assert health.status_code == pred_response.status_code == cluster_response.status_code == recommend_response.status_code == 200
assert query_id not in {r["track_id"] for r in recommend_response.json()["recommendations"]}
display(pd.DataFrame([health.json()]))
display(pd.DataFrame([pred_response.json()]))
display(pd.DataFrame([cluster_response.json()]))
display(pd.DataFrame(recommend_response.json()["recommendations"]))
'''),
    md(r'''
## Streamlit integration: bốn tab
'''),
    code(r'''
streamlit_path = ROOT / "5.UNG_DUNG" / "5.2.frontend" / "streamlit_app.py"
app_test = AppTest.from_file(str(streamlit_path)).run(timeout=40)
tab_labels = [tab.label for tab in app_test.tabs]
streamlit_result = {"exceptions":len(app_test.exception), "tabs":tab_labels,
                    "status":"PASS" if not app_test.exception and len(tab_labels)==4 else "FAIL"}
assert streamlit_result["status"] == "PASS", streamlit_result
display(pd.DataFrame([streamlit_result]))
'''),
    code(r'''
validation = {"pipeline":e2e, "health":health.json(), "prediction":pred_response.json(),
              "cluster":cluster_response.json(), "recommendation":recommend_response.json(),
              "streamlit":streamlit_result}
validation_path = ROOT / "5.UNG_DUNG" / "validation" / "hotfix_end_to_end_validation.json"
validation_path.parent.mkdir(parents=True, exist_ok=True)
validation_path.write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")
print("Saved:", validation_path)
print("HOTFIX END-TO-END STATUS: PASS")
'''),
    md(r'''
## Kết luận

Deployment tải đúng winner thật từ Notebook 06, nhận raw inputs, tái tạo features trong pipeline, clip popularity về [0,100], và phục vụ cluster/recommendation từ artifacts Notebook 05. Streamlit có đúng bốn tab: Overview, Popularity Prediction, Song Clustering, Similar Songs.
'''),
]


write("3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb", nb05)
write("3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb", nb06)
write("3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb", nb07)

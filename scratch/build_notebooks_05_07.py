"""Generate executable canonical notebooks 05-07 from shared production code."""

import argparse
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
    DROPPED_ENGINEERED_FEATURE_REASONS, FEATURE_KEEP_JUSTIFICATIONS,
    IDENTIFIER, MODEL_FEATURES, RAW_INPUT_FEATURES,
    RECOMMENDATION_FEATURES, SELECTED_ENGINEERED_FEATURES,
    TARGET, TARGET_ASSOCIATION_SCOPE, TEST_START_YEAR,
    FeatureBuilder, build_feature_contract, candidate_target_associations,
    selection_train_association_index,
    audit_feature_dependencies, validate_selected_engineered_features,
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

Association là |Spearman| cho numeric và correlation ratio (η) cho categorical. **Target association chỉ là bằng chứng mô tả trên Selection Train (`release_year <= 2017`)**; validation 2018 và final 2019+ labels bị loại khỏi phép tính. Chỉ số này không phải quy tắc Keep/Drop tự động. Redundancy numeric là |Spearman| lớn nhất với raw numeric features trên cùng deterministic sample.
'''),
    code(r'''
association_mask = pd.to_numeric(df_raw["release_year"], errors="coerce") <= 2017
association_train = df_raw.loc[association_mask].copy()
association_builder = FeatureBuilder(include_engineered=True).fit(
    association_train[RAW_INPUT_FEATURES]
)
association_candidate_matrix = association_builder.transform_candidates(
    association_train[RAW_INPUT_FEATURES]
)
audit_index = selection_train_association_index(association_train)
assert association_mask.loc[audit_index].all()
assert association_builder.fit_row_count_ == int(association_mask.sum())
audit_X = association_candidate_matrix.loc[audit_index]
raw_numeric = [c for c in BASELINE_MODEL_FEATURES if c in audit_X and pd.api.types.is_numeric_dtype(audit_X[c])]

def redundancy(feature):
    s = audit_X[feature]
    if not pd.api.types.is_numeric_dtype(s):
        return np.nan
    return max(abs(float(pd.to_numeric(s, errors="coerce").corr(
        pd.to_numeric(audit_X[c], errors="coerce"), method="spearman"))) for c in raw_numeric)

dependency_audit = audit_feature_dependencies()
assert dependency_audit["Status"].eq("PASS").all(), dependency_audit
dependency_status = dependency_audit.set_index("Feature")["Status"]

candidate_evaluation = candidate_register.copy()
candidate_evaluation["Missing Count"] = [int(candidate_matrix[f].isna().sum()) for f in CANDIDATE_ENGINEERED_FEATURES]
candidate_evaluation["Infinite Count"] = [int(np.isinf(candidate_matrix[f].to_numpy(dtype=float)).sum()) if pd.api.types.is_numeric_dtype(candidate_matrix[f]) else 0 for f in CANDIDATE_ENGINEERED_FEATURES]
association_evidence = candidate_target_associations(
    association_train, association_candidate_matrix
)
assert association_evidence["Target Association Scope"].eq(TARGET_ASSOCIATION_SCOPE).all()
assert association_evidence["Target Association Rows"].eq(len(audit_index)).all()
candidate_evaluation = candidate_evaluation.merge(
    association_evidence, on="Feature", validate="one_to_one"
)
candidate_evaluation["Target Association Builder Fit Scope"] = TARGET_ASSOCIATION_SCOPE
candidate_evaluation["Target Association Builder Fit Rows"] = association_builder.fit_row_count_
candidate_evaluation["Max Raw Redundancy"] = [redundancy(f) for f in CANDIDATE_ENGINEERED_FEATURES]
candidate_evaluation["Leakage Audit"] = candidate_evaluation["Feature"].map(
    lambda f: "Automated Dependency PASS" if dependency_status[f] == "PASS" else "Automated Dependency FAIL"
)
candidate_evaluation["Interpretability"] = "Design Audit PASS"

def decide_candidate(row):
    feature = row["Feature"]
    if row["Missing Count"] or row["Infinite Count"]:
        return "DROP", "DROP: executable validation failed due to missing/infinite values."
    if row["Leakage Audit"] != "Automated Dependency PASS":
        return "DROP", "DROP: forbidden or unknown dependency detected."
    if feature in DROPPED_ENGINEERED_FEATURE_REASONS:
        assert row["Max Raw Redundancy"] >= 0.999, (
            f"Evidence-backed drop threshold not met for {feature}: {row['Max Raw Redundancy']}"
        )
        return "DROP", (
            DROPPED_ENGINEERED_FEATURE_REASONS[feature]
            + f" Measured selection-train |Spearman|={row['Max Raw Redundancy']:.6f}."
        )
    return "KEEP", FEATURE_KEEP_JUSTIFICATIONS[feature]

decisions = candidate_evaluation.apply(decide_candidate, axis=1)
candidate_evaluation["Decision"] = [decision for decision, _ in decisions]
candidate_evaluation["Decision Reason"] = [reason for _, reason in decisions]
assert set(candidate_evaluation.query("Decision == 'KEEP'")["Feature"]) == set(SELECTED_ENGINEERED_FEATURES)
assert len(SELECTED_ENGINEERED_FEATURES) >= 12
print(f"Target Association Scope: {TARGET_ASSOCIATION_SCOPE}")
print(f"Target Association Rows: {len(audit_index):,}")
print(f"Target Association Builder Fit Rows: {association_builder.fit_row_count_:,}")
display(candidate_evaluation.sort_values(["Decision", "Target Association"], ascending=[True, False]))
display(dependency_audit)
'''),
    md(r'''
`key_sin` và `key_cos` được giữ như một cặp tọa độ: association riêng lẻ thấp không phủ định giá trị biểu diễn chu kỳ. Interaction tương quan cao không bị mô tả sai là “low redundancy”; mỗi feature được giữ vì biểu diễn nonlinear/contextual cụ thể. Hai log chỉ bị drop sau khi selection-train audit đo lại redundancy và vượt ngưỡng 0.999.
'''),
    code(r'''
statistics = feature_builder.get_learned_statistics()
threshold_table = pd.DataFrame([
    {"Feature":"mood_quadrant", "Thresholds":"energy=0.5, valence=0.5", "Source":"fixed midpoint of normalized [0,1] domain", "Fit Scope":"domain constant"},
    {"Feature":"duration_category", "Thresholds":f"q33={statistics['duration_q33']:.4f}, q67={statistics['duration_q67']:.4f}", "Source":"empirical quantiles", "Fit Scope":"train only"},
    {"Feature":"tempo_category", "Thresholds":f"q25={statistics['tempo_q25']:.3f}, q50={statistics['tempo_q50']:.3f}, q75={statistics['tempo_q75']:.3f}", "Source":"empirical quantiles", "Fit Scope":"train only"},
])
display(threshold_table)

# Executable learned-stat immutability and target-independence checks.
stats_before = feature_builder.get_learned_statistics()
probe = df_raw.loc[~train_mask, RAW_INPUT_FEATURES].head(20).copy()
probe["energy"] = 0.0
probe["danceability"] = 0.0
feature_builder.transform(probe)
stats_after = feature_builder.get_learned_statistics()
assert stats_before == stats_after

fit_probe = df_raw.loc[train_mask, RAW_INPUT_FEATURES].head(20_000)
target_probe = df_raw.loc[fit_probe.index, TARGET]
builder_y_a = FeatureBuilder().fit(fit_probe, target_probe)
builder_y_b = FeatureBuilder().fit(fit_probe, target_probe.iloc[::-1].to_numpy())
target_independent = builder_y_a.get_learned_statistics() == builder_y_b.get_learned_statistics()
assert target_independent

# The descriptive audit builder is fit only on <=2017. Later raw-feature
# distribution changes cannot alter its learned statistics when scope is reapplied.
validation_shifted = df_raw.copy()
validation_shifted.loc[validation_shifted["release_year"] == 2018, ["energy", "tempo"]] = [0.0, 1.0]
final_shifted = df_raw.copy()
final_shifted.loc[final_shifted["release_year"] >= 2019, ["energy", "tempo"]] = [1.0, 300.0]
association_stats = association_builder.get_learned_statistics()
validation_shifted_stats = FeatureBuilder().fit(
    validation_shifted.loc[association_mask, RAW_INPUT_FEATURES]
).get_learned_statistics()
final_shifted_stats = FeatureBuilder().fit(
    final_shifted.loc[association_mask, RAW_INPUT_FEATURES]
).get_learned_statistics()
assert association_stats == validation_shifted_stats == final_shifted_stats
immutability_result = {
    "transform_preserves_learned_statistics": stats_before == stats_after,
    "statistics_independent_of_y_values": target_independent,
    "association_builder_fit_scope": TARGET_ASSOCIATION_SCOPE,
    "association_builder_fit_rows": association_builder.fit_row_count_,
    "later_raw_distribution_changes_preserve_association_statistics": True,
    "fit_design_note": "sklearn may pass y for API compatibility; FeatureBuilder.fit never reads y",
    "status": "PASS",
}
print(immutability_result)
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
    "validation": FE_DIR / "feature_validation.csv",
    "contract": FE_DIR / "feature_contract.json",
    "statistics": FE_DIR / "train_statistics.json",
    "dependency_audit": FE_DIR / "feature_dependency_leakage_audit.csv",
    "immutability": FE_DIR / "train_stat_immutability.json",
}
df.to_parquet(paths["engineered"], index=False)
candidate_register.to_csv(paths["candidate_register"], index=False)
candidate_evaluation.to_csv(paths["candidate_evaluation"], index=False)
candidate_evaluation[["Feature", "Decision", "Decision Reason"]].to_csv(paths["keep_drop"], index=False)
feature_validation.to_csv(paths["validation"], index=False)
paths["contract"].write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
paths["statistics"].write_text(json.dumps(statistics, indent=2, ensure_ascii=False), encoding="utf-8")
dependency_audit.to_csv(paths["dependency_audit"], index=False)
paths["immutability"].write_text(json.dumps(immutability_result, indent=2), encoding="utf-8")
reloaded = pd.read_parquet(paths["engineered"])
assert validate_selected_engineered_features(reloaded)["Status"].eq("PASS").all()
assert len(CANDIDATE_ENGINEERED_FEATURES) == contract["candidate_engineered_feature_count"]
assert len(SELECTED_ENGINEERED_FEATURES) == contract["selected_engineered_feature_count"]
assert all(feature in reloaded.columns for feature in contract["selected_engineered_features"])
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
print("Interpretation: this score indicates modest, not clearly separated, audio clusters.")

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
# Notebook 06 — Leakage-Safe Temporal Model Selection

Protocol: **Selection Train (`release_year <= 2017`) → Validation (`2018`) → lock configuration → refit from scratch on Development (`<2019`) → Final Test (`>=2019`) exactly once**. Final-test performance cannot change the locked winner. Trong lần chạy Round 2 đã hiệu chỉnh, 2019+ không được dùng để chọn winner; tuy nhiên chính giai đoạn này đã được xem trong một vòng phát triển trước, nên không được hiểu là test set chưa từng được quan sát trong toàn bộ lịch sử dự án.
'''),
    code(common_setup + r'''
from datetime import datetime, timezone
import matplotlib.pyplot as plt

from src.evaluation import (
    DEVELOPMENT_SCOPE, EVALUATION_SCOPE_LABEL, FINAL_TEST_SCOPE,
    FIT_SCOPE_LABEL, SELECTION_TRAIN_SCOPE, VALIDATION_SCOPE,
    select_validation_winner, temporal_masks, write_winner_lock,
)
from src.features import (
    RAW_INPUT_FEATURES, SELECTED_ENGINEERED_FEATURES, TARGET,
    FeatureBuilder, get_model_features,
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
## 1. Partition validation and development parity

Trong lần chạy Round 2 đã hiệu chỉnh, labels 2019+ không được nạp vào biến chọn mô hình; trước khi lock chỉ hiển thị số dòng. Đây là phạm vi của bằng chứng lock trong Round 2, không phải khẳng định rằng giai đoạn 2019+ chưa từng được kiểm tra trong lịch sử dự án.
'''),
    code(r'''
raw = pd.read_parquet(DATA_PATH)
saved = pd.read_parquet(ENGINEERED_PATH)
assert len(raw) == len(saved)
masks = temporal_masks(raw)

partition_rows = pd.DataFrame([
    {"Partition":"Selection Train", "Scope":SELECTION_TRAIN_SCOPE, "Rows":int(masks["selection_train"].sum())},
    {"Partition":"Validation", "Scope":VALIDATION_SCOPE, "Rows":int(masks["validation"].sum())},
    {"Partition":"Development", "Scope":DEVELOPMENT_SCOPE, "Rows":int(masks["development"].sum())},
    {"Partition":"Final Test", "Scope":FINAL_TEST_SCOPE, "Rows":int(masks["final_test"].sum())},
])
assert partition_rows.set_index("Partition").loc["Validation", "Rows"] >= 1000
display(partition_rows)

prelock_target_summary = pd.DataFrame({
    "Selection Train": raw.loc[masks["selection_train"], TARGET].describe(),
    "Validation 2018": raw.loc[masks["validation"], TARGET].describe(),
    "Development": raw.loc[masks["development"], TARGET].describe(),
}).T
display(prelock_target_summary)
print("Final Test target summary: deferred until after winner lock.")

X_selection = raw.loc[masks["selection_train"], RAW_INPUT_FEATURES]
y_selection = raw.loc[masks["selection_train"], TARGET]
X_validation = raw.loc[masks["validation"], RAW_INPUT_FEATURES]
y_validation = raw.loc[masks["validation"], TARGET]
X_development = raw.loc[masks["development"], RAW_INPUT_FEATURES]
y_development = raw.loc[masks["development"], TARGET]

parity_builder = FeatureBuilder(include_engineered=True).fit(X_development)
parity_index = raw.loc[masks["validation"]].sample(min(10_000, int(masks["validation"].sum())), random_state=1512).index
rebuilt = parity_builder.transform(raw.loc[parity_index, RAW_INPUT_FEATURES]).reset_index(drop=True)
expected = saved.loc[parity_index, rebuilt.columns].reset_index(drop=True)
numeric = rebuilt.select_dtypes(include=np.number).columns.tolist()
categorical = [c for c in rebuilt.columns if c not in numeric]
numeric_ok = bool(np.allclose(rebuilt[numeric], expected[numeric], rtol=1e-9, atol=1e-10, equal_nan=True))
categorical_ok = all(rebuilt[c].astype("string").equals(expected[c].astype("string")) for c in categorical)
parity_result = {"rows_checked":len(rebuilt), "fit_scope":DEVELOPMENT_SCOPE,
                 "numeric_allclose":numeric_ok, "categorical_exact":categorical_ok,
                 "status":"PASS" if numeric_ok and categorical_ok else "FAIL"}
assert parity_result["status"] == "PASS", parity_result
(EVAL_DIR / "feature_builder_saved_parity.json").write_text(json.dumps(parity_result, indent=2), encoding="utf-8")
print(parity_result)
'''),
    md(r'''
## 2. Phase A — fit nine candidates on Selection Train; evaluate only Validation 2018

All category encoders, imputers, scalers, FeatureBuilder statistics, and estimators are fit only on selection-train rows. Both raw and deployed clipped metrics are retained.
'''),
    code(r'''
experiments = [
    {"Experiment":"Baseline With-Time", "include_engineered":False, "include_time":True},
    {"Experiment":"Engineered With-Time", "include_engineered":True, "include_time":True},
    {"Experiment":"Engineered No-Time", "include_engineered":True, "include_time":False},
]
selection_rows = []
for experiment in experiments:
    declared = get_model_features(include_engineered=experiment["include_engineered"], include_time=experiment["include_time"])
    for model_name in MODEL_NAMES:
        print("Selection fit:", experiment["Experiment"], "/", model_name)
        candidate = build_model_pipeline(model_name, include_engineered=experiment["include_engineered"], include_time=experiment["include_time"])
        candidate.fit(X_selection, y_selection)
        assert candidate.named_steps["features"].fit_row_count_ == len(X_selection)
        validation_pred_raw = candidate.predict(X_validation)
        for variant, metric in regression_metric_variants(y_validation, validation_pred_raw).items():
            selection_rows.append({
                "Experiment":experiment["Experiment"], "Model":model_name,
                "Prediction Variant":variant, "Feature Count":len(declared), **metric,
                "Fit Scope":FIT_SCOPE_LABEL, "Evaluation Scope":EVALUATION_SCOPE_LABEL,
            })
selection_metrics = pd.DataFrame(selection_rows).sort_values(
    ["Prediction Variant", "RMSE", "MAE", "Experiment", "Model"], kind="mergesort"
).reset_index(drop=True)
SELECTION_METRICS_PATH = EVAL_DIR / "model_selection_validation_metrics.csv"
selection_metrics.to_csv(SELECTION_METRICS_PATH, index=False)
display(selection_metrics)
'''),
    md(r'''
## 3. Lock winner from validation only

The winner is the minimum clipped validation RMSE, then MAE, then deterministic lexical tie-break. The lock is written before final-test labels or predictions are accessed.
'''),
    code(r'''
winner_row = select_validation_winner(selection_metrics)
winner_experiment = next(e for e in experiments if e["Experiment"] == winner_row["Experiment"])
WINNER_LOCK_PATH = MODEL_DIR / "selection_winner_lock.json"
winner_lock = write_winner_lock(
    WINNER_LOCK_PATH, winner=winner_row,
    validation_metrics_path=SELECTION_METRICS_PATH,
    include_engineered=winner_experiment["include_engineered"],
    include_time=winner_experiment["include_time"],
)
assert winner_lock["final_test_labels_observed_before_round2_lock"] is False
assert winner_lock["historically_never_observed_claim"] is False
print("LOCKED WINNER:", winner_lock["selection_winner_experiment"], "/", winner_lock["selection_winner_model"])
display(winner_row.to_frame().T)

clipped_validation = selection_metrics.query("`Prediction Variant` == 'Clipped [0,100]'")
time_bias_rows = []
for model_name in MODEL_NAMES:
    with_time = clipped_validation.query("Model == @model_name and Experiment == 'Engineered With-Time'").iloc[0]
    no_time = clipped_validation.query("Model == @model_name and Experiment == 'Engineered No-Time'").iloc[0]
    delta = float(no_time.RMSE - with_time.RMSE)
    time_bias_rows.append({"Model":model_name, "Evaluation Scope":EVALUATION_SCOPE_LABEL,
        "With-Time RMSE":float(with_time.RMSE), "No-Time RMSE":float(no_time.RMSE),
        "No-Time minus With-Time RMSE":delta,
        "Interpretation":"positive means time features improved validation RMSE" if delta > 0 else "non-positive means no-time was equal/better"})
time_bias_table = pd.DataFrame(time_bias_rows)
time_bias_table.to_csv(EVAL_DIR / "validation_time_bias_comparison.csv", index=False)
display(time_bias_table)
'''),
    md(r'''
## 4. Phase B — refit the locked configuration from scratch on all Development rows

Nothing fitted during Phase A is reused. Feature medians, thresholds, decade statistics, imputer, scaler, encoder, and estimator are all refit on `release_year < 2019`.
'''),
    code(r'''
final_pipeline = build_model_pipeline(
    winner_lock["selection_winner_model"],
    include_engineered=winner_lock["include_engineered"],
    include_time=winner_lock["include_time"],
)
final_pipeline.fit(X_development, y_development)
assert final_pipeline.named_steps["features"].fit_row_count_ == len(X_development)
final_model_path = MODEL_DIR / "popularity_pipeline.joblib"
joblib.dump(final_pipeline, final_model_path, compress=3)
print(f"Final refit rows: {len(X_development):,}; scope: {DEVELOPMENT_SCOPE}")
'''),
    md(r'''
## 5. Phase C — evaluate Final Test exactly once after lock and refit

The locked winner is not reconsidered after these results. Raw metrics describe direct model output; clipped metrics match deployed API behavior.
'''),
    code(r'''
assert WINNER_LOCK_PATH.exists() and final_model_path.exists()
X_final_test = raw.loc[masks["final_test"], RAW_INPUT_FEATURES]
y_final_test = raw.loc[masks["final_test"], TARGET]
print("Final Test target distribution (first observed after lock):")
display(y_final_test.describe().to_frame().T)

final_pred_raw = final_pipeline.predict(X_final_test)  # the one final-test prediction call
final_test_evaluation_count = 1
final_pred_clipped = np.clip(final_pred_raw, 0, 100)
metric_variants = regression_metric_variants(y_final_test, final_pred_raw)
display(pd.DataFrame(metric_variants).T)

diagnostics = pd.DataFrame({"Actual":np.asarray(y_final_test), "Prediction Raw":final_pred_raw,
                            "Prediction Clipped":final_pred_clipped})
diagnostics["Residual (Actual-Prediction)"] = diagnostics["Actual"] - diagnostics["Prediction Clipped"]
diagnostics["Popularity Group"] = pd.cut(diagnostics["Actual"], [-np.inf,29,49,69,np.inf],
    labels=["Low 0-29","Emerging 30-49","Medium 50-69","High 70-100"])

def group_metrics(group):
    residual = group["Residual (Actual-Prediction)"].to_numpy()
    bias = residual.mean()
    return pd.Series({"Rows":len(group), "MAE":np.abs(residual).mean(),
        "RMSE":np.sqrt(np.mean(residual**2)), "Bias (Actual-Prediction)":bias,
        "Bias Direction":"underprediction" if bias > 0 else "overprediction" if bias < 0 else "neutral"})

error_groups = diagnostics.groupby("Popularity Group", observed=True).apply(group_metrics, include_groups=False).reset_index()
display(error_groups)

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].scatter(diagnostics["Actual"], diagnostics["Prediction Clipped"], s=5, alpha=.2)
axes[0].plot([0,100],[0,100], color="red", ls="--"); axes[0].set(title="Actual vs clipped prediction", xlabel="Actual", ylabel="Prediction")
axes[1].hist(diagnostics["Residual (Actual-Prediction)"], bins=50); axes[1].set(title="Residual distribution", xlabel="Actual - prediction")
axes[2].scatter(diagnostics["Prediction Clipped"], diagnostics["Residual (Actual-Prediction)"], s=5, alpha=.2)
axes[2].axhline(0, color="red", ls="--"); axes[2].set(title="Residual vs prediction", xlabel="Prediction", ylabel="Actual - prediction")
plt.tight_layout(); fig.savefig(EVAL_DIR / "final_test_diagnostics.png", dpi=140, bbox_inches="tight"); plt.show()
'''),
    md(r'''
## 6. Save canonical artifacts and reload parity

Feature importance is descriptive of the locked, development-fitted model; it is not causal evidence.
'''),
    code(r'''
detailed_importance = transformed_feature_importance(final_pipeline)
grouped_importance = grouped_feature_importance(final_pipeline)
display(detailed_importance.head(25)); display(grouped_importance.head(25))

error_groups.to_csv(EVAL_DIR / "final_error_groups.csv", index=False)
detailed_importance.to_csv(EVAL_DIR / "final_transformed_feature_importance.csv", index=False)
grouped_importance.to_csv(EVAL_DIR / "final_grouped_feature_importance.csv", index=False)
pd.DataFrame({"track_id":raw.loc[masks["final_test"], "track_id"].astype(str).values,
              "actual":np.asarray(y_final_test), "prediction_raw":final_pred_raw,
              "prediction_clipped":final_pred_clipped}).to_parquet(EVAL_DIR / "final_test_predictions.parquet", index=False)
partition_rows.to_csv(EVAL_DIR / "temporal_partition_rows.csv", index=False)

final_contract_features = get_model_features(
    include_engineered=winner_lock["include_engineered"], include_time=winner_lock["include_time"]
)
final_metrics = {
    "selection_protocol":winner_lock["selection_protocol"],
    "selection_winner_experiment":winner_lock["selection_winner_experiment"],
    "selection_winner_model":winner_lock["selection_winner_model"],
    "winner_locked_at_utc":winner_lock["locked_at_utc"],
    "winner_locked_before_final_test":True,
    "include_engineered":winner_lock["include_engineered"],
    "include_time":winner_lock["include_time"],
    "model_features":final_contract_features,
    "selected_engineered_features":SELECTED_ENGINEERED_FEATURES,
    "final_refit_scope":DEVELOPMENT_SCOPE,
    "final_refit_rows":len(X_development),
    "feature_builder_fit_rows":final_pipeline.named_steps["features"].fit_row_count_,
    "final_test_scope":FINAL_TEST_SCOPE,
    "final_test_rows":len(X_final_test),
    "final_test_evaluation_count":final_test_evaluation_count,
    "final_test_evaluated_at_utc":datetime.now(timezone.utc).isoformat(),
    "raw_test_metrics":metric_variants["Raw"],
    "clipped_test_metrics":metric_variants["Clipped [0,100]"],
    "deployed_prediction_variant":"Clipped [0,100]",
    "residual_convention":"actual - prediction; positive means underprediction",
    "feature_parity":parity_result,
    "validation_metrics_artifact":SELECTION_METRICS_PATH.name,
    "winner_lock_artifact":WINNER_LOCK_PATH.name,
}
FINAL_METRICS_PATH = MODEL_DIR / "final_test_metrics.json"
FINAL_METRICS_PATH.write_text(json.dumps(final_metrics, indent=2), encoding="utf-8")

reloaded_pipeline = joblib.load(final_model_path)
reload_probe = X_final_test.head(20)
reload_ok = bool(np.allclose(reloaded_pipeline.predict(reload_probe), final_pipeline.predict(reload_probe)))
reload_result = {"rows_checked":len(reload_probe), "prediction_allclose":reload_ok, "status":"PASS" if reload_ok else "FAIL"}
assert reload_ok
(EVAL_DIR / "pipeline_reload_parity.json").write_text(json.dumps(reload_result, indent=2), encoding="utf-8")
print(json.dumps(final_metrics, indent=2))
print("Winner remains locked regardless of final-test performance.")
'''),
    md(r'''
## 7. Conclusion

The selection table contains validation-2018 evidence only. The final pipeline configuration equals the persisted lock, was refit on all pre-2019 development data, and then evaluated on the 2019+ horizon without changing the winner. The corrected Round-2 pipeline did not use that horizon for winner selection; however, the same horizon had been inspected during an earlier development iteration, so it is not a historically never-observed test set.
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

from src.features import CLUSTER_FEATURES, RAW_INPUT_FEATURES, get_model_features
from src.prediction_policy import (
    FINAL_HOLDOUT_MAX_YEAR, OBSERVED_DATA_MAX_YEAR,
    PRODUCT_SUPPORT_END_YEAR, prediction_support_status,
)

MODEL_DIR = ROOT / "4.MODELS" / "hitradar_popularity"
SECONDARY_DIR = ROOT / "4.MODELS" / "hitradar_secondary"
DATA_PATH = ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet"
metrics = json.loads((MODEL_DIR / "final_test_metrics.json").read_text(encoding="utf-8"))
pipeline = joblib.load(MODEL_DIR / "popularity_pipeline.joblib")
expected_features = get_model_features(include_engineered=metrics["include_engineered"], include_time=metrics["include_time"])
assert metrics["model_features"] == expected_features
estimator_name = pipeline.named_steps["model"].__class__.__name__
expected_estimator = {"Linear Regression":"LinearRegression", "Random Forest":"RandomForestRegressor", "XGBoost":"XGBRegressor"}[metrics["selection_winner_model"]]
assert estimator_name == expected_estimator
assert pipeline.named_steps["features"].fit_row_count_ == metrics["final_refit_rows"]
print("Locked final configuration:", metrics["selection_winner_experiment"], "/", metrics["selection_winner_model"])
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
spec = importlib.util.spec_from_file_location("hitradar_round4_api", api_path)
api_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(api_module)
client = TestClient(api_module.app)
payload = raw_example.iloc[0].to_dict()
payload["explicit"] = bool(payload["explicit"])
for key in ("release_year","key","mode","time_signature","release_month"):
    payload[key] = int(payload[key])

health = client.get("/health")
pred_response = client.post("/predict", json=payload)
payload_2020 = dict(payload, release_year=2020)
payload_2026 = dict(payload, release_year=2026)
pred_2020 = client.post("/predict", json=payload_2020)
pred_2026 = client.post("/predict", json=payload_2026)
cluster_payload = {feature: payload[feature] for feature in CLUSTER_FEATURES}
cluster_response = client.post("/cluster", json=cluster_payload)
query_id = str(raw_data.iloc[0]["track_id"])
recommend_response = client.get(f"/recommend/{query_id}?n=5")
assert health.status_code == pred_response.status_code == pred_2020.status_code == pred_2026.status_code == cluster_response.status_code == recommend_response.status_code == 200
assert health.json()["model_ready"] and health.json()["cluster_ready"] and health.json()["recommender_ready"]
assert abs(pred_response.json()["predicted_popularity"] - prediction) < 0.001
assert pred_2020.json()["temporal_extrapolation"] is False
assert pred_2020.json()["prediction_support_status"] == "within_product_support"
assert pred_2026.json()["temporal_extrapolation"] is True
assert pred_2026.json()["support_note"]
assert pred_2026.json()["product_support_end_year"] == PRODUCT_SUPPORT_END_YEAR
assert pred_2026.json()["observed_data_max_year"] == OBSERVED_DATA_MAX_YEAR
assert pred_2026.json()["final_holdout_max_year"] == FINAL_HOLDOUT_MAX_YEAR
direct_2026 = float(np.clip(pipeline.predict(pd.DataFrame([payload_2026])[RAW_INPUT_FEATURES])[0], 0, 100))
assert abs(pred_2026.json()["predicted_popularity"] - direct_2026) < 0.001
assert query_id not in {r["track_id"] for r in recommend_response.json()["recommendations"]}
display(pd.DataFrame([health.json()]))
display(pd.DataFrame([pred_response.json()]))
display(pd.DataFrame([pred_2020.json(), pred_2026.json()]))
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
release_year_input = next(item for item in app_test.number_input if item.label == "Release year")
warnings_2020 = [warning.value for warning in app_test.warning]
future_app = release_year_input.set_value(2026).run(timeout=40)
warnings_2026 = [warning.value for warning in future_app.warning]
streamlit_result = {
    "exceptions":len(app_test.exception) + len(future_app.exception), "tabs":tab_labels,
    "year_2020_warning_count":len(warnings_2020),
    "year_2026_warning_count":len(warnings_2026),
    "year_2026_warning":warnings_2026[0] if warnings_2026 else "",
    "status":"PASS" if (
        not app_test.exception and not future_app.exception and len(tab_labels)==4
        and not warnings_2020 and warnings_2026
        and "product support cutoff" in warnings_2026[0]
    ) else "FAIL",
}
assert streamlit_result["status"] == "PASS", streamlit_result
display(pd.DataFrame([streamlit_result]))
'''),
    code(r'''
validation = {"pipeline":e2e, "api_direct_prediction_parity":True,
              "prediction_support_policy":{
                  "product_support_end_year":PRODUCT_SUPPORT_END_YEAR,
                  "observed_data_max_year":OBSERVED_DATA_MAX_YEAR,
                  "final_holdout_max_year":FINAL_HOLDOUT_MAX_YEAR,
                  "year_2020":pred_2020.json(), "year_2026":pred_2026.json(),
                  "warning_does_not_change_prediction":True,
                  "status":"PASS"},
              "loaded_estimator":estimator_name,
              "metadata_winner_model":metrics["selection_winner_model"],
              "health":health.json(), "prediction":pred_response.json(),
              "cluster":cluster_response.json(), "recommendation":recommend_response.json(),
              "streamlit":streamlit_result}
validation_path = ROOT / "5.UNG_DUNG" / "validation" / "round4_end_to_end_validation.json"
validation_path.parent.mkdir(parents=True, exist_ok=True)
validation_path.write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")
print("Saved:", validation_path)
print("ROUND 4 END-TO-END STATUS: PASS")
'''),
    md(r'''
## Kết luận

Deployment tải đúng winner đã lock từ Notebook 06, nhận raw inputs, tái tạo features trong pipeline, clip popularity về [0,100], và phục vụ cluster/recommendation từ artifacts Notebook 05. Dự đoán sau 2020 vẫn được phép nhưng được đánh dấu là ngoại suy theo thời gian; cảnh báo không thay đổi giá trị dự đoán. Streamlit có đúng bốn tab: Overview, Popularity Prediction, Song Clustering, Similar Songs.
'''),
]


parser = argparse.ArgumentParser()
parser.add_argument(
    "--only",
    default="05,06,07",
    help="Comma-separated notebook numbers to regenerate (default: 05,06,07).",
)
requested = {item.strip() for item in parser.parse_args().only.split(",")}
if "05" in requested:
    write("3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb", nb05)
if "06" in requested:
    write("3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb", nb06)
if "07" in requested:
    write("3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb", nb07)

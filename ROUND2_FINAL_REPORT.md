# HitRadar Round 2 — Final Evaluation and Cleanup Report

Generated from canonical artifacts; no metric below is manually entered.

## A. Canonical files modified

- `src/features.py`, `src/evaluation.py`
- `3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb`
- `3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb`
- `3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb`
- `5.UNG_DUNG/5.1.backend_api/api.py`, `5.UNG_DUNG/5.1.backend_api/models/prediction.py`
- `5.UNG_DUNG/5.2.frontend/streamlit_app.py`
- `5.UNG_DUNG/5.3.config/requirements.txt`, `5.UNG_DUNG/5.3.config/RUNTIME_ENVIRONMENT.md`
- `tests/test_feature_pipeline.py`, `.gitignore`
- `scratch/execute_notebook.py`, `scratch/build_notebooks_05_07.py`, `scratch/copy_round2_review.ps1`
- `9.SCRIPTS/run_round2_tests.py`, `9.SCRIPTS/generate_round2_report.py`

Revalidated without unnecessary Round-2 rewrites: `src/modeling.py`, `src/secondary_tasks.py`.

## B. Archived stale files

66 pre-Round-2 project files were moved under `10.ARCHIVE/pre_round2_20260813`; 75 old flat-review copies were moved under `10.ARCHIVE/review_round1_flat`. Active production and review directories contain only canonical current artifacts. Archived project paths include:

- `ROUND1_HOTFIX_REPORT.md`
- `canonical_before_round2/05_feature_engineering_round1.ipynb`
- `canonical_before_round2/06_machine_learning_round1.ipynb`
- `canonical_before_round2/07_ai_deployment_round1.ipynb`
- `canonical_before_round2/api_round1.py`
- `canonical_before_round2/features_round1.py`
- `canonical_before_round2/modeling_round1.py`
- `canonical_before_round2/prediction_round1.py`
- `canonical_before_round2/secondary_tasks_round1.py`
- `canonical_before_round2/streamlit_app_round1.py`
- `deployment_validation/hard_requirement_deployment_smoke_test.json`
- `deployment_validation/hotfix_end_to_end_validation.json`
- `evaluation/feature_builder_saved_parity.json`
- `evaluation/feature_importance.json`
- `evaluation/hard_requirement_test_predictions.parquet`
- `evaluation/hotfix_all_experiment_metrics.csv`
- `evaluation/hotfix_error_groups.csv`
- `evaluation/hotfix_grouped_feature_importance.csv`
- `evaluation/hotfix_time_bias_comparison.csv`
- `evaluation/hotfix_transformed_feature_importance.csv`
- `evaluation/model_metrics.json`
- `feature_engineering/audio_interaction_ablation_results.json`
- `feature_engineering/baseline_feature_set.json`
- `feature_engineering/baseline_feature_validation.json`
- `feature_engineering/baseline_metrics.json`
- `feature_engineering/baseline_model_config.json`
- `feature_engineering/baseline_validation_predictions.parquet`
- `feature_engineering/candidate_feature_evaluation.csv`
- `feature_engineering/candidate_feature_register.csv`
- `feature_engineering/duration_feature_ablation_results.json`
- `feature_engineering/duration_thresholds.json`
- `feature_engineering/feature_2_3_closure_gate.json`
- `feature_engineering/feature_2_3_generation_context.json`
- `feature_engineering/feature_2_3_validation_results.json`
- `feature_engineering/feature_2_4_input_contract.json`
- `feature_engineering/feature_ablation_results.json`
- `feature_engineering/feature_engineering_pipeline.joblib`
- `feature_engineering/feature_engineering_pipeline_manifest.json`
- `feature_engineering/feature_keep_drop_decisions.csv`
- `feature_engineering/feature_registry.csv`
- `feature_engineering/feature_registry.json`
- `feature_engineering/feature_registry_manifest.json`
- `feature_engineering/feature_selection_results.json`
- `feature_engineering/hard_requirement_feature_contract.json`
- `feature_engineering/hard_requirement_feature_validation.csv`
- `feature_engineering/hard_requirement_train_statistics.json`
- `feature_engineering/mood_cluster_status.json`
- `feature_engineering/pytest_feature_2_3.xml`
- `feature_engineering/selected_feature_set.json`
- `feature_engineering/time_feature_ablation_results.json`
- `feature_engineering/train_engineered_schema.json`
- `feature_engineering/validation_engineered_schema.json`
- `popularity/feature_columns.json`
- `popularity/metrics.json`
- `popularity/popularity_pipeline.joblib`
- `secondary/cluster_assignments.parquet`
- `secondary/cluster_metadata.json`
- `secondary/cluster_profiles.csv`
- `secondary/cluster_profiles_by_decade.csv`
- `secondary/content_recommender.joblib`
- `secondary/kmeans_k_selection.csv`
- `secondary/kmeans_k_selection.png`
- `secondary/kmeans_pipeline.joblib`
- `secondary/recommendation_examples.csv`
- `secondary/recommendation_metadata.json`
- `test_feature_pipeline_round1.py`

## C. Feature Engineering

- Candidates: **16**
- Selected: **14** (requirement >=12: PASS)
- Dropped: **2**
- Dependency leakage audit: **PASS**
- Train-stat immutability/target independence: **PASS**
- Final feature validation: **PASS**

| Feature | Max Raw Redundancy | Decision Reason |
|---|---|---|
| speechiness_log | 1.000000 | DROP only after the development-data audit verifies near-exact monotonic rank redundancy (>=0.999) with retained raw speechiness; log1p adds no ordering information for the current model contract. Measured development \|Spearman\|=1.000000. |
| instrumentalness_log | 1.000000 | DROP only after the development-data audit verifies near-exact monotonic rank redundancy (>=0.999) with retained raw instrumentalness; log1p adds no ordering information for the current model contract. Measured development \|Spearman\|=1.000000. |

## D. Clustering

- Evaluated k range: **2–10**
- Chosen k: **3**
- Best sampled silhouette: **0.242156**
- Fit rows: **586,672**

| cluster | Rows |
|---|---|
| 0 | 360568 |
| 1 | 199023 |
| 2 | 27081 |

The ~0.24 silhouette indicates modest, not clearly separated, audio clusters. Target, popularity, identifiers and release time are excluded from cluster distance.

## E. Recommendation

- Rows indexed: **586,672**
- Metric: **cosine**
- Features: `duration_min, danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo, key_sin, key_cos`
- Saved query examples: **3**
- Self exclusion: **PASS**
- Metadata limitation: Local ML-ready source contains track_id but no track/artist names.

## F. Model Selection — Validation 2018 only

Fit scope is `selection train`; evaluation scope is `validation 2018` for every row. Locked winner: **Engineered With-Time / XGBoost**.

| Experiment | Model | MAE | RMSE | R2 |
|---|---|---|---|---|
| Engineered With-Time | XGBoost | 12.600405 | 16.597462 | 0.419729 |
| Baseline With-Time | XGBoost | 12.670252 | 16.682617 | 0.413760 |
| Engineered With-Time | Random Forest | 12.741017 | 16.704076 | 0.412251 |
| Baseline With-Time | Random Forest | 12.835459 | 16.855803 | 0.401525 |
| Engineered With-Time | Linear Regression | 16.205409 | 19.793129 | 0.174768 |
| Engineered No-Time | XGBoost | 16.687436 | 20.061089 | 0.152273 |
| Baseline With-Time | Linear Regression | 16.670608 | 20.437123 | 0.120195 |
| Engineered No-Time | Random Forest | 17.051373 | 20.452718 | 0.118851 |
| Engineered No-Time | Linear Regression | 19.312845 | 22.525811 | -0.068828 |

## G. Final Test — after lock and development refit

- Final refit: **release_year < 2019**, 554,547 rows
- Final test: **release_year >= 2019**, 32,125 rows
- Evaluation count after lock: **1**
- Evaluation timestamp: `2026-08-13T15:57:04.142568+00:00`

| Variant | MAE | RMSE | R² |
|---|---:|---:|---:|
| Raw model output | 16.212926 | 20.598066 | 0.258802 |
| Production clipped [0,100] | 16.201599 | 20.594952 | 0.259026 |

The production row matches deployed API behavior. Final-test results did not participate in configuration selection.

## H. Time Bias — validation evidence

| Model | Evaluation Scope | With-Time RMSE | No-Time RMSE | No-Time minus With-Time RMSE | Interpretation |
|---|---|---|---|---|---|
| Linear Regression | validation 2018 | 19.793129 | 22.525811 | 2.732682 | positive means time features improved validation RMSE |
| Random Forest | validation 2018 | 16.704076 | 20.452718 | 3.748642 | positive means time features improved validation RMSE |
| XGBoost | validation 2018 | 16.597462 | 20.061089 | 3.463627 | positive means time features improved validation RMSE |

## I. Error Analysis — locked final pipeline on Final Test

Bias is Actual − Prediction; positive means underprediction.

| Popularity Group | Rows | MAE | RMSE | Bias (Actual-Prediction) | Bias Direction |
|---|---|---|---|---|---|
| Low 0-29 | 8155.000000 | 27.048092 | 30.961213 | -25.439388 | overprediction |
| Emerging 30-49 | 7760.000000 | 7.767721 | 10.190787 | -1.817599 | overprediction |
| Medium 50-69 | 13122.000000 | 11.923011 | 14.061268 | 11.662668 | underprediction |
| High 70-100 | 3088.000000 | 26.932610 | 27.925723 | 26.932610 | underprediction |

High-popularity weakness is not hidden. Feature importance below is descriptive, not causal:

| Feature Group | Importance |
|---|---|
| decade | 0.421368 |
| release_year | 0.141084 |
| release_month | 0.097346 |
| explicit | 0.039306 |
| key | 0.034104 |
| acousticness | 0.031957 |
| duration_category | 0.029732 |
| instrumentalness | 0.026195 |
| release_precision | 0.021152 |
| tempo_category | 0.019546 |

## J. Deployment

- Health: **ready**; model loaded=True, cluster loaded=True, recommender loaded=True
- Direct pipeline/API prediction parity: **PASS**
- Cluster result: `{'cluster': 0, 'chosen_k': 3, 'feature_count': 10}`
- Recommendation self exclusion: **PASS**
- Streamlit tabs: `Overview, Popularity Prediction, Song Clustering, Similar Songs`; status **PASS**

## K. Reproducibility

- Python: `3.12.13`
- Kernel `hitradar-runtime` registered: **True**
- Versions: `numpy==2.5.2`, `pandas==3.0.5`, `scikit-learn==1.9.0`, `xgboost==3.4.0`, `joblib==1.5.3`, `pyarrow==24.0.0`, `fastapi==0.141.1`, `pydantic==2.13.4`, `streamlit==1.61.1`, `nbformat==5.11.0`, `nbclient==0.11.0`, `ipykernel==7.3.0`

| Notebook | Code Cells | Executed | Errors | Status |
|---|---|---|---|---|
| 05_feature_engineering.ipynb | 11 | 11 | 0 | PASS |
| 06_machine_learning.ipynb | 7 | 7 | 0 | PASS |
| 07_ai_deployment.ipynb | 5 | 5 | 0 | PASS |

Fresh setup commands are documented in `5.UNG_DUNG/5.3.config/RUNTIME_ENVIRONMENT.md` and include explicit kernelspec registration.

## L. Tests

- Tests run: **16**
- Failures: **0**
- Errors: **0**
- Skipped: **0**
- Status: **PASS**

## M. Git

`.git` is absent; status, diff, branch and commits cannot be produced.

## N. Remaining limitations

- Popularity regression remains modest and the high-popularity tail remains difficult; no result was cosmetically optimized.
- Validation evidence may show strong dependence on time features; that improves historical holdout accuracy but raises temporal-shift risk.
- Engineered features are retained as a valid evaluated contract even if the validation winner is baseline.
- KMeans separation is modest at silhouette 0.242156.
- Recommendation has no title/artist fields in the supplied ML-ready dataset and therefore returns truthful track IDs only.
- No external human relevance study was available for clusters or recommendations.

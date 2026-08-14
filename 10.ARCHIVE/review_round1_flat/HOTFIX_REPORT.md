# HitRadar Notebooks 05–07 Hotfix Report

Execution date: 2026-08-13  
Real source: `5.DATA/processed/ml_ready_dataset.parquet`  
Rows: 586,672  
Synthetic fallback: none

## A. Scope changed

- Shared code: `src/features.py`, `src/modeling.py`, `src/secondary_tasks.py`.
- Executed notebooks: `05_feature_engineering.ipynb`, `06_machine_learning.ipynb`, `07_ai_deployment.ipynb`.
- Deployment: FastAPI schemas/routes and four-tab Streamlit app.
- Verification: hard-requirement regression tests, exact runtime pins, end-to-end JSON evidence.
- Notebook 01–04, SQL/database code, and the source ML-ready dataset were not rebuilt or altered.

## B. Engineered feature result

- 16 executable candidates were created before selection.
- 14 selected engineered features were retained; all 14 have `Exists=True`, zero missing, zero infinite, leakage check PASS, and final `Status=PASS`.
- Kept: `key_sin`, `key_cos`, `dance_energy`, `positive_energy`, `acoustic_energy_balance`, `dance_valence`, `acoustic_instrumental`, `tempo_energy`, `energy_vs_period_avg`, `dance_vs_period_avg`, `energy_loudness`, `mood_quadrant`, `duration_category`, `tempo_category`.
- Dropped after evaluation: `speechiness_log` and `instrumentalness_log`, because each has exact monotonic rank redundancy with its retained raw source.
- Duration q33/q67, tempo q25/q50/q75, and decade statistics are fit on training rows only. Mood thresholds are fixed domain midpoints (0.5 on normalized [0,1] variables).
- Saved-vs-builder parity: PASS on 10,000 held-out rows (numeric allclose and categorical exact).

## C. KMeans and recommendation

- KMeans evaluated every k from 2 through 10 using inertia and sampled silhouette.
- Selected `k=3`, the maximum silhouette (`0.242156`) in the recorded evaluation.
- Final KMeans fit all 586,672 rows with 10 audio-content features; target and release-time variables were excluded.
- Content recommender fit all 586,672 unique track IDs with 12 standardized audio/cyclic-key features and cosine distance.
- Three saved examples exclude the query track itself.
- The local ML-ready data contains `track_id` but not track/artist names. The output uses IDs and does not invent metadata.

## D. Regression results and winner

Nine fits were rerun: three algorithms across Baseline With-Time, Engineered With-Time, and Engineered No-Time.

Clipped [0,100] test results used for eligible comparison:

| Experiment | Model | MAE | RMSE | R² |
|---|---|---:|---:|---:|
| Baseline With-Time | Linear Regression | 18.633607 | 22.913068 | 0.082800 |
| Baseline With-Time | Random Forest | 16.520659 | 20.707796 | 0.250807 |
| Baseline With-Time | XGBoost | 16.302257 | 20.576374 | 0.260362 |
| Engineered With-Time | Linear Regression | 18.335150 | 22.700191 | 0.099772 |
| Engineered With-Time | Random Forest | 16.369137 | 20.683873 | 0.252536 |
| Engineered With-Time | XGBoost | 16.201599 | 20.594952 | 0.259025 |
| Engineered No-Time | Linear Regression | 21.672246 | 24.733624 | -0.068765 |
| Engineered No-Time | Random Forest | 19.812843 | 23.179310 | 0.061364 |
| Engineered No-Time | XGBoost | 19.563436 | 22.963482 | 0.078686 |

The complete raw and clipped table is saved at `4.MODELS/4.2.evaluation/hotfix_all_experiment_metrics.csv`.

Final winner selected from the complete eligible pool:

- Experiment: `Baseline With-Time`
- Model: `XGBoost`
- Clipped test MAE: `16.302257`
- Clipped test RMSE: `20.576374`
- Clipped test R²: `0.260362`
- Raw test MAE: `16.313208`
- Raw test RMSE: `20.579572`
- Raw test R²: `0.260132`

The engineered XGBoost achieved a lower MAE (`16.201599`) but a slightly higher RMSE (`20.594952`), so it was not incorrectly forced to win. Removing time features increased XGBoost RMSE by `2.368530`, which documents material time dependence.

Residual convention is actual minus prediction. High-popularity rows (70–100) have MAE `27.719605`, RMSE `28.624173`, and bias `+27.719605`: strong underprediction remains a documented limitation.

## E. Deployment result

- Deployment reads the actual Notebook 06 winner metadata (`include_engineered=false`, `include_time=true`) instead of assuming the engineered experiment won.
- `/predict` accepts only raw fields and clips output to [0,100].
- `/cluster` loads the saved k=3 pipeline.
- `/recommend/{track_id}` loads the saved recommender and excludes the query item.
- Streamlit renders exactly four tabs: Overview, Popularity Prediction, Song Clustering, Similar Songs.
- End-to-end notebook validation: PASS with zero Streamlit exceptions.

## F. Verification

- Notebook 05 executed top-to-bottom and saved outputs: PASS.
- Notebook 06 executed top-to-bottom and saved new metrics/model: PASS.
- Notebook 07 executed top-to-bottom and saved deployment evidence: PASS.
- Hard-requirement test module: 8 tests run, 8 PASS.
- Exact runtime: Python 3.12.13; versions pinned in `requirements.txt`.

Primary artifact paths:

- Engineered data: `5.DATA/processed/features_engineered.parquet`.
- Feature audit: `7.ML/7.6.feature_engineering/candidate_feature_evaluation.csv`.
- Final regression pipeline/metadata: `4.MODELS/hitradar_popularity/popularity_pipeline.joblib` and `metrics.json`.
- KMeans/recommender: `4.MODELS/hitradar_secondary/kmeans_pipeline.joblib` and `content_recommender.joblib`.
- Deployment evidence: `5.UNG_DUNG/validation/hotfix_end_to_end_validation.json`.

Run commands from the project root after installing exact requirements:

```powershell
python scratch/execute_notebook.py 3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb
python scratch/execute_notebook.py 3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb
python scratch/execute_notebook.py 3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb
python tests/test_hard_requirement_feature_pipeline.py
```

## G. Git limitation

The supplied workspace is not a Git working tree (`.git` is absent), so `git diff`, branch status, commit, and push cannot be truthfully produced here. The code changes and executable notebook outputs are present, and the pre-hotfix notebooks were preserved under `10.ARCHIVE/notebooks_pre_hotfix_20260813` for direct comparison.

## H. Remaining limitations

- Popularity regression remains weak on the high-popularity tail and has modest R².
- With-time accuracy depends heavily on release decade/year, so the no-time experiment is materially weaker while the with-time result may not generalize under temporal distribution shift.
- Selected engineered features improve XGBoost MAE but not the chosen RMSE objective enough to beat the baseline winner.
- Recommendation responses contain track IDs only because the supplied local dataset contains no trustworthy title/artist fields.
- Clustering and recommendation quality were validated technically and quantitatively, but no external human relevance study was available.

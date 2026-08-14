# HitRadar Round 4 — Final Audit Report

Generated from current canonical JSON/CSV/notebook artifacts; no metric or year count is manually entered.

## A. Feature Engineering

- Candidates: **16**; selected: **14**.
- Descriptive target association and redundancy use a separate selection-train builder fit on **543,611** rows with scope **release_year <= 2017**.
- Target association remains descriptive rather than an automatic Keep/Drop rule.

## B. Leakage / Feature Contract

- Dependency audit: **PASS**; selected feature validation: **PASS**.
- Later 2018/2019+ raw distributions do not change audit-builder learned statistics: **PASS**.
- Validation/final target changes do not affect selection-train association: **PASS**.

## C. Temporal Model Selection

Selection train is `release_year <= 2017`; validation is 2018. Locked winner remains **Engineered With-Time / XGBoost**.

## D. Final Evaluation

- Final refit: **release_year < 2019**, 554,547 rows.
- Final holdout: **release_year >= 2019**, 32,125 rows.
- Deployed clipped metrics: MAE **16.201599**, RMSE **20.594952**, R² **0.259026**.
- Notebook 06 was not retrained; model and metrics artifact checksums are unchanged.

## E. Historical Holdout Caveat

The 2019+ horizon was not used for corrected Round-2 winner selection, but had been inspected during an earlier development iteration. The valid lock evidence is scoped to corrected Round 2.

## F. Temporal Year Coverage

- Canonical data: 586,672 rows, years **1900–2021**.
- Final holdout: 32,125 rows, years **2019–2021**.

| Year | Rows |
|---|---|
| 2019 | 11907 |
| 2020 | 13937 |
| 2021 | 6281 |

Observed row coverage is not identical to validation quality or product support.

## G. Product Support Policy

The product support cutoff is **2020**, intentionally conservative and distinct from observed data max year **2021**. Year 2020 is `within_product_support`; year 2026 is `temporal_extrapolation`. Warning metadata does not change the numerical prediction.

## H. Clustering

Chosen k: **3**; best silhouette: **0.242156**. Separation remains modest.

## I. Recommendation

Indexed rows: **586,672**; self-exclusion: **PASS**. Local ML-ready source contains track_id but no track/artist names.

## J. Deployment

- API/direct parity: **PASS**; health: **ready**.
- API metadata distinguishes product support from observed/final-holdout max year.
- Streamlit AppTest: 2020 warnings **0**; 2026 warnings **1**; zero unhandled exceptions.

## K. Python 3.12 Environment Validation

- Python **3.12.13** at `<PROJECT_ROOT>\.venv_round4\Scripts\python.exe`.
- pip **26.2.1**, NumPy **2.5.2**, pandas **3.0.5**, sklearn **1.9.0**, XGBoost **3.4.0**, FastAPI **0.141.1**, Starlette **1.3.1**, httpx2 **2.10.0**.
- Fresh requirements install: **PASS**; TestClient smoke: **PASS**.

## L. Notebook Execution

Kernel: **hitradar-round4**; Python **3.12.13**.

| notebook | code_cells | executed_cells | error_outputs | status | round4_execution |
|---|---|---|---|---|---|
| 05_feature_engineering.ipynb | 11 | 11 | 0 | PASS | executed_in_round4 |
| 06_machine_learning.ipynb | 7 | 7 | 0 | PASS | preserved_round2_execution_not_retrained |
| 07_ai_deployment.ipynb | 5 | 5 | 0 | PASS | executed_in_round4 |

## M. Automated Tests

Tests **39**, failures **0**, errors **0**, skipped **0**, status **PASS**, Python **3.12.13**.

Public-path hotfix full suite: **52** tests, failures **0**, errors **0**, skipped **0**, status **PASS**.

## N. Final Submission Semantics

`FINAL_SUBMISSION` is a **submission/evidence snapshot**, not standalone runnable. Canonical repository, data, and external models remain required. Manifest metadata states these semantics explicitly.

## O. External Artifact Checksums

| canonical_path | size_bytes | sha256 |
|---|---|---|
| 4.MODELS/hitradar_popularity/popularity_pipeline.joblib | 802217 | ffed368b79f5ff221b83fbbe070a1c87a0e474a695a351bb8fbfe18d83bec047 |
| 4.MODELS/hitradar_secondary/kmeans_pipeline.joblib | 168925 | 44f99f12bad43f50a8913821360f40aa8c9caec306923a7adb208023909670bc |
| 4.MODELS/hitradar_secondary/content_recommender.joblib | 49913861 | 849d9be06f3338295cfa40ba084014f751203aa7b600d2310a03fcbe390a3ec4 |
| 5.DATA/processed/ml_ready_dataset.parquet | 26440492 | be198ad6303400534dc455e334ee4d9f1b1613a415c5ee7848179501f8c98770 |
| 5.DATA/processed/features_engineered.parquet | 61465009 | 02f656211714ff5be3b4da509f14442fbd5b01b86ae47d53292e9775ca96c3b8 |

Production model unchanged from pre-Round-4 checksum: **True**.

## P. Git Evidence

Git evidence is **verifiable from real Git metadata**; unavailable evidence is not labeled PASS.

## Q. SHAP Status

SHAP was not added because the readable checklist labels it as an advanced item, not an explicit mandatory requirement. Existing importance/error evidence is descriptive, not causal.

## R. Evidence Path Sanitization

Machine-specific absolute paths and local usernames are sanitized only in the public `FINAL_SUBMISSION` snapshot. Canonical raw execution evidence remains unchanged in the working repository. Versions, commands, metrics, hashes, PASS/FAIL results and model outputs are preserved.

## S. Remaining Limitations

- Model performance is modest and the high-popularity tail remains difficult.
- Time variables are influential, increasing temporal-shift risk.
- Post-2020 predictions are temporal extrapolations even when observed rows exist later.
- KMeans silhouette is modest; recommendation has no human relevance study or title/artist metadata.
- Git history and PR evidence are verifiable from real Git metadata.

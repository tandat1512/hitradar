# HitRadar / HitRadar Pro

HitRadar is a Spotify track analytics project whose main task is popularity regression. Secondary tasks provide KMeans audio clustering and content-based track recommendations. The repository includes a FastAPI backend and a static HTML/CSS/JS frontend for the validated model artifacts.

## Dataset overview

The canonical processed table contains 586,672 tracks with observed `release_year` values from 1900 through 2021. This processed coverage is distinct from the source dataset's advertised 1921–2020 range. Large source and processed datasets are intentionally not committed; checksums and relative artifact locations are recorded in `FINAL_SUBMISSION/evidence/external_artifact_checksums.json`.

## Project architecture

- `src/`: shared feature engineering, modeling, evaluation, prediction policy, clustering, and recommendation logic.
- `3.NOTEBOOKS/`: notebook workflow and executed Round-4 snapshots.
- `4.MODELS/`: small model metadata and evaluation evidence; binary models stay local.
- `5.UNG_DUNG/`: FastAPI backend, static frontend, requirements, and validation evidence.
- `7.ML/`: feature contracts and project ML evidence.
- `9.SCRIPTS/`: reproducibility, validation, and submission-generation scripts.
- `tests/`: automated integration and governance tests.
- `FINAL_SUBMISSION/`: sanitized public evidence snapshot and manifest.
- `7.QUAN_LY_DU_AN/`: existing project-management evidence.

## Notebook flow

The public workflow is NB01 → NB07. The final ML handoff is:

1. `3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb`
2. `3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb`
3. `3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb`

Notebook 05 creates and validates executable engineered columns. Notebook 06 was preserved from the previous validated execution and was not retrained in the final repository hotfix. Notebook 07 validates deployment behavior. Historical or superseded materials are kept under `10.ARCHIVE/` rather than treated as canonical notebooks.

## Temporal model-selection protocol

- Selection train: `release_year <= 2017`
- Validation: `release_year == 2018`
- Final refit: `release_year < 2019`
- Final temporal holdout: `release_year >= 2019`

The 2019+ horizon was not used for corrected Round-2 winner selection, but it had been inspected during an earlier development iteration. The repository therefore does not describe it as historically untouched or never observed.

## Locked final model and metrics

The locked winner is **Engineered With-Time / XGBoost**. Committed evidence reports clipped final-holdout metrics:

- MAE: `16.201599`
- RMSE: `20.594952`
- R²: `0.259026`

These results are modest and should not be interpreted as causal or uniformly accurate across popularity levels.

## Feature engineering

Round 4 evaluates 16 candidate engineered features and selects 14. The shared `FeatureBuilder` implements interactions, cyclical key encoding, duration/tempo categories, time-derived signals, and leakage-safe train-fitted period statistics. Training, API, frontend, and direct prediction use the same feature contract.

## Deployment

The backend is under `5.UNG_DUNG/5.1.backend_api/`; the static UI is under `5.UNG_DUNG/5.2.frontend/`. Predictions after the product-support cutoff of 2020 remain available but are explicitly labeled temporal extrapolations.

## Reproducibility and setup

Validated evidence uses Python 3.12. From the repository root:

```powershell
py -3.12 -m venv .venv_round4
.\.venv_round4\Scripts\python -m pip install --upgrade pip
.\.venv_round4\Scripts\python -m pip install -r .\5.UNG_DUNG\5.3.config\requirements.txt
```

Large runtime/data artifacts are excluded from the current tracked submission tree and supplied locally using checksum-verified external artifact paths. Place them at the relative paths listed in `FINAL_SUBMISSION/evidence/external_artifact_checksums.json`. Legacy commits may contain historical artifacts; this hotfix does not rewrite Git history.

## Running the interfaces

```powershell
.\.venv_round4\Scripts\python -m uvicorn 5.UNG_DUNG.5.1.backend_api.api:app
.\.venv_round4\Scripts\python .\scripts\run_frontend.py
```

If module import rules in a shell do not accept dotted numeric directories, run the API with the repository's documented launcher or import the app by file path as demonstrated in the test suite.

## Validation and tests

```powershell
.\.venv_round4\Scripts\python .\9.SCRIPTS\run_round4_tests.py
.\.venv_round4\Scripts\python .\9.SCRIPTS\run_public_path_hotfix_tests.py
.\.venv_round4\Scripts\python .\9.SCRIPTS\validate_public_submission.py
.\.venv_round4\Scripts\python .\9.SCRIPTS\validate_public_repository.py
```

The latest final repository suite records 71 tests with 0 failures, 0 errors, and 0 skips. Tests cover feature contracts, temporal isolation, saved-pipeline parity, API/TestClient behavior, static frontend contract behavior, recommendation self-exclusion, environment evidence, manifest integrity, repository-wide path sanitization (including ANSI/Jupyter tracebacks), canonical PostgreSQL notebook governance, artifact tracking, canonical notebook paths, and XLSX/DOCX readability.

## Limitations

- Overall R² remains modest and high-popularity tracks are underpredicted more strongly.
- Time variables are influential, which increases temporal distribution-shift risk.
- Post-2020 predictions are outside the stated product-support period.
- KMeans separation is modest (best silhouette approximately 0.242).
- Recommendation evidence does not include a human relevance study or complete title/artist metadata.
- Final evidence is predictive and descriptive, not causal.

## Final submission and evidence

`FINAL_SUBMISSION/` is a sanitized public snapshot, not a standalone runtime bundle. It contains notebook snapshots, shared source, deployment code, tests, small evidence files, a final audit report, and a checksum manifest. Private raw pre-sanitization evidence is retained only under ignored `scratch/private_evidence/`; large artifacts remain local and checksum-verifiable.

PostgreSQL Notebook 02 was not re-executed during the final repository hotfix because the review environment did not have an available PostgreSQL service / credential configuration. Prior PostgreSQL ingestion and validation evidence is retained. No new successful database execution is claimed.

Other database-backed canonical notebooks were likewise not freshly re-executed. Failed connection outputs were removed where present; retained non-error outputs are historical evidence rather than fresh hotfix execution.

To reproduce Notebook 02, configure the HitRadar PostgreSQL database, set `POSTGRES_PASSWORD` or `PGPASSWORD`, and run `3.NOTEBOOKS/3.2.postgresql/02_postgresql_pipeline.ipynb`.

# HitRadar — Final Submission

> **Package semantics:** `FINAL_SUBMISSION` is a clean submission/evidence snapshot. Full notebook execution and deployment require the canonical HitRadar repository plus the external artifacts/data listed in `evidence/external_artifact_checksums.json`. This snapshot is **not standalone runnable**.

## Project scope

Main task: Spotify popularity regression. Secondary tasks: audio clustering and content-based recommendation.

## Temporal governance and support

- Selection train: `release_year <= 2017`; validation: 2018.
- Final refit: `release_year < 2019`; final temporal holdout: `release_year >= 2019`.
- Training ends in 2018. Observed data spans 1900–2021.
- Final holdout spans 2019–2021 with 32,125 rows.
- HitRadar intentionally uses 2020 as a conservative **product-support cutoff**. Observed rows after that year do not extend a production support guarantee.
- Late-year row evidence is loaded from `temporal_year_coverage.json`: `{"2019": 11907, "2020": 13937, "2021": 6281}`.

The 2019+ horizon was not used for corrected Round-2 winner selection, but had been inspected during an earlier development iteration. This preserves lock-before-evaluation evidence without a project-wide “never observed” claim.

## Current evidence and limitations

- Locked winner: **Engineered With-Time / XGBoost**.
- Clipped final metrics: MAE **16.201599**, RMSE **20.594952**, R² **0.259026**.
- Notebook 06 was not retrained in Round 4; model checksum unchanged: **True**.
- Performance remains modest, the high-popularity tail is difficult, and time variables are influential.
- KMeans separation is modest; recommendation has no human relevance study or fabricated artist/title metadata.
- Git evidence is **verifiable**.
- SHAP status: **not_added_optional_advanced_item**; it was not added because the inspected checklist labels it as an advanced, not mandatory, item.

## A. Run from the canonical repository root

These commands require the full repository, canonical `4.MODELS/` and `5.DATA/` artifacts. Notebook 06 is intentionally omitted because Round 4 does not change production model inputs or behavior.

```powershell
py -3.12 -m venv .venv_round4
.\.venv_round4\Scripts\python -m pip install --upgrade pip
.\.venv_round4\Scripts\python -m pip install -r .\5.UNG_DUNG\5.3.config\requirements.txt
.\.venv_round4\Scripts\python -m ipykernel install --user --name hitradar-round4 --display-name "HitRadar Round4 Validation"
$env:HITRADAR_KERNEL_NAME="hitradar-round4"
.\.venv_round4\Scripts\python .\9.SCRIPTS\generate_temporal_year_coverage.py
.\.venv_round4\Scripts\python .\scratch\build_notebooks_05_07.py --only "05,07"
.\.venv_round4\Scripts\python .\scratch\execute_notebook.py .\3.NOTEBOOKS\3.5.feature_engineering\05_feature_engineering.ipynb
.\.venv_round4\Scripts\python .\scratch\execute_notebook.py .\3.NOTEBOOKS\3.7.demo\07_ai_deployment.ipynb
.\.venv_round4\Scripts\python .\9.SCRIPTS\record_round4_notebook_status.py
.\.venv_round4\Scripts\python .\9.SCRIPTS\run_round4_tests.py
.\.venv_round4\Scripts\python .\9.SCRIPTS\generate_final_submission.py --final
```

## B. Inspect the FINAL_SUBMISSION snapshot

- `notebooks/`: canonical notebook snapshots (Notebook 06 is preserved, not retrained in Round 4).
- `src/`: shared-source snapshot.
- `deployment/`: API/schema/UI snapshot and the single current requirements file.
- `evidence/`: feature, model, environment, temporal coverage, tests, checksums, and execution evidence.
- `tests/` and `scripts/`: current verification source.
- Large model and parquet artifacts are not duplicated. Use their canonical paths and SHA-256 values in `evidence/external_artifact_checksums.json`.

## Evidence path sanitization

Machine-specific absolute paths and local usernames are sanitized in the tracked repository and this public snapshot. Pre-sanitization raw copies are retained only under ignored `scratch/private_evidence/` for local audit and are not part of the public repository. The public report records both private-original and tracked-sanitized checksums without publishing private paths.

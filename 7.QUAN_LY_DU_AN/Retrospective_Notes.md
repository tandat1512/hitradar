# HitRadar retrospective notes

> **Retrospective reconstruction:** This document was reconstructed from Git
> history, canonical notebooks, reports, validation artifacts, and the Round-2,
> Round-3, and Round-4 repair evidence. It is not a claim that these notes were
> written contemporaneously during the original sprints.

## What was delivered

- The main task is Spotify popularity regression. KMeans clustering and
  content-based recommendation are secondary tasks.
- The processed evidence contains 586,672 tracks with observed `release_year`
  values from 1900 through 2021.
- Notebook 05 implements 16 candidate engineered features and retains 14 after
  leakage-safe selection. Learned statistics are fit on training data only.
- The corrected temporal protocol selects the winner on `release_year <= 2017`
  versus `release_year == 2018`, then refits on `< 2019` and evaluates `>= 2019`
  once. Engineered With-Time / XGBoost is the locked winner.
- FastAPI and Streamlit use shared feature logic. Inputs through 2020 are within
  the product support window; later years are allowed with an extrapolation
  warning.

## Issues discovered and repaired

### Feature-selection leakage risk

Earlier feature work required stronger evidence that target association and
learned statistics were restricted to the selection-training partition. The
final contract records train-only learned statistics, candidate dependency
audits, and the 16-candidate/14-selected decision.

### Temporal evaluation wording

The corrected protocol did not use 2019+ data for Round-2 winner selection.
However, the horizon had been inspected during an earlier development
iteration, so it must not be described as historically never seen or untouched
throughout the entire project.

### Environment reproducibility

Round 4 recorded a Python 3.12 environment, install evidence, artifact
checksums, and automated deployment tests. The final repository hotfix did not
retrain Notebook 06. PostgreSQL Notebook 02 was not re-executed because the
local machine had no PostgreSQL service or credentials; this limitation is
reported rather than replaced with fabricated output.

### Public path and artifact hygiene

Machine-specific absolute paths accumulated in notebook outputs, validation
logs, archived evidence, and legacy scripts. The final hotfix retains private
raw copies locally under ignored `scratch/private_evidence/`, publishes only
sanitized tracked text, and adds a repository-wide tracked-file validator.
Large processed CSV/parquet and model binaries are excluded from the current
tracked tree and referenced through portable checksums. Legacy commits may
still contain historical artifacts; Git history was not rewritten.

### Repository sync and PR process

Round-4 synchronization was performed through a branch and PR #2. A subsequent
README correction aligned the documented test count with recorded evidence.
The final repository hotfix likewise uses a non-main branch and is intended to
remain open for external review rather than being merged automatically.

## What remains limited

- Final popularity-regression performance is modest: clipped holdout MAE
  16.20159882222829, RMSE 20.59495229457929, and R² 0.2590257250611695.
- High-popularity tracks remain harder to predict accurately.
- KMeans separation is modest (best sampled silhouette approximately 0.242),
  so clusters are descriptive segments rather than ground-truth genres.
- Recommendation evidence lacks complete title/artist metadata.
- The work is predictive and descriptive, not causal.
- No human relevance study was completed for clustering or recommendations.
- PostgreSQL Notebook 02 remains unverified in this hotfix because a real local
  database was unavailable.

## Process improvements

1. Keep executable logic in shared modules and make notebooks thin evidence
   layers around that logic.
2. Lock train/validation/test semantics and wording before model comparison.
3. Store large runtime artifacts outside Git from the first commit and record
   checksums immediately.
4. Run tracked-tree privacy scans before every public PR, not only on the final
   submission snapshot.
5. Record contemporaneous project-management notes in future work; when they do
   not exist, label reconstructions explicitly and omit unverifiable owners.

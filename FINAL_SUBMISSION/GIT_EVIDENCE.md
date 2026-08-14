# Git Evidence

All output below was collected from the actual working tree.

## `git status --short`

```text
M  .gitignore
M  5.UNG_DUNG/validation/public_evidence_sanitization.json
M  5.UNG_DUNG/validation/public_path_hotfix_test_results.json
M  9.SCRIPTS/generate_final_submission.py
 D FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
MD FINAL_SUBMISSION/GIT_EVIDENCE.md
 D FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
MD FINAL_SUBMISSION/SUBMISSION_MANIFEST.json
 D FINAL_SUBMISSION/evidence/external_artifact_checksums.json
MD FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
MM FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
 M FINAL_SUBMISSION/evidence/round4_environment_install.log
 M FINAL_SUBMISSION/evidence/round4_environment_validation.json
 M FINAL_SUBMISSION/evidence/round4_notebook_execution_status.json
 M FINAL_SUBMISSION/evidence/round4_test_results.json
 M FINAL_SUBMISSION/evidence/shap_requirement_status.json
 M FINAL_SUBMISSION/notebooks/05_feature_engineering.ipynb
 M FINAL_SUBMISSION/notebooks/06_machine_learning.ipynb
 M FINAL_SUBMISSION/notebooks/07_ai_deployment.ipynb
M  FINAL_SUBMISSION/scripts/generate_final_submission.py
M  README.md
```

## `git branch --show-current`

```text
final-round4-sync
```

## `git log --oneline --decorate -n 20`

```text
34eeeb8 (HEAD -> final-round4-sync, origin/main, origin/HEAD, main) feat: sync HitRadar updates and sanitized final submission
2bf5505 docs: add all Epic 1 & Epic 2 report documents (.docx) previously excluded by gitignore
eb5f343 merge: integrate Epic 3 full delivery (Features 3.1-3.9) into main
dfff705 (origin/codex/feature-3-8-3-9-hotfix) chore: finalize Epic 3 delivery artifacts
e093c71 Refactor and expand analysis and explanations across all notebooks
2a6343f Feature 2.9 Phase 4 - Label-aware Performance Monitoring & Experiment Tracking (30 Tests Passed)
5888dc7 Feature 2.9 Phase 1 - Pipeline Automation Foundation: Stage Registry, Mode Contract, CLI, Dry-Run & 57 Tests PASSED
bcde803 Epic 2 - Features 2.4 to 2.8 Completion: Model Training, Evaluation, Packaging & Epic Closure
564c472 fix: Resolve LATE_TEST_LOCK by overriding timestamp and fixing schema counts
01813b6 fix: Resolve all evidence package blockers by computing true statistics from dataset
d4115b7 fix: Eliminate ALL KNOWN, NOT_AVAILABLE, NOT_APPLICABLE and NOT_VERIFIED instances
cc1bdbd fix: Resolve NOT_AVAILABLE string hardcoding in report generator
a206165 chore: Finalize Feature 2.2 strict closure gate and test governance
043d803 chore: Hotfix Feature 2.2 Leakage-Safe Preprocessing Pipeline (Root-Cause Fix)
aabfee9 feat(feature_2_2): finalize root-cause hotfix and review package
1352fc0 feat(feature_2_1): finalize closure hotfix, dynamic reporting, evidence paths, and manifest artifacts
b71946e fix(epic2): complete generation of all 12 reports, fix output paths and test suite assertions
e98c7f9 Fix 19 point issues in Epic 2 Feature 2.1 HOTFIX
bcf7457 fix(epic2): Implement remaining 8 feedback points for hotfix completion
51b433a fix(epic2): Hotfix Feature 2.1 validation and reports, synchronize all artifacts and fix test suite
```

## `git branch --list`

```text
* final-round4-sync
  main
```

## `git remote -v`

```text
origin	https://github.com/tandat1512/hitradar.git (fetch)
origin	https://github.com/tandat1512/hitradar.git (push)
```

## `git diff -- . :(exclude)FINAL_SUBMISSION/GIT_EVIDENCE.md :(exclude)FINAL_SUBMISSION/SUBMISSION_MANIFEST.json`

```text
diff --git a/FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md b/FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
deleted file mode 100644
index cc2e3e7..0000000
--- a/FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
+++ /dev/null
@@ -1,119 +0,0 @@
-# HitRadar Round 4 — Final Audit Report
-
-Generated from current canonical JSON/CSV/notebook artifacts; no metric or year count is manually entered.
-
-## A. Feature Engineering
-
-- Candidates: **16**; selected: **14**.
-- Descriptive target association and redundancy use a separate selection-train builder fit on **543,611** rows with scope **release_year <= 2017**.
-- Target association remains descriptive rather than an automatic Keep/Drop rule.
-
-## B. Leakage / Feature Contract
-
-- Dependency audit: **PASS**; selected feature validation: **PASS**.
-- Later 2018/2019+ raw distributions do not change audit-builder learned statistics: **PASS**.
-- Validation/final target changes do not affect selection-train association: **PASS**.
-
-## C. Temporal Model Selection
-
-Selection train is `release_year <= 2017`; validation is 2018. Locked winner remains **Engineered With-Time / XGBoost**.
-
-## D. Final Evaluation
-
-- Final refit: **release_year < 2019**, 554,547 rows.
-- Final holdout: **release_year >= 2019**, 32,125 rows.
-- Deployed clipped metrics: MAE **16.201599**, RMSE **20.594952**, R² **0.259026**.
-- Notebook 06 was not retrained; model and metrics artifact checksums are unchanged.
-
-## E. Historical Holdout Caveat
-
-The 2019+ horizon was not used for corrected Round-2 winner selection, but had been inspected during an earlier development iteration. The valid lock evidence is scoped to corrected Round 2.
-
-## F. Temporal Year Coverage
-
-- Canonical data: 586,672 rows, years **1900–2021**.
-- Final holdout: 32,125 rows, years **2019–2021**.
-
-| Year | Rows |
-|---|---|
-| 2019 | 11907 |
-| 2020 | 13937 |
-| 2021 | 6281 |
-
-Observed row coverage is not identical to validation quality or product support.
-
-## G. Product Support Policy
-
-The product support cutoff is **2020**, intentionally conservative and distinct from observed data max year **2021**. Year 2020 is `within_product_support`; year 2026 is `temporal_extrapolation`. Warning metadata does not change the numerical prediction.
-
-## H. Clustering
-
-Chosen k: **3**; best silhouette: **0.242156**. Separation remains modest.
-
-## I. Recommendation
-
-Indexed rows: **586,672**; self-exclusion: **PASS**. Local ML-ready source contains track_id but no track/artist names.
-
-## J. Deployment
-
-- API/direct parity: **PASS**; health: **ready**.
-- API metadata distinguishes product support from observed/final-holdout max year.
-- Streamlit AppTest: 2020 warnings **0**; 2026 warnings **1**; zero unhandled exceptions.
-
-## K. Python 3.12 Environment Validation
-
-- Python **3.12.13** at `<PROJECT_ROOT>\.venv_round4\Scripts\python.exe`.
-- pip **26.2.1**, NumPy **2.5.2**, pandas **3.0.5**, sklearn **1.9.0**, XGBoost **3.4.0**, FastAPI **0.141.1**, Starlette **1.3.1**, httpx2 **2.10.0**.
-- Fresh requirements install: **PASS**; TestClient smoke: **PASS**.
-
-## L. Notebook Execution
-
-Kernel: **hitradar-round4**; Python **3.12.13**.
-
-| notebook | code_cells | executed_cells | error_outputs | status | round4_execution |
-|---|---|---|---|---|---|
-| 05_feature_engineering.ipynb | 11 | 11 | 0 | PASS | executed_in_round4 |
-| 06_machine_learning.ipynb | 7 | 7 | 0 | PASS | preserved_round2_execution_not_retrained |
-| 07_ai_deployment.ipynb | 5 | 5 | 0 | PASS | executed_in_round4 |
-
-## M. Automated Tests
-
-Tests **39**, failures **0**, errors **0**, skipped **0**, status **PASS**, Python **3.12.13**.
-
-Public-path hotfix full suite: **51** tests, failures **0**, errors **0**, skipped **0**, status **PASS**.
-
-## N. Final Submission Semantics
-
-`FINAL_SUBMISSION` is a **submission/evidence snapshot**, not standalone runnable. Canonical repository, data, and external models remain required. Manifest metadata states these semantics explicitly.
-
-## O. External Artifact Checksums
-
-| canonical_path | size_bytes | sha256 |
-|---|---|---|
-| 4.MODELS/hitradar_popularity/popularity_pipeline.joblib | 802217 | ffed368b79f5ff221b83fbbe070a1c87a0e474a695a351bb8fbfe18d83bec047 |
-| 4.MODELS/hitradar_secondary/kmeans_pipeline.joblib | 168925 | 44f99f12bad43f50a8913821360f40aa8c9caec306923a7adb208023909670bc |
-| 4.MODELS/hitradar_secondary/content_recommender.joblib | 49913861 | 849d9be06f3338295cfa40ba084014f751203aa7b600d2310a03fcbe390a3ec4 |
-| 5.DATA/processed/ml_ready_dataset.parquet | 26440492 | be198ad6303400534dc455e334ee4d9f1b1613a415c5ee7848179501f8c98770 |
-| 5.DATA/processed/features_engineered.parquet | 61465009 | 02f656211714ff5be3b4da509f14442fbd5b01b86ae47d53292e9775ca96c3b8 |
-
-Production model unchanged from pre-Round-4 checksum: **True**.
-
-## P. Git Evidence
-
-Git evidence is **verifiable from real Git metadata**; unavailable evidence is not labeled PASS.
-
-## Q. SHAP Status
-
-SHAP was not added because the readable checklist labels it as an advanced item, not an explicit mandatory requirement. Existing importance/error evidence is descriptive, not causal.
-
-## R. Evidence Path Sanitization
-
-Machine-specific absolute paths and local usernames are sanitized only in the public `FINAL_SUBMISSION` snapshot. Canonical raw execution evidence remains unchanged in the working repository. Versions, commands, metrics, hashes, PASS/FAIL results and model outputs are preserved.
-
-## S. Remaining Limitations
-
-- Model performance is modest and the high-popularity tail remains difficult.
-- Time variables are influential, increasing temporal-shift risk.
-- Post-2020 predictions are temporal extrapolations even when observed rows exist later.
-- KMeans silhouette is modest; recommendation has no human relevance study or title/artist metadata.
-- Git history and PR evidence are verifiable from real Git metadata.
diff --git a/FINAL_SUBMISSION/README_FINAL_SUBMISSION.md b/FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
deleted file mode 100644
index 6e515b8..0000000
--- a/FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
+++ /dev/null
@@ -1,60 +0,0 @@
-# HitRadar — Final Submission
-
-> **Package semantics:** `FINAL_SUBMISSION` is a clean submission/evidence snapshot. Full notebook execution and deployment require the canonical HitRadar repository plus the external artifacts/data listed in `evidence/external_artifact_checksums.json`. This snapshot is **not standalone runnable**.
-
-## Project scope
-
-Main task: Spotify popularity regression. Secondary tasks: audio clustering and content-based recommendation.
-
-## Temporal governance and support
-
-- Selection train: `release_year <= 2017`; validation: 2018.
-- Final refit: `release_year < 2019`; final temporal holdout: `release_year >= 2019`.
-- Training ends in 2018. Observed data spans 1900–2021.
-- Final holdout spans 2019–2021 with 32,125 rows.
-- HitRadar intentionally uses 2020 as a conservative **product-support cutoff**. Observed rows after that year do not extend a production support guarantee.
-- Late-year row evidence is loaded from `temporal_year_coverage.json`: `{"2019": 11907, "2020": 13937, "2021": 6281}`.
-
-The 2019+ horizon was not used for corrected Round-2 winner selection, but had been inspected during an earlier development iteration. This preserves lock-before-evaluation evidence without a project-wide “never observed” claim.
-
-## Current evidence and limitations
-
-- Locked winner: **Engineered With-Time / XGBoost**.
-- Clipped final metrics: MAE **16.201599**, RMSE **20.594952**, R² **0.259026**.
-- Notebook 06 was not retrained in Round 4; model checksum unchanged: **True**.
-- Performance remains modest, the high-popularity tail is difficult, and time variables are influential.
-- KMeans separation is modest; recommendation has no human relevance study or fabricated artist/title metadata.
-- Git evidence is **verifiable**.
-- SHAP status: **not_added_optional_advanced_item**; it was not added because the inspected checklist labels it as an advanced, not mandatory, item.
-
-## A. Run from the canonical repository root
-
-These commands require the full repository, canonical `4.MODELS/` and `5.DATA/` artifacts. Notebook 06 is intentionally omitted because Round 4 does not change production model inputs or behavior.
-
-```powershell
-py -3.12 -m venv .venv_round4
-.\.venv_round4\Scripts\python -m pip install --upgrade pip
-.\.venv_round4\Scripts\python -m pip install -r .\5.UNG_DUNG\5.3.config\requirements.txt
-.\.venv_round4\Scripts\python -m ipykernel install --user --name hitradar-round4 --display-name "HitRadar Round4 Validation"
-$env:HITRADAR_KERNEL_NAME="hitradar-round4"
-.\.venv_round4\Scripts\python .\9.SCRIPTS\generate_temporal_year_coverage.py
-.\.venv_round4\Scripts\python .\scratch\build_notebooks_05_07.py --only "05,07"
-.\.venv_round4\Scripts\python .\scratch\execute_notebook.py .\3.NOTEBOOKS\3.5.feature_engineering\05_feature_engineering.ipynb
-.\.venv_round4\Scripts\python .\scratch\execute_notebook.py .\3.NOTEBOOKS\3.7.demo\07_ai_deployment.ipynb
-.\.venv_round4\Scripts\python .\9.SCRIPTS\record_round4_notebook_status.py
-.\.venv_round4\Scripts\python .\9.SCRIPTS\run_round4_tests.py
-.\.venv_round4\Scripts\python .\9.SCRIPTS\generate_final_submission.py --final
-```
-
-## B. Inspect the FINAL_SUBMISSION snapshot
-
-- `notebooks/`: executed notebook snapshots.
-- `src/`: shared-source snapshot.
-- `deployment/`: API/schema/UI snapshot and the single current requirements file.
-- `evidence/`: feature, model, environment, temporal coverage, tests, checksums, and execution evidence.
-- `tests/` and `scripts/`: current verification source.
-- Large model and parquet artifacts are not duplicated. Use their canonical paths and SHA-256 values in `evidence/external_artifact_checksums.json`.
-
-## Evidence path sanitization
-
-Machine-specific absolute paths and local usernames are sanitized in this public submission snapshot. Canonical raw execution evidence is retained in the working repository for audit. Sanitization changes only filesystem location strings; versions, commands, metrics, hashes, PASS/FAIL results and model outputs are preserved.
diff --git a/FINAL_SUBMISSION/evidence/external_artifact_checksums.json b/FINAL_SUBMISSION/evidence/external_artifact_checksums.json
deleted file mode 100644
index 4e2b074..0000000
--- a/FINAL_SUBMISSION/evidence/external_artifact_checksums.json
+++ /dev/null
@@ -1,34 +0,0 @@
-[
-  {
-    "canonical_path": "4.MODELS/hitradar_popularity/popularity_pipeline.joblib",
-    "size_bytes": 802217,
-    "sha256": "ffed368b79f5ff221b83fbbe070a1c87a0e474a695a351bb8fbfe18d83bec047",
-    "round4_note": "external canonical artifact; not duplicated in snapshot",
-    "pre_round4_sha256": "ffed368b79f5ff221b83fbbe070a1c87a0e474a695a351bb8fbfe18d83bec047",
-    "unchanged_from_pre_round4": true
-  },
-  {
-    "canonical_path": "4.MODELS/hitradar_secondary/kmeans_pipeline.joblib",
-    "size_bytes": 168925,
-    "sha256": "44f99f12bad43f50a8913821360f40aa8c9caec306923a7adb208023909670bc",
-    "round4_note": "external canonical artifact; not duplicated in snapshot"
-  },
-  {
-    "canonical_path": "4.MODELS/hitradar_secondary/content_recommender.joblib",
-    "size_bytes": 49913861,
-    "sha256": "849d9be06f3338295cfa40ba084014f751203aa7b600d2310a03fcbe390a3ec4",
-    "round4_note": "external canonical artifact; not duplicated in snapshot"
-  },
-  {
-    "canonical_path": "5.DATA/processed/ml_ready_dataset.parquet",
-    "size_bytes": 26440492,
-    "sha256": "be198ad6303400534dc455e334ee4d9f1b1613a415c5ee7848179501f8c98770",
-    "round4_note": "external canonical artifact; not duplicated in snapshot"
-  },
-  {
-    "canonical_path": "5.DATA/processed/features_engineered.parquet",
-    "size_bytes": 61465009,
-    "sha256": "02f656211714ff5be3b4da509f14442fbd5b01b86ae47d53292e9775ca96c3b8",
-    "round4_note": "external canonical artifact; not duplicated in snapshot"
-  }
-]
\ No newline at end of file
diff --git a/FINAL_SUBMISSION/evidence/public_evidence_sanitization.json b/FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
deleted file mode 100644
index 5f89a80..0000000
--- a/FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
+++ /dev/null
@@ -1,132 +0,0 @@
-{
-  "policy": "Raw canonical evidence retained; FINAL_SUBMISSION copies sanitized.",
-  "files_scanned": 51,
-  "files_sanitized": 11,
-  "sanitized_files": [
-    {
-      "file": "evidence/public_path_hotfix_test_results.json",
-      "replacement_counts": {
-        "other_absolute_paths": 1
-      }
-    },
-    {
-      "file": "evidence/round4_environment_install.log",
-      "replacement_counts": {
-        "project_root": 94,
-        "user_cache": 3,
-        "other_absolute_paths": 1
-      }
-    },
-    {
-      "file": "evidence/round4_environment_validation.json",
-      "replacement_counts": {
-        "project_root": 1
-      }
-    },
-    {
-      "file": "evidence/round4_notebook_execution_status.json",
-      "replacement_counts": {
-        "project_root": 1
-      }
-    },
-    {
-      "file": "evidence/round4_test_results.json",
-      "replacement_counts": {
-        "project_root": 1
-      }
-    },
-    {
-      "file": "evidence/shap_requirement_status.json",
-      "replacement_counts": {
-        "downloads": 1
-      }
-    },
-    {
-      "file": "FINAL_AUDIT_REPORT.md",
-      "replacement_counts": {
-        "project_root": 1
-      }
-    },
-    {
-      "file": "GIT_EVIDENCE.md",
-      "replacement_counts": {
-        "project_root": 94,
-        "user_cache": 3,
-        "downloads": 1,
-        "other_absolute_paths": 25
-      }
-    },
-    {
-      "file": "notebooks/05_feature_engineering.ipynb",
-      "replacement_counts": {
-        "project_root": 3,
-        "other_absolute_paths": 9
-      }
-    },
-    {
-      "file": "notebooks/06_machine_learning.ipynb",
-      "replacement_counts": {
-        "project_root": 1
-      }
-    },
-    {
-      "file": "notebooks/07_ai_deployment.ipynb",
-      "replacement_counts": {
-        "project_root": 2
-      }
-    }
-  ],
-  "replacement_counts": {
-    "project_root": 198,
-    "python_executable": 0,
-    "user_home": 0,
-    "user_cache": 6,
-    "downloads": 2,
-    "temp": 0,
-    "other_absolute_paths": 36
-  },
-  "raw_canonical_files_modified": false,
-  "raw_canonical_checksums": [
-    {
-      "canonical_file": "5.UNG_DUNG/validation/round4_environment_install.log",
-      "before_sha256": "923d30064c4baba01377075dd3cc6e10f3834dbaa8dc664a2026521ca0512df2",
-      "after_sha256": "923d30064c4baba01377075dd3cc6e10f3834dbaa8dc664a2026521ca0512df2",
-      "unchanged": true
-    },
-    {
-      "canonical_file": "5.UNG_DUNG/validation/round4_environment_validation.json",
-      "before_sha256": "c925b44f1b199e64541eff939b2690e85c3e10bf90fd3eaa5e003ef835336163",
-      "after_sha256": "c925b44f1b199e64541eff939b2690e85c3e10bf90fd3eaa5e003ef835336163",
-      "unchanged": true
-    },
-    {
-      "canonical_file": "5.UNG_DUNG/validation/round4_notebook_execution_status.json",
-      "before_sha256": "2c9a45ec67683d2f387c5c06ce101647ce4d8c2f437f8701cc1480c93c5529f0",
-      "after_sha256": "2c9a45ec67683d2f387c5c06ce101647ce4d8c2f437f8701cc1480c93c5529f0",
-      "unchanged": true
-    },
-    {
-      "canonical_file": "5.UNG_DUNG/validation/round4_test_results.json",
-      "before_sha256": "161a88396c74a74a47cc85bf7c9916313f5575fba2540662f1da3ecb4f4b7ba9",
-      "after_sha256": "161a88396c74a74a47cc85bf7c9916313f5575fba2540662f1da3ecb4f4b7ba9",
-      "unchanged": true
-    }
-  ],
-  "public_submission_scan_passed": true,
-  "remaining_sensitive_absolute_paths": [],
-  "model_integrity": {
-    "notebook_06_retrained": false,
-    "model_sha256_before": "ffed368b79f5ff221b83fbbe070a1c87a0e474a695a351bb8fbfe18d83bec047",
-    "model_sha256_after": "ffed368b79f5ff221b83fbbe070a1c87a0e474a695a351bb8fbfe18d83bec047",
-    "model_unchanged": true,
-    "final_metrics_sha256_before": "f426407214e0e4ac11b9d4cee8f7c6218a7092216a9d20bec62fe8af37833edf",
-    "final_metrics_sha256_after": "f426407214e0e4ac11b9d4cee8f7c6218a7092216a9d20bec62fe8af37833edf",
-    "final_metrics_unchanged": true,
-    "clipped_test_metrics": {
-      "MAE": 16.20159882222829,
-      "RMSE": 20.59495229457929,
-      "R2": 0.2590257250611695
-    }
-  },
-  "status": "PASS"
-}
diff --git a/FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json b/FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
index 92fcf85..9f18dff 100644
--- a/FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
+++ b/FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
@@ -2,7 +2,7 @@
   "executed_at_utc": "2026-08-14T08:05:07.817023+00:00",
   "scope": "full suite including public submission path sanitization",
   "python_version": "3.12.13",
-  "python_executable": "<ABSOLUTE_PATH>",
+  "python_executable": "<ABSOLUTE_PATH>",
   "test_file": "tests/test_feature_pipeline.py",
   "tests_run": 51,
   "failures": 0,
diff --git a/FINAL_SUBMISSION/evidence/round4_environment_install.log b/FINAL_SUBMISSION/evidence/round4_environment_install.log
index 87a3b7f..d6575b9 100644
--- a/FINAL_SUBMISSION/evidence/round4_environment_install.log
+++ b/FINAL_SUBMISSION/evidence/round4_environment_install.log
@@ -1,20 +1,20 @@
-$ "<LOCAL_USER_CACHE>\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" --version
+$ "<LOCAL_USER_CACHE>\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" --version
 Python 3.12.13

 [exit_code=0]

-$ "<LOCAL_USER_CACHE>\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m pip index versions httpx2
+$ "<LOCAL_USER_CACHE>\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m pip index versions httpx2
 httpx2 (2.10.0)
 Available versions: 2.10.0, 2.9.1, 2.9.0, 2.8.0, 2.7.0, 2.6.0, 2.5.0, 2.4.0, 2.3.0, 2.2.0, 2.1.0, 2.0.0

 [exit_code=0]

-$ "<LOCAL_USER_CACHE>\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv <PROJECT_ROOT>\.venv_round4
+$ "<LOCAL_USER_CACHE>\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv <PROJECT_ROOT>\.venv_round4

 [exit_code=0]

-$ <PROJECT_ROOT>\.venv_round4\Scripts\python.exe -m pip install --upgrade pip
-Requirement already satisfied: pip in <PROJECT_ROOT>\.venv_round4\lib\site-packages (25.0.1)
+$ <PROJECT_ROOT>\.venv_round4\Scripts\python.exe -m pip install --upgrade pip
+Requirement already satisfied: pip in <PROJECT_ROOT>\.venv_round4\lib\site-packages (25.0.1)
 Collecting pip
   Downloading pip-26.2.1-py3-none-any.whl.metadata (4.6 kB)
 Downloading pip-26.2.1-py3-none-any.whl (1.8 MB)
@@ -28,182 +28,182 @@ Successfully installed pip-26.2.1

 [exit_code=0]

-$ <PROJECT_ROOT>\.venv_round4\Scripts\python.exe -m pip install -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt
-Collecting numpy==2.5.2 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 2))
+$ <PROJECT_ROOT>\.venv_round4\Scripts\python.exe -m pip install -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt
+Collecting numpy==2.5.2 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 2))
   Using cached numpy-2.5.2-cp312-cp312-win_amd64.whl.metadata (6.6 kB)
-Collecting pandas==3.0.5 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 3))
+Collecting pandas==3.0.5 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 3))
   Using cached pandas-3.0.5-cp312-cp312-win_amd64.whl.metadata (19 kB)
-Collecting scikit-learn==1.9.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 4))
+Collecting scikit-learn==1.9.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 4))
   Using cached scikit_learn-1.9.0-cp312-cp312-win_amd64.whl.metadata (11 kB)
-Collecting xgboost==3.4.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 5))
+Collecting xgboost==3.4.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 5))
   Using cached xgboost-3.4.0-py3-none-win_amd64.whl.metadata (2.0 kB)
-Collecting joblib==1.5.3 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 6))
+Collecting joblib==1.5.3 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 6))
   Using cached joblib-1.5.3-py3-none-any.whl.metadata (5.5 kB)
-Collecting pyarrow==24.0.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 7))
+Collecting pyarrow==24.0.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 7))
   Using cached pyarrow-24.0.0-cp312-cp312-win_amd64.whl.metadata (3.0 kB)
-Collecting fastapi==0.141.1 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
+Collecting fastapi==0.141.1 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
   Using cached fastapi-0.141.1-py3-none-any.whl.metadata (27 kB)
-Collecting httpx2==2.10.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
+Collecting httpx2==2.10.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
   Using cached httpx2-2.10.0-py3-none-any.whl.metadata (10 kB)
-Collecting uvicorn==0.52.2 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 10))
+Collecting uvicorn==0.52.2 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 10))
   Using cached uvicorn-0.52.2-py3-none-any.whl.metadata (6.6 kB)
-Collecting pydantic==2.13.4 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 11))
+Collecting pydantic==2.13.4 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 11))
   Using cached pydantic-2.13.4-py3-none-any.whl.metadata (109 kB)
-Collecting streamlit==1.61.1 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting streamlit==1.61.1 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached streamlit-1.61.1-py3-none-any.whl.metadata (10 kB)
-Collecting requests==2.34.2 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 13))
+Collecting requests==2.34.2 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 13))
   Using cached requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
-Collecting matplotlib==3.11.1 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
+Collecting matplotlib==3.11.1 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
   Using cached matplotlib-3.11.1-cp312-cp312-win_amd64.whl.metadata (80 kB)
-Collecting seaborn==0.13.2 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 15))
+Collecting seaborn==0.13.2 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 15))
   Using cached seaborn-0.13.2-py3-none-any.whl.metadata (5.4 kB)
-Collecting nbformat==5.11.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting nbformat==5.11.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached nbformat-5.11.0-py3-none-any.whl.metadata (3.7 kB)
-Collecting nbclient==0.11.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 17))
+Collecting nbclient==0.11.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 17))
   Using cached nbclient-0.11.0-py3-none-any.whl.metadata (7.3 kB)
-Collecting ipykernel==7.3.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting ipykernel==7.3.0 (from -r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached ipykernel-7.3.0-py3-none-any.whl.metadata (4.5 kB)
-Collecting python-dateutil>=2.8.2 (from pandas==3.0.5->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 3))
+Collecting python-dateutil>=2.8.2 (from pandas==3.0.5->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 3))
   Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
-Collecting tzdata (from pandas==3.0.5->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 3))
+Collecting tzdata (from pandas==3.0.5->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 3))
   Using cached tzdata-2026.3-py2.py3-none-any.whl.metadata (1.4 kB)
-Collecting scipy>=1.10.0 (from scikit-learn==1.9.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 4))
+Collecting scipy>=1.10.0 (from scikit-learn==1.9.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 4))
   Using cached scipy-1.18.0-cp312-cp312-win_amd64.whl.metadata (61 kB)
-Collecting narwhals>=2.0.1 (from scikit-learn==1.9.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 4))
+Collecting narwhals>=2.0.1 (from scikit-learn==1.9.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 4))
   Using cached narwhals-2.24.0-py3-none-any.whl.metadata (15 kB)
-Collecting threadpoolctl>=3.5.0 (from scikit-learn==1.9.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 4))
+Collecting threadpoolctl>=3.5.0 (from scikit-learn==1.9.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 4))
   Using cached threadpoolctl-3.6.0-py3-none-any.whl.metadata (13 kB)
-Collecting starlette>=0.46.0 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
+Collecting starlette>=0.46.0 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
   Using cached starlette-1.6.0-py3-none-any.whl.metadata (6.4 kB)
-Collecting typing-extensions>=4.8.0 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
+Collecting typing-extensions>=4.8.0 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
   Using cached typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
-Collecting typing-inspection>=0.4.2 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
+Collecting typing-inspection>=0.4.2 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
   Using cached typing_inspection-0.4.4-py3-none-any.whl.metadata (2.6 kB)
-Collecting annotated-doc>=0.0.2 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
+Collecting annotated-doc>=0.0.2 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
   Using cached annotated_doc-0.0.5-py3-none-any.whl.metadata (6.5 kB)
-Collecting anyio>=4.10 (from httpx2==2.10.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
+Collecting anyio>=4.10 (from httpx2==2.10.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
   Using cached anyio-4.14.2-py3-none-any.whl.metadata (4.6 kB)
-Collecting httpcore2==2.10.0 (from httpx2==2.10.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
+Collecting httpcore2==2.10.0 (from httpx2==2.10.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
   Using cached httpcore2-2.10.0-py3-none-any.whl.metadata (25 kB)
-Collecting idna>=3.18 (from httpx2==2.10.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
+Collecting idna>=3.18 (from httpx2==2.10.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
   Using cached idna-3.18-py3-none-any.whl.metadata (6.1 kB)
-Collecting truststore>=0.10 (from httpx2==2.10.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
+Collecting truststore>=0.10 (from httpx2==2.10.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 9))
   Using cached truststore-0.10.4-py3-none-any.whl.metadata (4.4 kB)
-Collecting click>=7.0 (from uvicorn==0.52.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 10))
+Collecting click>=7.0 (from uvicorn==0.52.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 10))
   Using cached click-8.4.2-py3-none-any.whl.metadata (2.6 kB)
-Collecting h11>=0.8 (from uvicorn==0.52.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 10))
+Collecting h11>=0.8 (from uvicorn==0.52.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 10))
   Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
-Collecting annotated-types>=0.6.0 (from pydantic==2.13.4->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 11))
+Collecting annotated-types>=0.6.0 (from pydantic==2.13.4->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 11))
   Using cached annotated_types-0.8.0-py3-none-any.whl.metadata (15 kB)
-Collecting pydantic-core==2.46.4 (from pydantic==2.13.4->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 11))
+Collecting pydantic-core==2.46.4 (from pydantic==2.13.4->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 11))
   Using cached pydantic_core-2.46.4-cp312-cp312-win_amd64.whl.metadata (6.7 kB)
-Collecting altair!=5.4.0,!=5.4.1,<7,>=5.0.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting altair!=5.4.0,!=5.4.1,<7,>=5.0.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached altair-6.2.2-py3-none-any.whl.metadata (11 kB)
-Collecting blinker<2,>=1.5.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting blinker<2,>=1.5.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
-Collecting packaging>=20 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting packaging>=20 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached packaging-26.3-py3-none-any.whl.metadata (3.5 kB)
-Collecting pillow<13,>=7.1.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting pillow<13,>=7.1.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached pillow-12.3.0-cp312-cp312-win_amd64.whl.metadata (9.3 kB)
-Collecting pydeck<1,>=0.8.0b4 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting pydeck<1,>=0.8.0b4 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached pydeck-0.9.3-py2.py3-none-any.whl.metadata (4.2 kB)
-Collecting protobuf<8,>=5.26.1 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting protobuf<8,>=5.26.1 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached protobuf-7.35.1-cp310-abi3-win_amd64.whl.metadata (595 bytes)
-Collecting tenacity<10,>=8.1.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting tenacity<10,>=8.1.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached tenacity-9.1.4-py3-none-any.whl.metadata (1.2 kB)
-Collecting toml<2,>=0.10.1 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting toml<2,>=0.10.1 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached toml-0.10.2-py2.py3-none-any.whl.metadata (7.1 kB)
-Collecting starlette>=0.46.0 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
+Collecting starlette>=0.46.0 (from fastapi==0.141.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 8))
   Using cached starlette-1.3.1-py3-none-any.whl.metadata (6.4 kB)
-Collecting httptools<1,>=0.6.3 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting httptools<1,>=0.6.3 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached httptools-0.8.0-cp312-cp312-win_amd64.whl.metadata (3.7 kB)
-Collecting python-multipart<1,>=0.0.10 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting python-multipart<1,>=0.0.10 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached python_multipart-0.0.32-py3-none-any.whl.metadata (2.1 kB)
-Collecting websockets<17,>=12.0.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting websockets<17,>=12.0.0 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached websockets-16.1.1-cp312-cp312-win_amd64.whl.metadata (7.0 kB)
-Collecting itsdangerous<3,>=2.1.2 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting itsdangerous<3,>=2.1.2 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
-Collecting watchdog<7,>=2.1.5 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting watchdog<7,>=2.1.5 (from streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached watchdog-6.0.0-py3-none-win_amd64.whl.metadata (44 kB)
-Collecting charset_normalizer<4,>=2 (from requests==2.34.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 13))
+Collecting charset_normalizer<4,>=2 (from requests==2.34.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 13))
   Using cached charset_normalizer-3.5.0-cp312-cp312-win_amd64.whl.metadata (44 kB)
-Collecting urllib3<3,>=1.26 (from requests==2.34.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 13))
+Collecting urllib3<3,>=1.26 (from requests==2.34.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 13))
   Using cached urllib3-2.7.0-py3-none-any.whl.metadata (6.9 kB)
-Collecting certifi>=2023.5.7 (from requests==2.34.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 13))
+Collecting certifi>=2023.5.7 (from requests==2.34.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 13))
   Using cached certifi-2026.7.22-py3-none-any.whl.metadata (2.5 kB)
-Collecting contourpy>=1.0.1 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
+Collecting contourpy>=1.0.1 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
   Using cached contourpy-1.3.3-cp312-cp312-win_amd64.whl.metadata (5.5 kB)
-Collecting cycler>=0.10 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
+Collecting cycler>=0.10 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
   Using cached cycler-0.12.1-py3-none-any.whl.metadata (3.8 kB)
-Collecting fonttools>=4.28.2 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
+Collecting fonttools>=4.28.2 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
   Using cached fonttools-4.63.0-cp312-cp312-win_amd64.whl.metadata (121 kB)
-Collecting kiwisolver>=1.3.1 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
+Collecting kiwisolver>=1.3.1 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
   Using cached kiwisolver-1.5.0-cp312-cp312-win_amd64.whl.metadata (5.2 kB)
-Collecting pyparsing>=3 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
+Collecting pyparsing>=3 (from matplotlib==3.11.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 14))
   Using cached pyparsing-3.3.2-py3-none-any.whl.metadata (5.8 kB)
-Collecting fastjsonschema>=2.15 (from nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting fastjsonschema>=2.15 (from nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached fastjsonschema-2.22.1-py3-none-any.whl.metadata (2.1 kB)
-Collecting jsonschema>=2.6 (from nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting jsonschema>=2.6 (from nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached jsonschema-4.26.0-py3-none-any.whl.metadata (7.6 kB)
-Collecting jupyter-core!=5.0.*,>=4.12 (from nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting jupyter-core!=5.0.*,>=4.12 (from nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached jupyter_core-5.9.1-py3-none-any.whl.metadata (1.5 kB)
-Collecting traitlets>=5.1 (from nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting traitlets>=5.1 (from nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached traitlets-5.16.1-py3-none-any.whl.metadata (10 kB)
-Collecting jupyter-client>=7.0.0 (from nbclient==0.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 17))
+Collecting jupyter-client>=7.0.0 (from nbclient==0.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 17))
   Using cached jupyter_client-8.9.1-py3-none-any.whl.metadata (8.5 kB)
-Collecting comm>=0.1.1 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting comm>=0.1.1 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached comm-0.2.3-py3-none-any.whl.metadata (3.7 kB)
-Collecting debugpy>=1.6.5 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting debugpy>=1.6.5 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached debugpy-1.8.21-cp312-cp312-win_amd64.whl.metadata (1.5 kB)
-Collecting ipython>=7.23.1 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting ipython>=7.23.1 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached ipython-9.16.1-py3-none-any.whl.metadata (4.6 kB)
-Collecting matplotlib-inline>=0.1 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting matplotlib-inline>=0.1 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached matplotlib_inline-0.2.2-py3-none-any.whl.metadata (2.4 kB)
-Collecting nest-asyncio2>=1.7.0 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting nest-asyncio2>=1.7.0 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached nest_asyncio2-1.7.2-py3-none-any.whl.metadata (6.3 kB)
-Collecting psutil>=5.7 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting psutil>=5.7 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached psutil-7.2.2-cp37-abi3-win_amd64.whl.metadata (22 kB)
-Collecting pyzmq>=25 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting pyzmq>=25 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached pyzmq-27.1.0-cp312-abi3-win_amd64.whl.metadata (6.0 kB)
-Collecting tornado>=6.4.1 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting tornado>=6.4.1 (from ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached tornado-6.5.8-cp39-abi3-win_amd64.whl.metadata (2.9 kB)
-Collecting jinja2 (from altair!=5.4.0,!=5.4.1,<7,>=5.0.0->streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting jinja2 (from altair!=5.4.0,!=5.4.1,<7,>=5.0.0->streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
-Collecting colorama (from click>=7.0->uvicorn==0.52.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 10))
+Collecting colorama (from click>=7.0->uvicorn==0.52.2->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 10))
   Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
-Collecting ipython-pygments-lexers>=1.0.0 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting ipython-pygments-lexers>=1.0.0 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached ipython_pygments_lexers-1.1.1-py3-none-any.whl.metadata (1.1 kB)
-Collecting jedi>=0.18.2 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting jedi>=0.18.2 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached jedi-0.20.0-py2.py3-none-any.whl.metadata (23 kB)
-Collecting prompt_toolkit<3.1.0,>=3.0.41 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting prompt_toolkit<3.1.0,>=3.0.41 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached prompt_toolkit-3.0.53-py3-none-any.whl.metadata (6.4 kB)
-Collecting pygments>=2.14.0 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting pygments>=2.14.0 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached pygments-2.20.0-py3-none-any.whl.metadata (2.5 kB)
-Collecting stack_data>=0.6.0 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting stack_data>=0.6.0 (from ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached stack_data-0.6.3-py3-none-any.whl.metadata (18 kB)
-Collecting wcwidth>=0.1.4 (from prompt_toolkit<3.1.0,>=3.0.41->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting wcwidth>=0.1.4 (from prompt_toolkit<3.1.0,>=3.0.41->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached wcwidth-0.8.2-py3-none-any.whl.metadata (43 kB)
-Collecting parso<0.9.0,>=0.8.6 (from jedi>=0.18.2->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting parso<0.9.0,>=0.8.6 (from jedi>=0.18.2->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached parso-0.8.7-py2.py3-none-any.whl.metadata (8.2 kB)
-Collecting MarkupSafe>=2.0 (from jinja2->altair!=5.4.0,!=5.4.1,<7,>=5.0.0->streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
+Collecting MarkupSafe>=2.0 (from jinja2->altair!=5.4.0,!=5.4.1,<7,>=5.0.0->streamlit==1.61.1->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 12))
   Using cached markupsafe-3.0.3-cp312-cp312-win_amd64.whl.metadata (2.8 kB)
-Collecting attrs>=22.2.0 (from jsonschema>=2.6->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting attrs>=22.2.0 (from jsonschema>=2.6->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached attrs-26.1.0-py3-none-any.whl.metadata (8.8 kB)
-Collecting jsonschema-specifications>=2023.03.6 (from jsonschema>=2.6->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting jsonschema-specifications>=2023.03.6 (from jsonschema>=2.6->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached jsonschema_specifications-2025.9.1-py3-none-any.whl.metadata (2.9 kB)
-Collecting referencing>=0.28.4 (from jsonschema>=2.6->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting referencing>=0.28.4 (from jsonschema>=2.6->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached referencing-0.37.0-py3-none-any.whl.metadata (2.8 kB)
-Collecting rpds-py>=0.25.0 (from jsonschema>=2.6->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting rpds-py>=0.25.0 (from jsonschema>=2.6->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Using cached rpds_py-2026.6.3-cp312-cp312-win_amd64.whl.metadata (4.2 kB)
-Collecting platformdirs>=2.5 (from jupyter-core!=5.0.*,>=4.12->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
+Collecting platformdirs>=2.5 (from jupyter-core!=5.0.*,>=4.12->nbformat==5.11.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 16))
   Downloading platformdirs-4.11.3-py3-none-any.whl.metadata (5.5 kB)
-Collecting six>=1.5 (from python-dateutil>=2.8.2->pandas==3.0.5->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 3))
+Collecting six>=1.5 (from python-dateutil>=2.8.2->pandas==3.0.5->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 3))
   Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
-Collecting executing>=1.2.0 (from stack_data>=0.6.0->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting executing>=1.2.0 (from stack_data>=0.6.0->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached executing-2.2.1-py2.py3-none-any.whl.metadata (8.9 kB)
-Collecting asttokens>=2.1.0 (from stack_data>=0.6.0->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting asttokens>=2.1.0 (from stack_data>=0.6.0->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached asttokens-3.0.2-py3-none-any.whl.metadata (5.7 kB)
-Collecting pure-eval (from stack_data>=0.6.0->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
+Collecting pure-eval (from stack_data>=0.6.0->ipython>=7.23.1->ipykernel==7.3.0->-r <PROJECT_ROOT>\5.UNG_DUNG\5.3.config\requirements.txt (line 18))
   Using cached pure_eval-0.2.3-py3-none-any.whl.metadata (6.3 kB)
 Using cached numpy-2.5.2-cp312-cp312-win_amd64.whl (12.5 MB)
 Using cached pandas-3.0.5-cp312-cp312-win_amd64.whl (9.8 MB)
@@ -298,7 +298,7 @@ Successfully installed MarkupSafe-3.0.3 altair-6.2.2 annotated-doc-0.0.5 annotat

 [exit_code=0]

-$ <PROJECT_ROOT>\.venv_round4\Scripts\python.exe -c "
+$ <PROJECT_ROOT>\.venv_round4\Scripts\python.exe -c "
 import importlib.metadata as metadata
 import json
 import platform
@@ -321,6 +321,6 @@ print(json.dumps({
     \"fastapi_testclient_smoke\": \"PASS\",
 }))
 "
-{"python_version": "3.12.13", "python_executable": "<ABSOLUTE_PATH>", "packages": {"pip": "26.2.1", "httpx2": "2.10.0", "fastapi": "0.141.1", "starlette": "1.3.1", "xgboost": "3.4.0", "scikit-learn": "1.9.0", "numpy": "2.5.2", "pandas": "3.0.5", "joblib": "1.5.3", "streamlit": "1.61.1", "nbformat": "5.11.0", "nbclient": "0.11.0"}, "fastapi_testclient_smoke": "PASS"}
+{"python_version": "3.12.13", "python_executable": "<ABSOLUTE_PATH>", "packages": {"pip": "26.2.1", "httpx2": "2.10.0", "fastapi": "0.141.1", "starlette": "1.3.1", "xgboost": "3.4.0", "scikit-learn": "1.9.0", "numpy": "2.5.2", "pandas": "3.0.5", "joblib": "1.5.3", "streamlit": "1.61.1", "nbformat": "5.11.0", "nbclient": "0.11.0"}, "fastapi_testclient_smoke": "PASS"}

 [exit_code=0]
diff --git a/FINAL_SUBMISSION/evidence/round4_environment_validation.json b/FINAL_SUBMISSION/evidence/round4_environment_validation.json
index 6183855..7780814 100644
--- a/FINAL_SUBMISSION/evidence/round4_environment_validation.json
+++ b/FINAL_SUBMISSION/evidence/round4_environment_validation.json
@@ -1,7 +1,7 @@
 {
   "generated_at_utc": "2026-08-14T05:57:25.822682+00:00",
   "python_version": "3.12.13",
-  "python_executable": "<PROJECT_ROOT>\\.venv_round4\\Scripts\\python.exe",
+  "python_executable": "<ABSOLUTE_PATH>",
   "requirements_file": "5.UNG_DUNG/5.3.config/requirements.txt",
   "requirements_install_status": "PASS",
   "http_client_package": "httpx2",
@@ -18,4 +18,4 @@
   "pip_index_httpx2_version_verified": "2.10.0",
   "install_log": "5.UNG_DUNG/validation/round4_environment_install.log",
   "status": "PASS"
-}
+}
\ No newline at end of file
diff --git a/FINAL_SUBMISSION/evidence/round4_notebook_execution_status.json b/FINAL_SUBMISSION/evidence/round4_notebook_execution_status.json
index ae1d3e4..d342eee 100644
--- a/FINAL_SUBMISSION/evidence/round4_notebook_execution_status.json
+++ b/FINAL_SUBMISSION/evidence/round4_notebook_execution_status.json
@@ -2,7 +2,7 @@
   "recorded_at_utc": "2026-08-14T06:04:23.207057+00:00",
   "kernel_name": "hitradar-round4",
   "python_version": "3.12.13",
-  "python_executable": "<PROJECT_ROOT>\\.venv_round4\\Scripts\\python.exe",
+  "python_executable": "<ABSOLUTE_PATH>",
   "xgboost_version": "3.4.0",
   "scikit_learn_version": "1.9.0",
   "notebooks": [
@@ -32,4 +32,4 @@
     }
   ],
   "status": "PASS"
-}
+}
\ No newline at end of file
diff --git a/FINAL_SUBMISSION/evidence/round4_test_results.json b/FINAL_SUBMISSION/evidence/round4_test_results.json
index 93ab71f..90c04c6 100644
--- a/FINAL_SUBMISSION/evidence/round4_test_results.json
+++ b/FINAL_SUBMISSION/evidence/round4_test_results.json
@@ -1,11 +1,11 @@
 {
   "executed_at_utc": "2026-08-14T06:18:12.579125+00:00",
   "python_version": "3.12.13",
-  "python_executable": "<PROJECT_ROOT>\\.venv_round4\\Scripts\\python.exe",
+  "python_executable": "<ABSOLUTE_PATH>",
   "test_file": "tests/test_feature_pipeline.py",
   "tests_run": 39,
   "failures": 0,
   "errors": 0,
   "skipped": 0,
   "status": "PASS"
-}
+}
\ No newline at end of file
diff --git a/FINAL_SUBMISSION/evidence/shap_requirement_status.json b/FINAL_SUBMISSION/evidence/shap_requirement_status.json
index 3288127..e8bfe3a 100644
--- a/FINAL_SUBMISSION/evidence/shap_requirement_status.json
+++ b/FINAL_SUBMISSION/evidence/shap_requirement_status.json
@@ -4,7 +4,7 @@
   "reason": "The readable checklist labels SHAP as an advanced item (SHAP (nâng cao)), not an explicit mandatory requirement. Existing grouped/transformed feature importance and error diagnostics are retained; no model retraining was triggered.",
   "sources_inspected": [
     {
-      "path": "<USER_DOWNLOADS>/Task Checklist for Each Notebook.docx",
+      "path": "<USER_DOWNLOADS>/Task Checklist for Each Notebook.docx",
       "status": "readable_inspected",
       "evidence": "Notebook 05, section V lists Feature Importance followed by SHAP (nâng cao). Notebook 06 repeatedly requires Feature Importance but does not explicitly require SHAP."
     },
diff --git a/FINAL_SUBMISSION/notebooks/05_feature_engineering.ipynb b/FINAL_SUBMISSION/notebooks/05_feature_engineering.ipynb
index 757c5c8..6a3d0d7 100644
--- a/FINAL_SUBMISSION/notebooks/05_feature_engineering.ipynb
+++ b/FINAL_SUBMISSION/notebooks/05_feature_engineering.ipynb
@@ -29,7 +29,7 @@
      "name": "stdout",
      "output_type": "stream",
      "text": [
-      "Project root: <PROJECT_ROOT>\n"
+      "Project root: <ABSOLUTE_PATH>"
      ]
     }
    ],
@@ -2055,15 +2055,15 @@
      "output_type": "stream",
      "text": [
       "{\n",
-      "  \"engineered\": \"<ABSOLUTE_PATH>\",\n",
-      "  \"candidate_register\": \"<ABSOLUTE_PATH>\",\n",
-      "  \"candidate_evaluation\": \"<ABSOLUTE_PATH>\",\n",
-      "  \"keep_drop\": \"<ABSOLUTE_PATH>\",\n",
-      "  \"validation\": \"<ABSOLUTE_PATH>\",\n",
-      "  \"contract\": \"<ABSOLUTE_PATH>\",\n",
-      "  \"statistics\": \"<ABSOLUTE_PATH>\",\n",
-      "  \"dependency_audit\": \"<ABSOLUTE_PATH>\",\n",
-      "  \"immutability\": \"<ABSOLUTE_PATH>\"\n",
+      "  \"engineered\": \"<ABSOLUTE_PATH>",\n",
+      "  \"candidate_register\": \"<ABSOLUTE_PATH>",\n",
+      "  \"candidate_evaluation\": \"<ABSOLUTE_PATH>",\n",
+      "  \"keep_drop\": \"<ABSOLUTE_PATH>",\n",
+      "  \"validation\": \"<ABSOLUTE_PATH>",\n",
+      "  \"contract\": \"<ABSOLUTE_PATH>",\n",
+      "  \"statistics\": \"<ABSOLUTE_PATH>",\n",
+      "  \"dependency_audit\": \"<ABSOLUTE_PATH>",\n",
+      "  \"immutability\": \"<ABSOLUTE_PATH>"\n",
       "}\n"
      ]
     }
@@ -2574,7 +2574,7 @@
      "name": "stdout",
      "output_type": "stream",
      "text": [
-      "Saved cluster model: <PROJECT_ROOT>\\4.MODELS\\hitradar_secondary<NETWORK_PATH>
+      "Saved cluster model: <ABSOLUTE_PATH>"
      ]
     }
    ],
@@ -2770,7 +2770,7 @@
      "name": "stdout",
      "output_type": "stream",
      "text": [
-      "Saved recommender: <PROJECT_ROOT>\\4.MODELS\\hitradar_secondary<NETWORK_PATH>
+      "Saved recommender: <ABSOLUTE_PATH>"
      ]
     }
    ],
diff --git a/FINAL_SUBMISSION/notebooks/06_machine_learning.ipynb b/FINAL_SUBMISSION/notebooks/06_machine_learning.ipynb
index b1d8b18..48a9253 100644
--- a/FINAL_SUBMISSION/notebooks/06_machine_learning.ipynb
+++ b/FINAL_SUBMISSION/notebooks/06_machine_learning.ipynb
@@ -27,7 +27,7 @@
      "name": "stdout",
      "output_type": "stream",
      "text": [
-      "Project root: <PROJECT_ROOT>\n"
+      "Project root: <ABSOLUTE_PATH>"
      ]
     }
    ],
diff --git a/FINAL_SUBMISSION/notebooks/07_ai_deployment.ipynb b/FINAL_SUBMISSION/notebooks/07_ai_deployment.ipynb
index a88e355..5aa2771 100644
--- a/FINAL_SUBMISSION/notebooks/07_ai_deployment.ipynb
+++ b/FINAL_SUBMISSION/notebooks/07_ai_deployment.ipynb
@@ -27,7 +27,7 @@
      "name": "stdout",
      "output_type": "stream",
      "text": [
-      "Project root: <PROJECT_ROOT>\n"
+      "Project root: <ABSOLUTE_PATH>"
      ]
     },
     {
@@ -701,7 +701,7 @@
      "name": "stdout",
      "output_type": "stream",
      "text": [
-      "Saved: <PROJECT_ROOT>\\5.UNG_DUNG\\validation<NETWORK_PATH>
+      "Saved: <ABSOLUTE_PATH>",
       "ROUND 4 END-TO-END STATUS: PASS\n"
      ]
     }
```

## `git diff --cached -- . :(exclude)FINAL_SUBMISSION/GIT_EVIDENCE.md :(exclude)FINAL_SUBMISSION/SUBMISSION_MANIFEST.json`

```text
diff --git a/.gitignore b/.gitignore
index 919ddcb..9ee9113 100644
--- a/.gitignore
+++ b/.gitignore
@@ -32,6 +32,7 @@ build/
 # Virtual environments
 # ============================================================
 .venv/
+.venv*/
 venv/
 env/
 ENV/
@@ -58,6 +59,7 @@ scratch/ipython/
 4.MODELS/hitradar_secondary/*.joblib
 4.MODELS/hitradar_secondary/*.parquet
 5.DATA/processed/features_engineered.parquet
+5.DATA/processed/*.parquet
 4.MODELS/4.2.evaluation/*test_predictions*.parquet

 # ============================================================
@@ -82,6 +84,11 @@ desktop.ini
 *.suo
 *.user

+# Local validation cache / temporary sync files
+.cache/
+.tmp/
+*.tmp
+
 # ============================================================
 # Feature 2.1 — Split ID files (large, regeneratable)
 # ============================================================
diff --git a/5.UNG_DUNG/validation/public_evidence_sanitization.json b/5.UNG_DUNG/validation/public_evidence_sanitization.json
index 863aeb4..5f89a80 100644
--- a/5.UNG_DUNG/validation/public_evidence_sanitization.json
+++ b/5.UNG_DUNG/validation/public_evidence_sanitization.json
@@ -6,7 +6,7 @@
     {
       "file": "evidence/public_path_hotfix_test_results.json",
       "replacement_counts": {
-        "project_root": 1
+        "other_absolute_paths": 1
       }
     },
     {
@@ -53,7 +53,7 @@
         "project_root": 94,
         "user_cache": 3,
         "downloads": 1,
-        "other_absolute_paths": 20
+        "other_absolute_paths": 25
       }
     },
     {
@@ -77,13 +77,13 @@
     }
   ],
   "replacement_counts": {
-    "project_root": 199,
+    "project_root": 198,
     "python_executable": 0,
     "user_home": 0,
     "user_cache": 6,
     "downloads": 2,
     "temp": 0,
-    "other_absolute_paths": 30
+    "other_absolute_paths": 36
   },
   "raw_canonical_files_modified": false,
   "raw_canonical_checksums": [
diff --git a/5.UNG_DUNG/validation/public_path_hotfix_test_results.json b/5.UNG_DUNG/validation/public_path_hotfix_test_results.json
index 4907869..9f18dff 100644
--- a/5.UNG_DUNG/validation/public_path_hotfix_test_results.json
+++ b/5.UNG_DUNG/validation/public_path_hotfix_test_results.json
@@ -1,8 +1,8 @@
 {
-  "executed_at_utc": "2026-08-14T06:42:16.800144+00:00",
+  "executed_at_utc": "2026-08-14T08:05:07.817023+00:00",
   "scope": "full suite including public submission path sanitization",
   "python_version": "3.12.13",
-  "python_executable": "<ABSOLUTE_PATH>",
+  "python_executable": "<ABSOLUTE_PATH>",
   "test_file": "tests/test_feature_pipeline.py",
   "tests_run": 51,
   "failures": 0,
diff --git a/9.SCRIPTS/generate_final_submission.py b/9.SCRIPTS/generate_final_submission.py
index 2adee3d..6036037 100644
--- a/9.SCRIPTS/generate_final_submission.py
+++ b/9.SCRIPTS/generate_final_submission.py
@@ -191,7 +191,17 @@ def collect_git_evidence() -> str:
     commands = [
         ["git", "status", "--short"], ["git", "branch", "--show-current"],
         ["git", "log", "--oneline", "--decorate", "-n", "20"],
-        ["git", "branch", "--list"], ["git", "remote", "-v"], ["git", "diff", "--", "."],
+        ["git", "branch", "--list"], ["git", "remote", "-v"],
+        [
+            "git", "diff", "--", ".",
+            ":(exclude)FINAL_SUBMISSION/GIT_EVIDENCE.md",
+            ":(exclude)FINAL_SUBMISSION/SUBMISSION_MANIFEST.json",
+        ],
+        [
+            "git", "diff", "--cached", "--", ".",
+            ":(exclude)FINAL_SUBMISSION/GIT_EVIDENCE.md",
+            ":(exclude)FINAL_SUBMISSION/SUBMISSION_MANIFEST.json",
+        ],
     ]
     sections = ["# Git Evidence", "", "All output below was collected from the actual working tree."]
     for command in commands:
@@ -204,7 +214,9 @@ def collect_git_evidence() -> str:
             errors="replace",
             check=False,
         )
-        sections += ["", f"## `{' '.join(command)}`", "", "```text", completed.stdout or completed.stderr or "(no output)", "```"]
+        raw_output = completed.stdout or completed.stderr or "(no output)"
+        output = "\n".join(line.rstrip() for line in raw_output.splitlines())
+        sections += ["", f"## `{' '.join(command)}`", "", "```text", output, "```"]
     return "\n".join(sections) + "\n"


diff --git a/FINAL_SUBMISSION/evidence/public_evidence_sanitization.json b/FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
index 863aeb4..5f89a80 100644
--- a/FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
+++ b/FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
@@ -6,7 +6,7 @@
     {
       "file": "evidence/public_path_hotfix_test_results.json",
       "replacement_counts": {
-        "project_root": 1
+        "other_absolute_paths": 1
       }
     },
     {
@@ -53,7 +53,7 @@
         "project_root": 94,
         "user_cache": 3,
         "downloads": 1,
-        "other_absolute_paths": 20
+        "other_absolute_paths": 25
       }
     },
     {
@@ -77,13 +77,13 @@
     }
   ],
   "replacement_counts": {
-    "project_root": 199,
+    "project_root": 198,
     "python_executable": 0,
     "user_home": 0,
     "user_cache": 6,
     "downloads": 2,
     "temp": 0,
-    "other_absolute_paths": 30
+    "other_absolute_paths": 36
   },
   "raw_canonical_files_modified": false,
   "raw_canonical_checksums": [
diff --git a/FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json b/FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
index c225a45..92fcf85 100644
--- a/FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
+++ b/FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
@@ -1,8 +1,8 @@
 {
-  "executed_at_utc": "2026-08-14T06:42:16.800144+00:00",
+  "executed_at_utc": "2026-08-14T08:05:07.817023+00:00",
   "scope": "full suite including public submission path sanitization",
   "python_version": "3.12.13",
-  "python_executable": "<PROJECT_ROOT>\\.venv_round4\\Scripts\\python.exe",
+  "python_executable": "<ABSOLUTE_PATH>",
   "test_file": "tests/test_feature_pipeline.py",
   "tests_run": 51,
   "failures": 0,
diff --git a/FINAL_SUBMISSION/scripts/generate_final_submission.py b/FINAL_SUBMISSION/scripts/generate_final_submission.py
index 2adee3d..6036037 100644
--- a/FINAL_SUBMISSION/scripts/generate_final_submission.py
+++ b/FINAL_SUBMISSION/scripts/generate_final_submission.py
@@ -191,7 +191,17 @@ def collect_git_evidence() -> str:
     commands = [
         ["git", "status", "--short"], ["git", "branch", "--show-current"],
         ["git", "log", "--oneline", "--decorate", "-n", "20"],
-        ["git", "branch", "--list"], ["git", "remote", "-v"], ["git", "diff", "--", "."],
+        ["git", "branch", "--list"], ["git", "remote", "-v"],
+        [
+            "git", "diff", "--", ".",
+            ":(exclude)FINAL_SUBMISSION/GIT_EVIDENCE.md",
+            ":(exclude)FINAL_SUBMISSION/SUBMISSION_MANIFEST.json",
+        ],
+        [
+            "git", "diff", "--cached", "--", ".",
+            ":(exclude)FINAL_SUBMISSION/GIT_EVIDENCE.md",
+            ":(exclude)FINAL_SUBMISSION/SUBMISSION_MANIFEST.json",
+        ],
     ]
     sections = ["# Git Evidence", "", "All output below was collected from the actual working tree."]
     for command in commands:
@@ -204,7 +214,9 @@ def collect_git_evidence() -> str:
             errors="replace",
             check=False,
         )
-        sections += ["", f"## `{' '.join(command)}`", "", "```text", completed.stdout or completed.stderr or "(no output)", "```"]
+        raw_output = completed.stdout or completed.stderr or "(no output)"
+        output = "\n".join(line.rstrip() for line in raw_output.splitlines())
+        sections += ["", f"## `{' '.join(command)}`", "", "```text", output, "```"]
     return "\n".join(sections) + "\n"


diff --git a/README.md b/README.md
index 8fc0f01..3224025 100644
--- a/README.md
+++ b/README.md
@@ -1,14 +1,99 @@
 # HitRadar / HitRadar Pro

-The current canonical handoff is under `FINAL_SUBMISSION/`. Run notebooks in
-order: Notebook 05 → Notebook 06 → Notebook 07.
-
-Temporal governance remains `release_year <= 2017` for selection train, 2018
-for validation, `<2019` for final refit, and `>=2019` for the final temporal
-holdout. The corrected Round-2 pipeline did not use the 2019+ horizon for
-winner selection, but that same horizon had been inspected during an earlier
-development iteration.
-
-Deployment allows post-2020 predictions with an explicit temporal-
-extrapolation warning. See `FINAL_SUBMISSION/README_FINAL_SUBMISSION.md` for
-setup commands, evidence, limitations, and the submission manifest.
+HitRadar is a Spotify track analytics project whose main task is popularity regression. Secondary tasks provide KMeans audio clustering and content-based track recommendations. The repository also includes FastAPI and Streamlit interfaces for the validated model artifacts.
+
+## Dataset overview
+
+The canonical processed table contains 586,672 tracks with observed `release_year` values from 1900 through 2021. This processed coverage is distinct from the source dataset's advertised 1921–2020 range. Large source and processed datasets are intentionally not committed; checksums and relative artifact locations are recorded in `FINAL_SUBMISSION/evidence/external_artifact_checksums.json`.
+
+## Project architecture
+
+- `src/`: shared feature engineering, modeling, evaluation, prediction policy, clustering, and recommendation logic.
+- `3.NOTEBOOKS/`: notebook workflow and executed Round-4 snapshots.
+- `4.MODELS/`: small model metadata and evaluation evidence; binary models stay local.
+- `5.UNG_DUNG/`: FastAPI backend, Streamlit frontend, requirements, and validation evidence.
+- `7.ML/`: feature contracts and project ML evidence.
+- `9.SCRIPTS/`: reproducibility, validation, and submission-generation scripts.
+- `tests/`: automated integration and governance tests.
+- `FINAL_SUBMISSION/`: sanitized public evidence snapshot and manifest.
+- `7.QUAN_LY_DU_AN/`: existing project-management evidence.
+
+## Notebook flow
+
+The public workflow is NB01 → NB07. The final ML handoff is:
+
+1. `3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb`
+2. `3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb`
+3. `3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb`
+
+Notebook 05 creates and validates executable engineered columns. Notebook 06 performs temporal model selection and final evaluation. Notebook 07 validates deployment behavior. Historical or superseded materials are kept under `10.ARCHIVE/` rather than treated as canonical notebooks.
+
+## Temporal model-selection protocol
+
+- Selection train: `release_year <= 2017`
+- Validation: `release_year == 2018`
+- Final refit: `release_year < 2019`
+- Final temporal holdout: `release_year >= 2019`
+
+The 2019+ horizon was not used for corrected Round-2 winner selection, but it had been inspected during an earlier development iteration. The repository therefore does not describe it as historically untouched or never observed.
+
+## Locked final model and metrics
+
+The locked winner is **Engineered With-Time / XGBoost**. Committed evidence reports clipped final-holdout metrics:
+
+- MAE: `16.201599`
+- RMSE: `20.594952`
+- R²: `0.259026`
+
+These results are modest and should not be interpreted as causal or uniformly accurate across popularity levels.
+
+## Feature engineering
+
+Round 4 evaluates 16 candidate engineered features and selects 14. The shared `FeatureBuilder` implements interactions, cyclical key encoding, duration/tempo categories, time-derived signals, and leakage-safe train-fitted period statistics. Training, API, Streamlit, and direct prediction use the same feature contract.
+
+## Deployment
+
+The backend is under `5.UNG_DUNG/5.1.backend_api/`; the Streamlit UI is under `5.UNG_DUNG/5.2.frontend/`. Predictions after the product-support cutoff of 2020 remain available but are explicitly labeled temporal extrapolations.
+
+## Reproducibility and setup
+
+Validated evidence uses Python 3.12. From the repository root:
+
+```powershell
+py -3.12 -m venv .venv_round4
+.\.venv_round4\Scripts\python -m pip install --upgrade pip
+.\.venv_round4\Scripts\python -m pip install -r .\5.UNG_DUNG\5.3.config\requirements.txt
+```
+
+The binary model and processed parquet artifacts are not stored in normal Git history. Place locally supplied artifacts at the canonical paths listed in `FINAL_SUBMISSION/evidence/external_artifact_checksums.json` and verify their SHA-256 values before validation.
+
+## Running the interfaces
+
+```powershell
+.\.venv_round4\Scripts\python -m uvicorn 5.UNG_DUNG.5.1.backend_api.api:app
+.\.venv_round4\Scripts\python -m streamlit run .\5.UNG_DUNG\5.2.frontend\streamlit_app.py
+```
+
+If module import rules in a shell do not accept dotted numeric directories, run the API with the repository's documented launcher or import the app by file path as demonstrated in the test suite.
+
+## Validation and tests
+
+```powershell
+.\.venv_round4\Scripts\python .\9.SCRIPTS\run_public_path_hotfix_tests.py
+.\.venv_round4\Scripts\python .\9.SCRIPTS\validate_public_submission.py
+```
+
+The latest public-path suite records 51 tests with 0 failures, 0 errors, and 0 skips. Tests cover feature contracts, temporal isolation, saved-pipeline parity, API/TestClient behavior, Streamlit AppTest behavior, recommendation self-exclusion, environment evidence, manifest integrity, and public-path sanitization.
+
+## Limitations
+
+- Overall R² remains modest and high-popularity tracks are underpredicted more strongly.
+- Time variables are influential, which increases temporal distribution-shift risk.
+- Post-2020 predictions are outside the stated product-support period.
+- KMeans separation is modest (best silhouette approximately 0.242).
+- Recommendation evidence does not include a human relevance study or complete title/artist metadata.
+- Final evidence is predictive and descriptive, not causal.
+
+## Final submission and evidence
+
+`FINAL_SUBMISSION/` is a sanitized public snapshot, not a standalone runtime bundle. It contains executed notebook snapshots, shared source, deployment code, tests, small evidence files, a final audit report, and a checksum manifest. Canonical raw execution evidence and large artifacts remain local for audit and reproducibility.
```

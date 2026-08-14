# Git Evidence

All output below was collected from the actual working tree.

## `git status --short`

```text
 M 3.NOTEBOOKS/3.1.hieu_du_lieu/01_data_understanding.ipynb
 M 3.NOTEBOOKS/3.3.lam_sach_python/01_feature_1_4_cleaning_exploration.ipynb
 M 3.NOTEBOOKS/3.3.lam_sach_python/02_feature_1_4_clean_validation.ipynb
 M 3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb
 M 3.NOTEBOOKS/3.4.eda/01_dataset_overview.ipynb
 M 3.NOTEBOOKS/3.4.eda/02_popularity_analysis.ipynb
 M 3.NOTEBOOKS/3.4.eda/03_audio_features_distribution.ipynb
 M 3.NOTEBOOKS/3.4.eda/04_time_decade_trends.ipynb
 M 3.NOTEBOOKS/3.4.eda/05_artist_genre_analysis.ipynb
 M 3.NOTEBOOKS/3.4.eda/06_correlation_outlier_analysis.ipynb
 M 5.UNG_DUNG/validation/round4_test_results.json
 M 9.SCRIPTS/generate_final_submission.py
 M FINAL_REPOSITORY_HOTFIX_PR.md
 D FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
 D FINAL_SUBMISSION/GIT_EVIDENCE.md
 D FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
 D FINAL_SUBMISSION/SUBMISSION_MANIFEST.json
 D FINAL_SUBMISSION/evidence/external_artifact_checksums.json
 D FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
 M FINAL_SUBMISSION/evidence/round4_test_results.json
 M FINAL_SUBMISSION/scripts/generate_final_submission.py
 M FINAL_SUBMISSION/tests/test_feature_pipeline.py
 M README.md
 M tests/test_feature_pipeline.py
```

## `git branch --show-current`

```text
final-repository-hotfix
```

## `git log --oneline --decorate -n 20`

```text
18fbf2c (HEAD -> final-repository-hotfix, origin/final-repository-hotfix) fix: document NB02 limitation and close final audit gaps
91fb95a chore: regenerate final submission evidence snapshot
a232594 docs: restore submission and project deliverables
2de9657 fix: sanitize repository and externalize runtime artifacts
7f6ee89 (origin/main, origin/HEAD, main) docs: sync README test count with final validation
7238c57 Merge pull request #2 from tandat1512/final-round4-sync
5033ffc (origin/final-round4-sync, final-round4-sync) chore: sanitize public validation executable path
221ea53 chore: finalize Round 4 reproducibility package
34eeeb8 feat: sync HitRadar updates and sanitized final submission
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
```

## `git branch --list`

```text
* final-repository-hotfix
  final-round4-sync
  main
```

## `git remote -v`

```text
origin	https://github.com/tandat1512/hitradar.git (fetch)
origin	https://github.com/tandat1512/hitradar.git (push)
```

## `git diff --stat`

```text
 .../3.1.hieu_du_lieu/01_data_understanding.ipynb   |  50 ++--
 .../01_feature_1_4_cleaning_exploration.ipynb      |  28 ++-
 .../02_feature_1_4_clean_validation.ipynb          |  54 ++--
 3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb    |  53 ++--
 3.NOTEBOOKS/3.4.eda/01_dataset_overview.ipynb      |  27 +-
 3.NOTEBOOKS/3.4.eda/02_popularity_analysis.ipynb   |  27 +-
 .../3.4.eda/03_audio_features_distribution.ipynb   |  27 +-
 3.NOTEBOOKS/3.4.eda/04_time_decade_trends.ipynb    |  27 +-
 3.NOTEBOOKS/3.4.eda/05_artist_genre_analysis.ipynb |  27 +-
 .../3.4.eda/06_correlation_outlier_analysis.ipynb  |  27 +-
 5.UNG_DUNG/validation/round4_test_results.json     |   4 +-
 9.SCRIPTS/generate_final_submission.py             |   2 +
 FINAL_REPOSITORY_HOTFIX_PR.md                      |   5 +-
 FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md             | 130 ----------
 FINAL_SUBMISSION/GIT_EVIDENCE.md                   | 152 -----------
 FINAL_SUBMISSION/README_FINAL_SUBMISSION.md        |  61 -----
 FINAL_SUBMISSION/SUBMISSION_MANIFEST.json          | 278 ---------------------
 .../evidence/external_artifact_checksums.json      |  53 ----
 .../evidence/public_evidence_sanitization.json     |  79 ------
 FINAL_SUBMISSION/evidence/round4_test_results.json |   4 +-
 .../scripts/generate_final_submission.py           |   2 +
 FINAL_SUBMISSION/tests/test_feature_pipeline.py    |  92 ++++++-
 README.md                                          |   4 +-
 tests/test_feature_pipeline.py                     |  88 +++++++
 24 files changed, 455 insertions(+), 846 deletions(-)
```

## `git diff --name-status`

```text
M	3.NOTEBOOKS/3.1.hieu_du_lieu/01_data_understanding.ipynb
M	3.NOTEBOOKS/3.3.lam_sach_python/01_feature_1_4_cleaning_exploration.ipynb
M	3.NOTEBOOKS/3.3.lam_sach_python/02_feature_1_4_clean_validation.ipynb
M	3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb
M	3.NOTEBOOKS/3.4.eda/01_dataset_overview.ipynb
M	3.NOTEBOOKS/3.4.eda/02_popularity_analysis.ipynb
M	3.NOTEBOOKS/3.4.eda/03_audio_features_distribution.ipynb
M	3.NOTEBOOKS/3.4.eda/04_time_decade_trends.ipynb
M	3.NOTEBOOKS/3.4.eda/05_artist_genre_analysis.ipynb
M	3.NOTEBOOKS/3.4.eda/06_correlation_outlier_analysis.ipynb
M	5.UNG_DUNG/validation/round4_test_results.json
M	9.SCRIPTS/generate_final_submission.py
M	FINAL_REPOSITORY_HOTFIX_PR.md
D	FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
D	FINAL_SUBMISSION/GIT_EVIDENCE.md
D	FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
D	FINAL_SUBMISSION/SUBMISSION_MANIFEST.json
D	FINAL_SUBMISSION/evidence/external_artifact_checksums.json
D	FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
M	FINAL_SUBMISSION/evidence/round4_test_results.json
M	FINAL_SUBMISSION/scripts/generate_final_submission.py
M	FINAL_SUBMISSION/tests/test_feature_pipeline.py
M	README.md
M	tests/test_feature_pipeline.py
```

## `git diff --cached --stat`

```text
(no output)
```

## `git diff --cached --name-status`

```text
(no output)
```

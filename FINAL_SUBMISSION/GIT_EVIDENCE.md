# Git Evidence

All output below was collected from the actual working tree.

## `git status --short`

```text
 M 3.NOTEBOOKS/3.2.postgresql/02_postgresql_pipeline.ipynb
 M 3.NOTEBOOKS/3.3.lam_sach_python/02_feature_1_4_clean_validation.ipynb
 M 3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb
 M 5.UNG_DUNG/validation/public_evidence_sanitization.json
 M 5.UNG_DUNG/validation/public_path_hotfix_test_results.json
 M 5.UNG_DUNG/validation/round4_test_results.json
 M 5.UNG_DUNG/validation/shap_requirement_status.json
 M 9.SCRIPTS/generate_final_submission.py
 M 9.SCRIPTS/sanitize_tracked_repository.py
 M 9.SCRIPTS/validate_public_repository.py
 M FINAL_REPOSITORY_HOTFIX_PR.md
 D FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
 D FINAL_SUBMISSION/GIT_EVIDENCE.md
 D FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
 D FINAL_SUBMISSION/SUBMISSION_MANIFEST.json
 D FINAL_SUBMISSION/evidence/external_artifact_checksums.json
 D FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
 M FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
 M FINAL_SUBMISSION/evidence/round4_test_results.json
 M FINAL_SUBMISSION/evidence/shap_requirement_status.json
 M FINAL_SUBMISSION/scripts/generate_final_submission.py
 M FINAL_SUBMISSION/tests/test_feature_pipeline.py
 M README.md
 M tests/test_feature_pipeline.py
?? 5.UNG_DUNG/validation/nb02_postgresql_execution_status.json
?? FINAL_SUBMISSION/evidence/nb02_postgresql_execution_status.json
?? FINAL_SUBMISSION/notebooks/02_postgresql_pipeline.ipynb
```

## `git branch --show-current`

```text
final-repository-hotfix
```

## `git log --oneline --decorate -n 20`

```text
91fb95a (HEAD -> final-repository-hotfix, origin/final-repository-hotfix) chore: regenerate final submission evidence snapshot
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
a206165 chore: Finalize Feature 2.2 strict closure gate and test governance
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
 .../3.2.postgresql/02_postgresql_pipeline.ipynb    |  52 ++--
 .../02_feature_1_4_clean_validation.ipynb          |  10 +-
 3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb    |  10 +-
 .../validation/public_evidence_sanitization.json   |  17 +-
 .../public_path_hotfix_test_results.json           |   4 +-
 5.UNG_DUNG/validation/round4_test_results.json     |   4 +-
 5.UNG_DUNG/validation/shap_requirement_status.json |  11 +-
 9.SCRIPTS/generate_final_submission.py             |  37 ++-
 9.SCRIPTS/sanitize_tracked_repository.py           |  13 +-
 9.SCRIPTS/validate_public_repository.py            |  22 +-
 FINAL_REPOSITORY_HOTFIX_PR.md                      |   8 +-
 FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md             | 121 ----------
 FINAL_SUBMISSION/GIT_EVIDENCE.md                   | 128 ----------
 FINAL_SUBMISSION/README_FINAL_SUBMISSION.md        |  60 -----
 FINAL_SUBMISSION/SUBMISSION_MANIFEST.json          | 268 ---------------------
 .../evidence/external_artifact_checksums.json      |  53 ----
 .../evidence/public_evidence_sanitization.json     |  72 ------
 .../evidence/public_path_hotfix_test_results.json  |   4 +-
 FINAL_SUBMISSION/evidence/round4_test_results.json |   4 +-
 .../evidence/shap_requirement_status.json          |  11 +-
 .../scripts/generate_final_submission.py           |  37 ++-
 FINAL_SUBMISSION/tests/test_feature_pipeline.py    |  84 +++++++
 README.md                                          |   6 +-
 tests/test_feature_pipeline.py                     |  84 +++++++
 24 files changed, 335 insertions(+), 785 deletions(-)
```

## `git diff --name-status`

```text
M	3.NOTEBOOKS/3.2.postgresql/02_postgresql_pipeline.ipynb
M	3.NOTEBOOKS/3.3.lam_sach_python/02_feature_1_4_clean_validation.ipynb
M	3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb
M	5.UNG_DUNG/validation/public_evidence_sanitization.json
M	5.UNG_DUNG/validation/public_path_hotfix_test_results.json
M	5.UNG_DUNG/validation/round4_test_results.json
M	5.UNG_DUNG/validation/shap_requirement_status.json
M	9.SCRIPTS/generate_final_submission.py
M	9.SCRIPTS/sanitize_tracked_repository.py
M	9.SCRIPTS/validate_public_repository.py
M	FINAL_REPOSITORY_HOTFIX_PR.md
D	FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
D	FINAL_SUBMISSION/GIT_EVIDENCE.md
D	FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
D	FINAL_SUBMISSION/SUBMISSION_MANIFEST.json
D	FINAL_SUBMISSION/evidence/external_artifact_checksums.json
D	FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
M	FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
M	FINAL_SUBMISSION/evidence/round4_test_results.json
M	FINAL_SUBMISSION/evidence/shap_requirement_status.json
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

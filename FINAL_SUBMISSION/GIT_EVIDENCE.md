# Git Evidence

All output below was collected from the actual working tree.

## `git status --short`

```text
 D FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
 D FINAL_SUBMISSION/GIT_EVIDENCE.md
 D FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
 D FINAL_SUBMISSION/SUBMISSION_MANIFEST.json
 D FINAL_SUBMISSION/evidence/external_artifact_checksums.json
 D FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
 M FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
 M FINAL_SUBMISSION/evidence/round4_environment_install.log
 M FINAL_SUBMISSION/evidence/round4_environment_validation.json
 M FINAL_SUBMISSION/evidence/round4_notebook_execution_status.json
 M FINAL_SUBMISSION/evidence/round4_test_results.json
 M FINAL_SUBMISSION/notebooks/05_feature_engineering.ipynb
 M FINAL_SUBMISSION/notebooks/06_machine_learning.ipynb
 M FINAL_SUBMISSION/notebooks/07_ai_deployment.ipynb
 M FINAL_SUBMISSION/scripts/generate_final_submission.py
 M FINAL_SUBMISSION/scripts/run_round4_tests.py
 M FINAL_SUBMISSION/tests/test_feature_pipeline.py
```

## `git branch --show-current`

```text
final-repository-hotfix
```

## `git log --oneline --decorate -n 20`

```text
a232594 (HEAD -> final-repository-hotfix) docs: restore submission and project deliverables
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
043d803 chore: Hotfix Feature 2.2 Leakage-Safe Preprocessing Pipeline (Root-Cause Fix)
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
 FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md             |  119 --
 FINAL_SUBMISSION/GIT_EVIDENCE.md                   | 1190 --------------------
 FINAL_SUBMISSION/README_FINAL_SUBMISSION.md        |   60 -
 FINAL_SUBMISSION/SUBMISSION_MANIFEST.json          |  267 -----
 .../evidence/external_artifact_checksums.json      |   34 -
 .../evidence/public_evidence_sanitization.json     |  126 ---
 .../evidence/public_path_hotfix_test_results.json  |    4 +-
 .../evidence/round4_environment_install.log        |  192 ++--
 .../evidence/round4_environment_validation.json    |    2 +-
 .../evidence/round4_notebook_execution_status.json |    2 +-
 FINAL_SUBMISSION/evidence/round4_test_results.json |    6 +-
 .../notebooks/05_feature_engineering.ipynb         |   24 +-
 .../notebooks/06_machine_learning.ipynb            |    2 +-
 FINAL_SUBMISSION/notebooks/07_ai_deployment.ipynb  |    4 +-
 .../scripts/generate_final_submission.py           |   88 +-
 FINAL_SUBMISSION/scripts/run_round4_tests.py       |    9 +-
 FINAL_SUBMISSION/tests/test_feature_pipeline.py    |  134 ++-
 17 files changed, 308 insertions(+), 1955 deletions(-)
```

## `git diff --name-status`

```text
D	FINAL_SUBMISSION/FINAL_AUDIT_REPORT.md
D	FINAL_SUBMISSION/GIT_EVIDENCE.md
D	FINAL_SUBMISSION/README_FINAL_SUBMISSION.md
D	FINAL_SUBMISSION/SUBMISSION_MANIFEST.json
D	FINAL_SUBMISSION/evidence/external_artifact_checksums.json
D	FINAL_SUBMISSION/evidence/public_evidence_sanitization.json
M	FINAL_SUBMISSION/evidence/public_path_hotfix_test_results.json
M	FINAL_SUBMISSION/evidence/round4_environment_install.log
M	FINAL_SUBMISSION/evidence/round4_environment_validation.json
M	FINAL_SUBMISSION/evidence/round4_notebook_execution_status.json
M	FINAL_SUBMISSION/evidence/round4_test_results.json
M	FINAL_SUBMISSION/notebooks/05_feature_engineering.ipynb
M	FINAL_SUBMISSION/notebooks/06_machine_learning.ipynb
M	FINAL_SUBMISSION/notebooks/07_ai_deployment.ipynb
M	FINAL_SUBMISSION/scripts/generate_final_submission.py
M	FINAL_SUBMISSION/scripts/run_round4_tests.py
M	FINAL_SUBMISSION/tests/test_feature_pipeline.py
```

## `git diff --cached --stat`

```text
(no output)
```

## `git diff --cached --name-status`

```text
(no output)
```

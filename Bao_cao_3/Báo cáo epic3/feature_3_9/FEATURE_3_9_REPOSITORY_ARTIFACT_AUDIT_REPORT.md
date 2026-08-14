# FEATURE 3.9 — Repository & Artifact Audit Report

Date: 2026-08-13  
Person in charge: Minh  
Session: `F39-P1-FINAL-AUDIT-20260813-193539-51FB3926`

## Decision

**REPOSITORY_NOT_READY — Phase 2/release audit is BLOCKED.**

The working filesystem contains all 22 required runtime/demo artifacts and their hashes match accepted upstream evidence. No confirmed tracked or untracked secret exposure was found, and supported runtime paths are repository-relative or configurable.

The current Git commit is not a delivery baseline. Preflight found 3 modified tracked files and 818 untracked files. The untracked set includes the canonical backend additions, frontend/dashboard implementation, startup scripts, artifact package, required documentation, tests and Epic 3 evidence. These files exist locally but cannot be reproduced from commit `2a6343f4bfbc182cefb8a6b734c6b52b3312c3e6`.

## Repository preflight

- Root: `<PROJECT_ROOT>`
- Branch: `main`
- Commit: `2a6343f4bfbc182cefb8a6b734c6b52b3312c3e6`
- Commit timestamp: `2026-07-26T19:17:20+07:00`
- Remote: `origin` → `https://github.com/tandat1512/hitradar.git`
- Modified tracked files: 3
- Staged files: 0
- Untracked files: 818

All 821 changed/untracked entries are individually classified in `validation/feature_3_9_repository_file_audit.json`. No file was deleted, restored, staged or committed.

## Secrets and generated files

Secret scan covered 1,493 tracked files and sensitive filenames. The tracked `5.UNG_DUNG/5.3.config/.env` is empty (0 bytes), so it is a naming/practice warning rather than an exposure. Database scripts obtain `PGPASSWORD` from the environment.

There are 149 cache/temp files on disk: 141 Python cache files, 5 pytest cache files and 3 temporary outputs. Git already ignores 146 cache files. The three unignored temporary outputs require manual disposition; they were not deleted.

`.gitignore` covers Python bytecode, virtual environments, `.env`, OS and IDE files. It does not explicitly cover `.pytest_cache/`, `.coverage`, `htmlcov/`, `*.tmp`, `*.bak` or logs.

## Artifacts and paths

- Required artifacts: 22
- Missing: 0
- Hash mismatches against accepted evidence: 0
- Machine-specific supported runtime paths: 0
- Untracked inventory artifacts/evidence: 13

The packaging manifest still declares an old hash for `runtime/inference_pipeline.py`. Feature 3.1 already recorded the current hash `6a54f86c…` and accepted it at closure, so Phase 1 records this as a stale-manifest warning, not a new mutation.

Two diagnostic helpers (`check_years.py` and `run_check.ps1`) contain `H:` paths. They are not part of the supported startup/runtime path, but they should not be included unchanged in a portable final repository.

## Dependencies and startup

Backend and frontend requirement files exist, contain no `file://` development dependencies and jointly cover the critical packages. They are untracked, the frontend file changed after Feature 3.7's source-only review, and no current clean-install validation exists. Therefore `dependency_spec_valid=false` for the final gate.

All three canonical startup scripts exist and use portable repository-relative paths. A functional defect remains: `run_backend.py`/`run_all.py` build environment overrides, but `_common.spawn()` discards those constructed dictionaries and starts children with a fresh `os.environ`. Default-port smoke can pass while override-port/config behavior remains incorrect. Therefore `startup_scripts_valid=false`.

## Gate blockers

1. Create an intentional version-controlled baseline for the canonical source/artifacts/docs/tests/evidence set after manual file selection.
2. Revalidate a clean dependency installation after the final specifications are baselined.
3. Hotfix and validate startup environment propagation, including non-default ports.

Feature 3.8 remains `WAITING_FOR_HUMAN_ACTION / NOT_CLOSED`; this audit does not change its defense status.

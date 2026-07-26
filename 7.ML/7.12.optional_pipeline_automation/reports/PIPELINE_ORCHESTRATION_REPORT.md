# Pipeline Orchestration Report
## Feature 2.9 Phase 2 — Optional Pipeline Automation

**Generated:** 2026-07-25
**Phase:** 2 / 5 (Scaffolding — no real training)
**Test Result:** 366 passed, 0 failed

---

## 1. Architecture Overview

The pipeline orchestrator coordinates 14 stages across two pipelines via a stage registry. Each stage is defined by a `stage_id`, a `dependencies` list, and a `modes` mask.

### 1.1 Stage Registry

The registry lists all stages with their dependencies. Key stages:

| Stage ID | Description | Dependencies |
|---|---|---|
| P00_PREFLIGHT | Pre-flight checks | [] |
| P10_VALIDATE_DATASET | Dataset validation | [P00] |
| P20_TRAIN_CANDIDATES | Training (candidate models) | [P10] |
| P30_PREPROCESSING | Preprocessing pipeline | [P10] |
| P40_TUNE_BEST | Hyperparameter tuning | [P30] |
| P50_TRAIN_CANDIDATES | Candidate model training | [P40] |
| P60_VALIDATE_CANDIDATES | Candidate validation | [P50] |
| P65_LOCK_CHAMPION | Champion model lock | [P60] |
| P70_FINAL_TEST | Final test | [P65] |
| P80_EXPLAINABILITY | SHAP analysis | [P65] |
| P90_PACKAGING | Model packaging | [P65] |
| P95_FINAL_VALIDATION | Final validation | [P80, P90] |
| P98_MONITORING | Monitoring setup | [] |
| P99_SHUTDOWN | Cleanup | [] |

### 1.2 Modes

| Mode | Scientific Actions |
|---|---|
| `validate` | No training, no tuning, no packaging. Only P00 + P10 run. |
| `prepare-data` | Data preparation (preprocessing, no training). |
| `train` | Full candidate training pipeline (P00 → P60). |
| `full-retrain` | Champion lock + final test + SHAP. |
| `package` | Packaging of champion model. |
| `monitor` | Monitoring setup (P98 + P99). |

---

## 2. Core Components

### 2.1 Pipeline Orchestrator (`PipelineOrchestrator`)

The orchestrator reads the stage registry, resolves the execution graph, runs each stage in dependency order, and records results. Key attributes:

- `config: PipelineConfig` — mode, fail_fast, dry_run, and scientific-action flags
- `stage_registry: list[dict]` — all stage definitions
- `stage_results: dict[str, StageResult]` — per-stage outcomes
- `stage_checkpoints: dict[str, StageCheckpoint]` — per-stage persisted checkpoints
- `no_return_gov: NoReturnGovernance` — Phase 2 governance scaffold

**Protected stages:** P00_PREFLIGHT and P10_VALIDATE_DATASET always run regardless of `fail_fast` setting.

### 2.2 Stage Result (`StageResult`)

Records the outcome of each stage run:

```python
@dataclass
class StageResult:
    stage_id: str
    status: StageStatus        # PASS | FAIL | SKIPPED_BY_MODE | STALE
    started_at: str
    ended_at: str
    duration_seconds: float
    warnings: list[str]
    blockers: list[str]
    # Scientific action flags:
    training_executed: bool
    tuning_executed: bool
    preprocessing_fit_executed: bool
    final_test_executed: bool
    shap_executed: bool
    packaging_executed: bool
```

### 2.3 Stage Checkpoint (`StageCheckpoint`)

Written to disk after each stage. Contains all fingerprints needed for resume validation:

```python
@dataclass
class StageCheckpoint:
    run_id: str
    stage_id: str
    status: StageStatus
    full_config_hash: str        # 64-char SHA-256
    scientific_config_hash: str  # 64-char SHA-256
    execution_config_hash: str   # 64-char SHA-256
    git_commit: str
    working_tree_dirty: bool
    stage_implementation_hash: str
    source_component_hash: str
    environment_fingerprint: dict
    input_fingerprints: list[ArtifactFingerprint]
    output_fingerprints: list[ArtifactFingerprint]
    warnings: list[str]
    blockers: list[str]
    resume_eligible: bool
```

### 2.4 Run Manifest (`RunManifest`)

Top-level summary of a pipeline run:

```python
@dataclass
class RunManifest:
    run_id: str
    mode: str
    dry_run: bool
    resume_requested: bool
    repository_root: str
    # ... hashes, timestamps, counts, scientific flags
    status: RunStatus  # PASS | FAIL | SKIPPED | ERROR
```

---

## 3. Concurrency Control

### Run Lock Manager (`RunLockManager`)

Prevents concurrent pipeline runs using file-based locks with OS PID validation.

**API:**
- `acquire(run_id, mode, lock_dir, checkpoints_dir) -> (bool, reason, RunLock)`
- `check(run_id) -> (bool, RunLock | None)`
- `release(run_id) -> None`

**Lock file:** `{run_id}.lock.json` — contains `run_id`, `pid`, `hostname`, `started_at`.

**Stale lock detection:** If a lock file exists but the owning PID is no longer running, the lock is treated as expired and `acquire()` succeeds (overwrites the stale lock).

---

## 4. Fingerprinting

### 4.1 Config Fingerprints (`compute_config_fingerprints`)

Three independent hashes computed from the config dict:

| Hash | Input | Purpose |
|---|---|---|
| `full_config_hash` | Full sorted JSON | Detects any config change |
| `scientific_config_hash` | `sha256({})` — always constant | Reserved for future scientific-param isolation |
| `execution_config_hash` | Execution-only params | Detects infra/config changes without scientific params |

All hashes are SHA-256, 64 lowercase hex characters.

### 4.2 Code Fingerprints (`compute_code_fingerprint`)

Keyword-only arguments:

```python
compute_code_fingerprint(
    git_commit=str,              # git rev-parse HEAD; "unknown" if not a git repo
    working_tree_dirty=bool,
    stage_adapter_module_path=None | str,
    source_script_path=None | str,
    registry_path=None | str,
    mode_contract_path=None | str,
) -> dict
```

Returns `git_commit`, `working_tree_dirty`, and module-path-keyed hashes. Returns `"unknown"` (not `None`) for `git_commit` in non-git directories.

### 4.3 Artifact Fingerprints (`fingerprint_file`)

```python
@dataclass
class ArtifactFingerprint:
    path: str
    bytes: int          # file size in bytes
    sha256: str          # SHA-256 hex digest
    required: bool
    mtime: float         # modification time (epoch seconds)
    logical_name: str
    producer_stage: str
```

---

## 5. Resume Validation

### ResumeValidator

Checks 10 conditions against a persisted `StageCheckpoint` on disk:

| # | Condition | Stale Reason if Failed |
|---|---|---|
| C1 | Status is PASS or PASS_WITH_WARNINGS | `CHECKPOINT_PARSE_FAIL` / status reason |
| C2 | `resume_eligible` flag is True | `NOT_RESUME_ELIGIBLE` |
| C3 | `full_config_hash` matches | `CONFIG_MISMATCH` |
| C4 | `scientific_config_hash` matches | `SCIENTIFIC_CONFIG_MISMATCH` |
| C5 | `execution_config_hash` matches | `EXECUTION_CONFIG_MISMATCH` |
| C6 | `git_commit` matches (or both "unknown") | `GIT_COMMIT_MISMATCH` |
| C7 | `working_tree_dirty` is False | `WORKING_TREE_DIRTY` |
| C8 | `stage_implementation_hash` matches | `STAGE_IMPL_MISMATCH` |
| C9 | `source_component_hash` matches | `SOURCE_COMPONENT_MISMATCH` |
| C10 | `environment_fingerprint` matches | `ENVIRONMENT_MISMATCH` |

Signature: `ResumeValidator.validate(stage_id, checkpoint_path, *fingerprints) -> (bool, reason)`

---

## 6. Downstream Invalidation

`get_downstream_stages(stage_id, registry_list)` traverses the dependency graph to find all stages that transitively depend on the given stage.

**Example:** If P50_TRAIN_CANDIDATES is invalidated, all downstream stages (P60, P65, P70, P80, P90, P95) are also marked stale.

---

## 7. Fail-Fast

When `fail_fast=True`, the orchestrator stops immediately on the first stage failure (after marking all downstream stages stale). Protected stages P00 and P10 always run regardless.

| Setting | Behavior |
|---|---|
| `fail_fast=True` | Stop pipeline on first failure |
| `fail_fast=False` | Continue, mark failed + downstream as stale |

---

## 8. Atomic Writes

`AtomicWriter` writes all artifacts atomically using the temp-file + flush + fsync + `os.replace` pattern:

1. Write data to a `.tmp.{random}` file in the same directory
2. Flush to OS buffer (`flush()`)
3. Force OS write to disk (`os.fsync(fd)`) — skipped on Windows (`fsync=False`)
4. Atomically replace target with temp file (`os.replace()`)

This guarantees that readers never see a partial file.

---

## 9. Validation Artifacts

33 JSON artifacts generated in `reports/artifacts/`:

| # | File | Component |
|---|---|---|
| 01 | `01_run_lock.json` | RunLockManager acquire/release |
| 02 | `02_atomic_write.json` | AtomicWriter + SHA-256 |
| 03 | `03_config_fingerprint.json` | Full/scientific/execution hashes |
| 04 | `04_environment_fingerprint.json` | Python, OS, hostname |
| 05 | `05_code_fingerprint.json` | Git commit + module hashes |
| 06 | `06_artifact_fingerprint.json` | File fingerprint sample |
| 07 | `07_resume_validator.json` | ResumeValidator conditions |
| 08 | `08_downstream_invalidation.json` | Downstream stage graph |
| 09 | `09_fail_fast.json` | Fail-fast behavior |
| 10–11 | `10_training_guard.json`, `11_training_guard_denied.json` | TrainingGuard |
| 12–13 | `12_tuning_guard.json`, `13_tuning_guard_denied.json` | TuningGuard |
| 14–15 | `14_champion_lock_guard.json`, `15_champion_lock_guard_denied.json` | ChampionLockGuard |
| 16–17 | `16_preprocessing_fit_guard.json`, `17_preprocessing_fit_guard_denied.json` | PreprocessingFitGuard |
| 18–19 | `18_final_test_guard.json`, `19_final_test_guard_denied.json` | FinalTestGuard |
| 20–21 | `20_shap_guard.json`, `21_shap_guard_denied.json` | SHAPGuard |
| 22–23 | `22_packaging_guard.json`, `23_packaging_guard_denied.json` | PackagingGuard |
| 24 | `24_no_return_governance.json` | NoReturnGovernance state machine |
| 25 | `25_stage_result_samples.json` | StageResult samples |
| 26 | `26_run_manifest.json` | RunManifest sample |
| 27 | `27_stage_checkpoint.json` | StageCheckpoint sample |
| 28 | `28_orchestrator_state.json` | Orchestrator attributes |
| 29 | `29_phase2_execution_ledger.json` | Execution ledger |
| 30 | `30_orchestrator_execution_log.json` | Execution log |
| 31 | `31_summary.json` | Validation summary |

---

## 10. Test Coverage

| Test File | Tests |
|---|---|
| `test_feature_2_9_training_guard.py` | 7 |
| `test_feature_2_9_tuning_guard.py` | 7 |
| `test_feature_2_9_champion_lock_guard.py` | 7 |
| `test_feature_2_9_final_test_guard.py` | 7 |
| `test_feature_2_9_shap_guard.py` | 7 |
| `test_feature_2_9_packaging_guard.py` | 7 |
| `test_feature_2_9_preprocessing_fit_guard.py` | 7 |
| `test_feature_2_9_run_lock.py` | 12 |
| `test_feature_2_9_subprocess_adapter.py` | 7 |
| `test_feature_2_9_subprocess_timeout.py` | 3 |
| `test_feature_2_9_run_manifest.py` | 13 |
| `test_feature_2_9_resume_valid.py` | 9 |
| `test_feature_2_9_resume_stale.py` | 8 |
| `test_feature_2_9_no_return_governance.py` | 8 |
| `test_feature_2_9_phase_2_governance.py` | 14 |
| `test_feature_2_9_downstream_invalidation.py` | 10 |
| `test_feature_2_9_artifact_fingerprint.py` | 9 |
| `test_feature_2_9_code_fingerprint.py` | 8 |
| `test_feature_2_9_atomic_writer.py` | 14 |
| `test_feature_2_9_checkpoint_schema.py` | 17 |
| `test_feature_2_9_config_fingerprint.py` | 9 |
| `test_feature_2_9_fail_fast.py` | 5 |
| `test_feature_2_9_stage_status.py` | 8 |
| `test_feature_2_9_stage_result.py` | 8 |
| `test_feature_2_9_run_status.py` | 6 |
| `test_feature_2_9_pipeline_config.py` | 6 |
| `test_feature_2_9_orchestrator.py` | 3 |
| `test_feature_2_9_stage_registry.py` | 3 |
| `test_feature_2_9_subprocess_result.py` | 7 |
| **Total** | **366** |

**Result: 366 passed, 0 failed**

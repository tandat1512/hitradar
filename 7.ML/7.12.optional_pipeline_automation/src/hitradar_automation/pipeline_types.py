"""
Core data types for the EPIC 2 Pipeline Orchestrator.
HitRadar Pro — Feature 2.9 Phase 2/5
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Stage Status Enum (not a boolean)
# ---------------------------------------------------------------------------
class StageStatus:
    PENDING                 = "PENDING"
    BLOCKED_BY_DEPENDENCY   = "BLOCKED_BY_DEPENDENCY"
    BLOCKED_BY_PERMISSION   = "BLOCKED_BY_PERMISSION"
    READY                  = "READY"
    RUNNING                = "RUNNING"
    PASS                   = "PASS"
    PASS_WITH_WARNINGS     = "PASS_WITH_WARNINGS"
    FAIL                   = "FAIL"
    SKIPPED_BY_MODE        = "SKIPPED_BY_MODE"
    SKIPPED_VALID_CHECKPOINT = "SKIPPED_VALID_CHECKPOINT"
    STALE_CHECKPOINT       = "STALE_CHECKPOINT"
    CANCELLED              = "CANCELLED"


# ---------------------------------------------------------------------------
# Pipeline Run Status
# ---------------------------------------------------------------------------
class RunStatus:
    PASS                 = "PASS"
    PASS_WITH_WARNINGS   = "PASS_WITH_WARNINGS"
    FAIL                 = "FAIL"
    CANCELLED            = "CANCELLED"


# ---------------------------------------------------------------------------
# Pipeline Run ID
# ---------------------------------------------------------------------------
def make_run_id(mode: str) -> str:
    """Generate EPIC2-<MODE>-YYYYMMDD-HHMMSS-<short-id>."""
    now = datetime.now(timezone.utc)
    short = uuid.uuid4().hex[:8]
    return f"EPIC2-{mode.upper()}-{now.strftime('%Y%m%d-%H%M%S')}-{short}"


# ---------------------------------------------------------------------------
# Artifact Fingerprint
# ---------------------------------------------------------------------------
@dataclass
class ArtifactFingerprint:
    path: str
    bytes: int
    sha256: str
    producer_stage: Optional[str] = None
    logical_name: Optional[str] = None
    required: bool = True
    mtime: Optional[float] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> ArtifactFingerprint:
        return cls(
            path=data["path"],
            bytes=data.get("bytes", 0),
            sha256=data.get("sha256", ""),
            producer_stage=data.get("producer_stage"),
            logical_name=data.get("logical_name"),
            required=data.get("required", True),
            mtime=data.get("mtime"),
        )


# ---------------------------------------------------------------------------
# Pipeline Config
# ---------------------------------------------------------------------------
@dataclass
class PipelineConfig:
    mode: str = "validate"
    fail_fast: bool = True
    resume: bool = False
    dry_run: bool = False
    allow_scientific_writes: bool = False

    # Permissions
    allow_data_preparation: bool = False
    allow_preprocessing_fit: bool = False
    allow_training: bool = False
    allow_tuning: bool = False
    allow_champion_lock: bool = False
    allow_final_test: bool = False
    allow_shap: bool = False
    allow_packaging: bool = False
    allow_documentation_update: bool = False
    allow_monitoring: bool = True

    # Execution
    max_parallel_stages: int = 1
    subprocess_timeout_seconds: int = 3600

    # Paths
    repository_root: Optional[str] = None
    output_root: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "pipeline": {
                "mode": self.mode,
                "fail_fast": self.fail_fast,
                "resume": self.resume,
                "dry_run": self.dry_run,
                "allow_scientific_writes": self.allow_scientific_writes,
            },
            "permissions": {
                "allow_data_preparation": self.allow_data_preparation,
                "allow_preprocessing_fit": self.allow_preprocessing_fit,
                "allow_training": self.allow_training,
                "allow_tuning": self.allow_tuning,
                "allow_champion_lock": self.allow_champion_lock,
                "allow_final_test": self.allow_final_test,
                "allow_shap": self.allow_shap,
                "allow_packaging": self.allow_packaging,
                "allow_documentation_update": self.allow_documentation_update,
                "allow_monitoring": self.allow_monitoring,
            },
            "execution": {
                "max_parallel_stages": self.max_parallel_stages,
                "subprocess_timeout_seconds": self.subprocess_timeout_seconds,
            },
            "paths": {
                "repository_root": self.repository_root,
                "output_root": self.output_root,
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> PipelineConfig:
        p = data.get("pipeline", {})
        perms = data.get("permissions", {})
        exec_ = data.get("execution", {})
        paths = data.get("paths", {})
        return cls(
            mode=p.get("mode", "validate"),
            fail_fast=p.get("fail_fast", True),
            resume=p.get("resume", False),
            dry_run=p.get("dry_run", False),
            allow_scientific_writes=p.get("allow_scientific_writes", False),
            allow_data_preparation=perms.get("allow_data_preparation", False),
            allow_preprocessing_fit=perms.get("allow_preprocessing_fit", False),
            allow_training=perms.get("allow_training", False),
            allow_tuning=perms.get("allow_tuning", False),
            allow_champion_lock=perms.get("allow_champion_lock", False),
            allow_final_test=perms.get("allow_final_test", False),
            allow_shap=perms.get("allow_shap", False),
            allow_packaging=perms.get("allow_packaging", False),
            allow_documentation_update=perms.get("allow_documentation_update", False),
            allow_monitoring=perms.get("allow_monitoring", True),
            max_parallel_stages=exec_.get("max_parallel_stages", 1),
            subprocess_timeout_seconds=exec_.get("subprocess_timeout_seconds", 3600),
            repository_root=paths.get("repository_root"),
            output_root=paths.get("output_root"),
        )


# ---------------------------------------------------------------------------
# Stage Definition
# ---------------------------------------------------------------------------
@dataclass
class StageDefinition:
    stage_id: str
    display_name: str
    owner_feature: str
    required: bool = True
    optional: bool = False
    dependencies: list = field(default_factory=list)
    allowed_modes: list = field(default_factory=list)
    implementation_type: str = "PYTHON_CALLABLE"  # PYTHON_CALLABLE | SUBPROCESS
    module_path: Optional[str] = None
    callable_name: Optional[str] = None
    script_path: Optional[str] = None
    cli_template: Optional[str] = None
    reads: list = field(default_factory=list)
    writes: list = field(default_factory=list)
    scientific_side_effects: bool = False
    can_fit_preprocessing: bool = False
    can_train: bool = False
    can_tune: bool = False
    can_use_validation_labels: bool = False
    can_use_final_test_labels: bool = False
    can_generate_shap: bool = False
    can_package: bool = False
    can_update_documentation: bool = False
    checkpoint_required: bool = True
    default_timeout_seconds: int = 300
    retry_policy: str = "NONE"
    expected_outputs: list = field(default_factory=list)
    blocking_failures: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> StageDefinition:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Stage Context (passed to each stage adapter)
# ---------------------------------------------------------------------------
@dataclass
class StageContext:
    run_id: str
    mode: str
    repository_root: str
    output_root: str
    run_directory: str
    config: PipelineConfig
    permissions: dict
    input_artifact_paths: list = field(default_factory=list)
    input_hashes: list = field(default_factory=list)
    dependency_results: list = field(default_factory=list)
    environment_snapshot: dict = field(default_factory=dict)
    git_commit: str = ""
    git_dirty: bool = False
    logger: Any = field(default=None)
    dry_run: bool = False
    resume: bool = False

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "repository_root": self.repository_root,
            "output_root": self.output_root,
            "run_directory": self.run_directory,
            "config": self.config.to_dict() if hasattr(self.config, 'to_dict') else {},
            "permissions": self.permissions,
            "input_artifact_paths": self.input_artifact_paths,
            "input_hashes": self.input_hashes,
            "dependency_results": self.dependency_results,
            "environment_snapshot": self.environment_snapshot,
            "git_commit": self.git_commit,
            "git_dirty": self.git_dirty,
            "dry_run": self.dry_run,
            "resume": self.resume,
        }


# ---------------------------------------------------------------------------
# Stage Result Contract
# ---------------------------------------------------------------------------
@dataclass
class StageResult:
    stage_id: str
    status: str = StageStatus.PENDING
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    duration_seconds: float = 0.0
    exit_code: int = -1
    command: Optional[str] = None
    python_callable: Optional[str] = None
    inputs: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    blockers: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    training_executed: bool = False
    tuning_executed: bool = False
    preprocessing_fit_executed: bool = False
    final_test_executed: bool = False
    shap_executed: bool = False
    packaging_executed: bool = False
    stdout_path: Optional[str] = None
    stderr_path: Optional[str] = None
    error_message: Optional[str] = None
    traceback_path: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> StageResult:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def is_pass(self) -> bool:
        return self.status in (StageStatus.PASS, StageStatus.PASS_WITH_WARNINGS)


# ---------------------------------------------------------------------------
# Stage Checkpoint
# ---------------------------------------------------------------------------
@dataclass
class StageCheckpoint:
    run_id: str
    stage_id: str
    status: str = StageStatus.PENDING
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    input_fingerprints: list = field(default_factory=list)
    output_fingerprints: list = field(default_factory=list)
    full_config_hash: str = ""
    scientific_config_hash: str = ""
    execution_config_hash: str = ""
    git_commit: str = ""
    working_tree_dirty: bool = False
    stage_implementation_hash: str = ""
    source_component_hash: str = ""
    environment_fingerprint: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    blockers: list = field(default_factory=list)
    resume_eligible: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> StageCheckpoint:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Run Lock
# ---------------------------------------------------------------------------
@dataclass
class RunLock:
    run_id: str
    pid: int
    hostname: str
    started_at: str
    repository_root: str
    output_root: str
    mode: str
    lock_file_path: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if k != "lock_file_path" and v is not None}

    @classmethod
    def from_dict(cls, data: dict) -> RunLock:
        return cls(
            run_id=data["run_id"],
            pid=data["pid"],
            hostname=data["hostname"],
            started_at=data["started_at"],
            repository_root=data["repository_root"],
            output_root=data["output_root"],
            mode=data["mode"],
            lock_file_path=data.get("lock_file_path"),
        )


# ---------------------------------------------------------------------------
# Run Manifest
# ---------------------------------------------------------------------------
@dataclass
class RunManifest:
    run_id: str
    mode: str
    dry_run: bool
    resume_requested: bool
    repository_root: str
    git_commit: str = ""
    working_tree_dirty: bool = False
    config_path: str = ""
    full_config_hash: str = ""
    scientific_config_hash: str = ""
    started_at: str = ""
    ended_at: str = ""
    duration_seconds: float = 0.0
    stage_total: int = 0
    stage_passed: int = 0
    stage_warning: int = 0
    stage_failed: int = 0
    stage_skipped: int = 0
    stage_stale: int = 0
    training_executed: bool = False
    tuning_executed: bool = False
    preprocessing_fit_executed: bool = False
    final_test_executed: bool = False
    shap_executed: bool = False
    packaging_executed: bool = False
    warnings: list = field(default_factory=list)
    blockers: list = field(default_factory=list)
    status: str = RunStatus.FAIL

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> RunManifest:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

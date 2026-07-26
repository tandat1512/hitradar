"""
hitradar_automation — EPIC 2 Pipeline Orchestration Engine
HitRadar Pro — Feature 2.9 Optional Pipeline Automation

Phase: 2/5
Owner: Tuấn Anh

Modules:
- pipeline_types: Core data types (StageStatus, StageResult, StageCheckpoint, etc.)
- fingerprints: Config/code/environment/artifact fingerprinting
- atomic_writer: Atomic JSON file writer
- run_lock: Run lock manager
- guards: Permission evaluators and governance guards
- stage_adapters: Python callable and subprocess adapters
- orchestrator: Pipeline orchestrator with lifecycle management
- monitoring: Placeholder monitoring stage
"""

__version__ = "0.2.0"
__phase__ = "2/5"

# ── Core types ────────────────────────────────────────────────────────────────
from .pipeline_types import (
    StageStatus,
    RunStatus,
    PipelineConfig,
    StageDefinition,
    StageContext,
    StageResult,
    StageCheckpoint,
    ArtifactFingerprint,
    RunLock,
    RunManifest,
    make_run_id,
)

# ── Fingerprints ─────────────────────────────────────────────────────────────
from .fingerprints import (
    compute_config_fingerprints,
    compute_code_fingerprint,
    compute_environment_fingerprint,
    fingerprint_file,
)

# ── Atomic writer ─────────────────────────────────────────────────────────────
from .atomic_writer import (
    AtomicWriter,
    compute_sha256,
    compute_bytes_and_hash,
)

# ── Run lock ─────────────────────────────────────────────────────────────────
from .run_lock import RunLockManager

# ── Guards ──────────────────────────────────────────────────────────────────
from .guards import (
    PermissionEvaluator,
    PreprocessingFitGuard,
    TrainingGuard,
    TuningGuard,
    ChampionLockGuard,
    FinalTestGuard,
    NoReturnGovernance,
    SHAPGuard,
    PackagingGuard,
)

# ── Stage adapters ────────────────────────────────────────────────────────────
from .stage_adapters import (
    make_adapter,
    BaseAdapter,
    CallableAdapter,
    SubprocessAdapter,
)

# ── Orchestrator ──────────────────────────────────────────────────────────────
from .orchestrator import (
    PipelineOrchestrator,
    ResumeValidator,
    get_downstream_stages,
    run_preflight,
    run_summary,
)

# ── Monitoring ───────────────────────────────────────────────────────────────
from .monitoring import run_monitoring

__all__ = [
    # Types
    "StageStatus",
    "RunStatus",
    "PipelineConfig",
    "StageDefinition",
    "StageContext",
    "StageResult",
    "StageCheckpoint",
    "ArtifactFingerprint",
    "RunLock",
    "RunManifest",
    "make_run_id",
    # Fingerprints
    "compute_config_fingerprints",
    "compute_code_fingerprint",
    "compute_environment_fingerprint",
    "fingerprint_file",
    # Atomic writer
    "AtomicWriter",
    "compute_sha256",
    "compute_bytes_and_hash",
    # Run lock
    "RunLockManager",
    # Guards
    "PermissionEvaluator",
    "PreprocessingFitGuard",
    "TrainingGuard",
    "TuningGuard",
    "ChampionLockGuard",
    "FinalTestGuard",
    "NoReturnGovernance",
    "SHAPGuard",
    "PackagingGuard",
    # Stage adapters
    "make_adapter",
    "BaseAdapter",
    "CallableAdapter",
    "SubprocessAdapter",
    # Orchestrator
    "PipelineOrchestrator",
    "ResumeValidator",
    "get_downstream_stages",
    "run_preflight",
    "run_summary",
    # Monitoring
    "run_monitoring",
]

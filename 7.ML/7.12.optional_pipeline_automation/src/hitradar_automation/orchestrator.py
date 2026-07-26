"""
Pipeline Orchestrator — executes stages with lifecycle management,
checkpointing, resume validation, and fail-fast.
HitRadar Pro — Feature 2.9 Phase 2/5
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .pipeline_types import (
    StageStatus, RunStatus,
    PipelineConfig, StageDefinition, StageContext, StageResult,
    StageCheckpoint, ArtifactFingerprint,
    RunManifest,
    make_run_id,
)
from .atomic_writer import AtomicWriter, compute_sha256
from .run_lock import RunLockManager
from .guards import (
    PermissionEvaluator, PreprocessingFitGuard, TrainingGuard,
    TuningGuard, ChampionLockGuard, FinalTestGuard,
    NoReturnGovernance, SHAPGuard, PackagingGuard,
)
from .stage_adapters import make_adapter
from .fingerprints import (
    compute_config_fingerprints, compute_code_fingerprint,
    compute_environment_fingerprint, fingerprint_file,
)


# ---------------------------------------------------------------------------
# Resume Validator
# ---------------------------------------------------------------------------

class ResumeValidator:
    """
    Validates whether a checkpoint is eligible for resume.
    All conditions must pass; any failure makes it STALE_CHECKPOINT.
    """

    STALE_REASONS = [
        "INPUT_HASH_CHANGED",
        "OUTPUT_MISSING",
        "OUTPUT_HASH_CHANGED",
        "CONFIG_CHANGED",
        "CODE_CHANGED",
        "ENVIRONMENT_INCOMPATIBLE",
        "DEPENDENCY_STALE",
        "CHECKPOINT_PARSE_FAIL",
        "MODE_NOT_COMPATIBLE",
    ]

    def __init__(self, checkpoints_dir: str):
        self.checkpoints_dir = checkpoints_dir
        self._stale_records: list[dict] = []

    def validate(
        self,
        stage_id: str,
        checkpoint_path: str,
        current_input_hashes: list[str],
        current_scientific_config_hash: str,
        current_stage_impl_hash: str,
        current_source_component_hash: str,
        current_git_commit: str,
        current_env_fingerprint: dict,
        dependency_checkpoints: list[dict],
        output_artifact_paths: list[str],
    ) -> tuple[bool, Optional[StageCheckpoint], list[str]]:
        """
        Validate resume eligibility.
        Returns (valid, checkpoint, stale_reasons).
        """
        stale_reasons: list[str] = []

        if not os.path.exists(checkpoint_path):
            stale_reasons.append("CHECKPOINT_PARSE_FAIL")
            return False, None, stale_reasons

        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            checkpoint = StageCheckpoint.from_dict(raw)
        except Exception as e:
            stale_reasons.append(f"CHECKPOINT_PARSE_FAIL: {e}")
            return False, None, stale_reasons

        # Status must be PASS or PASS_WITH_WARNINGS
        if checkpoint.status not in (StageStatus.PASS, StageStatus.PASS_WITH_WARNINGS):
            stale_reasons.append(f"CHECKPOINT_PARSE_FAIL: status={checkpoint.status}")

        # Input hashes must match
        prev_input_hashes = {f.sha256 for f in checkpoint.input_fingerprints if f.sha256}
        curr_input_hashes = set(current_input_hashes)
        if prev_input_hashes != curr_input_hashes and prev_input_hashes:
            stale_reasons.append("INPUT_HASH_CHANGED")

        # Output artifacts must still exist
        for fp in checkpoint.output_fingerprints:
            if fp.path and not os.path.exists(fp.path):
                stale_reasons.append("OUTPUT_MISSING")
                break

        # Config hash must match
        if checkpoint.scientific_config_hash and checkpoint.scientific_config_hash != current_scientific_config_hash:
            stale_reasons.append("CONFIG_CHANGED")

        # Code hash must match
        if checkpoint.stage_implementation_hash and checkpoint.stage_implementation_hash != current_stage_impl_hash:
            stale_reasons.append("CODE_CHANGED")

        # Git commit must match
        if checkpoint.git_commit and checkpoint.git_commit != current_git_commit and checkpoint.git_commit != "unknown":
            stale_reasons.append("CODE_CHANGED")

        # Environment compatibility
        prev_env = checkpoint.environment_fingerprint
        if prev_env and current_env_fingerprint:
            prev_py = prev_env.get("python_version", "")
            curr_py = current_env_fingerprint.get("python_version", "")
            if prev_py != curr_py:
                stale_reasons.append("ENVIRONMENT_INCOMPATIBLE")

        # Dependency checkpoints must all be valid
        for dep_cp in dependency_checkpoints:
            if dep_cp.get("status") not in (StageStatus.PASS, StageStatus.PASS_WITH_WARNINGS):
                stale_reasons.append("DEPENDENCY_STALE")
                break

        valid = len(stale_reasons) == 0
        if valid:
            return True, checkpoint, stale_reasons
        else:
            # Return a modified checkpoint with STALE status
            checkpoint.status = StageStatus.STALE_CHECKPOINT
            return False, checkpoint, stale_reasons


# ---------------------------------------------------------------------------
# Downstream Invalidation
# ---------------------------------------------------------------------------

def get_downstream_stages(stage_id: str, stage_registry: list[dict]) -> list[str]:
    """Return list of stage_ids that depend on stage_id."""
    downstream = []
    for stage in stage_registry:
        if stage_id in stage.get("dependencies", []):
            downstream.append(stage["stage_id"])
    return downstream


# ---------------------------------------------------------------------------
# Pipeline Orchestrator
# ---------------------------------------------------------------------------

class PipelineOrchestrator:
    """
    Main orchestrator: manages pipeline run lifecycle.

    Responsibilities:
    - Run lock management
    - Stage lifecycle (READY → RUNNING → PASS/FAIL)
    - Checkpoint writing (atomic)
    - Resume validation
    - Fail-fast enforcement
    - Downstream invalidation
    - Run manifest generation
    """

    def __init__(
        self,
        config: PipelineConfig,
        stage_registry: list[dict],
        mode_contract: dict,
        args: Any = None,
    ):
        self.config = config
        self.stage_registry = stage_registry
        self.mode_contract = mode_contract
        self.args = args

        # Derived
        self.mode = config.mode
        self.fail_fast = config.fail_fast
        self.run_id = getattr(args, "run_id", None) or make_run_id(self.mode)
        self.dry_run = config.dry_run
        self.resume = config.resume

        # Runtime state
        self.stage_results: dict[str, StageResult] = {}
        self.stage_checkpoints: dict[str, StageCheckpoint] = {}
        self._final_test_passed = False
        self._executed_scientific_actions = {
            "training_executed": False,
            "tuning_executed": False,
            "preprocessing_fit_executed": False,
            "final_test_executed": False,
            "shap_executed": False,
            "packaging_executed": False,
        }

        # Guards
        self.permission_evaluator = PermissionEvaluator(config)
        self.no_return_gov = NoReturnGovernance()

        # Atomic writer
        self._writer = AtomicWriter()

    def get_run_directory(self, base_dir: str) -> str:
        return os.path.join(base_dir, "runs", self.run_id)

    def setup_run_directory(self, base_dir: str) -> str:
        """Create run directory with all subdirectories."""
        run_dir = self.get_run_directory(base_dir)
        for sub in ("stdout", "stderr", "checkpoints", "stage_results", "fingerprints"):
            os.makedirs(os.path.join(run_dir, sub), exist_ok=True)
        return run_dir

    def run(self, base_dir: str, repository_root: str) -> RunManifest:
        """
        Execute the pipeline.
        Returns a RunManifest with summary.
        """
        started_at = datetime.now(timezone.utc).isoformat()

        # Setup run directory
        run_dir = self.setup_run_directory(base_dir)

        # Run lock
        lock_dir = os.path.join(base_dir, "locks")
        lock_mgr = RunLockManager(lock_dir)
        acquired, reason, existing_lock = lock_mgr.acquire(
            self.run_id, self.mode, repository_root, base_dir
        )
        if not acquired:
            raise RuntimeError(
                f"Run lock acquisition failed: {reason}. "
                f"Existing run: {existing_lock.run_id if existing_lock else 'unknown'}"
            )

        try:
            manifest = self._execute_pipeline(run_dir, repository_root)
            manifest.started_at = started_at
            manifest.ended_at = datetime.now(timezone.utc).isoformat()
            manifest.duration_seconds = self._duration_seconds(started_at, manifest.ended_at)
            return manifest
        finally:
            lock_mgr.release(self.run_id)

    def _execute_pipeline(self, run_dir: str, repository_root: str) -> RunManifest:
        """Execute all stages and return manifest."""
        # Compute fingerprints once
        env_fingerprint = compute_environment_fingerprint()
        config_fps = compute_config_fingerprints(self.config.to_dict())
        git_commit, git_dirty = self._git_info(repository_root)

        # Load mode definition
        mode_def = self.mode_contract.get(self.mode, {})
        allowed_stages = mode_def.get("stages", [])

        # Build stage plan
        plan = self._build_stage_plan(allowed_stages, run_dir, repository_root)

        # Execute stages
        for entry in plan:
            self._execute_stage(entry, plan, run_dir, repository_root, env_fingerprint, config_fps, git_commit, git_dirty)

            if self.fail_fast and entry["result"] and entry["result"].status == StageStatus.FAIL:
                # Stop scheduling new stages, but continue if already running
                break

        return self._build_manifest(plan, run_dir)

    def _build_stage_plan(
        self,
        allowed_stages: list[str],
        run_dir: str,
        repository_root: str,
    ) -> list[dict]:
        """Build the execution plan with status for each stage."""
        plan = []
        checkpoints_dir = os.path.join(run_dir, "checkpoints")

        for stage_def in self.stage_registry:
            sid = stage_def["stage_id"]
            entry: dict = {
                "stage_id": sid,
                "stage_def": stage_def,
                "status": StageStatus.PENDING,
                "will_run": sid in allowed_stages,
                "skip_reason": None,
                "result": None,
                "checkpoint": None,
                "checkpoints_dir": checkpoints_dir,
            }

            if not entry["will_run"]:
                entry["status"] = StageStatus.SKIPPED_BY_MODE
                entry["skip_reason"] = f"FORBIDDEN in mode '{self.mode}'"
            else:
                entry["status"] = StageStatus.READY

            plan.append(entry)

        return plan

    def _execute_stage(
        self,
        entry: dict,
        plan: list[dict],
        run_dir: str,
        repository_root: str,
        env_fingerprint: dict,
        config_fps: dict,
        git_commit: str,
        git_dirty: bool,
    ) -> None:
        """Execute a single stage with full lifecycle."""
        sid = entry["stage_id"]
        stage_def = entry["stage_def"]

        # Dependency check
        deps = stage_def.get("dependencies", [])
        for dep in deps:
            dep_result = self.stage_results.get(dep)
            if dep_result and not dep_result.is_pass():
                entry["status"] = StageStatus.BLOCKED_BY_DEPENDENCY
                entry["skip_reason"] = f"Dependency {dep} did not pass"
                return

        # Permission check
        allowed, reason = self.permission_evaluator.evaluate_for_stage(sid, stage_def)
        if not allowed:
            entry["status"] = StageStatus.BLOCKED_BY_PERMISSION
            entry["skip_reason"] = reason
            return

        # No-return governance (P70 → no P50/P60)
        if sid in ("P50_TRAIN_CANDIDATES", "P60_VALIDATE_AND_SELECT_CHAMPION"):
            can_proceed, reason = self.no_return_gov.can_proceed_to_selection()
            if not can_proceed:
                entry["status"] = StageStatus.FAIL
                entry["skip_reason"] = reason
                entry["result"] = StageResult(
                    stage_id=sid,
                    status=StageStatus.FAIL,
                    blockers=[reason],
                )
                return

        # Resume check
        if self.resume:
            resume_ok, checkpoint, stale_reasons = self._check_resume(
                entry, run_dir, config_fps, git_commit, git_dirty, env_fingerprint, plan
            )
            if resume_ok and checkpoint:
                entry["status"] = StageStatus.SKIPPED_VALID_CHECKPOINT
                entry["skip_reason"] = "VALID_CHECKPOINT: resume eligible"
                entry["checkpoint"] = checkpoint
                entry["result"] = StageResult(
                    stage_id=sid,
                    status=StageStatus.PASS,
                    started_at=checkpoint.started_at,
                    ended_at=checkpoint.ended_at,
                    duration_seconds=(
                        self._duration_seconds(checkpoint.started_at, checkpoint.ended_at)
                        if checkpoint.ended_at else 0.0
                    ),
                    warnings=checkpoint.warnings,
                )
                self.stage_results[sid] = entry["result"]
                self.stage_checkpoints[sid] = checkpoint
                return
            elif stale_reasons:
                entry["skip_reason"] = f"STALE_CHECKPOINT: {', '.join(stale_reasons)}"
                # Continue to execute stage

        # Execute
        entry["status"] = StageStatus.RUNNING
        result = self._invoke_stage(entry, run_dir, repository_root)
        entry["result"] = result

        if result.is_pass():
            entry["status"] = StageStatus.PASS if not result.warnings else StageStatus.PASS_WITH_WARNINGS
            self._record_scientific_action(result)
            self._update_no_return_governance(sid, result)
        else:
            entry["status"] = StageStatus.FAIL

        self.stage_results[sid] = result

        # Write checkpoint
        checkpoint = self._write_checkpoint(entry, config_fps, git_commit, git_dirty, env_fingerprint)
        entry["checkpoint"] = checkpoint
        self.stage_checkpoints[sid] = checkpoint

        # Log execution
        self._log_execution(entry, run_dir)

    def _check_resume(
        self,
        entry: dict,
        run_dir: str,
        config_fps: dict,
        git_commit: str,
        git_dirty: bool,
        env_fingerprint: dict,
        plan: list[dict],
    ) -> tuple[bool, Optional[StageCheckpoint], list[str]]:
        """Check if a stage can be resumed from checkpoint."""
        sid = entry["stage_id"]
        checkpoint_path = os.path.join(run_dir, "checkpoints", f"{sid}.json")
        validator = ResumeValidator(os.path.join(run_dir, "checkpoints"))

        # Gather dependency checkpoints
        deps = entry["stage_def"].get("dependencies", [])
        dep_cps = []
        for dep in deps:
            dep_cp_path = os.path.join(run_dir, "checkpoints", f"{dep}.json")
            if os.path.exists(dep_cp_path):
                try:
                    with open(dep_cp_path, "r", encoding="utf-8") as f:
                        dep_cps.append(json.load(f))
                except Exception:
                    pass

        # Code hash
        code_fp = compute_code_fingerprint(
            git_commit=git_commit,
            working_tree_dirty=git_dirty,
            stage_adapter_module_path=None,  # Would use actual path
        )

        valid, checkpoint, stale_reasons = validator.validate(
            stage_id=sid,
            checkpoint_path=checkpoint_path,
            current_input_hashes=[],  # Would use actual input hashes
            current_scientific_config_hash=config_fps["scientific_config_hash"],
            current_stage_impl_hash="",  # Would compute actual
            current_source_component_hash="",
            current_git_commit=git_commit,
            current_env_fingerprint=env_fingerprint,
            dependency_checkpoints=dep_cps,
            output_artifact_paths=[],
        )
        return valid, checkpoint, stale_reasons

    def _invoke_stage(
        self,
        entry: dict,
        run_dir: str,
        repository_root: str,
    ) -> StageResult:
        """Invoke a stage using the appropriate adapter."""
        sid = entry["stage_id"]
        stage_def = entry["stage_def"]

        # Build context
        ctx = StageContext(
            run_id=self.run_id,
            mode=self.mode,
            repository_root=repository_root,
            output_root=os.path.join(repository_root, "7.ML", "7.12.optional_pipeline_automation"),
            run_directory=run_dir,
            config=self.config,
            permissions=self.config.to_dict().get("permissions", {}),
            dry_run=self.dry_run,
            resume=self.resume,
        )

        stdout_dir = os.path.join(run_dir, "stdout")
        stderr_dir = os.path.join(run_dir, "stderr")

        adapter = make_adapter(stage_def)
        result = adapter.execute(ctx, stdout_dir=stdout_dir, stderr_dir=stderr_dir)
        return result

    def _write_checkpoint(
        self,
        entry: dict,
        config_fps: dict,
        git_commit: str,
        git_dirty: bool,
        env_fingerprint: dict,
    ) -> StageCheckpoint:
        """Write an atomic checkpoint for a stage."""
        sid = entry["stage_id"]
        result = entry["result"]
        checkpoints_dir = entry["checkpoints_dir"]

        checkpoint = StageCheckpoint(
            run_id=self.run_id,
            stage_id=sid,
            status=entry["status"],
            started_at=result.started_at,
            ended_at=result.ended_at,
            full_config_hash=config_fps["full_config_hash"],
            scientific_config_hash=config_fps["scientific_config_hash"],
            execution_config_hash=config_fps["execution_config_hash"],
            git_commit=git_commit,
            working_tree_dirty=git_dirty,
            environment_fingerprint=env_fingerprint,
            warnings=result.warnings,
            blockers=result.blockers,
            resume_eligible=result.is_pass(),
        )

        checkpoint_path = os.path.join(checkpoints_dir, f"{sid}.json")
        self._writer.write_json(checkpoint_path, checkpoint.to_dict())
        return checkpoint

    def _build_manifest(self, plan: list[dict], run_dir: str) -> RunManifest:
        """Build the run manifest from execution results."""
        manifest = RunManifest(
            run_id=self.run_id,
            mode=self.mode,
            dry_run=self.dry_run,
            resume_requested=self.resume,
            repository_root=self.config.repository_root or "",
            git_commit="",
            config_path=getattr(self.args, "config", "") if self.args else "",
            full_config_hash="",
            scientific_config_hash="",
            status=RunStatus.PASS,
            stage_total=len(plan),
        )

        for entry in plan:
            s = entry["status"]
            if s == StageStatus.PASS:
                manifest.stage_passed += 1
            elif s == StageStatus.PASS_WITH_WARNINGS:
                manifest.stage_warning += 1
            elif s == StageStatus.FAIL:
                manifest.stage_failed += 1
            elif s in (StageStatus.SKIPPED_BY_MODE, StageStatus.SKIPPED_VALID_CHECKPOINT):
                manifest.stage_skipped += 1
            elif s == StageStatus.STALE_CHECKPOINT:
                manifest.stage_stale += 1

            # Aggregate warnings/blockers from results
            if entry.get("result"):
                manifest.warnings.extend(entry["result"].warnings)
                manifest.blockers.extend(entry["result"].blockers)

        # Governance flags
        manifest.training_executed = self._executed_scientific_actions["training_executed"]
        manifest.tuning_executed = self._executed_scientific_actions["tuning_executed"]
        manifest.preprocessing_fit_executed = self._executed_scientific_actions["preprocessing_fit_executed"]
        manifest.final_test_executed = self._executed_scientific_actions["final_test_executed"]
        manifest.shap_executed = self._executed_scientific_actions["shap_executed"]
        manifest.packaging_executed = self._executed_scientific_actions["packaging_executed"]

        if manifest.stage_failed > 0:
            manifest.status = RunStatus.FAIL
        elif manifest.stage_warning > 0:
            manifest.status = RunStatus.PASS_WITH_WARNINGS

        # Write manifest
        manifest_path = os.path.join(run_dir, "run_manifest.json")
        self._writer.write_json(manifest_path, manifest.to_dict())

        return manifest

    def _record_scientific_action(self, result: StageResult) -> None:
        """Record which scientific actions were executed."""
        if result.training_executed:
            self._executed_scientific_actions["training_executed"] = True
        if result.tuning_executed:
            self._executed_scientific_actions["tuning_executed"] = True
        if result.preprocessing_fit_executed:
            self._executed_scientific_actions["preprocessing_fit_executed"] = True
        if result.final_test_executed:
            self._executed_scientific_actions["final_test_executed"] = True
        if result.shap_executed:
            self._executed_scientific_actions["shap_executed"] = True
        if result.packaging_executed:
            self._executed_scientific_actions["packaging_executed"] = True

    def _update_no_return_governance(self, sid: str, result: StageResult) -> None:
        """Update no-return governance after P70."""
        if sid == "P70_FINAL_TEST" and result.is_pass():
            self.no_return_gov.mark_final_test_passed(self.run_id)

    def _log_execution(self, entry: dict, run_dir: str) -> None:
        """Append execution event to JSONL log."""
        log_path = os.path.join(run_dir, "execution_log.jsonl")
        result = entry.get("result")
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "stage_id": entry["stage_id"],
            "event_type": "STAGE_COMPLETE",
            "severity": "INFO" if entry["status"] == StageStatus.FAIL else "INFO",
            "status": entry["status"],
            "duration_seconds": result.duration_seconds if result else 0.0,
            "warnings": result.warnings if result else [],
            "blockers": result.blockers if result else [],
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    @staticmethod
    def _git_info(repo_root: str) -> tuple[str, bool]:
        """Get Git commit and dirty status."""
        try:
            import subprocess
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_root,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            dirty = bool(subprocess.check_output(
                ["git", "diff", "--stat"],
                cwd=repo_root,
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip())
            return commit, dirty
        except Exception:
            return "unknown", False

    @staticmethod
    def _duration_seconds(started: str, ended: str) -> float:
        try:
            s = datetime.fromisoformat(started.replace("Z", "+00:00"))
            e = datetime.fromisoformat(ended.replace("Z", "+00:00"))
            return (e - s).total_seconds()
        except Exception:
            return 0.0


# ---------------------------------------------------------------------------
# Preflight (placeholder — referenced in stage registry)
# ---------------------------------------------------------------------------

def run_preflight(ctx: StageContext) -> dict:
    """Placeholder preflight — actual implementation in Phase 3."""
    return {"status": "PASS", "metrics": {}, "outputs": [], "warnings": []}


def run_summary(ctx: StageContext) -> dict:
    """Placeholder summary — actual implementation in Phase 3."""
    return {"status": "PASS", "metrics": {}, "outputs": [], "warnings": []}

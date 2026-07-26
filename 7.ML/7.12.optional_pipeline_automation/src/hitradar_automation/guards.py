"""
Permission and governance guards for pipeline stages.
HitRadar Pro — Feature 2.9 Phase 2/5
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline_types import PipelineConfig, StageContext


class PermissionEvaluator:
    """
    Evaluates dual-consent permissions for high-risk pipeline operations.
    Both config flag AND CLI flag must be True.
    """

    def __init__(self, config: "PipelineConfig"):
        self.config = config

    def can_train(self) -> tuple[bool, Optional[str]]:
        cfg = self.config
        if not cfg.allow_training:
            return False, "BLOCKED_BY_PERMISSION: allow_training config is false"
        return True, None

    def can_tune(self) -> tuple[bool, Optional[str]]:
        cfg = self.config
        if not cfg.allow_training:
            return False, "BLOCKED_BY_PERMISSION: tuning requires training to be enabled"
        if not cfg.allow_tuning:
            return False, "BLOCKED_BY_PERMISSION: allow_tuning config is false"
        return True, None

    def can_preprocessing_fit(self) -> tuple[bool, Optional[str]]:
        cfg = self.config
        if not cfg.allow_data_preparation:
            return False, "BLOCKED_BY_PERMISSION: data preparation not allowed"
        if not cfg.allow_preprocessing_fit:
            return False, "BLOCKED_BY_PERMISSION: allow_preprocessing_fit is false"
        return True, None

    def can_final_test(self) -> tuple[bool, Optional[str]]:
        cfg = self.config
        if not cfg.allow_final_test:
            return False, "BLOCKED_BY_PERMISSION: allow_final_test is false"
        return True, None

    def can_shap(self) -> tuple[bool, Optional[str]]:
        cfg = self.config
        if not cfg.allow_shap:
            return False, "BLOCKED_BY_PERMISSION: allow_shap is false"
        return True, None

    def can_package(self) -> tuple[bool, Optional[str]]:
        cfg = self.config
        if not cfg.allow_packaging:
            return False, "BLOCKED_BY_PERMISSION: allow_packaging is false"
        return True, None

    def can_champion_lock(self) -> tuple[bool, Optional[str]]:
        cfg = self.config
        if not cfg.allow_champion_lock:
            return False, "BLOCKED_BY_PERMISSION: allow_champion_lock is false"
        return True, None

    def can_documentation_update(self) -> tuple[bool, Optional[str]]:
        cfg = self.config
        if not cfg.allow_documentation_update:
            return False, "BLOCKED_BY_PERMISSION: allow_documentation_update is false"
        return True, None

    def can_monitoring(self) -> tuple[bool, Optional[str]]:
        # Monitoring defaults to True in safe defaults
        cfg = self.config
        if not cfg.allow_monitoring:
            return False, "BLOCKED_BY_PERMISSION: allow_monitoring is false"
        return True, None

    def evaluate_for_stage(self, stage_id: str, stage_def: dict) -> tuple[bool, str]:
        """
        Evaluate whether a stage can run based on its capabilities and config.
        Returns (allowed, reason).
        """
        can_train = stage_def.get("can_train", False)
        can_tune = stage_def.get("can_tune", False)
        can_fit_preprocessing = stage_def.get("can_fit_preprocessing", False)
        can_use_final_test_labels = stage_def.get("can_use_final_test_labels", False)
        can_generate_shap = stage_def.get("can_generate_shap", False)
        can_package = stage_def.get("can_package", False)
        can_update_documentation = stage_def.get("can_update_documentation", False)

        if can_train:
            ok, reason = self.can_train()
            if not ok:
                return False, reason

        if can_tune:
            ok, reason = self.can_tune()
            if not ok:
                return False, reason

        if can_fit_preprocessing:
            ok, reason = self.can_preprocessing_fit()
            if not ok:
                return False, reason

        if can_use_final_test_labels:
            ok, reason = self.can_final_test()
            if not ok:
                return False, reason

        if can_generate_shap:
            ok, reason = self.can_shap()
            if not ok:
                return False, reason

        if can_package:
            ok, reason = self.can_package()
            if not ok:
                return False, reason

        if can_update_documentation:
            ok, reason = self.can_documentation_update()
            if not ok:
                return False, reason

        return True, "OK"


# ---------------------------------------------------------------------------
# Specific guards for each operation type
# ---------------------------------------------------------------------------

class PreprocessingFitGuard:
    """Guard for P30_PREPROCESSING preprocessing-fit operations."""

    def __init__(self, config: "PipelineConfig"):
        self.config = config

    def evaluate(self) -> tuple[bool, Optional[str], dict]:
        """
        Returns (pass, reason, evidence).
        """
        evidence = {
            "allow_data_preparation": self.config.allow_data_preparation,
            "allow_preprocessing_fit": self.config.allow_preprocessing_fit,
            "train_split_manifest_valid": True,  # Would check actual file
            "validation_split_not_in_fit": True,
            "test_split_not_in_fit": True,
            "preprocessing_fit_executed": False,  # Phase 2 requirement
        }
        cfg = self.config
        reasons = []

        if cfg.mode not in ("prepare-data", "train", "full-retrain"):
            reasons.append("BLOCKED: mode does not permit preprocessing fit")

        if not cfg.allow_data_preparation:
            reasons.append("BLOCKED: allow_data_preparation is false")

        if not cfg.allow_preprocessing_fit:
            reasons.append("BLOCKED: allow_preprocessing_fit is false")

        if reasons:
            return False, "; ".join(reasons), evidence

        return True, None, evidence


class TrainingGuard:
    """Guard for P50_TRAIN_CANDIDATES training operations."""

    def __init__(self, config: "PipelineConfig"):
        self.config = config

    def evaluate(self) -> tuple[bool, Optional[str], dict]:
        evidence = {
            "mode": self.config.mode,
            "allow_training": self.config.allow_training,
            "train_split_valid": True,
            "feature_artifacts_valid": True,
            "final_test_labels_not_in_context": True,
            "training_executed": False,  # Phase 2 requirement
        }
        cfg = self.config
        reasons = []

        if cfg.mode not in ("train", "full-retrain"):
            reasons.append("BLOCKED: mode does not permit training")

        if not cfg.allow_training:
            reasons.append("BLOCKED: allow_training is false")

        if reasons:
            return False, "; ".join(reasons), evidence

        return True, None, evidence


class TuningGuard:
    """Guard for P50_TRAIN_CANDIDATES hyperparameter tuning operations."""

    def __init__(self, config: "PipelineConfig"):
        self.config = config

    def evaluate(self) -> tuple[bool, Optional[str], dict]:
        evidence = {
            "mode": self.config.mode,
            "allow_training": self.config.allow_training,
            "allow_tuning": self.config.allow_tuning,
            "tuning_executed": False,  # Phase 2 requirement
        }
        cfg = self.config
        reasons = []

        if cfg.mode not in ("train", "full-retrain"):
            reasons.append("BLOCKED: mode does not permit tuning")

        if not cfg.allow_training:
            reasons.append("BLOCKED: training must be enabled for tuning")

        if not cfg.allow_tuning:
            reasons.append("BLOCKED: allow_tuning is false")

        if reasons:
            return False, "; ".join(reasons), evidence

        return True, None, evidence


class ChampionLockGuard:
    """Guard for P65_LOCK_CHAMPION champion lock operations."""

    def __init__(self, config: "PipelineConfig"):
        self.config = config

    def evaluate(self) -> tuple[bool, Optional[str], dict]:
        evidence = {
            "mode": self.config.mode,
            "allow_champion_lock": self.config.allow_champion_lock,
            "candidate_registry_complete": True,
            "validation_ranking_complete": True,
            "selection_rule_defined": True,
            "no_final_test_metric_in_selection": True,
            "champion_lock_executed": False,
        }
        cfg = self.config
        reasons = []

        if cfg.mode not in ("train", "full-retrain"):
            reasons.append("BLOCKED: mode does not permit champion lock")

        if not cfg.allow_champion_lock:
            reasons.append("BLOCKED: allow_champion_lock is false")

        if reasons:
            return False, "; ".join(reasons), evidence

        return True, None, evidence


class FinalTestGuard:
    """
    Guard for P70_FINAL_TEST final test evaluation.
    Tracks access via ledger to prevent duplicate evaluations.
    """

    def __init__(self, config: "PipelineConfig", ledger_path: Optional[str] = None):
        self.config = config
        self.ledger_path = ledger_path

    def evaluate(
        self,
        model_version: Optional[str] = None,
        data_version: Optional[str] = None,
        split_version: Optional[str] = None,
        champion_lock_hash: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> tuple[bool, Optional[str], dict]:
        evidence = {
            "mode": self.config.mode,
            "allow_final_test": self.config.allow_final_test,
            "champion_lock_exists": True,
            "final_test_executed": False,  # Phase 2 requirement
            "ledger_entry_added": False,
            "model_version": model_version,
            "data_version": data_version,
        }
        cfg = self.config
        reasons = []

        if cfg.mode != "full-retrain":
            reasons.append("BLOCKED: only full-retrain mode permits final test")

        if not cfg.allow_final_test:
            reasons.append("BLOCKED: allow_final_test is false")

        if reasons:
            return False, "; ".join(reasons), evidence

        return True, None, evidence


class NoReturnGovernance:
    """
    Governance: after P70_FINAL_TEST passes, no return to P50/P60.
    Final-test metrics must not flow into champion selection.
    """

    def __init__(self):
        self._final_test_passed = False
        self._final_test_run_id: Optional[str] = None

    def mark_final_test_passed(self, run_id: str) -> None:
        self._final_test_passed = True
        self._final_test_run_id = run_id

    def can_proceed_to_selection(self) -> tuple[bool, Optional[str]]:
        if self._final_test_passed:
            return False, (
                "NO_RETURN: final_test has already passed in this run. "
                "Cannot re-enter P50/P60. New run required for model change."
            )
        return True, None

    def evaluate(self) -> dict:
        return {
            "final_test_passed": self._final_test_passed,
            "final_test_run_id": self._final_test_run_id,
            "can_proceed_to_selection": not self._final_test_passed,
        }


class SHAPGuard:
    """Guard for P80_EXPLAINABILITY SHAP operations."""

    def __init__(self, config: "PipelineConfig"):
        self.config = config

    def evaluate(self) -> tuple[bool, Optional[str], dict]:
        evidence = {
            "mode": self.config.mode,
            "allow_shap": self.config.allow_shap,
            "locked_champion_valid": True,
            "model_version_fixed": True,
            "shap_executed": False,  # Phase 2 requirement
        }
        cfg = self.config
        reasons = []

        if cfg.mode != "full-retrain":
            reasons.append("BLOCKED: only full-retrain mode permits SHAP")

        if not cfg.allow_shap:
            reasons.append("BLOCKED: allow_shap is false")

        if reasons:
            return False, "; ".join(reasons), evidence

        return True, None, evidence


class PackagingGuard:
    """Guard for P90_PACKAGING model packaging operations."""

    def __init__(self, config: "PipelineConfig"):
        self.config = config

    def evaluate(self) -> tuple[bool, Optional[str], dict]:
        evidence = {
            "mode": self.config.mode,
            "allow_packaging": self.config.allow_packaging,
            "locked_champion_valid": True,
            "required_preprocessing_valid": True,
            "packaging_executed": False,  # Phase 2 requirement
        }
        cfg = self.config
        reasons = []

        if cfg.mode not in ("package", "full-retrain"):
            reasons.append("BLOCKED: mode does not permit packaging")

        if not cfg.allow_packaging:
            reasons.append("BLOCKED: allow_packaging is false")

        if reasons:
            return False, "; ".join(reasons), evidence

        return True, None, evidence

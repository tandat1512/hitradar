"""
Tests for StageResult contract compliance.
Feature 2.9 Phase 2 — test_feature_2_9_stage_result.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.pipeline_types import (
    StageResult, StageCheckpoint, StageStatus,
)


class TestStageResultContract:
    """StageResult must conform exactly to the contract."""

    def test_contract_has_stage_id(self):
        result = StageResult(stage_id="P50_TRAIN_CANDIDATES")
        assert result.stage_id == "P50_TRAIN_CANDIDATES"

    def test_contract_has_status(self):
        result = StageResult(stage_id="P00", status=StageStatus.PASS)
        assert result.status == StageStatus.PASS

    def test_contract_has_started_at(self):
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        result = StageResult(stage_id="P00", started_at=ts)
        assert result.started_at == ts

    def test_contract_has_ended_at(self):
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).isoformat()
        result = StageResult(stage_id="P00", ended_at=ts)
        assert result.ended_at == ts

    def test_contract_has_duration_seconds(self):
        result = StageResult(stage_id="P00", duration_seconds=12.5)
        assert result.duration_seconds == 12.5

    def test_contract_has_exit_code(self):
        result = StageResult(stage_id="P00", exit_code=0)
        assert result.exit_code == 0

    def test_contract_has_command(self):
        result = StageResult(stage_id="P00", command="python run_phase2.py")
        assert "run_phase2" in result.command

    def test_contract_has_python_callable(self):
        result = StageResult(
            stage_id="P00",
            python_callable="src.hitradar_automation.orchestrator:run_preflight",
        )
        assert "run_preflight" in result.python_callable

    def test_contract_has_inputs(self):
        result = StageResult(
            stage_id="P00",
            inputs=["7.6.feature_engineering/features.parquet"],
        )
        assert len(result.inputs) == 1

    def test_contract_has_outputs(self):
        result = StageResult(
            stage_id="P50",
            outputs=["7.7.model_training/models/model.joblib"],
        )
        assert len(result.outputs) == 1

    def test_contract_has_warnings(self):
        result = StageResult(
            stage_id="P00",
            status=StageStatus.PASS_WITH_WARNINGS,
            warnings=["deprecated parameter used"],
        )
        assert len(result.warnings) == 1

    def test_contract_has_blockers(self):
        result = StageResult(
            stage_id="P00",
            status=StageStatus.FAIL,
            blockers=["SCHEMA_MISMATCH"],
        )
        assert len(result.blockers) == 1

    def test_contract_has_metrics(self):
        result = StageResult(
            stage_id="P00",
            metrics={"accuracy": 0.87, "auc": 0.91},
        )
        assert result.metrics["auc"] == 0.91

    def test_contract_has_training_executed_flag(self):
        result = StageResult(stage_id="P50", training_executed=False)
        assert result.training_executed is False

    def test_contract_has_tuning_executed_flag(self):
        result = StageResult(stage_id="P50", tuning_executed=False)
        assert result.tuning_executed is False

    def test_contract_has_preprocessing_fit_executed_flag(self):
        result = StageResult(stage_id="P30", preprocessing_fit_executed=False)
        assert result.preprocessing_fit_executed is False

    def test_contract_has_final_test_executed_flag(self):
        result = StageResult(stage_id="P70", final_test_executed=False)
        assert result.final_test_executed is False

    def test_contract_has_shap_executed_flag(self):
        result = StageResult(stage_id="P80", shap_executed=False)
        assert result.shap_executed is False

    def test_contract_has_packaging_executed_flag(self):
        result = StageResult(stage_id="P90", packaging_executed=False)
        assert result.packaging_executed is False

    def test_contract_has_stdout_path(self):
        result = StageResult(
            stage_id="P00",
            stdout_path="/run/stdout/P00.stdout.txt",
        )
        assert "P00" in result.stdout_path

    def test_contract_has_stderr_path(self):
        result = StageResult(
            stage_id="P00",
            stderr_path="/run/stderr/P00.stderr.txt",
        )
        assert "P00" in result.stderr_path

    def test_contract_serializes_to_dict(self):
        """StageResult serializes to dict with all required keys."""
        result = StageResult(
            stage_id="P00",
            status=StageStatus.PASS,
            training_executed=False,
            tuning_executed=False,
            preprocessing_fit_executed=False,
            final_test_executed=False,
            shap_executed=False,
            packaging_executed=False,
        )
        d = result.to_dict()
        assert "stage_id" in d
        assert "status" in d
        assert "training_executed" in d
        assert "tuning_executed" in d
        assert "preprocessing_fit_executed" in d
        assert "final_test_executed" in d
        assert "shap_executed" in d
        assert "packaging_executed" in d

    def test_contract_deserializes_from_dict(self):
        """StageResult can be reconstructed from dict."""
        d = {
            "stage_id": "P00",
            "status": StageStatus.PASS,
            "started_at": None,
            "ended_at": None,
            "duration_seconds": 0.0,
            "exit_code": 0,
            "command": None,
            "python_callable": None,
            "inputs": [],
            "outputs": [],
            "warnings": [],
            "blockers": [],
            "metrics": {},
            "training_executed": False,
            "tuning_executed": False,
            "preprocessing_fit_executed": False,
            "final_test_executed": False,
            "shap_executed": False,
            "packaging_executed": False,
            "stdout_path": None,
            "stderr_path": None,
            "error_message": None,
            "traceback_path": None,
        }
        result = StageResult.from_dict(d)
        assert result.stage_id == "P00"
        assert result.status == StageStatus.PASS
        assert result.training_executed is False

    def test_adapter_cannot_claim_pass_on_exception(self):
        """If an exception occurs, adapter must NOT claim PASS."""
        result = StageResult(
            stage_id="P00",
            status=StageStatus.FAIL,
            blockers=["EXCEPTION: ValueError: dimension mismatch"],
        )
        assert result.is_pass() is False

    def test_adapter_cannot_claim_pass_on_nonzero_exit(self):
        """If subprocess exits non-zero, adapter must NOT claim PASS."""
        result = StageResult(
            stage_id="P10",
            status=StageStatus.FAIL,
            exit_code=1,
            blockers=["SUBPROCESS_ERROR: exit code 1"],
        )
        assert result.is_pass() is False

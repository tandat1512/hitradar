import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_9" / "validation"


def test_phase_one_did_not_train_refit_or_mutate_locked_artifacts():
    audit = json.loads((REPORT / "feature_3_9_model_artifact_integrity.json").read_text(encoding="utf-8"))
    assert audit["training_executed"] is False
    assert audit["tuning_executed"] is False
    assert audit["refit_executed"] is False
    assert audit["model_artifacts_modified"] is False
    assert audit["dataset_modified"] is False
    assert audit["artifact_hash_mismatch_count"] == 0

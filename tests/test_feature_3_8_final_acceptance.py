import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def _json(name: str):
    return json.loads((REPORT / name).read_text(encoding="utf-8"))


def test_final_story_and_outline_use_current_dataset_scope():
    for name in ("feature_3_8_project_story.md", "feature_3_8_slide_outline.md"):
        text = (REPORT / name).read_text(encoding="utf-8")
        assert "586,672" in text
        assert "1900–2021" in text
        assert "169,681" not in text
        assert "1922–2019" not in text


def test_slide_fact_crosscheck_is_zero_after_correction():
    audit = _json("feature_3_8_final_slide_fact_crosscheck.json")
    keys = (
        "dataset_mismatches",
        "model_mismatches",
        "metric_mismatches",
        "feature_count_mismatches",
        "architecture_mismatches",
        "performance_mismatches",
        "test_result_mismatches",
    )
    assert all(audit[key] == 0 for key in keys)
    assert audit["total_mismatches"] == 0


def test_missing_deck_is_not_reported_ready():
    audit = _json("feature_3_8_final_slide_audit.json")
    assert audit["actual_deck_exists"] is False
    assert audit["semantic_placeholder_count"] == 1
    assert audit["slide_content_complete"] is False
    assert audit["render_validation"] == "NOT_POSSIBLE_NO_DECK"
    assert audit["status"] == "FAIL"


def test_live_smoke_uses_measured_canonical_results():
    smoke = _json("feature_3_8_final_live_demo_smoke.json")
    assert smoke["backend"]["health"]["model_loaded"] is True
    assert smoke["predict"]["prediction_raw"] == 46.421062
    assert smoke["explain"]["status"] == "PASS"
    assert smoke["what_if"]["delta"] == -2.375583
    assert smoke["music_trends"]["rows"] == 586672


def test_offline_fallback_failure_is_not_hidden():
    smoke = _json("feature_3_8_final_fallback_smoke.json")
    assert smoke["automatic_offline_ui_validated"] is False
    assert smoke["backup_screenshots_accessible"] is False
    assert smoke["backup_video_accessible"] is False
    assert smoke["status"] == "FAIL"


def test_human_rehearsals_remain_pending_and_counts_unknown():
    audit = _json("feature_3_8_final_rehearsal_audit.json")
    assert audit["rehearsal_1"]["actual_human_completed"] is False
    assert audit["rehearsal_2"]["actual_human_completed"] is False
    assert audit["remaining_blockers"] is None
    assert audit["remaining_high"] is None
    assert audit["status"] == "WAITING_FOR_HUMAN_ACTION"


def test_claim_audit_has_no_unsafe_positive_claims():
    audit = _json("feature_3_8_final_claim_audit.json")
    for key in (
        "unsupported_accuracy_claim_count",
        "guaranteed_success_claim_count",
        "causal_shap_claim_count",
        "causal_what_if_claim_count",
        "production_ready_overclaim_count",
        "offline_live_misrepresentation_count",
    ):
        assert audit[key] == 0
    scope = audit["scan_scope"]
    assert scope["includes_final_reports"] is True
    assert scope["includes_validation_subtree"] is True
    assert scope["includes_handoff_and_rehearsal_artifacts"] is True


def test_product_artifacts_match_known_hashes():
    audit = _json("feature_3_8_product_immutability_audit.json")
    assert audit["model_artifacts_modified"] is False
    assert audit["source_dataset_modified"] is False
    assert audit["shap_artifacts_modified"] is False
    assert audit["production_business_logic_modified"] is None
    assert audit["product_immutability_proven"] is False
    proven = [check for check in audit["checks"] if check["expected_sha256"]]
    assert {check["area"] for check in proven} >= {
        "model",
        "dataset",
        "shap_background_raw",
        "shap_background_transformed",
        "shap_values_global",
    }
    assert all(check["current_sha256"] == check["expected_sha256"] for check in proven)


def test_validation_subtree_is_synchronized_with_current_evidence():
    registry = _json("validation/feature_3_8_defense_source_registry.json")
    dataset = registry["source_sections"]["DATASET_FACTS"]
    shap = registry["source_sections"]["SHAP"]
    assert dataset["records"] == 586672
    assert dataset["year_range"] == "1900-2021"
    assert shap["epic2_artifact_background_samples"] == 1000
    assert shap["live_backend_background_argument"] is False

    scenario = _json("validation/feature_3_8_demo_scenario.json")
    assert scenario["final_explain_observation"]["status"] == "PASS"
    assert scenario["what_if"]["feature"] == "energy"
    assert scenario["what_if"]["delta"] == -2.375583


def test_shap_documentation_distinguishes_artifact_and_live_runtime():
    text = (REPORT / "DEFENSE_QA_SHAP.md").read_text(encoding="utf-8")
    assert "1,000" in text
    assert "TreeExplainer(model)" in text
    assert "không truyền background artifact" in text


def test_technical_environment_and_traceability_are_not_overstated():
    environment = _json("feature_3_8_final_technical_environment.json")
    gate = _json("feature_3_8_closure_gate.json")
    assert environment["ready"] is False
    assert environment["status"] == "PARTIAL"
    assert gate["git_commit"] is None
    assert gate["package_git_tracking_status"] == "UNTRACKED"
    assert gate["package_reproducible_from_git_commit"] is False
    assert gate["product_immutability_proven"] is False


def test_manifest_paths_hashes_and_sizes_match_files():
    manifest = _json("feature_3_8_defense_package_manifest.json")
    for item in manifest["items"]:
        if not item["exists"]:
            assert item["path"] is None
            assert item["sha256"] is None
            assert item["bytes"] == 0
            continue
        path = ROOT / Path(item["path"])
        assert path.is_file(), item["logical_name"]
        payload = path.read_bytes()
        assert len(payload) == item["bytes"], item["logical_name"]
        assert hashlib.sha256(payload).hexdigest() == item["sha256"], item["logical_name"]

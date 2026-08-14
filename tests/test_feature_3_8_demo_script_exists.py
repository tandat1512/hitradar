from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPIC3 = next((ROOT / "Bao_cao_3").glob("*epic3"))
REPORT = EPIC3 / "feature_3_8"


def test_phase_2_demo_artifacts_exist():
    required = {
        "feature_3_8_demo_source_validation.json",
        "feature_3_8_demo_scenario.json",
        "DEMO_SCRIPT_FEATURE_3_8.md",
        "feature_3_8_demo_step_registry.json",
        "feature_3_8_demo_timing_plan.json",
        "feature_3_8_demo_failure_tree.md",
        "feature_3_8_demo_backup_matrix.csv",
        "feature_3_8_demo_dry_run.json",
        "feature_3_8_demo_result_consistency.json",
        "feature_3_8_demo_claim_audit.json",
    }
    assert required <= {path.name for path in REPORT.iterdir() if path.is_file()}

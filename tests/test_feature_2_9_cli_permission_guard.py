import pytest, subprocess
from pathlib import Path

SCRIPT = Path(r"E:/Dự án 1 hitrada/hitradar/7.ML/7.12.optional_pipeline_automation/scripts/run_epic2_pipeline.py")

def test_train_mode_without_flags_shows_blocked():
    """Training mode without --allow-training should show blocked stages in dry-run.
    Note: We capture but do not let it overwrite the canonical dry-run plan."""
    result = subprocess.run(["python", str(SCRIPT), "--mode", "train", "--dry-run"],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "BLOCKED" in result.stdout or "blocked" in result.stdout.lower()

    # Restore the validate dry-run plan after this test
    import json
    from datetime import datetime, timezone
    F29 = Path(r"E:/Dự án 1 hitrada/hitradar/7.ML/7.12.optional_pipeline_automation")
    canonical_path = F29 / "validation" / "epic2_pipeline_dry_run_plan.json"
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        stages = json.load(f)
    with open(F29 / "registries" / "epic2_pipeline_mode_contract.json", encoding="utf-8") as f:
        mc = json.load(f)
    vs = mc["validate"]["stages"]
    vf = mc["validate"]["forbidden_stages"]
    plan = []
    for s in stages:
        sid = s["stage_id"]
        plan.append({
            "stage_id": sid, "display_name": s["display_name"],
            "will_run": sid in vs, "blocked": False,
            "skip_reason": "FORBIDDEN in mode validate" if sid in vf else None,
            "required_permissions": [], "input_artifacts": s.get("reads", []),
            "expected_outputs": s.get("expected_outputs", []),
            "scientific_side_effects": s.get("scientific_side_effects", False),
            "estimated_risk": "HIGH" if s.get("can_train") or s.get("can_use_final_test_labels") else "LOW"
        })
    data = {"mode": "validate", "dry_run": True, "plan": plan,
            "scientific_side_effect_count": 0, "training_in_plan": False,
            "final_test_in_plan": False, "shap_in_plan": False,
            "generated_at": datetime.now(timezone.utc).isoformat()}
    with open(canonical_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

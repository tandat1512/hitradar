#!/usr/bin/env python3
"""
run_epic2_pipeline.py — EPIC 2 Pipeline Orchestrator
HitRadar Pro — Feature 2.9 Optional Pipeline Automation

Usage:
    python run_epic2_pipeline.py --help
    python run_epic2_pipeline.py --config <path> --mode validate
    python run_epic2_pipeline.py --config <path> --mode validate --dry-run
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Exit codes
EXIT_PASS = 0
EXIT_PASS_WITH_WARNINGS = 2
EXIT_CONFIG_ERROR = 10
EXIT_MODE_ERROR = 11
EXIT_PERMISSION_BLOCK = 12
EXIT_UPSTREAM_GATE_BLOCK = 13
EXIT_STAGE_REGISTRY_ERROR = 14
EXIT_EXECUTION_FAILURE = 20
EXIT_GOVERNANCE_VIOLATION = 30

VALID_MODES = ["validate", "prepare-data", "train", "full-retrain", "package", "monitor"]

def load_yaml_config(path):
    """Load YAML config. Falls back to basic parsing if PyYAML unavailable."""
    try:
        import yaml
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except ImportError:
        print("WARNING: PyYAML not installed. Using minimal config.")
        return {
            "pipeline": {"mode": "validate", "fail_fast": True, "resume": False, "dry_run": False, "allow_scientific_writes": False},
            "permissions": {k: False for k in ["allow_data_preparation","allow_preprocessing_fit","allow_training",
                            "allow_tuning","allow_champion_lock","allow_final_test","allow_shap",
                            "allow_packaging","allow_documentation_update"]},
            "execution": {"max_parallel_stages": 1, "subprocess_timeout_seconds": 3600},
            "tracking": {"backend": "local_json", "mlflow_enabled": False},
            "paths": {}
        }

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def resolve_paths(config, script_dir):
    """Resolve relative paths from config or script location."""
    repo_root = config.get("paths", {}).get("repository_root")
    if not repo_root:
        # Walk up from script location to find .git
        current = Path(script_dir)
        while current != current.parent:
            if (current / ".git").exists():
                repo_root = str(current)
                break
            current = current.parent
    return repo_root

def check_dual_consent(config, args, operation, config_key, cli_flag_name):
    """Check dual-consent: config permission AND CLI flag."""
    config_val = config.get("permissions", {}).get(config_key, False)
    cli_val = getattr(args, cli_flag_name.replace("-", "_").lstrip("-"), False)
    return config_val and cli_val

def build_plan(stages, mode_contract, mode, args, config):
    """Build execution plan for a given mode."""
    mode_def = mode_contract.get(mode)
    if not mode_def:
        return None, f"Unknown mode: {mode}"

    allowed_stages = mode_def.get("stages", [])
    forbidden_stages = mode_def.get("forbidden_stages", [])

    plan = []
    for stage in stages:
        sid = stage["stage_id"]
        entry = {
            "stage_id": sid,
            "display_name": stage["display_name"],
            "will_run": sid in allowed_stages,
            "blocked": False,
            "skip_reason": None,
            "required_permissions": [],
            "input_artifacts": stage.get("reads", []),
            "expected_outputs": stage.get("expected_outputs", []),
            "scientific_side_effects": stage.get("scientific_side_effects", False),
            "estimated_risk": "HIGH" if stage.get("can_train") or stage.get("can_use_final_test_labels") else "LOW"
        }

        if sid in forbidden_stages:
            entry["will_run"] = False
            entry["skip_reason"] = f"FORBIDDEN in mode '{mode}'"

        # Permission checks for high-risk stages
        if entry["will_run"]:
            if stage.get("can_train") and not check_dual_consent(config, args, "training", "allow_training", "allow_training"):
                entry["blocked"] = True
                entry["skip_reason"] = "BLOCKED_BY_PERMISSION: training requires dual consent"
                entry["required_permissions"].append("allow_training (config + CLI)")

            if stage.get("can_tune") and not check_dual_consent(config, args, "tuning", "allow_tuning", "allow_tuning"):
                if stage.get("can_train"):
                    entry["required_permissions"].append("allow_tuning (config + CLI) — optional")

            if stage.get("can_use_final_test_labels") and not check_dual_consent(config, args, "final_test", "allow_final_test", "allow_final_test"):
                entry["blocked"] = True
                entry["skip_reason"] = "BLOCKED_BY_PERMISSION: final_test requires dual consent"
                entry["required_permissions"].append("allow_final_test (config + CLI)")

            if stage.get("can_generate_shap") and not check_dual_consent(config, args, "shap", "allow_shap", "allow_shap"):
                entry["blocked"] = True
                entry["skip_reason"] = "BLOCKED_BY_PERMISSION: SHAP requires dual consent"
                entry["required_permissions"].append("allow_shap (config + CLI)")

            if stage.get("can_package") and not check_dual_consent(config, args, "packaging", "allow_packaging", "allow_packaging"):
                entry["blocked"] = True
                entry["skip_reason"] = "BLOCKED_BY_PERMISSION: packaging requires dual consent"
                entry["required_permissions"].append("allow_packaging (config + CLI)")

            if stage.get("can_fit_preprocessing") and not check_dual_consent(config, args, "preprocessing_fit", "allow_preprocessing_fit", "allow_preprocessing_fit"):
                entry["blocked"] = True
                entry["skip_reason"] = "BLOCKED_BY_PERMISSION: preprocessing fit requires dual consent"
                entry["required_permissions"].append("allow_preprocessing_fit (config + CLI)")

        plan.append(entry)

    return plan, None

def main():
    parser = argparse.ArgumentParser(
        prog="run_epic2_pipeline",
        description="EPIC 2 Pipeline Orchestrator — HitRadar Pro (Feature 2.9)",
        epilog="All scientific operations require dual consent (config + CLI flag)."
    )
    parser.add_argument("--config", type=str, required=False, help="Path to YAML configuration file")
    parser.add_argument("--mode", type=str, choices=VALID_MODES, default=None, help="Pipeline execution mode")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Plan only, no execution")
    parser.add_argument("--resume", action="store_true", default=False, help="Resume from last checkpoint")
    parser.add_argument("--run-id", type=str, default=None, help="Explicit run ID")
    parser.add_argument("--from-stage", type=str, default=None, help="Start from specific stage")
    parser.add_argument("--to-stage", type=str, default=None, help="Stop after specific stage")

    # Permission flags (dual consent)
    parser.add_argument("--allow-scientific-writes", action="store_true", default=False)
    parser.add_argument("--allow-data-preparation", action="store_true", default=False)
    parser.add_argument("--allow-preprocessing-fit", action="store_true", default=False)
    parser.add_argument("--allow-training", action="store_true", default=False)
    parser.add_argument("--allow-tuning", action="store_true", default=False)
    parser.add_argument("--allow-champion-lock", action="store_true", default=False)
    parser.add_argument("--allow-final-test", action="store_true", default=False)
    parser.add_argument("--allow-shap", action="store_true", default=False)
    parser.add_argument("--allow-packaging", action="store_true", default=False)
    parser.add_argument("--allow-documentation-update", action="store_true", default=False)
    parser.add_argument("--allow-monitoring", action="store_true", default=False)

    parser.add_argument("--fail-fast", action="store_true", default=True)
    parser.add_argument("--no-fail-fast", action="store_true", default=False)
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG","INFO","WARNING","ERROR"])
    parser.add_argument("--json-summary", action="store_true", default=False, help="Output JSON summary")

    args = parser.parse_args()

    if args.no_fail_fast:
        args.fail_fast = False

    # Resolve script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    f29_dir = os.path.dirname(script_dir)  # Parent of scripts/

    # Load config
    config = {}
    if args.config:
        if not os.path.exists(args.config):
            print(f"ERROR: Config file not found: {args.config}")
            sys.exit(EXIT_CONFIG_ERROR)
        config = load_yaml_config(args.config)
    else:
        # Try default config location
        default_config = os.path.join(f29_dir, "configs", "epic2_pipeline_config.yaml")
        if os.path.exists(default_config):
            config = load_yaml_config(default_config)
        else:
            print("WARNING: No config file found, using safe defaults")
            config = {"pipeline": {"mode": "validate"}, "permissions": {}, "execution": {}, "tracking": {}, "paths": {}}

    # Resolve mode: CLI overrides config
    mode = args.mode or config.get("pipeline", {}).get("mode", "validate")
    if mode not in VALID_MODES:
        print(f"ERROR: Invalid mode '{mode}'. Valid: {VALID_MODES}")
        sys.exit(EXIT_MODE_ERROR)

    dry_run = args.dry_run or config.get("pipeline", {}).get("dry_run", False)

    # Resolve repo root
    repo_root = resolve_paths(config, script_dir)

    # Load stage registry
    registry_path = os.path.join(f29_dir, "registries", "epic2_pipeline_stage_registry.json")
    if not os.path.exists(registry_path):
        print(f"ERROR: Stage registry not found: {registry_path}")
        sys.exit(EXIT_STAGE_REGISTRY_ERROR)
    stages = load_json(registry_path)

    # Load mode contract
    mode_contract_path = os.path.join(f29_dir, "registries", "epic2_pipeline_mode_contract.json")
    if not os.path.exists(mode_contract_path):
        print(f"ERROR: Mode contract not found: {mode_contract_path}")
        sys.exit(EXIT_STAGE_REGISTRY_ERROR)
    mode_contract = load_json(mode_contract_path)

    # Build plan
    plan, error = build_plan(stages, mode_contract, mode, args, config)
    if error:
        print(f"ERROR: {error}")
        sys.exit(EXIT_MODE_ERROR)

    # Summary
    will_run = [p for p in plan if p["will_run"] and not p["blocked"]]
    blocked = [p for p in plan if p["blocked"]]
    skipped = [p for p in plan if not p["will_run"]]
    scientific_effects = [p for p in will_run if p["scientific_side_effects"]]

    print(f"\n{'='*60}")
    print(f"EPIC 2 PIPELINE — {mode.upper()} {'(DRY-RUN)' if dry_run else ''}")
    print(f"{'='*60}")
    print(f"Mode:              {mode}")
    print(f"Dry-run:           {dry_run}")
    print(f"Repository:        {repo_root}")
    print(f"Stages to run:     {len(will_run)}")
    print(f"Stages blocked:    {len(blocked)}")
    print(f"Stages skipped:    {len(skipped)}")
    print(f"Scientific effects:{len(scientific_effects)}")

    if dry_run:
        print(f"\n--- DRY-RUN PLAN ---")
        for p in plan:
            status = "RUN" if (p["will_run"] and not p["blocked"]) else "BLOCKED" if p["blocked"] else "SKIP"
            marker = "✓" if status == "RUN" else "✗" if status == "BLOCKED" else "–"
            print(f"  {marker} {p['stage_id']}: {status}")
            if p.get("skip_reason"):
                print(f"    Reason: {p['skip_reason']}")

        # Save dry-run plan
        dry_run_output = os.path.join(f29_dir, "validation", "epic2_pipeline_dry_run_plan.json")
        os.makedirs(os.path.dirname(dry_run_output), exist_ok=True)
        with open(dry_run_output, 'w', encoding='utf-8') as f:
            json.dump({"mode": mode, "dry_run": True, "plan": plan,
                       "scientific_side_effect_count": len(scientific_effects),
                       "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)
        print(f"\nDry-run plan saved: {dry_run_output}")
        sys.exit(EXIT_PASS)

    # Non dry-run: Phase 1 only supports dry-run for now
    print("\nNOTE: Full execution is not yet implemented (Phase 1 = Foundation only).")
    print("Use --dry-run to generate execution plan.")

    if args.json_summary:
        summary = {
            "mode": mode, "dry_run": dry_run,
            "stages_planned": len(will_run),
            "stages_blocked": len(blocked),
            "scientific_effects": len(scientific_effects),
            "status": "DRY_RUN_ONLY"
        }
        print(json.dumps(summary, indent=2))

    sys.exit(EXIT_PASS)

if __name__ == "__main__":
    main()

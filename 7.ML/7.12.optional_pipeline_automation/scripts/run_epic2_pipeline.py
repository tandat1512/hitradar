#!/usr/bin/env python3
"""
run_epic2_pipeline.py — EPIC 2 Pipeline Orchestrator
HitRadar Pro — Feature 2.9 Optional Pipeline Automation

Phase: 2/5 — Orchestrator Runtime, Stage Execution, Checkpoint, Safe Resume,
          Fail-Fast, Run Lock, Artifact Fingerprints, ML Governance Guards

Owner: Tuấn Anh

Usage:
    python run_epic2_pipeline.py --help
    python run_epic2_pipeline.py --config <path> --mode validate
    python run_epic2_pipeline.py --config <path> --mode validate --dry-run
    python run_epic2_pipeline.py --mode train --allow-training --allow-champion-lock
    python run_epic2_pipeline.py --mode full-retrain --allow-training --allow-tuning \
        --allow-final-test --allow-shap --allow-packaging
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add src to path for imports
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_F29_DIR = os.path.dirname(_SCRIPT_DIR)  # Parent of scripts/
_SRC_DIR = os.path.join(_F29_DIR, "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from hitradar_automation import (
    PipelineConfig,
    PipelineOrchestrator,
    compute_config_fingerprints,
    compute_environment_fingerprint,
    AtomicWriter,
)
from hitradar_automation.pipeline_types import StageStatus, RunStatus, make_run_id

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


# ---------------------------------------------------------------------------
# Config Loading
# ---------------------------------------------------------------------------

def load_yaml_config(path):
    """Load YAML config. Falls back to safe defaults if PyYAML unavailable."""
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        print("WARNING: PyYAML not installed. Using safe defaults.")
        return _safe_defaults()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _safe_defaults():
    return {
        "pipeline": {
            "mode": "validate",
            "fail_fast": True,
            "resume": False,
            "dry_run": False,
            "allow_scientific_writes": False,
        },
        "permissions": {
            k: False for k in [
                "allow_data_preparation", "allow_preprocessing_fit",
                "allow_training", "allow_tuning", "allow_champion_lock",
                "allow_final_test", "allow_shap", "allow_packaging",
                "allow_documentation_update", "allow_monitoring",
            ]
        },
        "execution": {"max_parallel_stages": 1, "subprocess_timeout_seconds": 3600},
        "tracking": {"backend": "local_json", "mlflow_enabled": False},
        "paths": {},
    }


def resolve_paths(config, script_dir):
    """Walk up from script location to find .git as repo root."""
    current = Path(script_dir)
    while current != current.parent:
        if (current / ".git").exists():
            return str(current)
        current = current.parent
    return str(Path(script_dir).parent)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="run_epic2_pipeline",
        description="EPIC 2 Pipeline Orchestrator — HitRadar Pro (Feature 2.9)",
        epilog="All scientific operations require dual consent (config + CLI flag).",
    )
    parser.add_argument("--config", type=str, help="Path to YAML configuration file")
    parser.add_argument("--mode", type=str, choices=VALID_MODES, help="Pipeline execution mode")
    parser.add_argument("--dry-run", action="store_true", help="Plan only, no execution")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--run-id", type=str, help="Explicit run ID")
    parser.add_argument("--from-stage", type=str, help="Start from specific stage (future)")
    parser.add_argument("--to-stage", type=str, help="Stop after specific stage (future)")

    # Permission flags (dual consent)
    parser.add_argument("--allow-scientific-writes", action="store_true")
    parser.add_argument("--allow-data-preparation", action="store_true")
    parser.add_argument("--allow-preprocessing-fit", action="store_true")
    parser.add_argument("--allow-training", action="store_true")
    parser.add_argument("--allow-tuning", action="store_true")
    parser.add_argument("--allow-champion-lock", action="store_true")
    parser.add_argument("--allow-final-test", action="store_true")
    parser.add_argument("--allow-shap", action="store_true")
    parser.add_argument("--allow-packaging", action="store_true")
    parser.add_argument("--allow-documentation-update", action="store_true")
    parser.add_argument("--allow-monitoring", action="store_true")

    # Execution control
    parser.add_argument("--fail-fast", action="store_true", default=True)
    parser.add_argument("--no-fail-fast", action="store_true")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--json-summary", action="store_true", help="Output JSON summary")
    parser.add_argument("--output-root", type=str, help="Override output root directory")

    return parser


# ---------------------------------------------------------------------------
# Config Builder
# ---------------------------------------------------------------------------

def build_config(args, raw_config: dict) -> PipelineConfig:
    """Build PipelineConfig from CLI args and raw config dict."""
    p = raw_config.get("pipeline", {})
    perms = raw_config.get("permissions", {})
    exec_ = raw_config.get("execution", {})
    paths = raw_config.get("paths", {})

    mode = args.mode or p.get("mode", "validate")
    fail_fast = p.get("fail_fast", True)
    if args.no_fail_fast:
        fail_fast = False

    def _flag(cli_name: str, cfg_name: str, default: bool = False) -> bool:
        cli_val = getattr(args, cli_name.replace("-", "_"), False)
        cfg_val = perms.get(cfg_name, default)
        return cli_val and cfg_val

    return PipelineConfig(
        mode=mode,
        fail_fast=fail_fast,
        resume=args.resume or p.get("resume", False),
        dry_run=args.dry_run or p.get("dry_run", False),
        allow_scientific_writes=args.allow_scientific_writes or p.get("allow_scientific_writes", False),
        allow_data_preparation=_flag("allow-data-preparation", "allow_data_preparation"),
        allow_preprocessing_fit=_flag("allow-preprocessing-fit", "allow_preprocessing_fit"),
        allow_training=_flag("allow-training", "allow_training"),
        allow_tuning=_flag("allow-tuning", "allow_tuning"),
        allow_champion_lock=_flag("allow-champion-lock", "allow_champion_lock"),
        allow_final_test=_flag("allow-final-test", "allow_final_test"),
        allow_shap=_flag("allow-shap", "allow_shap"),
        allow_packaging=_flag("allow-packaging", "allow_packaging"),
        allow_documentation_update=_flag("allow-documentation-update", "allow_documentation_update"),
        allow_monitoring=perms.get("allow_monitoring", True),
        max_parallel_stages=exec_.get("max_parallel_stages", 1),
        subprocess_timeout_seconds=exec_.get("subprocess_timeout_seconds", 3600),
        repository_root=paths.get("repository_root"),
        output_root=paths.get("output_root"),
    )


# ---------------------------------------------------------------------------
# Plan Builder (for dry-run display)
# ---------------------------------------------------------------------------

def build_plan(stages, mode_contract, mode, config: PipelineConfig):
    """Build execution plan with permission and mode checks."""
    mode_def = mode_contract.get(mode, {})
    allowed_stages = mode_def.get("stages", [])

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
            "scientific_side_effects": stage.get("scientific_side_effects", False),
        }

        if sid not in allowed_stages:
            entry["will_run"] = False
            entry["skip_reason"] = f"FORBIDDEN in mode '{mode}'"
        elif stage.get("can_train") and not config.allow_training:
            entry["blocked"] = True
            entry["skip_reason"] = "BLOCKED: training requires --allow-training and config flag"
            entry["required_permissions"].append("allow_training (dual consent)")
        elif stage.get("can_use_final_test_labels") and not config.allow_final_test:
            entry["blocked"] = True
            entry["skip_reason"] = "BLOCKED: final test requires --allow-final-test and config flag"
            entry["required_permissions"].append("allow_final_test (dual consent)")
        elif stage.get("can_generate_shap") and not config.allow_shap:
            entry["blocked"] = True
            entry["skip_reason"] = "BLOCKED: SHAP requires --allow-shap and config flag"
            entry["required_permissions"].append("allow_shap (dual consent)")
        elif stage.get("can_package") and not config.allow_packaging:
            entry["blocked"] = True
            entry["skip_reason"] = "BLOCKED: packaging requires --allow-packaging and config flag"
            entry["required_permissions"].append("allow_packaging (dual consent)")
        elif stage.get("can_fit_preprocessing") and not config.allow_preprocessing_fit:
            entry["blocked"] = True
            entry["skip_reason"] = "BLOCKED: preprocessing fit requires --allow-preprocessing-fit"
            entry["required_permissions"].append("allow_preprocessing_fit (dual consent)")

        plan.append(entry)

    return plan


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()

    # Load raw config
    raw_config = _safe_defaults()
    if args.config:
        if not os.path.exists(args.config):
            print(f"ERROR: Config file not found: {args.config}")
            sys.exit(EXIT_CONFIG_ERROR)
        raw_config = load_yaml_config(args.config)
    else:
        default_config = os.path.join(_F29_DIR, "configs", "epic2_pipeline_config.yaml")
        if os.path.exists(default_config):
            raw_config = load_yaml_config(default_config)

    # Resolve mode
    mode = args.mode or raw_config.get("pipeline", {}).get("mode", "validate")
    if mode not in VALID_MODES:
        print(f"ERROR: Invalid mode '{mode}'. Valid: {VALID_MODES}")
        sys.exit(EXIT_MODE_ERROR)

    dry_run = args.dry_run or raw_config.get("pipeline", {}).get("dry_run", False)

    # Resolve repo root
    repo_root = resolve_paths(raw_config, _SCRIPT_DIR)
    output_root = args.output_root or raw_config.get("paths", {}).get(
        "output_root") or os.path.join(_F29_DIR)

    # Build config
    config = build_config(args, raw_config)

    # Load stage registry
    registry_path = os.path.join(_F29_DIR, "registries", "epic2_pipeline_stage_registry.json")
    if not os.path.exists(registry_path):
        print(f"ERROR: Stage registry not found: {registry_path}")
        sys.exit(EXIT_STAGE_REGISTRY_ERROR)
    stages = load_json(registry_path)

    # Load mode contract
    mc_path = os.path.join(_F29_DIR, "registries", "epic2_pipeline_mode_contract.json")
    if not os.path.exists(mc_path):
        print(f"ERROR: Mode contract not found: {mc_path}")
        sys.exit(EXIT_STAGE_REGISTRY_ERROR)
    mode_contract = load_json(mc_path)

    # Generate run ID
    run_id = args.run_id or make_run_id(mode)

    # Build plan
    plan = build_plan(stages, mode_contract, mode, config)
    will_run = [p for p in plan if p["will_run"] and not p["blocked"]]
    blocked = [p for p in plan if p["blocked"]]
    skipped = [p for p in plan if not p["will_run"]]
    scientific = [p for p in will_run if p["scientific_side_effects"]]

    # Print header
    print(f"\n{'='*60}")
    print(f"EPIC 2 PIPELINE — {mode.upper()} {'(DRY-RUN)' if dry_run else ''}")
    print(f"{'='*60}")
    print(f"Run ID:          {run_id}")
    print(f"Mode:            {mode}")
    print(f"Dry-run:         {dry_run}")
    print(f"Fail-fast:       {config.fail_fast}")
    print(f"Resume:          {config.resume}")
    print(f"Repository:      {repo_root}")
    print(f"Output root:     {output_root}")
    print(f"Stages to run:   {len(will_run)}")
    print(f"Stages blocked:  {len(blocked)}")
    print(f"Stages skipped:  {len(skipped)}")
    print(f"Scientific eff.: {len(scientific)}")

    # Permission summary
    print(f"\n--- PERMISSION SUMMARY ---")
    print(f"  Training:            {config.allow_training}")
    print(f"  Tuning:              {config.allow_tuning}")
    print(f"  Preprocessing fit:   {config.allow_preprocessing_fit}")
    print(f"  Champion lock:       {config.allow_champion_lock}")
    print(f"  Final test:          {config.allow_final_test}")
    print(f"  SHAP:                {config.allow_shap}")
    print(f"  Packaging:           {config.allow_packaging}")

    # Dry-run: print plan and exit
    if dry_run:
        print(f"\n--- DRY-RUN PLAN ---")
        for p in plan:
            status = "RUN" if (p["will_run"] and not p["blocked"]) else \
                "BLOCKED" if p["blocked"] else "SKIP"
            marker = "✓" if status == "RUN" else "✗" if status == "BLOCKED" else "–"
            print(f"  {marker} {p['stage_id']}: {status}")
            if p.get("skip_reason"):
                print(f"      Reason: {p['skip_reason']}")

        dry_run_output = os.path.join(_F29_DIR, "validation", "epic2_pipeline_dry_run_plan.json")
        os.makedirs(os.path.dirname(dry_run_output), exist_ok=True)
        config_fps = compute_config_fingerprints(raw_config)
        dry_run_data = {
            "mode": mode,
            "run_id": run_id,
            "dry_run": True,
            "fail_fast": config.fail_fast,
            "plan": plan,
            "scientific_side_effect_count": len(scientific),
            "config_fingerprints": config_fps,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(dry_run_output, "w", encoding="utf-8") as f:
            json.dump(dry_run_data, f, indent=2)
        print(f"\nDry-run plan saved: {dry_run_output}")

        if args.json_summary:
            print(json.dumps({
                "run_id": run_id,
                "mode": mode,
                "dry_run": True,
                "stages_planned": len(will_run),
                "stages_blocked": len(blocked),
                "scientific_effects": len(scientific),
                "status": "DRY_RUN_ONLY",
            }, indent=2))

        sys.exit(EXIT_PASS)

    # Full execution
    print(f"\n--- EXECUTING PIPELINE ---")

    # Create orchestrator
    try:
        orchestrator = PipelineOrchestrator(
            config=config,
            stage_registry=stages,
            mode_contract=mode_contract,
            args=args,
        )
    except Exception as exc:
        print(f"ERROR: Failed to initialize orchestrator: {exc}")
        sys.exit(EXIT_STAGE_REGISTRY_ERROR)

    # Execute
    try:
        manifest = orchestrator.run(output_root, repo_root)

        # Print results
        print(f"\n--- PIPELINE COMPLETE ---")
        print(f"Run ID:           {manifest.run_id}")
        print(f"Status:           {manifest.status}")
        print(f"Stages passed:    {manifest.stage_passed}")
        print(f"Stages warnings:  {manifest.stage_warning}")
        print(f"Stages failed:    {manifest.stage_failed}")
        print(f"Stages skipped:   {manifest.stage_skipped}")
        print(f"Duration:         {manifest.duration_seconds:.1f}s")

        # Scientific actions
        print(f"\n--- SCIENTIFIC ACTIONS (canonical data) ---")
        print(f"  Training executed:           {manifest.training_executed} (MUST BE FALSE)")
        print(f"  Tuning executed:              {manifest.tuning_executed} (MUST BE FALSE)")
        print(f"  Preprocessing fit executed:   {manifest.preprocessing_fit_executed} (MUST BE FALSE)")
        print(f"  Final test executed:          {manifest.final_test_executed} (MUST BE FALSE)")
        print(f"  SHAP executed:                {manifest.shap_executed} (MUST BE FALSE)")
        print(f"  Packaging executed:           {manifest.packaging_executed} (MUST BE FALSE)")

        if manifest.warnings:
            print(f"\n--- WARNINGS ---")
            for w in manifest.warnings[:10]:
                print(f"  ⚠ {w}")

        if manifest.blockers:
            print(f"\n--- BLOCKERS ---")
            for b in manifest.blockers[:10]:
                print(f"  ✗ {b}")

        if args.json_summary:
            print(json.dumps(manifest.to_dict(), indent=2, default=str))

        # Exit code
        if manifest.status == RunStatus.FAIL:
            sys.exit(EXIT_EXECUTION_FAILURE)
        elif manifest.status == RunStatus.PASS_WITH_WARNINGS:
            sys.exit(EXIT_PASS_WITH_WARNINGS)
        else:
            sys.exit(EXIT_PASS)

    except RuntimeError as exc:
        if "lock" in str(exc).lower():
            print(f"\nERROR: {exc}")
            print("Another pipeline run is active. Use a different run-id or wait.")
            sys.exit(EXIT_EXECUTION_FAILURE)
        raise
    except Exception as exc:
        print(f"\nERROR: Pipeline execution failed: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(EXIT_EXECUTION_FAILURE)


if __name__ == "__main__":
    main()

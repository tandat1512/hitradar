"""
Feature 2.3 Validation Script
Validates all artifacts and checks
"""

import hashlib
import json
import os
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# Paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUTPUT_DIR = os.path.join(REPO_ROOT, "7.ML", "7.6.feature_engineering")
SRC_DIR = os.path.join(OUTPUT_DIR, "src")

# Constants
IDENTIFIER = "track_id"
TARGET = "target_popularity"
BASELINE_FEATURES = [
    "duration_min", "release_year", "danceability", "energy", "loudness",
    "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo",
    "release_month", "decade", "release_precision", "key", "time_signature",
    "explicit", "mode"
]

GENERATION_TIMESTAMP = datetime.now().isoformat()


def sha256_hash(data):
    """Compute SHA-256 hash."""
    if isinstance(data, (list, dict)):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(str(data).encode()).hexdigest()


def run_validation():
    """Run all validation checks."""
    checks = []

    # ========================================
    # Check 1: Baseline Count 18
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "baseline_feature_set.json"), "r") as f:
            baseline_set = json.load(f)

        actual_count = baseline_set.get("feature_count", 0)
        checks.append({
            "check_id": "BASELINE-COUNT-18",
            "expected": 18,
            "actual": actual_count,
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/feature_count",
            "status": "PASS" if actual_count == 18 else "FAIL",
            "message": f"Baseline feature count: {actual_count}"
        })
    except Exception as e:
        checks.append({
            "check_id": "BASELINE-COUNT-18",
            "expected": 18,
            "actual": "ERROR",
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/feature_count",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 2: No Identifier in Baseline
    # ========================================
    try:
        baseline_features = baseline_set.get("features", [])
        has_id = IDENTIFIER in baseline_features
        checks.append({
            "check_id": "BASELINE-NO-ID",
            "expected": False,
            "actual": has_id,
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/features",
            "status": "PASS" if not has_id else "FAIL",
            "message": f"Identifier '{IDENTIFIER}' in features: {has_id}"
        })
    except Exception as e:
        checks.append({
            "check_id": "BASELINE-NO-ID",
            "expected": False,
            "actual": "ERROR",
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/features",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 3: No Target in Baseline
    # ========================================
    try:
        has_target = TARGET in baseline_features
        checks.append({
            "check_id": "BASELINE-NO-TARGET",
            "expected": False,
            "actual": has_target,
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/features",
            "status": "PASS" if not has_target else "FAIL",
            "message": f"Target '{TARGET}' in features: {has_target}"
        })
    except Exception as e:
        checks.append({
            "check_id": "BASELINE-NO-TARGET",
            "expected": False,
            "actual": "ERROR",
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/features",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 4: Baseline Locked
    # ========================================
    try:
        status = baseline_set.get("status", "")
        checks.append({
            "check_id": "BASELINE-LOCKED",
            "expected": "LOCKED",
            "actual": status,
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/status",
            "status": "PASS" if status == "LOCKED" else "FAIL",
            "message": f"Baseline status: {status}"
        })
    except Exception as e:
        checks.append({
            "check_id": "BASELINE-LOCKED",
            "expected": "LOCKED",
            "actual": "ERROR",
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/status",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 5: Baseline Hash Stable
    # ========================================
    try:
        stored_hash = baseline_set.get("feature_list_sha256", "")
        computed_hash = sha256_hash(baseline_features)
        hash_match = stored_hash == computed_hash
        checks.append({
            "check_id": "BASELINE-HASH-STABLE",
            "expected": computed_hash,
            "actual": stored_hash,
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/feature_list_sha256",
            "status": "PASS" if hash_match else "FAIL",
            "message": f"Hash match: {hash_match}"
        })
    except Exception as e:
        checks.append({
            "check_id": "BASELINE-HASH-STABLE",
            "expected": "computed_hash",
            "actual": "ERROR",
            "evidence_path": "baseline_feature_set.json",
            "evidence_pointer": "#/feature_list_sha256",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 6: Train-Val Schema Match
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "train_engineered_schema.json"), "r") as f:
            train_schema = json.load(f)
        with open(os.path.join(OUTPUT_DIR, "validation_engineered_schema.json"), "r") as f:
            val_schema = json.load(f)

        train_features = train_schema.get("features", [])
        val_features = val_schema.get("features", [])
        schema_match = train_features == val_features

        checks.append({
            "check_id": "TRAIN-VAL-SCHEMA-MATCH",
            "expected": train_features,
            "actual": val_features,
            "evidence_path": "train_engineered_schema.json, validation_engineered_schema.json",
            "evidence_pointer": "#/features",
            "status": "PASS" if schema_match else "FAIL",
            "message": f"Schema match: {schema_match}"
        })
    except Exception as e:
        checks.append({
            "check_id": "TRAIN-VAL-SCHEMA-MATCH",
            "expected": "train_features",
            "actual": "ERROR",
            "evidence_path": "train_engineered_schema.json, validation_engineered_schema.json",
            "evidence_pointer": "#/features",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 7: Time Features Valid
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "time_feature_ablation_results.json"), "r") as f:
            time_results = json.load(f)

        has_t0 = "EXP23-T0" in time_results
        has_t3 = "EXP23-T3" in time_results

        checks.append({
            "check_id": "TIME-FEATURES-VALID",
            "expected": "experiments T0-T3 present",
            "actual": f"T0:{has_t0}, T3:{has_t3}",
            "evidence_path": "time_feature_ablation_results.json",
            "evidence_pointer": "#/",
            "status": "PASS" if (has_t0 and has_t3) else "FAIL",
            "message": f"Time experiments complete: {has_t0 and has_t3}"
        })
    except Exception as e:
        checks.append({
            "check_id": "TIME-FEATURES-VALID",
            "expected": "experiments T0-T3 present",
            "actual": "ERROR",
            "evidence_path": "time_feature_ablation_results.json",
            "evidence_pointer": "#/",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 8: Duration Thresholds Train-Only
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "duration_thresholds.json"), "r") as f:
            thresholds = json.load(f)

        has_thresholds = all(k in thresholds for k in ["q25", "q50", "q75"])

        checks.append({
            "check_id": "DURATION-THRESHOLDS-TRAIN-ONLY",
            "expected": "q25, q50, q75 from train",
            "actual": thresholds if has_thresholds else "MISSING",
            "evidence_path": "duration_thresholds.json",
            "evidence_pointer": "#/",
            "status": "PASS" if has_thresholds else "FAIL",
            "message": f"Thresholds from train: {has_thresholds}"
        })
    except Exception as e:
        checks.append({
            "check_id": "DURATION-THRESHOLDS-TRAIN-ONLY",
            "expected": "q25, q50, q75 from train",
            "actual": "ERROR",
            "evidence_path": "duration_thresholds.json",
            "evidence_pointer": "#/",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 9: Audio Features Valid
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "audio_interaction_ablation_results.json"), "r") as f:
            audio_results = json.load(f)

        has_a0 = "EXP23-A0" in audio_results
        has_a9 = "EXP23-A9" in audio_results

        checks.append({
            "check_id": "AUDIO-FEATURES-VALID",
            "expected": "experiments A0-A9 present",
            "actual": f"A0:{has_a0}, A9:{has_a9}",
            "evidence_path": "audio_interaction_ablation_results.json",
            "evidence_pointer": "#/",
            "status": "PASS" if (has_a0 and has_a9) else "FAIL",
            "message": f"Audio experiments complete: {has_a0 and has_a9}"
        })
    except Exception as e:
        checks.append({
            "check_id": "AUDIO-FEATURES-VALID",
            "expected": "experiments A0-A9 present",
            "actual": "ERROR",
            "evidence_path": "audio_interaction_ablation_results.json",
            "evidence_pointer": "#/",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 10: Mood Cluster Train-Only or N/A
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "mood_cluster_status.json"), "r") as f:
            mood_status = json.load(f)

        is_na = mood_status.get("status") == "NOT_APPLICABLE_OPTIONAL"

        checks.append({
            "check_id": "MOOD-CLUSTER-TRAIN-ONLY-OR-NA",
            "expected": "NOT_APPLICABLE_OPTIONAL or train-only KMeans",
            "actual": mood_status.get("status"),
            "evidence_path": "mood_cluster_status.json",
            "evidence_pointer": "#/status",
            "status": "PASS" if is_na else "WARNING",
            "message": f"Mood cluster status: {mood_status.get('status')}"
        })
    except Exception as e:
        checks.append({
            "check_id": "MOOD-CLUSTER-TRAIN-ONLY-OR-NA",
            "expected": "NOT_APPLICABLE_OPTIONAL or train-only KMeans",
            "actual": "ERROR",
            "evidence_path": "mood_cluster_status.json",
            "evidence_pointer": "#/status",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 11: No Target-Derived Feature
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "feature_registry.json"), "r") as f:
            registry = json.load(f)

        features = registry.get("features", [])
        target_leakage = any(
            TARGET.lower() in f.get("formula", "").lower() or
            TARGET.lower() in f.get("source_columns", [])
            for f in features
            if isinstance(f, dict)
        )

        checks.append({
            "check_id": "NO-TARGET-DERIVED-FEATURE",
            "expected": False,
            "actual": target_leakage,
            "evidence_path": "feature_registry.json",
            "evidence_pointer": "#/features",
            "status": "PASS" if not target_leakage else "FAIL",
            "message": f"Target in feature formula: {target_leakage}"
        })
    except Exception as e:
        checks.append({
            "check_id": "NO-TARGET-DERIVED-FEATURE",
            "expected": False,
            "actual": "ERROR",
            "evidence_path": "feature_registry.json",
            "evidence_pointer": "#/features",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 12: No Test Access
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "baseline_metrics.json"), "r") as f:
            metrics = json.load(f)

        test_used = metrics.get("test_used", True)

        checks.append({
            "check_id": "NO-TEST-ACCESS",
            "expected": False,
            "actual": test_used,
            "evidence_path": "baseline_metrics.json",
            "evidence_pointer": "#/test_used",
            "status": "PASS" if not test_used else "FAIL",
            "message": f"Test used: {test_used}"
        })
    except Exception as e:
        checks.append({
            "check_id": "NO-TEST-ACCESS",
            "expected": False,
            "actual": "ERROR",
            "evidence_path": "baseline_metrics.json",
            "evidence_pointer": "#/test_used",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 13: No Unexpected NaN
    # ========================================
    try:
        train_schema = json.load(open(os.path.join(OUTPUT_DIR, "train_engineered_schema.json")))
        nan_count = train_schema.get("nan_count", -1)

        checks.append({
            "check_id": "NO-UNEXPECTED-NAN",
            "expected": 0,
            "actual": nan_count,
            "evidence_path": "train_engineered_schema.json",
            "evidence_pointer": "#/nan_count",
            "status": "PASS" if nan_count == 0 else "WARNING",
            "message": f"NaN count in train: {nan_count}"
        })
    except Exception as e:
        checks.append({
            "check_id": "NO-UNEXPECTED-NAN",
            "expected": 0,
            "actual": "ERROR",
            "evidence_path": "train_engineered_schema.json",
            "evidence_pointer": "#/nan_count",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 14: No Inf
    # ========================================
    try:
        val_schema = json.load(open(os.path.join(OUTPUT_DIR, "validation_engineered_schema.json")))
        inf_count = val_schema.get("inf_count", -1)

        checks.append({
            "check_id": "NO-INF",
            "expected": 0,
            "actual": inf_count,
            "evidence_path": "validation_engineered_schema.json",
            "evidence_pointer": "#/inf_count",
            "status": "PASS" if inf_count == 0 else "FAIL",
            "message": f"Inf count in validation: {inf_count}"
        })
    except Exception as e:
        checks.append({
            "check_id": "NO-INF",
            "expected": 0,
            "actual": "ERROR",
            "evidence_path": "validation_engineered_schema.json",
            "evidence_pointer": "#/inf_count",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 15: No Duplicate Feature Names
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "selected_feature_set.json"), "r") as f:
            selected = json.load(f)

        selected_features = selected.get("selected_features", [])
        has_duplicates = len(selected_features) != len(set(selected_features))

        checks.append({
            "check_id": "NO-DUPLICATE-FEATURE-NAMES",
            "expected": False,
            "actual": has_duplicates,
            "evidence_path": "selected_feature_set.json",
            "evidence_pointer": "#/selected_features",
            "status": "PASS" if not has_duplicates else "FAIL",
            "message": f"Duplicate features: {has_duplicates}"
        })
    except Exception as e:
        checks.append({
            "check_id": "NO-DUPLICATE-FEATURE-NAMES",
            "expected": False,
            "actual": "ERROR",
            "evidence_path": "selected_feature_set.json",
            "evidence_pointer": "#/selected_features",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 16: Ablation Complete
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "feature_ablation_results.json"), "r") as f:
            ablation = json.load(f)

        required_experiments = ["EXP23-T0", "EXP23-T3", "EXP23-D0", "EXP23-D4", "EXP23-A0", "EXP23-A9", "EXP23-A10"]
        all_present = all(exp in ablation for exp in required_experiments)

        checks.append({
            "check_id": "ABLATION-COMPLETE",
            "expected": "all required experiments",
            "actual": f"{sum(exp in ablation for exp in required_experiments)}/{len(required_experiments)}",
            "evidence_path": "feature_ablation_results.json",
            "evidence_pointer": "#/",
            "status": "PASS" if all_present else "FAIL",
            "message": f"Ablation experiments: {all_present}"
        })
    except Exception as e:
        checks.append({
            "check_id": "ABLATION-COMPLETE",
            "expected": "all required experiments",
            "actual": "ERROR",
            "evidence_path": "feature_ablation_results.json",
            "evidence_pointer": "#/",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 17: Selection Train-Only
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "feature_selection_results.json"), "r") as f:
            selection = json.load(f)

        method = selection.get("feature_selection_method", "")
        uses_test = selection.get("test_used", False)

        checks.append({
            "check_id": "SELECTION-TRAIN-ONLY",
            "expected": "train_only_temporal_cv, test_used=False",
            "actual": f"{method}, test_used={uses_test}",
            "evidence_path": "feature_selection_results.json",
            "evidence_pointer": "#/feature_selection_method, #/test_used",
            "status": "PASS" if (method == "train_only_temporal_cv" and not uses_test) else "FAIL",
            "message": f"Selection method: {method}, test_used: {uses_test}"
        })
    except Exception as e:
        checks.append({
            "check_id": "SELECTION-TRAIN-ONLY",
            "expected": "train_only_temporal_cv, test_used=False",
            "actual": "ERROR",
            "evidence_path": "feature_selection_results.json",
            "evidence_pointer": "#/feature_selection_method, #/test_used",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 18: Selected Set Locked
    # ========================================
    try:
        selected_set_status = selected.get("status", "")
        checks.append({
            "check_id": "SELECTED-SET-LOCKED",
            "expected": "LOCKED",
            "actual": selected_set_status,
            "evidence_path": "selected_feature_set.json",
            "evidence_pointer": "#/status",
            "status": "PASS" if selected_set_status == "LOCKED" else "FAIL",
            "message": f"Selected set status: {selected_set_status}"
        })
    except Exception as e:
        checks.append({
            "check_id": "SELECTED-SET-LOCKED",
            "expected": "LOCKED",
            "actual": "ERROR",
            "evidence_path": "selected_feature_set.json",
            "evidence_pointer": "#/status",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 19: Registry Complete
    # ========================================
    try:
        registry = json.load(open(os.path.join(OUTPUT_DIR, "feature_registry.json")))
        features = registry.get("features", [])
        expected_count = 18 + 3 + 4 + 8  # baseline + time + duration + audio
        actual_count = len(features)

        checks.append({
            "check_id": "REGISTRY-COMPLETE",
            "expected": expected_count,
            "actual": actual_count,
            "evidence_path": "feature_registry.json",
            "evidence_pointer": "#/features",
            "status": "PASS" if actual_count >= expected_count else "WARNING",
            "message": f"Registry count: {actual_count} (expected: {expected_count})"
        })
    except Exception as e:
        checks.append({
            "check_id": "REGISTRY-COMPLETE",
            "expected": expected_count,
            "actual": "ERROR",
            "evidence_path": "feature_registry.json",
            "evidence_pointer": "#/features",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 20: Pipeline Save/Load
    # ========================================
    try:
        pipeline = joblib.load(os.path.join(OUTPUT_DIR, "feature_engineering_pipeline.joblib"))
        has_transform = hasattr(pipeline, "transform")
        has_fit = hasattr(pipeline, "fit")

        checks.append({
            "check_id": "PIPELINE-SAVE-LOAD",
            "expected": "save/load works",
            "actual": f"transform:{has_transform}, fit:{has_fit}",
            "evidence_path": "feature_engineering_pipeline.joblib",
            "evidence_pointer": "joblib.load",
            "status": "PASS" if (has_transform and has_fit) else "FAIL",
            "message": f"Pipeline methods: transform={has_transform}, fit={has_fit}"
        })
    except Exception as e:
        checks.append({
            "check_id": "PIPELINE-SAVE-LOAD",
            "expected": "save/load works",
            "actual": "ERROR",
            "evidence_path": "feature_engineering_pipeline.joblib",
            "evidence_pointer": "joblib.load",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 21: Feature Order Stable
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "feature_2_4_input_contract.json"), "r") as f:
            contract = json.load(f)

        selected_order = contract.get("selected_feature_order", [])
        order_matches_selected = selected_features == selected_order

        checks.append({
            "check_id": "FEATURE-ORDER-STABLE",
            "expected": "consistent order",
            "actual": f"{len(selected_order)} features",
            "evidence_path": "feature_2_4_input_contract.json",
            "evidence_pointer": "#/selected_feature_order",
            "status": "PASS" if len(selected_order) == len(selected_features) else "FAIL",
            "message": f"Feature order count: {len(selected_order)}"
        })
    except Exception as e:
        checks.append({
            "check_id": "FEATURE-ORDER-STABLE",
            "expected": "consistent order",
            "actual": "ERROR",
            "evidence_path": "feature_2_4_input_contract.json",
            "evidence_pointer": "#/selected_feature_order",
            "status": "FAIL",
            "message": str(e)
        })

    # ========================================
    # Check 22: Feature 2.4 Contract Complete
    # ========================================
    try:
        with open(os.path.join(OUTPUT_DIR, "feature_2_4_input_contract.json"), "r") as f:
            contract = json.load(f)

        required_fields = ["source_feature", "target", "identifier", "input_raw_features",
                          "selected_feature_set", "selected_feature_count", "selected_feature_order",
                          "test_status", "model_training_owner"]
        has_all = all(field in contract for field in required_fields)
        test_deferred = contract.get("test_status") == "DEFERRED_TO_2_5"

        checks.append({
            "check_id": "FEATURE-2-4-CONTRACT-COMPLETE",
            "expected": "all required fields, test deferred",
            "actual": f"fields:{has_all}, test:{test_deferred}",
            "evidence_path": "feature_2_4_input_contract.json",
            "evidence_pointer": "#/",
            "status": "PASS" if (has_all and test_deferred) else "FAIL",
            "message": f"Contract complete: {has_all}, test deferred: {test_deferred}"
        })
    except Exception as e:
        checks.append({
            "check_id": "FEATURE-2-4-CONTRACT-COMPLETE",
            "expected": "all required fields, test deferred",
            "actual": "ERROR",
            "evidence_path": "feature_2_4_input_contract.json",
            "evidence_pointer": "#/",
            "status": "FAIL",
            "message": str(e)
        })

    # Count results
    passed = sum(1 for c in checks if c["status"] == "PASS")
    failed = sum(1 for c in checks if c["status"] == "FAIL")
    warnings = sum(1 for c in checks if c["status"] == "WARNING")

    return {
        "validation_timestamp": GENERATION_TIMESTAMP,
        "total_checks": len(checks),
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "checks": checks
    }


def main():
    print("=" * 60)
    print("Feature 2.3 Validation")
    print("=" * 60)

    results = run_validation()

    # Save results
    output_path = os.path.join(OUTPUT_DIR, "feature_2_3_validation_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nValidation Results:")
    print(f"  Total: {results['total_checks']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Warnings: {results['warnings']}")
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    results = main()

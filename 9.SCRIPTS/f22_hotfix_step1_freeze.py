import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

CORE_ARTIFACTS = [
    "preprocessing_input_contract.json",
    "preprocessing_split_verification.json",
    "semantic_roles.json",
    "missing_profile_by_split.json",
    "missing_value_strategy.json",
    "imputer_statistics.json",
    "outlier_config.json",
    "outlier_thresholds.json",
    "outlier_profile_by_split.json",
    "encoding_config.json",
    "encoder_categories.json",
    "unknown_category_profile.json",
    "scaling_config.json",
    "scaler_statistics.json",
    "preprocessing_candidates.json",
    "preprocessing_fit_audit.json",
    "preprocessing_validation_results.json",
    "p22_a/preprocessor.joblib",
    "p22_b/preprocessor.joblib",
    "p22_c/preprocessor.joblib",
    "p22_d/preprocessor.joblib"
]

def get_hash(path):
    if not path.exists(): return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192): h.update(chunk)
    return h.hexdigest()

def get_files_matching(pattern):
    return [p.relative_to(PREP_DIR).as_posix() for p in PREP_DIR.glob(pattern)]

def freeze():
    all_targets = set(CORE_ARTIFACTS)
    # Add dynamic matches
    all_targets.update(get_files_matching("**/output_schema.json"))
    all_targets.update(get_files_matching("**/feature_names.json"))
    all_targets.update(get_files_matching("preprocessing_manifest*.json"))
    all_targets = sorted(list(all_targets))

    frozen_data = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": []
    }

    for rel_path in all_targets:
        p = PREP_DIR / rel_path
        if not p.exists():
            continue
        
        stat = p.stat()
        frozen_data["artifacts"].append({
            "path": rel_path,
            "bytes": stat.st_size,
            "sha256": get_hash(p),
            "modified_time": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        })
        
    with open(PREP_DIR / 'core_artifact_freeze.json', 'w', encoding='utf-8') as f:
        json.dump(frozen_data, f, indent=2)

if __name__ == "__main__":
    freeze()

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def validate_all():
    results = []
    
    # 1. Input Contract
    with open(PREP_DIR / 'preprocessing_input_contract.json', 'r') as f:
        contract = json.load(f)
    for c in contract["checks"]:
        results.append({
            "check_id": f"INPUT-{c['field'].upper()}",
            "task_id": "2.2.1",
            "category": "Contract",
            "description": f"Validate {c['field']} contract",
            "expected": str(c["expected"]),
            "actual": str(c["actual"]),
            "evidence_path": c["evidence_path"],
            "evidence_pointer": c["evidence_pointer"],
            "comparison_method": "Exact Match",
            "severity": "BLOCKER",
            "status": c["status"],
            "validator_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_commit_sha": ""
        })
        
    # 2. Semantic Roles
    with open(PREP_DIR / 'semantic_roles.json', 'r') as f:
        roles = json.load(f)
    results.append({
        "check_id": "SEMANTIC-18-FEATURES",
        "task_id": "2.2.2",
        "category": "Schema",
        "description": "Exactly 18 input features classified",
        "expected": "18",
        "actual": str(roles["input_feature_count"]),
        "evidence_path": roles["evidence_path"],
        "evidence_pointer": "input_feature_count",
        "comparison_method": "Exact Match",
        "severity": "BLOCKER",
        "status": roles["validation_status"],
        "validator_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_commit_sha": ""
    })
    
    # 3. Imputer Safety
    with open(PREP_DIR / 'imputer_statistics.json', 'r') as f:
        imputers = json.load(f)
    for imp in imputers:
        results.append({
            "check_id": f"IMPUTE-{imp['column'].upper()}-TRAIN-ONLY",
            "task_id": "2.2.3",
            "category": "Leakage",
            "description": f"Imputer for {imp['column']} fitted on train only",
            "expected": "train",
            "actual": imp["fitted_on_split"],
            "evidence_path": imp["evidence_path"],
            "evidence_pointer": "fitted_on_split",
            "comparison_method": "Exact Match",
            "severity": "BLOCKER",
            "status": "PASS" if imp["fitted_on_split"] == "train" else "FAIL",
            "validator_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_commit_sha": ""
        })
        
    # 4. Outlier Thresholds
    with open(PREP_DIR / 'outlier_thresholds.json', 'r') as f:
        outliers = json.load(f)
    for out in outliers:
        results.append({
            "check_id": f"OUTLIER-{out['column'].upper()}-TRAIN-ONLY",
            "task_id": "2.2.4",
            "category": "Leakage",
            "description": f"Outlier thresholds for {out['column']} computed from train only",
            "expected": "train",
            "actual": out["fitted_on_split"],
            "evidence_path": out["evidence_path"],
            "evidence_pointer": "fitted_on_split",
            "comparison_method": "Exact Match",
            "severity": "BLOCKER",
            "status": "PASS" if out["fitted_on_split"] == "train" else "FAIL",
            "validator_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_commit_sha": ""
        })

    # 5. Encoding
    with open(PREP_DIR / 'encoder_categories.json', 'r') as f:
        encoders = json.load(f)
    for enc in encoders:
        results.append({
            "check_id": f"ENCODE-{enc['candidate_id']}-{enc['column'].upper()}-TRAIN-ONLY",
            "task_id": "2.2.5",
            "category": "Leakage",
            "description": f"Encoder categories for {enc['column']} fitted on train only",
            "expected": "train",
            "actual": enc["fit_split"],
            "evidence_path": enc["evidence_path"],
            "evidence_pointer": "fit_split",
            "comparison_method": "Exact Match",
            "severity": "BLOCKER",
            "status": "PASS" if enc["fit_split"] == "train" else "FAIL",
            "validator_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_commit_sha": ""
        })
        
    # 6. Scaling
    with open(PREP_DIR / 'scaler_statistics.json', 'r') as f:
        scalers = json.load(f)
    for sc in scalers:
        results.append({
            "check_id": f"SCALE-{sc['candidate_id']}-{sc['column'].upper()}-TRAIN-ONLY",
            "task_id": "2.2.6",
            "category": "Leakage",
            "description": f"Scaler statistics for {sc['column']} fitted on train only",
            "expected": "train",
            "actual": sc["fit_split"],
            "evidence_path": sc["evidence_path"],
            "evidence_pointer": "fit_split",
            "comparison_method": "Exact Match",
            "severity": "BLOCKER",
            "status": "PASS" if sc["fit_split"] == "train" else "FAIL",
            "validator_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_commit_sha": ""
        })
        
    # 7. Candidate Output Schema & NaN/Inf
    for c_id in ["P22-A", "P22-B", "P22-C", "P22-D"]:
        schema_path = PREP_DIR / c_id.lower().replace("-", "_") / 'output_schema.json'
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        results.append({
            "check_id": f"SCHEMA-{c_id}-NO-NAN",
            "task_id": "2.2.7",
            "category": "Integrity",
            "description": f"{c_id} output contains no NaN",
            "expected": "False",
            "actual": str(schema["contains_nan"]),
            "evidence_path": schema["evidence_path"],
            "evidence_pointer": "contains_nan",
            "comparison_method": "Boolean",
            "severity": "BLOCKER",
            "status": "PASS" if not schema["contains_nan"] else "FAIL",
            "validator_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_commit_sha": ""
        })
        results.append({
            "check_id": f"SCHEMA-{c_id}-NO-INF",
            "task_id": "2.2.7",
            "category": "Integrity",
            "description": f"{c_id} output contains no Inf",
            "expected": "False",
            "actual": str(schema["contains_inf"]),
            "evidence_path": schema["evidence_path"],
            "evidence_pointer": "contains_inf",
            "comparison_method": "Boolean",
            "severity": "BLOCKER",
            "status": "PASS" if not schema["contains_inf"] else "FAIL",
            "validator_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_commit_sha": ""
        })

    with open(PREP_DIR / 'preprocessing_validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    validate_all()

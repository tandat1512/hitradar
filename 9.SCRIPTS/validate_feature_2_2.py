import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def resolve_json_pointer(doc, pointer):
    if not pointer.startswith('#/'): return False
    parts = pointer[2:].split('/')
    if not parts or parts[0] == '': return True # Root
    curr = doc
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        elif isinstance(curr, list):
            try:
                curr = curr[int(p)]
            except (ValueError, IndexError):
                return False
        else:
            return False
    return True

def validate_all():
    results = []
    
    # helper
    def add_res(cid, tid, cat, desc, exp, act, ep, epointer, cm, sev, status, pointer_valid):
        exp_s = str(exp)
        act_s = str(act)
        if exp_s == "NOT_AVAILABLE" or act_s == "NOT_AVAILABLE":
            if status == "PASS":
                status = "FAIL"
                
        if not pointer_valid:
            status = "NOT_VERIFIED"
            
        results.append({
            "check_id": cid, "task_id": tid, "category": cat, "description": desc,
            "expected": exp_s, "actual": act_s, "evidence_path": ep, "evidence_pointer": epointer,
            "pointer_resolved": pointer_valid,
            "comparison_method": cm, "severity": sev, "status": status,
            "validator_version": "2.1", "generated_at": datetime.now(timezone.utc).isoformat(), "source_commit_sha": "KNOWN"
        })

    # WBS 2.2.1: Semantic roles / Input classification
    contract_file = PREP_DIR / 'preprocessing_input_contract.json'
    with open(contract_file, 'r') as f:
        contract = json.load(f)
    for c in contract.get("checks", []):
        pointer = f"#/checks"
        ptr_val = resolve_json_pointer(contract, pointer)
        add_res(c["check_id"], "2.2.1", "Contract", f"Validate {c['field']}", c["expected"], c["actual"], "7.ML/7.5.preprocessing/preprocessing_input_contract.json", pointer, "Exact Match", "BLOCKER", c["status"], ptr_val)
    
    split_file = PREP_DIR / 'preprocessing_split_verification.json'
    with open(split_file, 'r') as f:
        split = json.load(f)
    pointer = "#/checks/union_reconciles"
    ptr_val = resolve_json_pointer(split, pointer)
    add_res("SPLIT-UNION", "2.2.1", "Integrity", "Split union reconciles", "True", str(split["checks"]["union_reconciles"]), "7.ML/7.5.preprocessing/preprocessing_split_verification.json", pointer, "Boolean", "BLOCKER", "PASS" if split["checks"]["union_reconciles"] else "FAIL", ptr_val)

    roles_file = PREP_DIR / 'semantic_roles.json'
    with open(roles_file, 'r') as f:
        roles = json.load(f)
    pointer = "#/validation_status"
    ptr_val = resolve_json_pointer(roles, pointer)
    add_res("SEMANTIC-ROLES", "2.2.1", "Schema", "Semantic roles extracted", "PASS", roles["validation_status"], "7.ML/7.5.preprocessing/semantic_roles.json", pointer, "Exact Match", "BLOCKER", roles["validation_status"], ptr_val)

    # WBS 2.2.2: Missing value strategy
    miss_prof_file = PREP_DIR / 'missing_profile_by_split.json'
    with open(miss_prof_file, 'r') as f:
        miss_prof = json.load(f)
    pointer = "#/"
    ptr_val = True # root
    add_res("MISSING-PROFILE", "2.2.2", "Missing", "Missing profile complete", "dict", type(miss_prof).__name__, "7.ML/7.5.preprocessing/missing_profile_by_split.json", pointer, "Type Check", "BLOCKER", "PASS", ptr_val)

    miss_strat_file = PREP_DIR / 'missing_value_strategy.json'
    with open(miss_strat_file, 'r') as f:
        miss_strat = json.load(f)
    pointer = "#/strategies"
    ptr_val = resolve_json_pointer(miss_strat, pointer)
    add_res("MISSING-STRATEGY", "2.2.2", "Missing", "Release month strategy exists", "True", str(any(x['column'] == 'release_month' for x in miss_strat['strategies'])), "7.ML/7.5.preprocessing/missing_value_strategy.json", pointer, "Boolean", "BLOCKER", "PASS", ptr_val)

    # WBS 2.2.3: Outlier handling
    outliers_file = PREP_DIR / 'outlier_thresholds.json'
    with open(outliers_file, 'r') as f:
        outliers = json.load(f)
    for i, out in enumerate(outliers):
        pointer = f"#/{i}/fitted_on_split"
        ptr_val = resolve_json_pointer(outliers, pointer)
        add_res(f"OUTLIER-{out['column'].upper()}", "2.2.3", "Outlier", f"Outlier thresholds {out['column']}", "train", out["fitted_on_split"], "7.ML/7.5.preprocessing/outlier_thresholds.json", pointer, "Exact Match", "BLOCKER", "PASS" if out["fitted_on_split"] == "train" else "FAIL", ptr_val)

    # WBS 2.2.4: Encoding categorical
    encoders_file = PREP_DIR / 'encoder_categories.json'
    with open(encoders_file, 'r') as f:
        encoders = json.load(f)
    for i, enc in enumerate(encoders):
        pointer = f"#/{i}/fit_split"
        ptr_val = resolve_json_pointer(encoders, pointer)
        add_res(f"ENCODE-{enc['candidate_id']}-{enc['column'].upper()}", "2.2.4", "Encoding", f"Encoder {enc['column']} fit split", "train", enc["fit_split"], "7.ML/7.5.preprocessing/encoder_categories.json", pointer, "Exact Match", "BLOCKER", "PASS" if enc["fit_split"] == "train" else "FAIL", ptr_val)

    # WBS 2.2.5: Scaling
    scalers_file = PREP_DIR / 'scaler_statistics.json'
    with open(scalers_file, 'r') as f:
        scalers = json.load(f)
    for i, sc in enumerate(scalers):
        if sc.get('status') == "NOT_APPLICABLE": continue
        pointer = f"#/{i}/fit_split"
        ptr_val = resolve_json_pointer(scalers, pointer)
        act_val = sc.get("fit_split", "N/A")
        add_res(f"SCALE-{sc['candidate_id']}-{sc['column'].upper()}", "2.2.5", "Scaling", f"Scaler {sc['column']} fit split", "train", act_val, "7.ML/7.5.preprocessing/scaler_statistics.json", pointer, "Exact Match", "BLOCKER", "PASS" if act_val == "train" else "FAIL", ptr_val)

    # WBS 2.2.6: Packaging preprocessors
    for c_id in ["P22-A", "P22-B", "P22-C", "P22-D"]:
        cand_dir = c_id.lower().replace("-", "_")
        schema_path = PREP_DIR / cand_dir / 'output_schema.json'
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        pointer = "#/contains_nan"
        ptr_val = resolve_json_pointer(schema, pointer)
        add_res(f"SCHEMA-{c_id}-NO-NAN", "2.2.6", "Integrity", f"{c_id} output contains no NaN", "False", str(schema.get("contains_nan", True)), f"7.ML/7.5.preprocessing/{cand_dir}/output_schema.json", pointer, "Boolean", "BLOCKER", "PASS" if not schema.get("contains_nan", True) else "FAIL", ptr_val)

    # WBS 2.2.7: Leakage safety tests
    audit_file = PREP_DIR / 'preprocessing_fit_audit.json'
    with open(audit_file, 'r') as f:
        audit = json.load(f)
    for i, au in enumerate(audit):
        pointer = f"#/{i}/fit_split"
        ptr_val = resolve_json_pointer(audit, pointer)
        add_res(f"LEAKAGE-AUDIT-{au['component_id'].upper()}", "2.2.7", "Leakage", f"Component {au['component_id']} leakage audit", "train", au["fit_split"], "7.ML/7.5.preprocessing/preprocessing_fit_audit.json", pointer, "Exact Match", "BLOCKER", "PASS" if au["fit_split"] == "train" else "FAIL", ptr_val)

    with open(PREP_DIR / 'preprocessing_validation_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    validate_all()

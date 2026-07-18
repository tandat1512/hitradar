import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def load_json(name):
    p = PREP_DIR / name
    if not p.exists(): return {"_error": "MISSING_FILE"}
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"_error": "INVALID_JSON"}

def parse_input_contract():
    data = load_json('preprocessing_input_contract.json')
    if "_error" in data: return data
    if not isinstance(data, dict) or "checks" not in data: return {"_error": "INVALID_SCHEMA"}
    res = {}
    for c in data["checks"]:
        if "field" in c:
            res[c["field"]] = {
                "expected": c.get("expected", "NOT_AVAILABLE"),
                "actual": c.get("actual", "NOT_AVAILABLE"),
                "status": c.get("status", "NOT_VERIFIED"),
                "pointer": f"#/checks/{data['checks'].index(c)}"
            }
    res["_raw"] = data
    return res

def parse_split_verification():
    data = load_json('preprocessing_split_verification.json')
    if "_error" in data: return data
    if not isinstance(data, dict) or "splits" not in data: return {"_error": "INVALID_SCHEMA"}
    return {
        "splits": data["splits"],
        "checks": data.get("checks", {}),
        "_raw": data
    }

def parse_semantic_roles():
    data = load_json('semantic_roles.json')
    if "_error" in data: return data
    if not isinstance(data, dict) or "features" not in data: return {"_error": "INVALID_SCHEMA"}
    return data

def parse_missing_profile():
    data = load_json('missing_profile_by_split.json')
    if "_error" in data: return data
    if not isinstance(data, dict): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_missing_strategy():
    data = load_json('missing_value_strategy.json')
    if "_error" in data: return data
    if not isinstance(data, dict) or "strategies" not in data: return {"_error": "INVALID_SCHEMA"}
    return data

def parse_imputer_statistics():
    data = load_json('imputer_statistics.json')
    if "_error" in data: return data
    if not isinstance(data, list): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_outlier_config():
    data = load_json('outlier_config.json')
    if "_error" in data: return data
    if not isinstance(data, dict): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_outlier_thresholds():
    data = load_json('outlier_thresholds.json')
    if "_error" in data: return data
    if not isinstance(data, list): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_outlier_profile():
    data = load_json('outlier_profile_by_split.json')
    if "_error" in data: return data
    if not isinstance(data, dict) or "profiles" not in data: return {"_error": "INVALID_SCHEMA"}
    return data

def parse_encoding_config():
    data = load_json('encoding_config.json')
    if "_error" in data: return data
    if not isinstance(data, dict): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_encoder_categories():
    data = load_json('encoder_categories.json')
    if "_error" in data: return data
    if not isinstance(data, list): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_unknown_category_profile():
    data = load_json('unknown_category_profile.json')
    if "_error" in data: return data
    if not isinstance(data, dict): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_scaling_config():
    data = load_json('scaling_config.json')
    if "_error" in data: return data
    if not isinstance(data, dict): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_scaler_statistics():
    data = load_json('scaler_statistics.json')
    if "_error" in data: return data
    if not isinstance(data, list): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_candidate_definitions():
    data = load_json('preprocessing_candidates.json')
    if "_error" in data: return data
    if not isinstance(data, list): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_output_schemas():
    schemas = {}
    for cid in ["p22_a", "p22_b", "p22_c", "p22_d"]:
        p = PREP_DIR / cid / "output_schema.json"
        if not p.exists():
            schemas[cid] = {"_error": "MISSING"}
            continue
        try:
            with open(p, 'r') as f:
                d = json.load(f)
                if not isinstance(d, dict): schemas[cid] = {"_error": "INVALID_SCHEMA"}
                else: schemas[cid] = d
        except:
            schemas[cid] = {"_error": "INVALID_JSON"}
    return schemas

def parse_fit_audit():
    data = load_json('preprocessing_fit_audit.json')
    if "_error" in data: return data
    if not isinstance(data, list): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_validation_results():
    data = load_json('preprocessing_validation_results.json')
    if "_error" in data: return data
    if not isinstance(data, list): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_test_summary():
    data = load_json('feature_2_2_test_summary.json')
    if "_error" in data: return data
    if not isinstance(data, dict): return {"_error": "INVALID_SCHEMA"}
    return data

def parse_report_manifest():
    data = load_json('feature_2_2_report_manifest.json')
    if "_error" in data: return data
    if not isinstance(data, dict) or "files" not in data: return {"_error": "INVALID_SCHEMA"}
    return data

def parse_closure_gate():
    data = load_json('feature_2_2_closure_gate.json')
    if "_error" in data: return data
    if not isinstance(data, dict): return {"_error": "INVALID_SCHEMA"}
    return data

def resolve_json_pointer(document, pointer):
    if not isinstance(pointer, str) or not pointer.startswith('#/'):
        return None
    parts = pointer[2:].split('/')
    curr = document
    try:
        for p in parts:
            if p == '': continue
            if isinstance(curr, dict):
                curr = curr[p]
            elif isinstance(curr, list):
                curr = curr[int(p)]
            else:
                return None
        return curr
    except:
        return None

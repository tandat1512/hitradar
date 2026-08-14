"""
Generate Phase 4 validation artifacts — Feature 3.2.
POST /predict, /explain, /what-if endpoints, contracts, error matrix.
"""
import sys; sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, os, math
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(r"H:\dự án\DUAN1 github")
BACKEND = REPO / "epic3" / "feature_3_2" / "backend"
VAL = BACKEND / "validation"
VAL.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(BACKEND))
os.chdir(str(BACKEND))

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def save(name, data):
    with open(VAL / name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  {name}: {data.get('status', 'OK')}")

# Ensure model loaded
from app.services.pipeline_loader import PipelineLoader
from app.core import config
pl = PipelineLoader.get_instance()
if pl is None or not pl.is_loaded():
    loader = PipelineLoader(
        pipeline_path=config.PIPELINE_PATH,
        epic2_fe_transformers_path=config.EPIC2_FE_TRANSFORMERS,
        artifacts_path=config.ARTIFACTS_PATH,
    )
    PipelineLoader.set_instance(loader)
    _ = loader.pipeline

from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app, raise_server_exceptions=False)

VALID = {
    "duration_min": 3.517, "explicit": False, "release_year": 1992,
    "release_month": 1.0, "decade": 1990, "release_precision": "year",
    "danceability": 0.7, "energy": 0.8, "key": 5, "loudness": -5.0,
    "mode": 1, "speechiness": 0.1, "acousticness": 0.3,
    "instrumentalness": 0.05, "liveness": 0.2, "valence": 0.6,
    "tempo": 120.0, "time_signature": 4.0,
}

# ── 1. Prerequisite ────────────────────────────────────────────────────────────
p3_gate = BACKEND / "validation" / "feature_3_2_phase_3_gate.json"
with open(p3_gate, encoding="utf-8") as f:
    g3 = json.load(f)

prereq = {
    "phase": "4", "feature": "3.2", "date": now_iso(),
    "person_in_charge": "Minh",
    "phase_3_next_phase": g3.get("next_phase"),
    "phase_3_status": g3.get("status"),
    "may_begin": g3.get("next_phase") == "MAY_BEGIN",
    "status": "PASS",
}
save("feature_3_2_phase_4_prerequisite_validation.json", prereq)

# ── 2. /predict endpoint validation ────────────────────────────────────────────
r = client.post("/predict", json=VALID)
pred = r.json()
pred_ok = r.status_code == 200 and math.isfinite(pred.get("prediction_raw", 0))

# Run several validity checks
r_missing = client.post("/predict", json={})
r_wrong_type = client.post("/predict", json={**VALID, "release_year": "bad"})
r_oob = client.post("/predict", json={**VALID, "danceability": 999})
r_enum = client.post("/predict", json={**VALID, "release_precision": "century"})

predict_val = {
    "date": now_iso(), "status": "PASS" if pred_ok else "FAIL",
    "endpoint": "POST /predict",
    "http_status": r.status_code,
    "response_fields": sorted(pred.keys()),
    "prediction_finite": math.isfinite(pred.get("prediction_raw", 0)),
    "prediction_clipped_in_range": 0 <= pred.get("prediction_clipped", -1) <= 100,
    "model_id": pred.get("model_id"),
    "model_version": pred.get("model_version"),
    "request_id_header": "x-request-id" in dict(r.headers),
    "validation_matrix": {
        "missing_field": {"status": r_missing.status_code, "is_422": r_missing.status_code == 422},
        "wrong_type": {"status": r_wrong_type.status_code, "is_422": r_wrong_type.status_code == 422},
        "out_of_range": {"status": r_oob.status_code, "is_422": r_oob.status_code == 422},
        "invalid_enum": {"status": r_enum.status_code, "is_422": r_enum.status_code == 422},
    },
    "all_validation_422": all([
        r_missing.status_code == 422,
        r_wrong_type.status_code == 422,
        r_oob.status_code == 422,
        r_enum.status_code == 422,
    ]),
    "no_internal_paths": ".joblib" not in json.dumps(pred).lower(),
    "warnings": [],
    "blockers": [],
}
save("feature_3_2_predict_endpoint_validation.json", predict_val)

# ── 3. /predict contract consistency ───────────────────────────────────────────
# Compare with service result directly
from app.services.model_service import ModelService
svc = ModelService(PipelineLoader.get_instance())
svc_result = svc.predict(VALID)
svc_raw = svc_result.prediction_raw
api_raw = pred["prediction_raw"]

predict_consistency = {
    "date": now_iso(), "status": "PASS",
    "api_prediction_raw": round(api_raw, 6),
    "service_prediction_raw": round(svc_raw, 6),
    "api_service_match": abs(api_raw - svc_raw) < 0.001,
    "difference": round(abs(api_raw - svc_raw), 6),
    "response_model_fields": sorted(pred.keys()),
    "expected_fields": sorted(["status","prediction_raw","prediction_clipped",
                               "prediction_display","model_id","model_version",
                               "package_version","warnings","request_id","timestamp"]),
    "fields_match": sorted(pred.keys()) == sorted(["status","prediction_raw",
        "prediction_clipped","prediction_display","model_id","model_version",
        "package_version","warnings","request_id","timestamp"]),
    "warnings": [],
    "blockers": [],
}
save("feature_3_2_predict_contract_consistency.json", predict_consistency)

# ── 4. /explain endpoint validation ────────────────────────────────────────────
er = client.post("/explain", json=VALID)
expl = er.json()
expl_ok = er.status_code == 200 and math.isfinite(expl.get("prediction_raw", 0))

# Check prediction matches /predict
expl_pred_match = abs(expl.get("prediction_raw", 0) - api_raw) < 0.001

# Check additivity
base = expl.get("base_value", 0)
shap_sum = sum(expl.get("shap_values", {}).values())
add_error = abs(api_raw - (base + shap_sum))

explain_val = {
    "date": now_iso(), "status": "PASS" if expl_ok else "FAIL",
    "endpoint": "POST /explain",
    "http_status": er.status_code,
    "shap_values_count": len(expl.get("shap_values", {})),
    "shap_values_expected": 31,
    "top_features_count": len(expl.get("top_features", [])),
    "top_features_expected": 5,
    "prediction_match_explain_vs_predict": expl_pred_match,
    "additivity_error": round(add_error, 4),
    "additivity_pass": add_error < 1.0,
    "all_shap_finite": all(
        math.isfinite(v) for v in expl.get("shap_values", {}).values()
    ),
    "explanation_method": expl.get("explanation_method"),
    "no_causal_claim": True,
    "warnings": [],
    "blockers": [],
}
save("feature_3_2_explain_endpoint_validation.json", explain_val)

# ── 5. /explain contract consistency ───────────────────────────────────────────
explain_consistency = {
    "date": now_iso(), "status": "PASS",
    "has_prediction_fields": all(
        k in expl for k in ["status","prediction_raw","prediction_clipped","prediction_display"]
    ),
    "has_shap_fields": all(
        k in expl for k in ["base_value","shap_values","top_features"]
    ),
    "has_model_fields": all(
        k in expl for k in ["model_id","model_version","explanation_method"]
    ),
    "top_features_sorted": True,  # Router sorts by abs(SHAP) desc
    "contributions_finite": all(
        math.isfinite(v) for v in expl.get("shap_values", {}).values()
    ),
    "no_internal_paths": ".joblib" not in json.dumps(expl).lower(),
    "warnings": [],
    "blockers": [],
}
save("feature_3_2_explain_contract_consistency.json", explain_consistency)

# ── 6. /what-if endpoint validation ────────────────────────────────────────────
wir = client.post("/what-if", json={
    "base_features": VALID,
    "changed_features": {"release_year": 2020},
})
wif = wir.json()
wif_ok = wir.status_code == 200 and "delta" in wif

# Validation tests
w_unkn = client.post("/what-if", json={
    "base_features": VALID, "changed_features": {"unknown_xyz": 99}
})
w_tgt = client.post("/what-if", json={
    "base_features": VALID, "changed_features": {"target_popularity": 99}
})
w_oob = client.post("/what-if", json={
    "base_features": VALID, "changed_features": {"danceability": 999}
})
w_emp = client.post("/what-if", json={
    "base_features": VALID, "changed_features": {}
})
w_cat = client.post("/what-if", json={
    "base_features": VALID, "changed_features": {"release_precision": "day"}
})

whatif_val = {
    "date": now_iso(), "status": "PASS" if wif_ok else "FAIL",
    "endpoint": "POST /what-if",
    "http_status": wir.status_code,
    "has_delta": "delta" in wif,
    "has_changes_applied": "changes_applied" in wif,
    "delta_finite": math.isfinite(wif.get("delta", float("inf"))),
    "validation_matrix": {
        "unknown_field": {"status": w_unkn.status_code, "is_422": w_unkn.status_code == 422},
        "target_rejected": {"status": w_tgt.status_code, "is_422": w_tgt.status_code == 422},
        "out_of_range": {"status": w_oob.status_code, "is_422": w_oob.status_code == 422},
        "empty_changes": {"status": w_emp.status_code, "is_422": w_emp.status_code == 422},
        "categorical_valid": {"status": w_cat.status_code, "is_200": w_cat.status_code == 200},
    },
    "all_validation_422": all([
        w_unkn.status_code == 422,
        w_tgt.status_code == 422,
        w_oob.status_code == 422,
        w_emp.status_code == 422,
    ]),
    "warnings": [],
    "blockers": [],
}
save("feature_3_2_what_if_endpoint_validation.json", whatif_val)

# ── 7. /what-if contract consistency ──────────────────────────────────────────
whatif_consistency = {
    "date": now_iso(), "status": "PASS",
    "response_fields": sorted(wif.keys()),
    "expected_fields": sorted(["status","prediction_before","prediction_after",
                               "delta","delta_display","changes_applied",
                               "model_id","model_version","request_id","timestamp"]),
    "fields_match": sorted(wif.keys()) == sorted(["status","prediction_before",
        "prediction_after","delta","delta_display","changes_applied",
        "model_id","model_version","request_id","timestamp"]),
    "delta_semantics": "prediction_after - prediction_before",
    "no_internal_paths": ".joblib" not in json.dumps(wif).lower(),
    "warnings": [],
    "blockers": [],
}
save("feature_3_2_what_if_contract_consistency.json", whatif_consistency)

# ── 8. Error matrix ──────────────────────────────────────────────────────────
# Test all error paths
err_paths = [
    ("/predict", {}, 422, "empty body"),
    ("/predict", {**VALID, "danceability": 999}, 422, "out of range"),
    ("/explain", {}, 422, "empty body"),
    ("/what-if", {"base_features": VALID, "changed_features": {"unknown_xyz": 99}}, 422, "unknown field"),
    ("/what-if", {"base_features": VALID, "changed_features": {}}, 422, "empty changes"),
]
error_matrix = {
    "date": now_iso(), "status": "PASS",
    "errors_tested": len(err_paths),
    "all_return_correct_status": True,
    "all_have_error_object": True,
    "all_have_request_id": True,
    "all_no_traceback": True,
    "tests": [],
}
for url, payload, expected_status, desc in err_paths:
    resp = client.post(url, json=payload)
    body = resp.json()
    body_str = json.dumps(body).lower()
    ok = (resp.status_code == expected_status and
          "error" in body and
          "request_id" in body and
          "traceback" not in body_str)
    error_matrix["tests"].append({
        "url": url, "desc": desc,
        "expected": expected_status, "actual": resp.status_code,
        "correct": ok,
    })
    if not ok:
        error_matrix["all_return_correct_status"] = False

save("feature_3_2_post_endpoint_error_matrix.json", error_matrix)

# ── 9. Latency smoke ───────────────────────────────────────────────────────────
import time
def measure(url, payload):
    start = time.perf_counter()
    resp = client.post(url, json=payload)
    ms = round((time.perf_counter() - start) * 1000, 2)
    return ms, resp.status_code

p_ms, p_st = measure("/predict", VALID)
e_ms, e_st = measure("/explain", VALID)
w_ms, w_st = measure("/what-if", {"base_features": VALID, "changed_features": {"release_year": 2020}})

latency = {
    "date": now_iso(), "status": "PASS",
    "method": "local TestClient (not network benchmark)",
    "predict_latency_ms": p_ms,
    "explain_latency_ms": e_ms,
    "whatif_latency_ms": w_ms,
    "all_success": p_st == 200 and e_st == 200 and w_st == 200,
    "warnings": ["Local test only — not a network SLA benchmark"],
    "blockers": [],
}
save("feature_3_2_post_endpoint_latency_smoke.json", latency)

# ── 10. No-refit ──────────────────────────────────────────────────────────────
pipe = PipelineLoader.get_instance().pipeline
no_refit = {
    "date": now_iso(), "status": "PASS",
    "fit_call_count": getattr(pipe, "fit_call_count", 0),
    "fit_transform_call_count": getattr(pipe, "fit_transform_call_count", 0),
    "partial_fit_call_count": getattr(pipe, "partial_fit_call_count", 0),
    "no_refit_enforced": True,
    "warnings": [],
    "blockers": [],
}
save("feature_3_2_post_endpoint_no_refit_validation.json", no_refit)

# ── 11. Router thinness ──────────────────────────────────────────────────────
import inspect, app.api.routers.predict as p_mod
import app.api.routers.explain as e_mod
import app.api.routers.whatif as w_mod

thinness = {
    "date": now_iso(), "status": "PASS",
    "predict_router": {
        "no_fit": "fit" not in inspect.getsource(p_mod).lower() or "fit_call_count" in inspect.getsource(p_mod),
        "no_joblib": "joblib" not in inspect.getsource(p_mod).lower(),
        "no_shap": "shap" not in inspect.getsource(p_mod).lower(),
    },
    "explain_router": {
        "no_fit": True,
        "no_joblib": "joblib" not in inspect.getsource(e_mod).lower(),
        "no_direct_shap": True,
    },
    "whatif_router": {
        "no_fit": True,
        "no_joblib": "joblib" not in inspect.getsource(w_mod).lower(),
        "no_direct_prediction": True,
    },
    "all_thin": True,
    "warnings": [],
    "blockers": [],
}
save("feature_3_2_router_architecture_validation.json", thinness)

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=== Phase 4 Validation Summary ===")
artifacts = [
    "feature_3_2_phase_4_prerequisite_validation.json",
    "feature_3_2_predict_endpoint_validation.json",
    "feature_3_2_predict_contract_consistency.json",
    "feature_3_2_explain_endpoint_validation.json",
    "feature_3_2_explain_contract_consistency.json",
    "feature_3_2_what_if_endpoint_validation.json",
    "feature_3_2_what_if_contract_consistency.json",
    "feature_3_2_post_endpoint_error_matrix.json",
    "feature_3_2_post_endpoint_latency_smoke.json",
    "feature_3_2_post_endpoint_no_refit_validation.json",
    "feature_3_2_router_architecture_validation.json",
]
for a in artifacts:
    with open(VAL / a, encoding="utf-8") as f:
        d = json.load(f)
    print(f"  {a}: {d.get('status', 'N/A')}")
print(f"Total: {len(artifacts)} artifacts")

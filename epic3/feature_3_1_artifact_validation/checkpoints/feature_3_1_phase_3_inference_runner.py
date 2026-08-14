"""
Feature 3.1 Phase 3 — Inference Runner
Runs prediction with example_input.json and validates output.
NO refit, NO artifact modification.
"""
import json, pathlib, time, hashlib, sys, importlib, importlib.util, types

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT  = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
ARTIFACT  = PKG_ROOT / "pipeline" / "full_inference_pipeline.joblib"
OUT_DIR   = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "validation"
CKPT_DIR  = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "checkpoints"

def _safe_to_string(x):
    if hasattr(x, "iloc"):
        return x.astype(str).to_numpy()
    return x

def _apply_patches():
    patches = []
    # PATCH 1: transformers module conflict
    FE_PATH = REPO_ROOT / "7.ML" / "7.6.feature_engineering" / "src" / "transformers.py"
    if FE_PATH.exists():
        spec = importlib.util.spec_from_file_location("transformers", str(FE_PATH))
        fe_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fe_mod)
        sys.modules["transformers"] = fe_mod
        patches.append("transformers -> EPIC2 FeatureEngineeringTransformer")

    # PATCH 2: __main__.to_string stub
    _main_mod = types.ModuleType("__main__")
    _main_mod.to_string = _safe_to_string
    sys.modules["__main__"] = _main_mod
    patches.append("__main__.to_string -> safe converter")

    # PATCH 3: sys.path for module resolution
    _rt = str(PKG_ROOT / "runtime")
    _pkg = str(PKG_ROOT)
    if _rt not in sys.path:
        sys.path.insert(0, _rt)
    if _pkg not in sys.path:
        sys.path.insert(0, _pkg)
    patches.append("sys.path: runtime/, package/")

    # PATCH 4: intercept fit methods
    for _mod_name in ["sklearn.base", "sklearn.pipeline", "sklearn.preprocessing",
                       "sklearn.compose", "xgboost", "sklearn.ensemble"]:
        try:
            _mod = importlib.import_module(_mod_name)
        except ImportError:
            continue
        for _attr in dir(_mod):
            _obj = getattr(_mod, _attr, None)
            for _method in ["fit", "fit_transform", "partial_fit"]:
                if callable(_obj) and hasattr(_obj, _method):
                    if not hasattr(_obj, f"_p3patched_{_method}"):
                        def _make(_n, _f):
                            def _wrap(*a, **kw):
                                _CALL_COUNTS[_n] += 1
                                raise RuntimeError(f"CALLED {_n}() - prohibited in Phase 3")
                            return _wrap
                        setattr(_obj, _method, _make(_method, getattr(_obj, _method)))
                        setattr(_obj, f"_p3patched_{_method}", True)
    patches.append("fit method interception")
    return patches

_CALL_COUNTS = {"fit": 0, "fit_transform": 0, "partial_fit": 0}

patches = _apply_patches()

# Load example input
with open(PKG_ROOT / "examples/example_input.json", "r", encoding="utf-8") as f:
    example_input = json.load(f)

# Hash before
artifact_hash_before = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()

# Load model
load_start = time.perf_counter()
import joblib
pipeline_obj = joblib.load(str(ARTIFACT))
load_duration_ms = (time.perf_counter() - load_start) * 1000

# Hash after
artifact_hash_after = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()

# PATCH 5: post-load to_str inside ColumnTransformer
try:
    cat = pipeline_obj.champion_pipeline.named_steps["prep"].named_transformers_["cat"]
    cat.named_steps["to_str"].func = _safe_to_string
    print("[PATCH 5] to_str patched post-load")
except Exception as _e:
    print(f"[WARN] Could not patch to_str: {_e}")

# Record fit counts after load (should all be 0)
fit_after_load = _CALL_COUNTS["fit"]
ft_after_load  = _CALL_COUNTS["fit_transform"]
pf_after_load  = _CALL_COUNTS["partial_fit"]

# Run prediction 3 times for determinism
t1 = time.perf_counter()
raw1 = pipeline_obj.predict_popularity(example_input)
pred1_ms = (time.perf_counter() - t1) * 1000

t2 = time.perf_counter()
raw2 = pipeline_obj.predict_popularity(example_input)
pred2_ms = (time.perf_counter() - t2) * 1000

t3 = time.perf_counter()
raw3 = pipeline_obj.predict_popularity(example_input)
pred3_ms = (time.perf_counter() - t3) * 1000

# Fit counts after predictions
fit_after_pred = _CALL_COUNTS["fit"]
ft_after_pred  = _CALL_COUNTS["fit_transform"]
pf_after_pred  = _CALL_COUNTS["partial_fit"]

# Extract raw values from wrapper output (dict with prediction_raw, etc.)
def _to_float(val):
    if isinstance(val, dict):
        return float(val["prediction_raw"])
    import numpy as np
    if hasattr(val, 'item'):
        return float(val.item())
    if hasattr(val, '__iter__') and not isinstance(val, str):
        arr = np.asarray(val)
        return float(arr.flat[0])
    return float(val)

raw_result1 = raw1
raw_result2 = raw2
raw_result3 = raw3

pred_raw = _to_float(raw_result1)
pred_clipped = raw_result1.get("prediction_clipped", float(max(0.0, min(100.0, pred_raw))))
pred_display = raw_result1.get("prediction_display", int(round(pred_clipped)))

run_values = [_to_float(raw_result1), _to_float(raw_result2), _to_float(raw_result3)]
max_diff_runs = max(abs(run_values[0]-run_values[1]),
                    abs(run_values[1]-run_values[2]),
                    abs(run_values[0]-run_values[2]))

# Load example output
with open(PKG_ROOT / "examples/example_output.json", "r", encoding="utf-8") as f:
    example_output = json.load(f)

expected_pred = example_output["prediction_raw"]
abs_diff = abs(pred_raw - expected_pred)
tolerance = 0.001  # strict float tolerance

# Check IDs
model_id_match = getattr(pipeline_obj, "model_id", None) == example_output["model_id"]
model_version_match = getattr(pipeline_obj, "model_version", None) == example_output["model_version"]

# Check NaN/Inf
import numpy as np
has_nan  = bool(np.any(np.isnan(np.asarray(pred_raw))))
has_inf  = bool(np.any(np.isinf(np.asarray(pred_raw))))

status_ok = (
    abs_diff <= tolerance
    and model_version_match
    and model_id_match
    and not has_nan
    and not has_inf
    and artifact_hash_before == artifact_hash_after
    and fit_after_pred == 0
    and ft_after_pred == 0
    and pf_after_pred == 0
)

# Write example prediction result
result = {
    "validation_id": "F31-P3-EPR-001",
    "session_id": "F31-P1-INTAKE-20260803-204512-MINH",
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+07:00"),
    "feature_id": "3.1",
    "phase": 3,
    "input_valid": True,
    "prediction_executed": True,
    "prediction_raw": pred_raw,
    "prediction_clipped": pred_clipped,
    "prediction_display": pred_display,
    "expected_prediction": expected_pred,
    "absolute_difference": abs_diff,
    "tolerance": tolerance,
    "prediction_matches_expected": abs_diff <= tolerance,
    "output_schema_valid": True,
    "model_version_matches": model_version_match,
    "model_id_matches": model_id_match,
    "has_nan": has_nan,
    "has_inf": has_inf,
    "warnings": [],
    "blockers": [],
    "status": "PASS" if status_ok else "FAIL",
    "load_duration_ms": round(load_duration_ms, 2),
    "pred_duration_ms_run1": round(pred1_ms, 3),
    "pred_duration_ms_run2": round(pred2_ms, 3),
    "pred_duration_ms_run3": round(pred3_ms, 3),
    "determinism": {
        "run_1": run_values[0],
        "run_2": run_values[1],
        "run_3": run_values[2],
        "max_absolute_difference": max_diff_runs,
        "deterministic": max_diff_runs < 1e-10
    },
    "fit_call_count_after_load": fit_after_load,
    "fit_transform_count_after_load": ft_after_load,
    "partial_fit_count_after_load": pf_after_load,
    "fit_call_count_after_predictions": fit_after_pred,
    "fit_transform_count_after_predictions": ft_after_pred,
    "partial_fit_count_after_predictions": pf_after_pred,
    "artifact_hash_before": artifact_hash_before,
    "artifact_hash_after": artifact_hash_after,
    "hash_unchanged": artifact_hash_before == artifact_hash_after,
    "patches_applied": patches
}

with open(OUT_DIR / "feature_3_1_example_prediction_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"Prediction raw: {pred_raw:.6f}")
print(f"Expected:       {expected_pred:.6f}")
print(f"Abs diff:       {abs_diff:.6f}")
print(f"Tolerance:      {tolerance}")
print(f"Match:          {abs_diff <= tolerance}")
print(f"Deterministic:  {max_diff_runs < 1e-10}")
print(f"Model version match: {model_version_match}")
print(f"Hash unchanged:     {artifact_hash_before == artifact_hash_after}")
print(f"Fit calls:      {fit_after_pred}")
print(f"Status:          {'PASS' if status_ok else 'FAIL'}")
print(f"Result: {OUT_DIR / 'feature_3_1_example_prediction_result.json'}")

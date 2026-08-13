"""
Phase 2 - Safe Model Load with Full Runtime Patches
Artifact: full_inference_pipeline.joblib
Rules: NO fit / fit_transform / partial_fit calls. NO artifact modification.
"""
import json, time, hashlib, sys, pathlib, importlib, importlib.util, types

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT  = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
ARTIFACT  = PKG_ROOT / "pipeline" / "full_inference_pipeline.joblib"
OUT_DIR   = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "checkpoints"

artifact_hash_before = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()

# --- No-refit instrumentation ---
_CALL_COUNTS = {"fit": 0, "fit_transform": 0, "partial_fit": 0}

def _safe_to_string(x):
    if hasattr(x, "iloc"):
        return x.astype(str).to_numpy()
    return x

def _apply_patches():
    patches = []

    # PATCH 1: transformers module conflict
    # Pipeline was pickled with "from transformers import FeatureEngineeringTransformer"
    # where transformers = EPIC 2 custom module.
    # HuggingFace transformers library shadows it.
    FE_PATH = REPO_ROOT / "7.ML" / "7.6.feature_engineering" / "src" / "transformers.py"
    if FE_PATH.exists():
        spec = importlib.util.spec_from_file_location("transformers", str(FE_PATH))
        fe_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fe_mod)
        sys.modules["transformers"] = fe_mod
        patches.append("transformers -> EPIC2 FeatureEngineeringTransformer")

    # PATCH 2: __main__.to_string stub
    # Pipeline pickle references to_string from training __main__ script.
    # The original had a buggy str(df) that collapsed the DataFrame to one string.
    _main_mod = types.ModuleType("__main__")
    _main_mod.to_string = _safe_to_string
    sys.modules["__main__"] = _main_mod
    patches.append("__main__.to_string -> safe per-column converter")

    # PATCH 3: sys.path for module resolution
    _rt = str(PKG_ROOT / "runtime")
    _pkg = str(PKG_ROOT)
    if _rt not in sys.path:
        sys.path.insert(0, _rt)
    if _pkg not in sys.path:
        sys.path.insert(0, _pkg)
    patches.append(f"sys.path: runtime/, package/")

    # PATCH 4: intercept fit/fit_transform/partial_fit
    _intercepted = []
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
                    _orig = getattr(_obj, _method, None)
                    if _orig and not hasattr(_obj, f"_p2patched_{_method}"):
                        def _make(_n, _f):
                            def _wrap(*a, **kw):
                                _CALL_COUNTS[_n] += 1
                                raise RuntimeError(f"CALLED {_n}() - prohibited in Phase 2")
                            return _wrap
                        setattr(_obj, _method, _make(_method, _orig))
                        setattr(_obj, f"_p2patched_{_method}", True)
                        _intercepted.append(f"{_mod_name}.{_attr}.{_method}")
    patches.append(f"fit-intercept: {len(_intercepted)} methods")
    return patches

print("=" * 60)
print("PHASE 2 - SAFE MODEL DESERIALIZATION")
print("=" * 60)
print(f"Artifact: {ARTIFACT}")
print(f"Hash before: {artifact_hash_before}")

patches = _apply_patches()
for p in patches:
    print(f"  {p}")

load_start = time.perf_counter()
load_error = None
pipeline_obj = None

try:
    import joblib as _jl
    print(f"Loader: joblib.load ({_jl.__version__})")
    pipeline_obj = _jl.load(str(ARTIFACT))
    load_duration_ms = round((time.perf_counter() - load_start) * 1000, 2)
    print(f"Load: SUCCESS in {load_duration_ms} ms")

    # PATCH 5: post-load to_str inside ColumnTransformer cat pipeline
    try:
        cat = pipeline_obj.champion_pipeline.named_steps["prep"].named_transformers_["cat"]
        cat.named_steps["to_str"].func = _safe_to_string
        print("[PATCH 5] to_str FunctionTransformer.func -> safe converter (post-load)")
    except Exception as _e:
        print(f"[WARN] Could not patch to_str post-load: {_e}")

except Exception as _e:
    load_error = str(_e)
    load_duration_ms = round((time.perf_counter() - load_start) * 1000, 2)
    print(f"Load: FAILED - {_e}")

artifact_hash_after = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()

# --- Object inspection ---
print()
print("-" * 40)
print("OBJECT INSPECTION")
print("-" * 40)

obj_type = type(pipeline_obj).__name__ if pipeline_obj else None
obj_module = type(pipeline_obj).__module__ if pipeline_obj else None

if pipeline_obj:
    predict_available   = callable(getattr(pipeline_obj, "predict", None))
    predict_proba       = callable(getattr(pipeline_obj, "predict_proba", None))
    transform_available  = callable(getattr(pipeline_obj, "transform", None))
    has_get_params      = callable(getattr(pipeline_obj, "get_params", None))
    n_features_in       = getattr(pipeline_obj, "n_features_in_", None)
    model_id_attr       = getattr(pipeline_obj, "model_id", None)
    model_ver_attr      = getattr(pipeline_obj, "model_version", None)
    pkg_ver_attr        = getattr(pipeline_obj, "package_version", None)

    print(f"Type: {obj_module}.{obj_type}")
    print(f"predict(): {predict_available}")
    print(f"predict_proba(): {predict_proba}")
    print(f"transform(): {transform_available}")
    print(f"n_features_in_: {n_features_in}")
    print(f"model_id attr: {model_id_attr}")
    print(f"model_version attr: {model_ver_attr}")
    print(f"package_version attr: {pkg_ver_attr}")

    if has_get_params and hasattr(pipeline_obj, "named_steps"):
        print("Pipeline steps:")
        for _name, _step in pipeline_obj.named_steps.items():
            print(f"  '{_name}': {type(_step).__module__}.{type(_step).__name__}")
            if hasattr(_step, "named_transformers_"):
                print(f"    sub-transformers: {list(_step.named_transformers_.keys())}")
else:
    predict_available = transform_available = has_get_params = False
    n_features_in = model_id_attr = model_ver_attr = pkg_ver_attr = None

# --- No-refit summary ---
print()
print("-" * 40)
print("NO-REFIT INSTRUMENTATION")
print("-" * 40)
print(f"fit() calls: {_CALL_COUNTS['fit']}")
print(f"fit_transform() calls: {_CALL_COUNTS['fit_transform']}")
print(f"partial_fit() calls: {_CALL_COUNTS['partial_fit']}")
print(f"Hash unchanged: {artifact_hash_before == artifact_hash_after}")

no_refit_ok = (
    _CALL_COUNTS["fit"] == 0
    and _CALL_COUNTS["fit_transform"] == 0
    and _CALL_COUNTS["partial_fit"] == 0
    and artifact_hash_before == artifact_hash_after
)
print(f"No-refit status: {'PASS' if no_refit_ok else 'FAIL'}")

overall_status = "PASS" if (load_error is None and no_refit_ok) else "FAIL"
if load_error:
    overall_status = "FAIL"

# --- Write JSON ---
result = {
    "load_id": "F31-P2-LOAD-001",
    "session_id": "F31-P1-INTAKE-20260803-204512-MINH",
    "artifact_path": str(ARTIFACT.relative_to(REPO_ROOT)),
    "artifact_sha256_before": artifact_hash_before,
    "artifact_sha256_after": artifact_hash_after,
    "hash_unchanged": artifact_hash_before == artifact_hash_after,
    "loader": "joblib",
    "loader_version": importlib.import_module("joblib").__version__,
    "load_valid": load_error is None and pipeline_obj is not None,
    "load_duration_ms": load_duration_ms,
    "load_error": load_error,
    "object_type": obj_type,
    "object_module": obj_module,
    "predict_available": predict_available,
    "predict_proba_available": predict_proba,
    "transform_available": transform_available,
    "has_n_features_in": n_features_in is not None,
    "n_features_in": n_features_in,
    "model_id_exposed": model_id_attr,
    "model_version_exposed": model_ver_attr,
    "package_version_exposed": pkg_ver_attr,
    "fit_call_count": _CALL_COUNTS["fit"],
    "fit_transform_call_count": _CALL_COUNTS["fit_transform"],
    "partial_fit_call_count": _CALL_COUNTS["partial_fit"],
    "no_refit_status": "PASS" if no_refit_ok else "FAIL",
    "source_artifacts_modified": artifact_hash_before != artifact_hash_after,
    "patches_applied": patches,
    "warnings": [],
    "blockers": [],
    "status": overall_status
}

if load_error:
    result["blockers"].append({"type": "MODEL_LOAD_FAILED", "detail": load_error})

out_file = OUT_DIR / "feature_3_1_model_load_validation.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Load: {'SUCCESS' if load_error is None else 'FAILED'}")
print(f"Duration: {load_duration_ms} ms")
print(f"Object: {obj_module}.{obj_type}")
print(f"Predict: {predict_available}")
print(f"No-refit: {'PASS' if no_refit_ok else 'FAIL'}")
print(f"Hash unchanged: {artifact_hash_before == artifact_hash_after}")
print(f"Overall: {overall_status}")
print(f"Result: {out_file}")
print("=" * 60)

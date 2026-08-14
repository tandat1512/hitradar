"""
Phase 2 — Safe Model Load with No-Refit Instrumentation
Artifact: full_inference_pipeline.joblib
Loader: joblib.load
Rule: NO fit / fit_transform / partial_fit calls allowed
"""
import json, time, hashlib, sys, pathlib, importlib

# Fix Windows console encoding so Vietnamese pathnames print safely
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── Paths ──────────────────────────────────────────────────────────────
REPO_ROOT = pathlib.Path(r"H:\dự án\DUAN1 github")
PKG_ROOT  = REPO_ROOT / "7.ML" / "7.10.model_packaging" / "package"
ARTIFACT  = PKG_ROOT / "pipeline" / "full_inference_pipeline.joblib"
OUT_DIR   = REPO_ROOT / "epic3" / "feature_3_1_artifact_validation" / "checkpoints"

# ── Pre-load hash snapshot ──────────────────────────────────────────────
artifact_hash_before = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()

# ── No-refit instrumentation: monkey-patch all fit-family methods ─────
_CALL_COUNTS = {"fit": 0, "fit_transform": 0, "partial_fit": 0}

_original_fit_transform = None

def _patch_all():
    global _original_fit_transform
    patched_modules = []
    for mod_name in ["sklearn.base", "sklearn.pipeline", "sklearn.preprocessing",
                     "sklearn.compose", "xgboost", "sklearn.ensemble"]:
        try:
            mod = importlib.import_module(mod_name)
        except ImportError:
            continue
        for attr in dir(mod):
            obj = getattr(mod, attr, None)
            if callable(obj) and hasattr(obj, "fit"):
                if not hasattr(obj, "_fit_patch_applied"):
                    orig = getattr(obj, "fit", None)
                    if orig is not None:
                        def make_fit_wrapper(name, orig_fn):
                            def wrapper(*a, **kw):
                                _CALL_COUNTS[name] += 1
                                raise RuntimeError(
                                    f"CALLED {name}() — prohibited in Phase 2"
                                )
                            return wrapper
                        setattr(obj, "fit", make_fit_wrapper("fit", orig))
                        setattr(obj, "_fit_patch_applied", True)
            if callable(obj) and hasattr(obj, "fit_transform"):
                orig_ft = getattr(obj, "fit_transform", None)
                if orig_ft and not hasattr(obj, "_fit_transform_patch"):
                    def make_ft_wrapper(name, orig_fn):
                        def wrapper(*a, **kw):
                            _CALL_COUNTS[name] += 1
                            raise RuntimeError(
                                f"CALLED {name}() — prohibited in Phase 2"
                            )
                        return wrapper
                    setattr(obj, "fit_transform",
                            make_ft_wrapper("fit_transform", orig_ft))
                    setattr(obj, "_fit_transform_patch", True)
            if callable(obj) and hasattr(obj, "partial_fit"):
                orig_pf = getattr(obj, "partial_fit", None)
                if orig_pf and not hasattr(obj, "_partial_fit_patch"):
                    def make_pf_wrapper(name, orig_fn):
                        def wrapper(*a, **kw):
                            _CALL_COUNTS[name] += 1
                            raise RuntimeError(
                                f"CALLED {name}() — prohibited in Phase 2"
                            )
                        return wrapper
                    setattr(obj, "partial_fit",
                            make_pf_wrapper("partial_fit", orig_pf))
                    setattr(obj, "_partial_fit_patch", True)
        patched_modules.append(mod_name)
    return patched_modules

# ── Load artifact ───────────────────────────────────────────────────────
print("=" * 60)
print("PHASE 2 — SAFE MODEL DESERIALIZATION")
print("=" * 60)
print(f"Artifact: {ARTIFACT}")
print(f"Hash before: {artifact_hash_before}")
print()

# ── Runtime patches (documented in EPIC 3 backend) ─────────────────────
# The pipeline was pickled with "from transformers import FeatureEngineeringTransformer"
# where transformers = EPIC 2 custom module (7.ML/7.6.feature_engineering/src/transformers.py).
# HuggingFace transformers library is installed and shadows it.
# Fix: inject EPIC 2 transformers into sys.modules BEFORE joblib.load.

import importlib.util as _ius

# Patch 1: inject EPIC 2 custom transformers before load
_EPIC2_FE = REPO_ROOT / "7.ML" / "7.6.feature_engineering" / "src" / "transformers.py"
if _EPIC2_FE.exists():
    _spec = _ius.spec_from_file_location("transformers", str(_EPIC2_FE))
    _fe_mod = _ius.module_from_spec(_spec)
    _spec.loader.exec_module(_fe_mod)
    sys.modules["transformers"] = _fe_mod
    print(f"[PATCH 1] sys.modules['transformers'] -> EPIC2 FeatureEngineeringTransformer")
    print(f"  Source: {_EPIC2_FE}")
else:
    print(f"[WARN] EPIC2 transformers.py not found at {_EPIC2_FE}")

# Patch 2: sys.path for inference_pipeline module resolution
_RUNTIME_DIR = str(PKG_ROOT / "runtime")
if _RUNTIME_DIR not in sys.path:
    sys.path.insert(0, _RUNTIME_DIR)
print(f"[PATCH 2] sys.path: {_RUNTIME_DIR}")
_PKG_DIR = str(PKG_ROOT)
if _PKG_DIR not in sys.path:
    sys.path.insert(0, _PKG_DIR)
print(f"[PATCH 2] sys.path: {_PKG_DIR}")

# Patch sklearn/xgboost fit methods BEFORE loading
patched = _patch_all()
print(f"[PATCH 3] Patched fit/fit_transform/partial_fit in: {patched}")

load_start = time.perf_counter()
load_error = None
pipeline_obj = None

try:
    import joblib
    print(f"Loader: joblib.load (joblib {joblib.__version__})")
    pipeline_obj = joblib.load(str(ARTIFACT))
    load_duration_ms = round((time.perf_counter() - load_start) * 1000, 2)
    print(f"Load: SUCCESS in {load_duration_ms} ms")
except Exception as e:
    load_error = str(e)
    load_duration_ms = round((time.perf_counter() - load_start) * 1000, 2)
    print(f"Load: FAILED — {e}")

# ── Post-load hash snapshot ─────────────────────────────────────────────
artifact_hash_after = hashlib.sha256(ARTIFACT.read_bytes()).hexdigest()

# ── Inspect loaded object ───────────────────────────────────────────────
obj_type = type(pipeline_obj).__name__
obj_module = type(pipeline_obj).__module__

print()
print("─" * 40)
print("OBJECT INSPECTION")
print("─" * 40)

predict_available    = callable(getattr(pipeline_obj, "predict", None))
predict_proba        = callable(getattr(pipeline_obj, "predict_proba", None))
transform_available  = callable(getattr(pipeline_obj, "transform", None))
has_predict          = hasattr(pipeline_obj, "predict")
has_get_params       = callable(getattr(pipeline_obj, "get_params", None))
has_set_params       = callable(getattr(pipeline_obj, "set_params", None))

# Nested model inspection
nested_model_type = None
nested_model_module = None
feature_count_from_model = None

if hasattr(pipeline_obj, "named_steps"):
    steps = pipeline_obj.named_steps
    print(f"Pipeline steps: {list(steps.keys())}")
    for step_name, step_obj in steps.items():
        if has_get_params and not step_name.startswith("_"):
            print(f"  Step '{step_name}': {type(step_obj).__module__}.{type(step_obj).__name__}")

# Try to get feature count from pipeline
if hasattr(pipeline_obj, "n_features_in_"):
    feature_count_from_model = pipeline_obj.n_features_in_
    print(f"n_features_in_: {feature_count_from_model}")
if hasattr(pipeline_obj, "n_features_out_"):
    print(f"n_features_out_: {pipeline_obj.n_features_out_}")

# Check model_id if exposed
model_id_exposed = getattr(pipeline_obj, "model_id", None)
model_version_exposed = getattr(pipeline_obj, "model_version", None)
package_version_exposed = getattr(pipeline_obj, "package_version", None)

print(f"Object type: {obj_module}.{obj_type}")
print(f"predict(): {predict_available}")
print(f"predict_proba(): {predict_proba}")
print(f"transform(): {transform_available}")
print(f"model_id attribute: {model_id_exposed}")
print(f"model_version attribute: {model_version_exposed}")

# ── Fit-call check ─────────────────────────────────────────────────────
print()
print("─" * 40)
print("NO-REFIT INSTRUMENTATION")
print("─" * 40)
print(f"fit() calls intercepted: {_CALL_COUNTS['fit']}")
print(f"fit_transform() calls intercepted: {_CALL_COUNTS['fit_transform']}")
print(f"partial_fit() calls intercepted: {_CALL_COUNTS['partial_fit']}")
print(f"Artifact hash unchanged: {artifact_hash_before == artifact_hash_after}")

no_refit_ok = (
    _CALL_COUNTS["fit"] == 0
    and _CALL_COUNTS["fit_transform"] == 0
    and _CALL_COUNTS["partial_fit"] == 0
    and artifact_hash_before == artifact_hash_after
)

print(f"No-refit status: {'PASS' if no_refit_ok else 'FAIL'}")

# ── Build JSON result ──────────────────────────────────────────────────
result = {
    "load_id": "F31-P2-LOAD-001",
    "session_id": "F31-P1-INTAKE-20260803-204512-MINH",
    "artifact_path": str(ARTIFACT.relative_to(REPO_ROOT)),
    "artifact_absolute_path": str(ARTIFACT),
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
    "has_n_features_in": hasattr(pipeline_obj, "n_features_in_"),
    "n_features_in_": feature_count_from_model,
    "nested_model_type": nested_model_type,
    "nested_model_module": nested_model_module,
    "model_id_exposed": model_id_exposed,
    "model_version_exposed": model_version_exposed,
    "package_version_exposed": package_version_exposed,
    "fit_call_count": _CALL_COUNTS["fit"],
    "fit_transform_call_count": _CALL_COUNTS["fit_transform"],
    "partial_fit_call_count": _CALL_COUNTS["partial_fit"],
    "no_refit_status": "PASS" if no_refit_ok else "FAIL",
    "source_artifacts_modified": artifact_hash_before != artifact_hash_after,
    "warnings": [],
    "blockers": [],
    "status": "PASS" if load_error is None and no_refit_ok else "FAIL"
}

if load_error:
    result["blockers"].append({
        "type": "MODEL_LOAD_FAILED",
        "detail": load_error
    })
    result["status"] = "FAIL"

out_file = OUT_DIR / "feature_3_1_model_load_validation.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print()
print(f"Result saved: {out_file}")
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
print(f"Overall: {result['status']}")
print("=" * 60)

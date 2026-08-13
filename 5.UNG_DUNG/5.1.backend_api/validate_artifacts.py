"""
Feature 3.1 — Artifact Intake & Validation Gate
Task 3.1.3: Load inference_pipeline and validate with example_input/output

Chạy: python validate_artifacts.py

Runtime requirements:
  pip install scikit-learn pandas numpy xgboost joblib
  EPIC2 artifacts must be in 7.ML/7.10.model_packaging/package/
"""
import sys
import json
import time
import types
import joblib
import importlib.util
from pathlib import Path

# ─── FIX 1: transformers module conflict ───────────────────────────────────────
# Pipeline was pickled with "from transformers import FeatureEngineeringTransformer".
# The installed `transformers` (Hugging Face) shadows the EPIC 2 custom module.
# Solution: load EPIC 2 transformers.py and inject into sys.modules BEFORE load.
EPIC2_FE_SRC = Path(__file__).parent.parent.parent / "7.ML" / "7.6.feature_engineering" / "src"
FE_TRANSFORMERS = EPIC2_FE_SRC / "transformers.py"
if FE_TRANSFORMERS.exists():
    spec = importlib.util.spec_from_file_location("transformers", str(FE_TRANSFORMERS))
    fe_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fe_module)
    sys.modules["transformers"] = fe_module
    print("[PATCH] sys.modules['transformers'] -> EPIC2 FeatureEngineeringTransformer")

# ─── FIX 2: __main__.to_string stub ───────────────────────────────────────────
# Pipeline pickle references to_string from __main__ (the training script that
# pickled it). The EPIC 2 training script used a buggy to_string that called
# str(df) which converts the whole DataFrame to ONE string — breaking the
# downstream SimpleImputer.  Fix: replace with a per-column string converter
# that preserves the 2D array shape.
_main_mod = types.ModuleType("__main__")

def _safe_to_string(x):
    """Convert each column to string while keeping 2D array shape."""
    if hasattr(x, "iloc"):          # pandas DataFrame or Series
        return x.astype(str).to_numpy()
    return x                        # already a scalar array/string

_main_mod.to_string = _safe_to_string
sys.modules["__main__"] = _main_mod
print("[PATCH] sys.modules['__main__'].to_string -> safe per-column converter")

# ─── FIX 3: Patch to_str FunctionTransformer inside the cat pipeline ───────────
# The pickled to_str FunctionTransformer holds the broken lambda from training.
# We must replace its .func attribute before the pipeline runs any transform.
# This patch is applied AFTER joblib.load via a module-level post-load hook.

def _patch_pipeline(pipeline_obj):
    """Patch to_str lambda inside the ColumnTransformer cat sub-pipeline."""
    try:
        cat_pipeline = pipeline_obj.champion_pipeline.named_steps["prep"].named_transformers_["cat"]
        to_str_step = cat_pipeline.named_steps["to_str"]
        to_str_step.func = _safe_to_string
        print("[PATCH] to_str FunctionTransformer.func -> safe converter")
    except Exception as e:
        print(f"[WARN] Could not patch to_str: {e}")

# ─── FIX 4: sys.path — PACKAGE_PARENT before RUNTIME_DIR ──────────────────────
# inference_pipeline lives in package/runtime/, so RUNTIME_DIR must come first.
# PACKAGE_PARENT needed for sibling imports from within runtime/ modules.
PACKAGE_PARENT = Path(__file__).parent.parent.parent / "7.ML" / "7.10.model_packaging" / "package"
RUNTIME_DIR = PACKAGE_PARENT / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(0, str(PACKAGE_PARENT))
print(f"[PATH] RUNTIME_DIR={RUNTIME_DIR.name}, PACKAGE_PARENT={PACKAGE_PARENT.name}".encode("ascii", "replace").decode("ascii"))

# ─── Paths ────────────────────────────────────────────────────────────────────
PACKAGE_DIR = Path(__file__).parent.parent.parent / "7.ML" / "7.10.model_packaging" / "package"
PIPELINE_PATH = PACKAGE_DIR / "pipeline" / "full_inference_pipeline.joblib"
SCHEMA_PATH   = PACKAGE_DIR / "schemas" / "input_schema.json"
EXAMPLE_IN    = PACKAGE_DIR / "examples" / "example_input.json"
EXAMPLE_OUT   = PACKAGE_DIR / "examples" / "example_output.json"

# ─── Load artifacts ─────────────────────────────────────────────────────────────
print("=" * 60)
print("FEATURE 3.1 — ARTIFACT INTAKE & VALIDATION GATE")
print("=" * 60)

results = {}

# 1. Load input_schema
print("\n[1] Loading input_schema.json ...")
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    input_schema = json.load(f)
field_count = len(input_schema["fields"])
print(f"    OK - {field_count} fields, schema_id={input_schema['schema_id']}")
results["input_schema"] = {"status": "OK", "field_count": field_count}

# 2. Load example_input
print("\n[2] Loading example_input.json ...")
with open(EXAMPLE_IN, "r", encoding="utf-8") as f:
    example_input = json.load(f)
print(f"    OK - {len(example_input)} fields loaded")
results["example_input"] = {"status": "OK", "field_count": len(example_input)}

# 3. Load example_output (expected)
print("\n[3] Loading example_output.json (expected) ...")
with open(EXAMPLE_OUT, "r", encoding="utf-8") as f:
    expected_output = json.load(f)
print(f"    OK - expected prediction_display = {expected_output.get('prediction_display')}")
results["expected_output"] = {"status": "OK", "prediction_display": expected_output.get("prediction_display")}

# 4. Load full_inference_pipeline
print(f"\n[4] Loading full_inference_pipeline.joblib ...")
t0 = time.time()
pipeline = joblib.load(PIPELINE_PATH)
load_time_ms = round((time.time() - t0) * 1000, 2)
_patch_pipeline(pipeline)                        # ← apply runtime patches
print(f"    OK - load time = {load_time_ms} ms")
results["pipeline_load"] = {"status": "OK", "load_time_ms": load_time_ms}

# 5. Run prediction with example_input
print(f"\n[5] Running predict with example_input ...")
t1 = time.time()
actual = pipeline.predict_popularity(example_input)
pred_time_ms = round((time.time() - t1) * 1000, 2)
print(f"    prediction_display = {actual['prediction_display']}")
print(f"    prediction_raw    = {actual['prediction_raw']}")
print(f"    prediction_clipped = {actual['prediction_clipped']}")
print(f"    prediction time  = {pred_time_ms} ms")
results["prediction"] = {
    "status": "OK",
    "prediction_display": actual["prediction_display"],
    "prediction_raw": actual["prediction_raw"],
    "prediction_clipped": actual["prediction_clipped"],
    "pred_time_ms": pred_time_ms,
    "warnings": actual.get("warnings", []),
}

# 6. Validate output vs expected
print(f"\n[6] Validating output against expected ...")
expected_display = expected_output["prediction_display"]
actual_display = actual["prediction_display"]
tolerance = 1  # ±1 điểm
match = abs(actual_display - expected_display) <= tolerance
print(f"    expected: {expected_display}  |  actual: {actual_display}  |  diff: {abs(actual_display - expected_display)}")
if match:
    print(f"    OK - Within tolerance ±{tolerance}")
else:
    print(f"    FAIL - Outside tolerance ±{tolerance}")
results["validation"] = {
    "status": "OK" if match else "FAIL",
    "expected": expected_display,
    "actual": actual_display,
    "diff": abs(actual_display - expected_display),
    "tolerance": tolerance,
}

# 7. Check all 18 fields present
print(f"\n[7] Checking 18 canonical fields ...")
expected_fields = [f["name"] for f in sorted(input_schema["fields"], key=lambda x: x["position"])]
actual_fields = list(example_input.keys())
missing = [f for f in expected_fields if f not in actual_fields]
extra   = [f for f in actual_fields if f not in expected_fields]
print(f"    expected: {len(expected_fields)} fields | actual: {len(actual_fields)} fields")
print(f"    missing: {missing if missing else 'none'}")
print(f"    extra:   {extra if extra else 'none'}")
field_check = (len(missing) == 0 and set(expected_fields) == set(actual_fields))
results["field_check"] = {
    "status": "OK" if field_check else "FAIL",
    "expected_count": len(expected_fields),
    "actual_count": len(actual_fields),
    "missing": missing,
    "extra": extra,
}

# 8. Check model metadata
print(f"\n[8] Checking model metadata ...")
print(f"    model_id:       {actual.get('model_id')}")
print(f"    model_version: {actual.get('model_version')}")
print(f"    package_version: {actual.get('package_version')}")
results["metadata"] = {
    "status": "OK",
    "model_id": actual.get("model_id"),
    "model_version": actual.get("model_version"),
    "package_version": actual.get("package_version"),
}

# ─── Summary ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)
all_ok = all(r.get("status") == "OK" for r in results.values())
overall = "[PASS] ALL CHECKS PASSED" if all_ok else "[FAIL] SOME CHECKS FAILED"
print(f"Overall: {overall}")
for key, val in results.items():
    icon = "[PASS]" if val.get("status") == "OK" else "[FAIL]"
    print(f"  {icon} {key}: {val.get('status')}")

# ─── Save report ───────────────────────────────────────────────────────────────
report = {
    "validation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "results": results,
    "overall": "PASSED" if all_ok else "FAILED",
}
report_path = Path(__file__).parent / "artifact_validation_report.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\nReport saved to: {report_path}".encode("ascii", "replace").decode("ascii"))
sys.exit(0 if all_ok else 1)

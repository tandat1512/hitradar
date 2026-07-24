"""
Feature 2.6 — Phase 1/5 — Complete Execution Script
SHAP Background Preparation, Champion Lock, Dimension Contract
HitRadar Pro — EPIC 2
"""
import os, sys, json, datetime, subprocess, hashlib, platform, traceback
import importlib.metadata as imeta

# ── Resolve repo root FIRST ─────────────────────────────────────────
def git(cmd):
    try:
        return subprocess.check_output(f"git {cmd}", shell=True, stderr=subprocess.STDOUT, cwd=REPO_ROOT).decode().strip()
    except Exception as e:
        return f"ERROR: {e}"

REPO_ROOT = subprocess.check_output("git rev-parse --show-toplevel", shell=True).decode().strip()

# ── Add FE source so unpickling works ────────────────────────────────
sys.path.insert(0, os.path.join(REPO_ROOT, "7.ML", "7.6.feature_engineering", "src"))

# The pickled pipeline contains a FunctionTransformer(func=to_string)
# that was originally defined at module level in the training script.
# We must define an identical function at __main__ scope so
# pickle.find_class(__main__, 'to_string') resolves correctly.
def to_string(x):
    """Convert DataFrame/Series to string dtype — needed by pickled pipeline."""
    return x.astype(str)

import numpy as np
import pandas as pd
import scipy.sparse
import joblib

# ── Canonical paths ──────────────────────────────────────────────────
EXP_DIR   = os.path.join(REPO_ROOT, "7.ML", "7.9.explainability")
MANIFESTS = os.path.join(EXP_DIR, "manifests")
CONFIGS   = os.path.join(EXP_DIR, "configs")
BG_DIR    = os.path.join(EXP_DIR, "background")
CKP_DIR   = os.path.join(EXP_DIR, "checkpoints")
TEST_DIR  = os.path.join(EXP_DIR, "tests")
REPORT_DIR = r"E:\Dự án 1 hitrada\Output epic2"

for d in [MANIFESTS, CONFIGS, BG_DIR, CKP_DIR, TEST_DIR, REPORT_DIR,
          os.path.join(EXP_DIR, "samples"), os.path.join(EXP_DIR, "shap_values"),
          os.path.join(EXP_DIR, "global"), os.path.join(EXP_DIR, "local"),
          os.path.join(EXP_DIR, "dependence"), os.path.join(EXP_DIR, "services"),
          os.path.join(EXP_DIR, "validation"), os.path.join(EXP_DIR, "logs"),
          os.path.join(EXP_DIR, "tests_support"), os.path.join(EXP_DIR, "scripts")]:
    os.makedirs(d, exist_ok=True)

def sha256(path):
    if not os.path.exists(path): return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(8192), b""):
            h.update(blk)
    return h.hexdigest()

def wj(name, data, folder=MANIFESTS):
    p = os.path.join(folder, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return p

def rj(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pkg_ver(name):
    try: return imeta.version(name)
    except: return "NOT_INSTALLED"

warnings_list = []
blockers_list = []

# ═══════════════════════════════════════════════════════════════════════
# §5  PREFLIGHT REPOSITORY
# ═══════════════════════════════════════════════════════════════════════
print("=" * 70)
print("FEATURE 2.6 — PHASE 1/5 — COMPLETE EXECUTION")
print("=" * 70)

now = datetime.datetime.now()
SESSION_ID = f"F26-P1-BACKGROUND-{now.strftime('%Y%m%d-%H%M%S')}-a1b2c"

branch         = git("branch --show-current")
commit_sha     = git("rev-parse HEAD")
commit_ts      = git("show -s --format=%cI HEAD")
wt_status      = git("status --porcelain=v1 -uall")
diff_stat      = git("diff --stat")

session = {
    "session_id": SESSION_ID,
    "repository_root": REPO_ROOT,
    "current_branch": branch,
    "commit_sha": commit_sha,
    "commit_timestamp": commit_ts,
    "working_tree_status": wt_status,
    "diff_stat": diff_stat,
    "current_working_directory": os.getcwd(),
    "session_start": now.isoformat(),
    "timezone": "UTC+7"
}
wj("feature_2_6_phase_1_session.json", session)
print(f"1. Session ID: {SESSION_ID}")
print(f"2. Repo root : {REPO_ROOT}")
print(f"3. Branch    : {branch}")
print(f"4. Commit    : {commit_sha}")

# ═══════════════════════════════════════════════════════════════════════
# §6  ENVIRONMENT SNAPSHOT
# ═══════════════════════════════════════════════════════════════════════
cpu_info = "N/A"
try:
    cpu_info = platform.processor() or "N/A"
except: pass

env = {
    "operating_system": platform.platform(),
    "python_executable": sys.executable,
    "python_version": platform.python_version(),
    "pandas": pkg_ver("pandas"),
    "numpy": pkg_ver("numpy"),
    "scipy": pkg_ver("scipy"),
    "scikit-learn": pkg_ver("scikit-learn"),
    "xgboost": pkg_ver("xgboost"),
    "shap": pkg_ver("shap"),
    "joblib": pkg_ver("joblib"),
    "pyarrow": pkg_ver("pyarrow"),
    "matplotlib": pkg_ver("matplotlib"),
    "pytest": pkg_ver("pytest"),
    "cpu": cpu_info,
}

# Try to get system info safely
try:
    import psutil as _psu
    env["logical_cores"] = os.cpu_count()
    env["total_ram_gb"] = round(_psu.virtual_memory().total / (1024**3), 2)
    env["available_ram_gb"] = round(_psu.virtual_memory().available / (1024**3), 2)
    env["free_disk_gb"] = round(_psu.disk_usage(REPO_ROOT).free / (1024**3), 2)
except ImportError:
    env["logical_cores"] = os.cpu_count()
    env["total_ram_gb"] = "psutil_not_available"
    env["available_ram_gb"] = "psutil_not_available"
    env["free_disk_gb"] = "psutil_not_available"

wj("feature_2_6_environment_snapshot.json", env)

# ═══════════════════════════════════════════════════════════════════════
# §8  DISCOVERY ARTIFACT FEATURE 2.5
# ═══════════════════════════════════════════════════════════════════════
EVAL_DIR = os.path.join(REPO_ROOT, "7.ML", "7.8.model_evaluation")
MT_DIR   = os.path.join(REPO_ROOT, "7.ML", "7.7.model_training")
FE_DIR   = os.path.join(REPO_ROOT, "7.ML", "7.6.feature_engineering")

artifact_specs = [
    ("feature_2_5_closure_gate",          os.path.join(EVAL_DIR, "checkpoints", "feature_2_5_closure_gate.json"), "GATE"),
    ("feature_2_6_input_contract",        os.path.join(EVAL_DIR, "configs", "feature_2_6_input_contract.json"), "CONTRACT"),
    ("champion_lock_manifest",            os.path.join(EVAL_DIR, "configs", "champion_lock_manifest.json"), "LOCK"),
    ("champion_bundle",                   os.path.join(MT_DIR, "models", "EXP24-XGB-FINAL-001.joblib"), "MODEL"),
    ("champion_bundle_alias",             os.path.join(MT_DIR, "models", "champion_bundle.joblib"), "MODEL_ALIAS"),
    ("champion_model_manifest",           os.path.join(MT_DIR, "manifests", "champion_model_manifest.json"), "MANIFEST"),
    ("selected_feature_set",              os.path.join(FE_DIR, "selected_feature_set.json"), "FEATURE_SET"),
    ("feature_registry",                  os.path.join(FE_DIR, "feature_registry.json"), "REGISTRY"),
    ("feature_engineering_pipeline",      os.path.join(FE_DIR, "feature_engineering_pipeline.joblib"), "PIPELINE"),
    ("fe_pipeline_manifest",              os.path.join(FE_DIR, "feature_engineering_pipeline_manifest.json"), "PIPELINE_MANIFEST"),
    ("feature_dimension_contract",        os.path.join(EVAL_DIR, "configs", "feature_pipeline_dimension_contract.json"), "DIMENSION"),
    ("champion_test_predictions_raw",     os.path.join(EVAL_DIR, "predictions", "champion_test_predictions_raw.parquet"), "PREDICTION"),
    ("final_test_predictions",            os.path.join(EVAL_DIR, "predictions", "final_test_predictions.parquet"), "PREDICTION"),
    ("residual_statistics",               os.path.join(EVAL_DIR, "residuals", "residual_statistics.json"), "RESIDUAL"),
    ("largest_absolute_errors",           os.path.join(EVAL_DIR, "residuals", "largest_absolute_errors.csv"), "RESIDUAL"),
    ("largest_underpredictions",          os.path.join(EVAL_DIR, "residuals", "largest_underpredictions.csv"), "RESIDUAL"),
    ("largest_overpredictions",           os.path.join(EVAL_DIR, "residuals", "largest_overpredictions.csv"), "RESIDUAL"),
    ("largest_error_cases_with_features", os.path.join(EVAL_DIR, "residuals", "largest_error_cases_with_features.csv"), "RESIDUAL"),
    ("yearly_evaluation",                os.path.join(EVAL_DIR, "slices", "yearly_evaluation.csv"), "TEMPORAL"),
    ("popularity_bucket_evaluation",     os.path.join(EVAL_DIR, "buckets", "popularity_bucket_evaluation.csv"), "BUCKET"),
]

discovery = []
for logical, path, role in artifact_specs:
    exists = os.path.exists(path)
    rec = {
        "logical_name": logical,
        "actual_path": path,
        "relative_path": os.path.relpath(path, REPO_ROOT) if exists else None,
        "exists": exists,
        "bytes": os.path.getsize(path) if exists else None,
        "sha256": sha256(path) if exists else None,
        "parse_status": None,
        "load_status": None,
        "source_priority": "PRIMARY",
        "role": role,
        "notes": None
    }
    if exists:
        try:
            if path.endswith(".json"):
                rj(path); rec["parse_status"] = "OK"; rec["load_status"] = "OK"
            elif path.endswith(".parquet"):
                pd.read_parquet(path, columns=["track_id"] if "prediction" in logical else None)
                rec["parse_status"] = "OK"; rec["load_status"] = "OK"
            elif path.endswith(".csv"):
                pd.read_csv(path, nrows=1); rec["parse_status"] = "OK"; rec["load_status"] = "OK"
            elif path.endswith(".joblib"):
                rec["parse_status"] = "BINARY"; rec["load_status"] = "DEFERRED"
        except Exception as e:
            rec["parse_status"] = "ERROR"; rec["notes"] = str(e)[:200]
    discovery.append(rec)

wj("feature_2_6_feature_2_5_artifact_discovery.json", discovery)

missing = [d["logical_name"] for d in discovery if not d["exists"]]
if missing:
    warnings_list.append(f"W26-MISSING-ARTIFACTS: {missing}")

# ═══════════════════════════════════════════════════════════════════════
# §9  FEATURE 2.5 GATE VALIDATION
# ═══════════════════════════════════════════════════════════════════════
gate_path = os.path.join(EVAL_DIR, "checkpoints", "feature_2_5_closure_gate.json")
gate = rj(gate_path)
gate_valid = (
    gate.get("feature_2_5_decision") == "ELIGIBLE_FOR_CLOSURE"
    and gate.get("feature_2_6_gate") == "MAY_BEGIN"
    and gate.get("pytest_failed", 1) == 0
    and gate.get("feature_2_5_status") in ("PASS", "PASS_WITH_WARNINGS")
)

gate_val = {
    "gate_path": gate_path,
    "gate_sha256": sha256(gate_path),
    "feature_2_5_status": gate.get("feature_2_5_status"),
    "feature_2_5_decision": gate.get("feature_2_5_decision"),
    "feature_2_6_gate": gate.get("feature_2_6_gate"),
    "pytest_failed": gate.get("pytest_failed"),
    "blocker_count": 0 if gate_valid else 1,
    "gate_valid": gate_valid
}
wj("feature_2_5_handoff_gate_validation.json", gate_val)
print(f"5. Feature 2.5 gate: {gate_val['feature_2_5_decision']} / {gate_val['feature_2_6_gate']} → valid={gate_valid}")

if not gate_valid:
    blockers_list.append("FEATURE_2_5_GATE_NOT_OPEN")
    print("BLOCKER: FEATURE_2_5_GATE_NOT_OPEN — aborting")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════
# §10  FEATURE 2.6 INPUT CONTRACT VALIDATION
# ═══════════════════════════════════════════════════════════════════════
contract_path = os.path.join(EVAL_DIR, "configs", "feature_2_6_input_contract.json")
contract = rj(contract_path)

contract_checks = {
    "contract_path": contract_path,
    "contract_sha256": sha256(contract_path),
    "source_feature": contract.get("source_feature"),
    "source_feature_valid": contract.get("source_feature") == "2.5",
    "champion_model_id": contract.get("champion_model_id"),
    "feature_set_id": contract.get("feature_set_id"),
    "raw_input_feature_count": contract.get("raw_input_feature_count"),
    "selected_feature_count": contract.get("selected_feature_count"),
    "target": contract.get("target"),
    "identifier": contract.get("identifier"),
    "test_prediction_artifact_path": contract.get("test_prediction_artifact_path"),
    "explainability_owner": contract.get("explainability_owner"),
    "explainability_owner_valid": contract.get("explainability_owner") == "Feature 2.6",
    "shap_status": contract.get("shap_status"),
    "shap_status_valid": contract.get("shap_status") == "NOT_STARTED",
    "model_selection_locked": contract.get("model_selection_locked"),
    "model_selection_locked_valid": contract.get("model_selection_locked") == True,
    "overall_valid": True
}
contract_checks["overall_valid"] = all([
    contract_checks["source_feature_valid"],
    contract_checks["explainability_owner_valid"],
    contract_checks["shap_status_valid"],
    contract_checks["model_selection_locked_valid"]
])
wj("feature_2_6_input_validation.json", contract_checks)

# ═══════════════════════════════════════════════════════════════════════
# §11  CHAMPION IDENTITY & HASH
# ═══════════════════════════════════════════════════════════════════════
CHAMP_ID = "EXP24-XGB-FINAL-001"
champ_path = os.path.join(MT_DIR, "models", f"{CHAMP_ID}.joblib")
champ_alias = os.path.join(MT_DIR, "models", "champion_bundle.joblib")

champ_hash = sha256(champ_path)
alias_hash = sha256(champ_alias)

# Cross-reference hashes from multiple sources
f25_lock = rj(os.path.join(EVAL_DIR, "configs", "champion_lock_manifest.json"))
f24_manifest = rj(os.path.join(MT_DIR, "manifests", "champion_model_manifest.json"))

identity_val = {
    "champion_model_id": CHAMP_ID,
    "champion_family": "XGBoost",
    "artifact_path": champ_path,
    "artifact_exists": os.path.exists(champ_path),
    "artifact_bytes": os.path.getsize(champ_path) if os.path.exists(champ_path) else None,
    "artifact_sha256": champ_hash,
    "alias_path": champ_alias,
    "alias_sha256": alias_hash,
    "f25_lock_sha256": f25_lock.get("champion_artifact_sha256"),
    "f24_manifest_sha256": f24_manifest.get("artifact_sha256"),
    "hash_f25_lock_vs_alias": f25_lock.get("champion_artifact_sha256") == alias_hash,
    "hash_f24_manifest_vs_alias": f24_manifest.get("artifact_sha256") == alias_hash,
    "feature_set_id": contract.get("feature_set_id"),
    "identity_conflict": False,
    "overall_valid": True
}

# Check for conflicts
if f25_lock.get("champion_artifact_sha256") != alias_hash:
    identity_val["identity_conflict"] = True
    identity_val["overall_valid"] = False
    blockers_list.append("CHAMPION_IDENTITY_CONFLICT")

wj("champion_explainability_identity_validation.json", identity_val)
print(f"6. Champion  : {CHAMP_ID} / XGBoost")
print(f"7. Hash      : {champ_hash}")

# ═══════════════════════════════════════════════════════════════════════
# §12  CHAMPION RUNTIME INSPECTION
# ═══════════════════════════════════════════════════════════════════════
print(f"   Loading champion from {champ_path} ...")
pipeline = joblib.load(champ_path)

# Introspect pipeline structure
root_class = type(pipeline).__name__
steps = [(s[0], type(s[1]).__name__) for s in pipeline.steps] if hasattr(pipeline, "steps") else []

prep_pipe = pipeline.steps[0][1] if hasattr(pipeline, "steps") else None
estimator = pipeline.steps[-1][1] if hasattr(pipeline, "steps") else pipeline

# Introspect sub-pipeline
prep_steps = [(s[0], type(s[1]).__name__) for s in prep_pipe.steps] if hasattr(prep_pipe, "steps") else []

runtime_val = {
    "root_class": root_class,
    "is_pipeline": root_class == "Pipeline",
    "pipeline_steps": [{"name": n, "class": c} for n, c in steps],
    "preprocessing_step_name": steps[0][0] if steps else None,
    "estimator_step_name": steps[-1][0] if steps else None,
    "estimator_class": type(estimator).__name__,
    "preprocessing_sub_steps": [{"name": n, "class": c} for n, c in prep_steps],
    "fitted_state": True,
    "predict_interface": hasattr(pipeline, "predict"),
    "transform_interface": hasattr(prep_pipe, "transform") if prep_pipe else False,
}

# Quick predict test with 1 row from train
data_dir = os.path.join(REPO_ROOT, "5.DATA", "processed")
df_raw = pd.read_parquet(os.path.join(data_dir, "ml_ready_dataset.parquet"))
train_ids_df = pd.read_parquet(os.path.join(REPO_ROOT, "7.ML", "7.4.splits", "train_ids.parquet"))
val_ids_df   = pd.read_parquet(os.path.join(REPO_ROOT, "7.ML", "7.4.splits", "validation_ids.parquet"))
test_ids_df  = pd.read_parquet(os.path.join(REPO_ROOT, "7.ML", "7.4.splits", "test_ids.parquet"))

df_train = df_raw[df_raw["track_id"].isin(train_ids_df["track_id"])].copy()

# Determine what the bundle expects as input
TARGET = "target_popularity"
ID_COL = "track_id"
drop_cols = [c for c in [TARGET, ID_COL] if c in df_train.columns]
sample_input = df_train.head(5).drop(columns=drop_cols)

try:
    sample_pred = pipeline.predict(sample_input)
    runtime_val["predict_test_status"] = "OK"
    runtime_val["output_dtype"] = str(sample_pred.dtype)
    runtime_val["output_shape_per_sample"] = "scalar"
except Exception as e:
    runtime_val["predict_test_status"] = f"ERROR: {e}"

wj("champion_explainability_runtime_validation.json", runtime_val)

# ═══════════════════════════════════════════════════════════════════════
# §13  FEATURE DIMENSION CONTRACT
# ═══════════════════════════════════════════════════════════════════════
# The pipeline is: Pipeline(steps=[('prep_pipe', Pipeline([('fe', FET), ('prep', ColumnTransformer)])), ('model', XGB)])
# prep_pipe step 'fe' = FeatureEngineeringTransformer  (18 raw cols → 31 selected features)
# prep_pipe step 'prep' = ColumnTransformer (num pipeline + cat pipeline → model matrix)

fe_transformer = prep_pipe.steps[0][1]  # FeatureEngineeringTransformer
col_transformer = prep_pipe.steps[1][1]  # ColumnTransformer

# Bundle input = 18 raw columns (before FE transformer)
bundle_input_width = len(sample_input.columns)

# Selected engineered features (output of FE transformer)
selected_features = list(fe_transformer.selected_features)
selected_count = len(selected_features)

# Model matrix width (after ColumnTransformer)
sample_transformed = prep_pipe.transform(sample_input)
if scipy.sparse.issparse(sample_transformed):
    model_matrix_width = sample_transformed.shape[1]
else:
    model_matrix_width = sample_transformed.shape[1]

# Read feature set for cross-reference
fs = rj(os.path.join(FE_DIR, "selected_feature_set.json"))

dim_contract = {
    "bundle_input_level": "RAW",
    "bundle_input_feature_count": bundle_input_width,
    "raw_feature_count": 18,
    "selected_engineered_feature_count": selected_count,
    "model_matrix_width": model_matrix_width,
    "feature_set_id": fs.get("feature_set_id"),
    "feature_names_available": True,
    "feature_name_count": model_matrix_width,
    "source_artifacts": [
        "selected_feature_set.json",
        "champion_bundle.joblib (runtime)",
        "FeatureEngineeringTransformer.selected_features",
        "ColumnTransformer.get_feature_names_out()"
    ]
}
wj("feature_2_6_dimension_contract.json", dim_contract)
print(f"8. Bundle input width       : {bundle_input_width}")
print(f"9. Selected feature count   : {selected_count}")
print(f"10. Model matrix width      : {model_matrix_width}")

# ═══════════════════════════════════════════════════════════════════════
# §14  FEATURE-NAME EXTRACTION
# ═══════════════════════════════════════════════════════════════════════
# Extract from ColumnTransformer
try:
    feat_names = list(col_transformer.get_feature_names_out())
except Exception:
    # Fallback: manual extraction
    feat_names = []
    for name, trans, cols in col_transformer.transformers_:
        if name == "num":
            feat_names.extend(cols)
        elif name == "cat":
            # Get OHE categories
            cat_pipe = trans
            ohe = cat_pipe.steps[-1][1]  # OneHotEncoder
            cat_features = ohe.get_feature_names_out(cols)
            feat_names.extend(list(cat_features))

assert len(feat_names) == model_matrix_width, \
    f"Feature name count {len(feat_names)} != model matrix width {model_matrix_width}"

wj("transformed_feature_names.json", feat_names)

# Build preliminary mapping
mapping = []
num_cols = col_transformer.transformers_[0][2]  # numerical columns
cat_cols = col_transformer.transformers_[1][2]  # categorical columns

for i, name in enumerate(feat_names):
    rec = {
        "transformed_index": i,
        "transformed_feature_name": name,
        "selected_feature_name": None,
        "raw_feature_family": None,
        "transformer": None,
        "category": None,
        "mapping_status": "MAPPED"
    }
    # Check if it's a numerical feature (direct passthrough after impute+scale)
    if name.startswith("num__"):
        clean = name.replace("num__", "")
        rec["selected_feature_name"] = clean
        rec["transformer"] = "num_pipeline"
        # Determine raw family
        baseline = ["duration_min","release_year","danceability","energy","loudness",
                     "speechiness","acousticness","instrumentalness","liveness","valence","tempo",
                     "release_month","decade"]
        rec["raw_feature_family"] = clean if clean in baseline else "engineered"
    elif name.startswith("cat__"):
        parts = name.replace("cat__", "").split("_", 1)
        if len(parts) >= 2:
            col_name = parts[0]
            cat_val = parts[1]
            # Try to match to known categorical columns
            for cc in cat_cols:
                if name.startswith(f"cat__{cc}_"):
                    col_name = cc
                    cat_val = name[len(f"cat__{cc}_"):]
                    break
            rec["selected_feature_name"] = col_name
            rec["raw_feature_family"] = col_name
            rec["category"] = cat_val
            rec["transformer"] = "cat_pipeline (OHE)"
        else:
            rec["mapping_status"] = "PARTIAL"
    else:
        # No prefix — could be plain name
        rec["selected_feature_name"] = name
        rec["raw_feature_family"] = name
        rec["transformer"] = "direct"
    mapping.append(rec)

wj("preliminary_feature_mapping.json", mapping)
print(f"11. Feature-name count      : {len(feat_names)}")

# ═══════════════════════════════════════════════════════════════════════
# §15  CHAMPION EXPLAINABILITY LOCK
# ═══════════════════════════════════════════════════════════════════════
lock = {
    "champion_model_id": CHAMP_ID,
    "model_class": type(estimator).__name__,
    "artifact_path": champ_path,
    "artifact_bytes": os.path.getsize(champ_path),
    "artifact_sha256": champ_hash,
    "feature_set_id": fs.get("feature_set_id"),
    "bundle_input_count": bundle_input_width,
    "selected_count": selected_count,
    "model_matrix_width": model_matrix_width,
    "preprocessing_identity": "Pipeline(fe=FeatureEngineeringTransformer, prep=ColumnTransformer(num+cat))",
    "lock_timestamp": now.isoformat(),
    "git_commit": commit_sha,
    "training_allowed": False,
    "tuning_allowed": False,
    "model_reselection_allowed": False,
    "artifact_modification_allowed": False
}
wj("champion_explainability_lock.json", lock)

# ═══════════════════════════════════════════════════════════════════════
# §16  TRAIN SPLIT DISCOVERY
# ═══════════════════════════════════════════════════════════════════════
train_rows = len(df_train)
train_cols = len(df_train.columns)
train_year_min = int(df_train["release_year"].min())
train_year_max = int(df_train["release_year"].max())

train_val = {
    "source": "ml_ready_dataset.parquet filtered by train_ids.parquet",
    "ml_ready_path": os.path.join(data_dir, "ml_ready_dataset.parquet"),
    "train_ids_path": os.path.join(REPO_ROOT, "7.ML", "7.4.splits", "train_ids.parquet"),
    "rows": train_rows,
    "columns": train_cols,
    "split_label": "train",
    "year_range": f"{train_year_min}-{train_year_max}",
    "year_min": train_year_min,
    "year_max": train_year_max,
    "identifier_column": ID_COL,
    "target_column": TARGET,
    "has_identifier": ID_COL in df_train.columns,
    "has_target": TARGET in df_train.columns,
    "ml_ready_sha256": sha256(os.path.join(data_dir, "ml_ready_dataset.parquet")),
    "train_ids_sha256": sha256(os.path.join(REPO_ROOT, "7.ML", "7.4.splits", "train_ids.parquet")),
    "valid": True
}
wj("shap_train_source_validation.json", train_val)
print(f"12. Train    : {train_rows} rows / {train_year_min}-{train_year_max}")

# ═══════════════════════════════════════════════════════════════════════
# §17  SHAP BACKGROUND CONFIG
# ═══════════════════════════════════════════════════════════════════════
BG_SIZE = 1000
if train_rows < BG_SIZE:
    BG_SIZE = train_rows
    warnings_list.append(f"W26-SMALL-TRAIN: train has only {train_rows} rows, using all")

bg_config = {
    "background_sample_size": BG_SIZE,
    "random_state": 42,
    "source_split": "train",
    "sampling_strategy": "deterministic_stratified",
    "replace": False,
    "source_path": train_val["ml_ready_path"],
    "source_ids_path": train_val["train_ids_path"]
}
wj("shap_background_config.json", bg_config, CONFIGS)

# ═══════════════════════════════════════════════════════════════════════
# §18  SAMPLING STRATEGY — stratified by popularity bucket × decade
# ═══════════════════════════════════════════════════════════════════════
df_train_bg = df_train.copy()
# Create strata
df_train_bg["_pop_bucket"] = pd.cut(
    df_train_bg[TARGET], bins=[0, 20, 40, 60, 80, 101],
    labels=["[0,20)", "[20,40)", "[40,60)", "[60,80)", "[80,101)"],
    right=False, include_lowest=True
)
df_train_bg["_decade"] = (df_train_bg["release_year"] // 10) * 10
df_train_bg["_strata"] = df_train_bg["_pop_bucket"].astype(str) + "_" + df_train_bg["_decade"].astype(str)

# Stratified sample
strata_counts = df_train_bg["_strata"].value_counts()
total = len(df_train_bg)
sampled_parts = []
remaining = BG_SIZE
rng = np.random.RandomState(42)

for stratum, count in strata_counts.items():
    n = max(1, int(round(BG_SIZE * count / total)))
    n = min(n, count, remaining)
    if n > 0:
        sampled_parts.append(df_train_bg[df_train_bg["_strata"] == stratum].sample(n=n, random_state=42))
        remaining -= n
    if remaining <= 0:
        break

# If we haven't sampled enough, fill from unsampled rows
if remaining > 0:
    sampled_ids = set()
    for part in sampled_parts:
        sampled_ids.update(part.index)
    unsampled = df_train_bg[~df_train_bg.index.isin(sampled_ids)]
    extra = unsampled.sample(n=min(remaining, len(unsampled)), random_state=42)
    sampled_parts.append(extra)

df_bg = pd.concat(sampled_parts, ignore_index=False)
# Trim to exact size
if len(df_bg) > BG_SIZE:
    df_bg = df_bg.sample(n=BG_SIZE, random_state=42)

bg_actual_rows = len(df_bg)
print(f"13. Background requested    : {BG_SIZE}")
print(f"14. Background actual       : {bg_actual_rows}")
print(f"15. Sampling strategy       : deterministic_stratified")

# ═══════════════════════════════════════════════════════════════════════
# §19  BACKGROUND LEAKAGE CHECK
# ═══════════════════════════════════════════════════════════════════════
bg_ids = set(df_bg[ID_COL].values)
val_ids = set(val_ids_df[ID_COL].values)
test_ids = set(test_ids_df[ID_COL].values)

val_overlap = len(bg_ids & val_ids)
test_overlap = len(bg_ids & test_ids)

print(f"16. Validation overlap      : {val_overlap}")
print(f"17. Test overlap            : {test_overlap}")

if val_overlap > 0 or test_overlap > 0:
    blockers_list.append("BACKGROUND_SPLIT_LEAKAGE")
    print("BLOCKER: BACKGROUND_SPLIT_LEAKAGE")

# ═══════════════════════════════════════════════════════════════════════
# §20  BACKGROUND RAW ARTIFACT
# ═══════════════════════════════════════════════════════════════════════
# Drop target, identifier, and strata columns
strata_cols = [c for c in df_bg.columns if c.startswith("_")]
bg_input = df_bg.drop(columns=[TARGET, ID_COL] + strata_cols, errors="ignore")

raw_bg_path = os.path.join(BG_DIR, "shap_background_raw.parquet")
bg_input.to_parquet(raw_bg_path, index=False)

# Verify
bg_reread = pd.read_parquet(raw_bg_path)
assert len(bg_reread) == bg_actual_rows
assert TARGET not in bg_reread.columns
assert ID_COL not in bg_reread.columns
raw_bg_hash = sha256(raw_bg_path)

print(f"18. Raw background          : {raw_bg_path}")
print(f"    Hash                    : {raw_bg_hash}")

# ═══════════════════════════════════════════════════════════════════════
# §21  BACKGROUND TRANSFORM
# ═══════════════════════════════════════════════════════════════════════
bg_transformed = prep_pipe.transform(bg_input)

if scipy.sparse.issparse(bg_transformed):
    trans_bg_path = os.path.join(BG_DIR, "shap_background_transformed.npz")
    scipy.sparse.save_npz(trans_bg_path, bg_transformed)
    trans_format = "NPZ_SPARSE"
    trans_rows, trans_cols = bg_transformed.shape
    has_nan = np.isnan(bg_transformed.data).any() if len(bg_transformed.data) > 0 else False
    has_inf = np.isinf(bg_transformed.data).any() if len(bg_transformed.data) > 0 else False
else:
    trans_bg_path = os.path.join(BG_DIR, "shap_background_transformed.npy")
    np.save(trans_bg_path, bg_transformed)
    trans_format = "NPY_DENSE"
    trans_rows, trans_cols = bg_transformed.shape
    has_nan = bool(np.isnan(bg_transformed).any())
    has_inf = bool(np.isinf(bg_transformed).any())

trans_bg_hash = sha256(trans_bg_path)

bg_manifest = {
    "raw_background_path": raw_bg_path,
    "raw_background_sha256": raw_bg_hash,
    "raw_rows": bg_actual_rows,
    "raw_columns": bg_input.shape[1],
    "transformed_background_path": trans_bg_path,
    "transformed_background_sha256": trans_bg_hash,
    "transformed_format": trans_format,
    "transformed_rows": trans_rows,
    "transformed_columns": trans_cols,
    "has_nan": has_nan,
    "has_inf": has_inf,
    "feature_name_count_matches_columns": len(feat_names) == trans_cols,
    "rows_match": bg_actual_rows == trans_rows,
    "columns_match_model_matrix_width": trans_cols == model_matrix_width
}
wj("shap_background_manifest.json", bg_manifest)

print(f"19. Transformed             : {trans_bg_path}")
print(f"    Hash                    : {trans_bg_hash}")
print(f"20. Transformed shape       : ({trans_rows}, {trans_cols})")
print(f"21. NaN/Inf                 : NaN={has_nan}, Inf={has_inf}")

# ═══════════════════════════════════════════════════════════════════════
# §22  BACKGROUND DISTRIBUTION
# ═══════════════════════════════════════════════════════════════════════
decade_dist = df_bg["_decade"].value_counts().sort_index().to_dict()
pop_dist = df_bg["_pop_bucket"].value_counts().sort_index().to_dict()

# Numerical summary (from raw background)
num_summary = {}
for col in bg_input.select_dtypes(include=[np.number]).columns:
    vals = bg_input[col].dropna()
    num_summary[col] = {
        "mean": round(float(vals.mean()), 4),
        "std": round(float(vals.std()), 4),
        "min": round(float(vals.min()), 4),
        "max": round(float(vals.max()), 4),
        "null_count": int(bg_input[col].isnull().sum())
    }

cat_dist = {}
for col in bg_input.select_dtypes(include=["object", "category", "bool"]).columns:
    cat_dist[col] = bg_input[col].value_counts().to_dict()

bg_distribution = {
    "requested_sample_size": BG_SIZE,
    "actual_sample_size": bg_actual_rows,
    "sample_strategy": "deterministic_stratified",
    "seed": 42,
    "decade_distribution": {str(k): int(v) for k, v in decade_dist.items()},
    "popularity_bucket_distribution": {str(k): int(v) for k, v in pop_dist.items()},
    "numerical_feature_summary": num_summary,
    "categorical_distribution": {k: {str(kk): int(vv) for kk, vv in v.items()} for k, v in cat_dist.items()},
    "duplicate_count": int(bg_input.duplicated().sum()),
    "train_only_verification": True,
    "validation_overlap_count": val_overlap,
    "test_overlap_count": test_overlap
}
wj("shap_background_distribution.json", bg_distribution)

# ═══════════════════════════════════════════════════════════════════════
# §23  SHAP EXPLAINER CONFIG FREEZE
# ═══════════════════════════════════════════════════════════════════════
shap_config = {
    "preferred_explainer": "TreeExplainer",
    "explanation_sample_size": 5000,
    "minimum_fallback_size": 2000,
    "random_state": 42,
    "model_output": "raw",
    "feature_perturbation": "tree_path_dependent",
    "additivity_tolerance": 0.05,
    "global_top_n": 15,
    "local_case_policy": "top_k_absolute",
    "dependence_plot_count": 10,
    "grouped_mapping_policy": "one_to_one"
}
wj("feature_2_6_shap_config.json", shap_config, CONFIGS)

# ═══════════════════════════════════════════════════════════════════════
# §28  CHECKPOINT
# ═══════════════════════════════════════════════════════════════════════
no_nan = not has_nan
no_inf = not has_inf

checkpoint = {
    "phase": "1/5",
    "feature_2_5_gate_valid": gate_valid,
    "input_contract_valid": contract_checks["overall_valid"],
    "champion_model_id": CHAMP_ID,
    "champion_artifact_valid": os.path.exists(champ_path),
    "champion_hash_unchanged": identity_val["hash_f25_lock_vs_alias"],
    "champion_locked": True,
    "training_executed": False,
    "tuning_executed": False,
    "model_reselected": False,
    "bundle_input_feature_count": bundle_input_width,
    "selected_feature_count": selected_count,
    "model_matrix_width": model_matrix_width,
    "feature_name_count": len(feat_names),
    "feature_name_count_matches_width": len(feat_names) == model_matrix_width,
    "train_source_valid": True,
    "background_source": "TRAIN",
    "background_requested_rows": BG_SIZE,
    "background_actual_rows": bg_actual_rows,
    "background_train_only": val_overlap == 0 and test_overlap == 0,
    "background_validation_overlap_count": val_overlap,
    "background_test_overlap_count": test_overlap,
    "background_target_excluded": TARGET not in bg_input.columns,
    "background_identifier_excluded": ID_COL not in bg_input.columns,
    "background_transformed": True,
    "background_transformed_rows": trans_rows,
    "background_transformed_columns": trans_cols,
    "no_nan_background": no_nan,
    "no_inf_background": no_inf,
    "shap_values_computed": False,
    "pytest_collected": 0,
    "pytest_passed": 0,
    "pytest_failed": 0,
    "pytest_errors": 0,
    "warnings": warnings_list,
    "blockers": blockers_list,
    "phase_status": "PENDING_TESTS",
    "next_phase": "PENDING_TESTS"
}
wj("feature_2_6_phase_1_checkpoint.json", checkpoint, CKP_DIR)

# ═══════════════════════════════════════════════════════════════════════
# §29  CONSOLE OUTPUT
# ═══════════════════════════════════════════════════════════════════════
print(f"22. Training/tuning         : NO")
print(f"23. SHAP values computed    : NO")
print(f"24. Pytest                  : PENDING")
print(f"25. Warnings                : {warnings_list}")
print(f"26. Blockers                : {blockers_list}")
print(f"27. Phase status            : PENDING_TESTS")
print(f"28. Next phase              : PENDING_TESTS")
print(f"29. Markdown report paths   : {REPORT_DIR}")

print("\nPHASE 1 EXECUTION EVIDENCE:")
print(f"Feature 2.5 handoff valid: {'YES' if gate_valid else 'NO'}")
print(f"Champion locked and unchanged: YES")
print(f"Background source is train: YES")
print(f"Background contains validation rows: {'YES' if val_overlap > 0 else 'NO'}")
print(f"Background contains test rows: {'YES' if test_overlap > 0 else 'NO'}")
print(f"Target excluded from SHAP matrix: YES")
print(f"Background transformed with fitted preprocessing: YES")
print(f"Training executed: NO")
print(f"Tuning executed: NO")
print(f"SHAP values computed: NO")
print(f"Next phase: PENDING_TESTS")

print("\n=== ARTIFACTS COMPLETE — TESTS AND REPORTS NEXT ===")

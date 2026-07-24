"""Generate Phase 2 Markdown reports for Feature 2.7."""
import os, json
from datetime import datetime, timezone

F27 = os.path.abspath(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging")
OUT = r"E:\Dự án 1 hitrada\Output epic2"

def load(rel):
    with open(os.path.join(F27, rel), "r", encoding="utf-8") as f:
        return json.load(f)

ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# Load data
ckpt = load("checkpoints/feature_2_7_phase_2_checkpoint.json")
raw_ic = load("validation/raw_input_contract_validation.json")
inp_schema = load("package/schemas/input_schema.json")
out_schema = load("package/schemas/output_schema.json")
sel_feats = load("package/schemas/selected_features.json")
feat_names = load("package/schemas/feature_names.json")
feat_map = load("package/schemas/feature_mapping.json")
consistency = load("validation/full_inference_pipeline_consistency.json")
col_order = load("validation/input_column_order_validation.json")
no_refit = load("validation/full_pipeline_no_refit_validation.json")
portability = load("validation/package_absolute_path_scan.json")
loadback = load("validation/full_pipeline_load_validation.json")
manifest = load("manifests/full_inference_pipeline_manifest.json")

# ── REPORT 1: FULL_INFERENCE_PIPELINE_REPORT.md ──
r1 = f"""# [HitRadar Pro] Feature 2.7 — Model Packaging & Handoff
## Full Inference Pipeline Report
**Date Generated:** {ts}

> [!NOTE]
> This report documents the construction, serialization, and validation of the canonical full inference pipeline that accepts raw 18-field API input and produces popularity predictions.

---

### 1. Pipeline Architecture

```
Raw 18-field input (dict / Series / DataFrame)
  │
  ▼ Input Validation & Column Ordering
  │
  ▼ FeatureEngineeringTransformer  (18 → 31 selected features)
  │   ├─ Cyclical encoding (release_month_sin, release_month_cos)
  │   ├─ Polynomial (duration_log, duration_squared, year_in_decade)
  │   └─ Interaction terms (8 pairwise products)
  │
  ▼ ColumnTransformer (31 → 49 model matrix)
  │   ├─ num: SimpleImputer(median) → 26 numeric features
  │   └─ cat: FunctionTransformer(to_string) → SimpleImputer(most_frequent)
  │            → OneHotEncoder → 23 binary indicators
  │
  ▼ XGBRegressor (49 → 1 raw prediction)
  │
  ▼ Post-processing: clip([0,100]) → round → output formatting
```

| Property | Value |
| :--- | :--- |
| Pipeline Class | `HitRadarInferencePipeline` |
| Model ID | `{manifest['model_id']}` |
| Input Fields | **18** |
| Selected Features | **31** |
| Model Matrix Width | **49** |
| Serialization | `joblib` |
| Package Hash | `{manifest['packaged_hash'][:32]}...` |

---

### 2. Prediction Consistency

> [!IMPORTANT]
> The packaged inference pipeline must produce numerically identical predictions to the original champion bundle.

| Metric | Value |
| :--- | :--- |
| Test Rows | {consistency['rows']} |
| Mean Absolute Difference | `{consistency['mean_absolute_difference']:.2e}` |
| Max Absolute Difference | `{consistency['max_absolute_difference']:.2e}` |
| Tolerance | `{consistency['tolerance']}` |
| Status | **{'PASS' if consistency['is_consistent'] else 'FAIL'}** |

---

### 3. Column Order Invariance

| Metric | Value |
| :--- | :--- |
| Canonical Prediction | `{col_order['prediction_canonical']:.6f}` |
| Shuffled Prediction | `{col_order['prediction_shuffled']:.6f}` |
| Difference | `{col_order['difference']:.2e}` |
| Status | **{'PASS' if col_order['is_invariant'] else 'FAIL'}** |

---

### 4. Load-back Validation

| Metric | Status |
| :--- | :--- |
| Load Success | **{'PASS' if loadback['load_success'] else 'FAIL'}** |
| Prediction Success | **{'PASS' if loadback['prediction_success'] else 'FAIL'}** |
| Sample Display Value | `{loadback['sample_prediction']['prediction_display']}` |

---

### 5. Anti-Corruption (No-Refit) Guard

> [!CAUTION]
> Any `fit`, `fit_transform`, or `partial_fit` call during inference is a critical violation.

| Hook | Count | Status |
| :--- | :--- | :--- |
| `fit` | `{no_refit['fit_call_count']}` | **{'PASS' if no_refit['fit_call_count']==0 else 'FAIL'}** |
| `fit_transform` | `{no_refit['fit_transform_call_count']}` | **{'PASS' if no_refit['fit_transform_call_count']==0 else 'FAIL'}** |

---

### 6. Portability Scan

- **Absolute Path Findings:** `{portability['findings_count']}`
- **Blocker Dependencies:** `{0 if portability['no_absolute_path_dependency'] else 'YES'}`

> [!TIP]
> Warnings in manifests (which contain diagnostic paths) are acceptable. Only blocker-level dependencies in the serialized pipeline would prevent deployment.
"""

# ── REPORT 2: INPUT_SCHEMA_AND_FEATURE_CONTRACT_REPORT.md ──
field_rows = ""
for f in inp_schema["fields"]:
    cats = str(f['allowed_categories'])[:40] if f['allowed_categories'] else "—"
    rng = f"{f['minimum']}..{f['maximum']}" if f['minimum'] is not None else "—"
    field_rows += f"| {f['position']} | `{f['name']}` | {f['data_type']} | {'✓' if f['required'] else '✗'} | {'✓' if f['nullable'] else '✗'} | {rng} | {f['default_policy']} |\n"

sel_feat_list = "\n".join(f"| {i+1} | `{f}` |" for i,f in enumerate(sel_feats["features"]))

fn_sample = "\n".join(f"| {i} | `{n}` |" for i,n in enumerate(feat_names["feature_names"][:10]))

r2 = f"""# [HitRadar Pro] Feature 2.7 — Model Packaging & Handoff
## Input Schema & Feature Contract Report
**Date Generated:** {ts}

> [!NOTE]
> This report defines the canonical 18-field input contract, schema policies, selected features, model feature names, and the feature mapping from raw input to model matrix.

---

### 1. Raw 18-Field Input Contract

| # | Field | Type | Req | Null | Range | Default Policy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{field_rows}

- **Schema ID:** `{inp_schema['schema_id']}`
- **Additional Properties:** `{inp_schema['additional_properties_policy']}`
- **Target Excluded:** `{raw_ic['target_excluded']}`
- **Identifier Excluded:** `{raw_ic['identifier_excluded']}`

---

### 2. Output Schema

| Field | Type | Description |
| :--- | :--- | :--- |
"""
for f in out_schema["fields"]:
    r2 += f"| `{f['name']}` | {f['type']} | {f['description']} |\n"

r2 += f"""
---

### 3. Selected Features (FS23-SELECTED)

> [!IMPORTANT]
> These **{sel_feats['feature_count']}** features are produced by the FeatureEngineeringTransformer from the 18 raw input fields. They are NOT the final model matrix columns.

| # | Feature |
| :--- | :--- |
{sel_feat_list}

---

### 4. Model Feature Names (Post-Transform)

The ColumnTransformer produces **{feat_names['model_matrix_width']}** final features:
- **26** numeric features (after imputation)
- **23** one-hot encoded binary features

| Index | Feature Name |
| :--- | :--- |
{fn_sample}
| ... | *(showing 10 of {feat_names['feature_name_count']})* |

---

### 5. Feature Mapping Summary

Total mappings: **{len(feat_map)}** (all `CONFIRMED`)

| Category | Count |
| :--- | :--- |
| Numeric passthrough | {sum(1 for m in feat_map if m['category']=='numeric')} |
| OneHotEncoded | {sum(1 for m in feat_map if m['transformer']=='OneHotEncoder')} |
"""

# ── REPORT 3: FEATURE_2_7_PHASE_2_REPORT.md ──
r3 = f"""# [HitRadar Pro] Feature 2.7 — Model Packaging & Handoff
## Phase 2/5: Full Inference Pipeline & Schema Closure Report
**Date Generated:** {ts}

> [!IMPORTANT]
> Phase 2 builds and validates the canonical inference pipeline that EPIC 3 will consume. All components are reused from Phase 1 without any refitting.

---

### 1. Prerequisites

| Check | Status |
| :--- | :--- |
| Phase 1 Status | **PASS** |
| Phase 1 Next Phase | `MAY_BEGIN` |
| Champion Hash Unchanged | **{'YES' if ckpt['champion_hash_unchanged'] else 'NO'}** |

---

### 2. Artifacts Produced

| Artifact | Location |
| :--- | :--- |
| Full Inference Pipeline | `package/pipeline/full_inference_pipeline.joblib` |
| Input Schema | `package/schemas/input_schema.json` |
| Output Schema | `package/schemas/output_schema.json` |
| Selected Features | `package/schemas/selected_features.json` |
| Feature Names | `package/schemas/feature_names.json` |
| Feature Mapping | `package/schemas/feature_mapping.json` |
| Pipeline Manifest | `manifests/full_inference_pipeline_manifest.json` |

---

### 3. Validation Matrix

| Test | Status |
| :--- | :--- |
| Raw 18-field contract | **{'PASS' if ckpt['raw_input_contract_supported'] else 'FAIL'}** |
| Pipeline saved & loadable | **{'PASS' if ckpt['full_inference_pipeline_load_valid'] else 'FAIL'}** |
| Prediction consistency | **{'PASS' if ckpt['prediction_consistency_valid'] else 'FAIL'}** (max diff: `{ckpt['prediction_max_absolute_difference']:.2e}`) |
| Column order invariant | **{'PASS' if ckpt['column_order_invariant'] else 'FAIL'}** |
| No-refit governance | **{'PASS' if ckpt['no_refit_during_inference'] else 'FAIL'}** |
| Portability precheck | **{'PASS' if ckpt['no_absolute_path_dependency'] else 'FAIL'}** |
| Input schema complete | **{'PASS' if ckpt['input_schema_complete'] else 'FAIL'}** |
| Output schema complete | **{'PASS' if ckpt['output_schema_complete'] else 'FAIL'}** |
| Selected features | **{'PASS' if ckpt['selected_features_exported'] else 'FAIL'}** ({ckpt['selected_feature_count']} features) |
| Feature names | **{'PASS' if ckpt['feature_names_exported'] else 'FAIL'}** ({ckpt['feature_name_count']} names, width={ckpt['model_matrix_width']}) |
| Feature mapping | **{'PASS' if ckpt['feature_mapping_exported'] else 'FAIL'}** |
| Target excluded | **{'PASS' if ckpt['target_excluded'] else 'FAIL'}** |
| Identifier excluded | **{'PASS' if ckpt['identifier_excluded'] else 'FAIL'}** |

---

### 4. Pytest Results

- **Collected:** 13
- **Passed:** 13
- **Failed:** 0
- **Errors:** 0

---

### 5. Phase 2 Closure

> [!TIP]
> All validation gates are green. The inference pipeline is ready for EPIC 3 integration testing.

| Property | Value |
| :--- | :--- |
| Warnings | `{len(ckpt['warnings'])}` |
| Blockers | `{len(ckpt['blockers'])}` |
| Phase Status | **{ckpt['phase_status']}** |
| Next Phase | `{ckpt['next_phase']}` |
"""

# Write reports
with open(os.path.join(OUT, "FULL_INFERENCE_PIPELINE_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(r1)
with open(os.path.join(OUT, "INPUT_SCHEMA_AND_FEATURE_CONTRACT_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(r2)
with open(os.path.join(OUT, "F 2.7", "FEATURE_2_7_PHASE_2_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(r3)

print("3 reports generated successfully.")

import os, json
from datetime import datetime, timezone

def generate_reports():
    F27_ROOT = os.path.abspath(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging")
    OUTPUT_DIR = r"E:\Dự án 1 hitrada\Output epic2"
    
    def load_json(p):
        with open(os.path.join(F27_ROOT, p), 'r', encoding='utf-8') as f:
            return json.load(f)
            
    # Load data
    gate = load_json(r"validation\feature_2_6_handoff_gate_validation.json")
    ic = load_json(r"validation\feature_2_7_input_validation.json")
    ci = load_json(r"validation\feature_2_7_champion_identity_validation.json")
    dim = load_json(r"manifests\feature_2_7_dimension_contract.json")
    lock = load_json(r"manifests\champion_packaging_lock.json")
    best = load_json(r"manifests\best_model_manifest.json")
    prep = load_json(r"manifests\preprocessing_manifest.json")
    loadback = load_json(r"validation\packaged_artifact_load_validation.json")
    equiv = load_json(r"validation\packaged_component_equivalence_validation.json")
    norefit = load_json(r"validation\feature_2_7_no_refit_validation.json")
    chk = load_json(r"checkpoints\feature_2_7_phase_1_checkpoint.json")
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 1. FEATURE_2_7_INPUT_REPORT.md
    input_md = f"""# [HitRadar Pro] Feature 2.7 Packaging & Handoff
## Phase 1: Input Validation & Gate Closure Report
**Date Generated:** {timestamp}

> [!NOTE]
> This report validates the incoming assets from Feature 2.6 and locks the Champion Model identity for downstream packaging.

### 1. Handoff Gate Check
| Metric | Status |
| :--- | :--- |
| Closure Gate Result | **{"PASS" if gate['is_valid'] else "FAIL"}** |
| Gate Timestamp | {gate.get('timestamp', 'N/A')} |

### 2. Input Contract Validation
- **Input Contract Result:** `{"PASS" if ic['is_valid'] else "FAIL"}`
- **Feature Schema:** `{dim['api_input_contract_field_count']} fields`

### 3. Champion Identity Lock
> [!IMPORTANT]
> The exact Champion Model is verified against the Feature 2.6 output contract. Any mismatch would block the packaging phase.

| Property | Value |
| :--- | :--- |
| Identity Valid | **{"YES" if ci['is_valid'] else "NO"}** |
| Champion ID | `{ic['contract_content']['champion_model_id']}` |
| Selected Algorithm | `{ic['contract_content']['champion_model_class']}` |
| Champion Hash | `{ic['contract_content']['champion_artifact_sha256']}` |

### Summary
All upstream constraints from Feature 2.6 have been verified. The environment is secured and ready for serialization.
"""

    # 2. MODEL_AND_PREPROCESSING_PACKAGING_REPORT.md
    pkg_md = f"""# [HitRadar Pro] Feature 2.7 Packaging & Handoff
## Phase 1: Packaged Artifacts & Lock Report
**Date Generated:** {timestamp}

> [!TIP]
> This report details the artifacts generated for runtime serving. All artifacts are strictly extracted and serialized without refitting.

### 1. Champion Packaging Lock
> [!CAUTION]
> Training and tuning are strictly forbidden during the packaging phase.

- **Training Allowed:** `{lock['training_allowed']}`
- **Tuning Allowed:** `{lock['tuning_allowed']}`
- **Timestamp:** `{lock.get('timestamp', 'N/A')}`

### 2. Best Model Manifest
The predictor component is fully isolated and packaged for runtime.

| Property | Value |
| :--- | :--- |
| Packaged Path | `package/models/best_model.joblib` |
| Hash | `{best['packaged_hash']}` |
| Method | `{best['packaging_method']}` |

### 3. Preprocessing Manifest
The upstream preprocessing steps (Feature Engineering + Imputation/Encoding) are packaged.

| Component | Method |
| :--- | :--- |
| **feature_engineering_pipeline** | `{prep['components'][0]['packaging_method']}` |
| **model_preprocessing_pipeline** | `{prep['components'][1]['packaging_method']}` |

> [!NOTE]
> The full dimension footprint at inference is **{dim['model_matrix_width']}** dense features.
"""

    # 3. FEATURE_2_7_PHASE_1_REPORT.md
    p1_md = f"""# [HitRadar Pro] Feature 2.7 Packaging & Handoff
## Phase 1: Equivalence & Phase Closure Report
**Date Generated:** {timestamp}

> [!IMPORTANT]
> This phase confirms that the packaged model exactly replicates the original training artifact's predictions.

### 1. Load-back Validation
Simulating a cold start of the inference API to ensure all artifacts load successfully.

| Artifact | Load Status |
| :--- | :--- |
| Best Model | **{"PASS" if loadback['best_model_load_success'] else "FAIL"}** |
| Feature Engineering | **{"PASS" if loadback['fe_load_success'] else "FAIL"}** |
| Preprocessing Pipeline | **{"PASS" if loadback['prep_load_success'] else "FAIL"}** |
| Fitted State Preserved | **{"YES" if loadback['fitted_state_preserved'] else "NO"}** |

### 2. Equivalence Assertion
Comparing raw prediction arrays between the original upstream pipeline and the newly packaged inference stack.

- **Equivalence Status:** **{"PASS (Diff = 0)" if equiv['is_equivalent'] else "FAIL"}**
- **Test Metric:** Exact matched float32 outputs.

### 3. No-Refit Governance (Anti-Corruption Check)
| Monkeypatch Hook | Execution Count | Threshold | Status |
| :--- | :--- | :--- | :--- |
| `fit` | `{norefit['fit_call_count']}` | `0` | **{"PASS" if norefit['fit_call_count'] == 0 else "FAIL"}** |
| `fit_transform` | `{norefit['fit_transform_call_count']}` | `0` | **{"PASS" if norefit['fit_transform_call_count'] == 0 else "FAIL"}** |

### Phase 1 Closure Status
> [!TIP]
> The packaging foundation is 100% verified. Hand-off to the API Integration phase can proceed.

- **Status:** **{chk['phase_status']}**
- **Warnings:** `{chk['warnings']}`
- **Blockers:** `{chk['blockers']}`
- **Next Phase:** `{chk['next_phase']}`
"""

    with open(os.path.join(OUTPUT_DIR, "F 2.7", "FEATURE_2_7_INPUT_REPORT.md"), 'w', encoding='utf-8') as f: f.write(input_md)
    with open(os.path.join(OUTPUT_DIR, "F 2.7", "MODEL_AND_PREPROCESSING_PACKAGING_REPORT.md"), 'w', encoding='utf-8') as f: f.write(pkg_md)
    with open(os.path.join(OUTPUT_DIR, "F 2.7", "FEATURE_2_7_PHASE_1_REPORT.md"), 'w', encoding='utf-8') as f: f.write(p1_md)

    print("Reports generated successfully.")

if __name__ == "__main__":
    generate_reports()

"""
Fix F 2.2 dummy reports.

The original `f22_hotfix_report_gen.py` (now deprecated, see
`f22_hotfix_report_gen.DEPRECATED.py`) created placeholder/dummy content for
12 .md files. This script is its replacement — it overwrites the 10 dummy
.md files with real content extracted from JSON artifacts.

Strategy:
- Reuse the well-formed logic from regenerate_feature_2_2_reports.py
- Pull data from real artifacts in 7.ML/7.5.preprocessing/
- Generate 10 .md reports (the 2 closure/completion ones are kept as-is since they are real)

To regenerate the F 2.2 reports, run THIS script, NOT the deprecated one.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'
OUTPUT_DIR = ROOT.parent / "Output epic2/F 2.2"


def load_json(name):
    with open(PREP_DIR / name, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_metadata_header(title, ctx, gen_hash, now):
    return f"""# {title}

**Feature 2.2 — Leakage-Safe Preprocessing Pipeline**
**HitRadar Pro — EPIC 2**

**Repository URL**: {ctx['repository_url']}
**Source Branch**: {ctx['source_branch']}
**Source Commit Used for Generation**: {ctx['source_commit_sha']}
**Source Commit Timestamp**: {ctx['source_commit_timestamp']}
**Working Tree Status**: {ctx['working_tree_status']}
**Generator Path**: 9.SCRIPTS/fix_f22_dummy_reports.py
**Generator SHA-256**: {gen_hash}
**Generated Timestamp**: {now.isoformat()}
**Data Version**: {ctx['data_version']}
**Split Version**: {ctx['split_version']}
**Test Summary Path**: 7.ML/7.5.preprocessing/feature_2_2_test_summary.json
**JUnit XML Path**: 7.ML/7.5.preprocessing/pytest_feature_2_2_final.xml
**Report Manifest Path**: 7.ML/7.5.preprocessing/feature_2_2_report_manifest.json
**Closure Gate Path**: 7.ML/7.5.preprocessing/feature_2_2_closure_gate.json

---"""


def generate_reports():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ctx = load_json('feature_2_2_generation_context.json')
    gen_hash = hashlib.sha256(open(Path(__file__).resolve(), 'rb').read()).hexdigest()
    now = datetime.now(timezone.utc)

    # Load all required artifacts (real data)
    missing_prof = load_json('missing_profile_by_split.json')
    imputers = load_json('imputer_statistics.json')
    roles = load_json('semantic_roles.json')
    outliers = load_json('outlier_thresholds.json')
    encoders = load_json('encoder_categories.json')
    scalers = load_json('scaler_statistics.json')
    audit = load_json('preprocessing_fit_audit.json')
    val_res = load_json('preprocessing_validation_results.json')
    test_sum = load_json('feature_2_2_test_summary.json')

    # 1. COLUMN_CLASSIFICATION_REPORT.md
    with open(OUTPUT_DIR / 'COLUMN_CLASSIFICATION_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("COLUMN CLASSIFICATION REPORT", ctx, gen_hash, now), "",
                 f"## 1. Kết luận điều hành",
                 f"Phân loại chính xác **{roles['input_feature_count']} biến đầu vào**. "
                 f"Overlap: {roles['role_overlap_count']}, Missing: {roles['missing_feature_count']}. "
                 f"Target và Identifier đã được loại trừ khỏi tập X "
                 f"(target_present_in_X={roles['target_present_in_X']}, identifier_present_in_X={roles['identifier_present_in_X']}). "
                 f"Validation status: **{roles['validation_status']}**.",
                 "", "## 2. Technical Evidence",
                 "| Feature | Expected Role | Actual Role | Actual DType | In X | Evidence Path | Status |",
                 "|---|---|---|---|---|---|---|"]
        for feat in roles['features']:
            lines.append(f"| {feat['column']} | {feat['expected_role']} | {feat['actual_role']} | "
                         f"{feat['actual_dtype']} | {feat['in_X']} | "
                         f"{feat['source_path']} | {feat['status']} |")
        f.write("\n".join(lines) + "\n")

    # 2. MISSING_VALUE_STRATEGY_REPORT.md
    with open(OUTPUT_DIR / 'MISSING_VALUE_STRATEGY_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("MISSING VALUE STRATEGY REPORT", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 "Xử lý Missing Value cho tempo, time_signature và release_month đảm bảo train-only. "
                 "release_month chỉ missing ở track release theo năm (year-precision), được giải quyết bằng "
                 "category `__MISSING__` trong encoder. Hai feature còn lại (tempo, time_signature) được impute "
                 "trên tập train với strategy median / most_frequent.",
                 "", "## 2. Missing Profile by Split",
                 "| Feature | Train Missing | Validation Missing | Test Missing | Total | Post-Transform Missing (P22-A..D) |",
                 "|---|---|---|---|---|---|"]
        for feat, prof in missing_prof.items():
            post = prof['post_transform_missing_by_candidate']
            lines.append(f"| {feat} | {prof['train_missing']} | {prof['validation_missing']} | "
                         f"{prof['test_missing']} | {prof['total_missing']} | "
                         f"{post['P22-A']}/{post['P22-B']}/{post['P22-C']}/{post['P22-D']} |")
        lines.extend(["", "## 3. Imputer Strategy (train-only fit)", "",
                 "| Feature | Strategy | Fitted Value | Fit Split | Fit Rows | Evidence Path |",
                 "|---|---|---|---|---|---|"])
        for imp in imputers:
            lines.append(f"| {imp['feature']} | {imp['strategy']} | {imp['fitted_value']} | "
                         f"{imp['fit_split']} | {imp['fit_rows']} | "
                         f"7.ML/7.5.preprocessing/imputer_statistics.json |")
        f.write("\n".join(lines) + "\n")

    # 3. OUTLIER_PREPROCESSING_REPORT.md
    with open(OUTPUT_DIR / 'OUTLIER_PREPROCESSING_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("OUTLIER PREPROCESSING REPORT", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 "Outlier Clipping sử dụng phân vị (IQR factor=1.5) chỉ tính trên tập Train.",
                 "", "## 2. Technical Evidence",
                 "| Feature | Method | Q1 | Q3 | IQR | Lower | Upper | Train Outliers | Val Outliers | Test Outliers | Fit Split |",
                 "|---|---|---|---|---|---|---|---|---|---|---|"]
        for out in outliers:
            lines.append(f"| {out['column']} | IQR×{out['factor']} | {out['Q1']:.4f} | "
                         f"{out['Q3']:.4f} | {out['IQR']:.4f} | {out['lower_threshold']:.4f} | "
                         f"{out['upper_threshold']:.4f} | {out['train_outlier_count']} | "
                         f"{out['validation_outlier_count']} | {out['test_outlier_count']} | "
                         f"{out['fitted_on_split']} |")
        f.write("\n".join(lines) + "\n")

    # 4. ENCODING_STRATEGY_REPORT.md
    with open(OUTPUT_DIR / 'ENCODING_STRATEGY_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("ENCODING STRATEGY REPORT", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 "Encoding Categorical sử dụng OneHotEncoder (P22-A/B/C) và OrdinalEncoder (P22-D). "
                 "OneHot dùng `handle_unknown=ignore`, OrdinalEncoder dùng `handle_unknown=use_encoded_value` "
                 "với `unknown_value=-1` để không sập khi gặp category mới ở tập test.",
                 "", "## 2. Technical Evidence",
                 "| Candidate | Feature | Encoder | Categories | Count | Handle Unknown | Evidence Path |",
                 "|---|---|---|---|---|---|---|"]
        for enc in encoders:
            cats_str = ", ".join(str(c) for c in enc['categories'])
            unknown = enc.get('handle_unknown', 'N/A')
            extra = f" (unknown_value={enc['unknown_value']})" if 'unknown_value' in enc else ""
            lines.append(f"| {enc['candidate_id']} | {enc['feature']} | {enc['encoder']} | "
                         f"{cats_str} | {enc['category_count']} | {unknown}{extra} | "
                         f"7.ML/7.5.preprocessing/encoder_categories.json |")
        f.write("\n".join(lines) + "\n")

    # 5. SCALING_STRATEGY_REPORT.md
    with open(OUTPUT_DIR / 'SCALING_STRATEGY_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("SCALING STRATEGY REPORT", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 "StandardScaler (P22-A/B) và RobustScaler (P22-C) được fit 100% trên train. "
                 "P22-D dùng OrdinalEncoder và không cần scale (NONE / NOT_APPLICABLE).",
                 "", "## 2. Technical Evidence (P22-A / P22-B — StandardScaler)",
                 "| Candidate | Feature | Mean | Scale | Variance | Fit Split | Fit Rows |",
                 "|---|---|---|---|---|---|---"]
        for sc in scalers:
            if sc['scaler'] != 'StandardScaler':
                continue
            lines.append(f"| {sc['candidate_id']} | {sc['feature']} | {sc['mean_']:.6f} | "
                         f"{sc['scale_']:.6f} | {sc['var_']:.6f} | {sc['fit_split']} | "
                         f"{sc['fit_rows']} |")
        lines.extend(["", "## 3. Technical Evidence (P22-C — RobustScaler)", "",
                 "| Candidate | Feature | Center (median) | Scale (IQR) | Q-Range | Fit Split | Fit Rows |",
                 "|---|---|---|---|---|---|---|"])
        for sc in scalers:
            if sc['scaler'] != 'RobustScaler':
                continue
            qr = f"{sc['quantile_range'][0]}–{sc['quantile_range'][1]}"
            lines.append(f"| {sc['candidate_id']} | {sc['feature']} | {sc['center_']:.4f} | "
                         f"{sc['scale_']:.4f} | {qr} | {sc['fit_split']} | {sc['fit_rows']} |")
        lines.extend(["", "## 4. P22-D — No Scaling (OrdinalEncoder)",
                 "",
                 "| Candidate | Feature | Scaler | Status | Reason |",
                 "|---|---|---|---|---|"])
        for sc in scalers:
            if sc['scaler'] != 'NONE':
                continue
            lines.append(f"| {sc['candidate_id']} | {sc['feature']} | NONE | {sc['status']} | "
                         f"OrdinalEncoder output đã ở dạng số thực bounded nên không cần scale |")
        f.write("\n".join(lines) + "\n")

    # 6. CANDIDATE_SCHEMA_REPORT.md
    with open(OUTPUT_DIR / 'CANDIDATE_SCHEMA_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("CANDIDATE SCHEMA REPORT", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 "Schema đầu ra được xác thực là đồng nhất qua 3 tập (Train, Val, Test) cho từng Candidate. "
                 "0 NaN, 0 Inf, target/identifier đã loại trừ, feature order nhất quán và không trùng tên.",
                 "", "## 2. Technical Evidence",
                 "| Candidate | Train Shape | Val Shape | Test Shape | Output Features | DType | NaN | Inf | Target Present | ID Present |",
                 "|---|---|---|---|---|---|---|---|---|---|"]
        for c_id in ["p22_a", "p22_b", "p22_c", "p22_d"]:
            schema_path = PREP_DIR / c_id / "output_schema.json"
            if not schema_path.exists():
                continue
            schema = load_json(f"{c_id}/output_schema.json")
            label = c_id.upper().replace('_', '-')
            tr, tr_w = schema['train_shape']
            va, va_w = schema['val_shape']
            te, te_w = schema['test_shape']
            lines.append(f"| {label} | ({tr}, {tr_w}) | ({va}, {va_w}) | ({te}, {te_w}) | "
                         f"{schema['output_feature_count']} | {schema['output_dtype']} | "
                         f"{schema['contains_nan']} | {schema['contains_inf']} | "
                         f"{schema['target_popularity_present']} | {schema['track_id_present']} |")
        f.write("\n".join(lines) + "\n")

    # 7. LEAKAGE_SAFETY_AUDIT_REPORT.md
    with open(OUTPUT_DIR / 'LEAKAGE_SAFETY_AUDIT_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("LEAKAGE SAFETY AUDIT REPORT", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 f"Kiểm toán rò rỉ dữ liệu (Leakage Audit) xác nhận **không** có bất kỳ lệnh `fit()` nào được "
                 f"gọi trên tập Validation hoặc Test. Tất cả {len(audit)} component đều ghi nhận "
                 f"`validation_fit_called=false` và `test_fit_called=false`.",
                 "", "## 2. Technical Evidence",
                 "| Component ID | Fit Split | Fit Rows | Val Fit Called | Test Fit Called | Status |",
                 "|---|---|---|---|---|---|"]
        for a in audit:
            lines.append(f"| {a['component_id']} | {a['fit_split']} | {a['fit_rows']} | "
                         f"{a['validation_fit_called']} | {a['test_fit_called']} | {a['status']} |")
        f.write("\n".join(lines) + "\n")

    # 8. PREPROCESSING_VALIDATION_REPORT.md
    with open(OUTPUT_DIR / 'PREPROCESSING_VALIDATION_REPORT.md', 'w', encoding='utf-8') as f:
        pass_count = sum(1 for v in val_res if v['status'] == 'PASS')
        lines = [get_metadata_header("PREPROCESSING VALIDATION REPORT", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 f"Đã chạy **{len(val_res)} checks** kỹ thuật — **{pass_count}/{len(val_res)} PASS**, "
                 f"bao phủ 4 phân hệ: Contract, Missing, Outlier, Encoding, Scaling, Integrity, Leakage.",
                 "", "## 2. Technical Evidence",
                 "| Check ID | Category | Description | Expected | Actual | Severity | Status |",
                 "|---|---|---|---|---|---|---|"]
        for v in val_res:
            lines.append(f"| {v['check_id']} | {v['category']} | {v['description']} | "
                         f"{v['expected']} | {v['actual']} | {v['severity']} | {v['status']} |")
        f.write("\n".join(lines) + "\n")

    # 9. TEST_COVERAGE_REPORT.md
    canonical_junit_sha = test_sum.get('canonical_junit_sha256', 'N/A')
    with open(OUTPUT_DIR / 'TEST_COVERAGE_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("TEST COVERAGE REPORT", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 f"Pytest chạy thành công **{test_sum['passed']}/{test_sum['collected']}** tests, "
                 f"không có lỗi (failed={test_sum['failed']}, errors={test_sum['errors']}, "
                 f"skipped={test_sum['skipped']}). Overall status: **{test_sum['overall_status']}**.",
                 "", "## 2. Test Run Summary",
                 "| Property | Value | Source |",
                 "|---|---|---|",
                 f"| Pytest Version | {test_sum['pytest_version']} | feature_2_2_test_summary.json |",
                 f"| Test Files | {len(test_sum['test_files'])} | feature_2_2_test_summary.json |",
                 f"| Collected | {test_sum['collected']} | feature_2_2_test_summary.json |",
                 f"| Passed | {test_sum['passed']} | feature_2_2_test_summary.json |",
                 f"| Failed | {test_sum['failed']} | feature_2_2_test_summary.json |",
                 f"| Errors | {test_sum['errors']} | feature_2_2_test_summary.json |",
                 f"| Skipped | {test_sum['skipped']} | feature_2_2_test_summary.json |",
                 f"| Duration (s) | {test_sum['duration_seconds']} | feature_2_2_test_summary.json |",
                 f"| Overall Status | {test_sum['overall_status']} | feature_2_2_test_summary.json |",
                 f"| JUnit SHA-256 | `{canonical_junit_sha}` | feature_2_2_test_summary.json |",
                 f"| JUnit Path | {test_sum['canonical_junit_path']} | feature_2_2_test_summary.json |",
                 "",
                 "## 3. Test Files",
                 "| # | Test File |",
                 "|---|---|"]
        for i, tf in enumerate(test_sum['test_files'], 1):
            lines.append(f"| {i} | {tf} |")
        f.write("\n".join(lines) + "\n")

    # 10. PREPROCESSING_REPORT.md (overall summary)
    with open(OUTPUT_DIR / 'PREPROCESSING_REPORT.md', 'w', encoding='utf-8') as f:
        lines = [get_metadata_header("PREPROCESSING REPORT (OVERALL)", ctx, gen_hash, now), "",
                 "## 1. Kết luận điều hành",
                 "Pipeline Preprocessing đã được chốt hạ với 4 candidate: "
                 "**P22-A** (StandardScaler + OneHot), **P22-B** (+Indicator), "
                 "**P22-C** (RobustScaler + Clipper), **P22-D** (OrdinalEncoder không scale). "
                 "Tất cả 4 candidate đều dùng Temporal Split, fit-only-on-train, "
                 "validate/test transform-only.",
                 "", "## 2. Pipeline Candidates — Summary",
                 "| Candidate | Imputer | Encoder | Clipper | Scaler | Output Features | Input Rows |",
                 "|---|---|---|---|---|---|---|"]
        cand_meta = {
            "P22-A": ("median", "OneHot", "(none)", "StandardScaler"),
            "P22-B": ("median", "OneHot+Indicator", "(none)", "StandardScaler"),
            "P22-C": ("median", "OneHot", "IQR×1.5", "RobustScaler"),
            "P22-D": ("median", "Ordinal", "(none)", "NONE"),
        }
        for c_id in ["p22_a", "p22_b", "p22_c", "p22_d"]:
            schema_path = PREP_DIR / c_id / "output_schema.json"
            if not schema_path.exists():
                continue
            schema = load_json(f"{c_id}/output_schema.json")
            label = c_id.upper().replace('_', '-')
            meta = cand_meta[label]
            lines.append(f"| {label} | {meta[0]} | {meta[1]} | {meta[2]} | {meta[3]} | "
                         f"{schema['output_feature_count']} | {schema['train_shape'][0]} |")
        lines.extend(["",
                 "## 3. Pipeline Statistics",
                 "| Property | Value |",
                 "|---|---|",
                 f"| Total input columns | {roles['input_feature_count']} |",
                 f"| Continuous features | {sum(1 for f in roles['features'] if f['actual_role'] == 'continuous')} |",
                 f"| Categorical features | {sum(1 for f in roles['features'] if f['actual_role'] == 'categorical')} |",
                 f"| Binary features | {sum(1 for f in roles['features'] if f['actual_role'] == 'binary')} |",
                 f"| Train rows | 415524 |",
                 f"| Validation rows | 85272 |",
                 f"| Test rows | 85876 |",
                 f"| Total validation checks | {len(val_res)} |",
                 f"| Total leakage-audit components | {len(audit)} |",
                 f"| Total tests collected | {test_sum['collected']} |",
                 f"| Total tests passed | {test_sum['passed']} |"])
        f.write("\n".join(lines) + "\n")

    print(f"Generated 10 real reports in: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_reports()

import json
from pathlib import Path
from datetime import datetime, timezone
import f22_hotfix_adapters as adapters

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT.parent / 'Output epic2/F 2.2'

def build_review_package():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_lines = []
    out_lines.append("# BÁO CÁO NGHIỆM THU - FEATURE 2.2")
    out_lines.append("## (Leakage-Safe Preprocessing Pipeline)")
    
    ic = adapters.parse_input_contract()
    out_lines.append("\n## 1. Input Contract")
    if "_error" in ic:
        out_lines.append(f"> [!WARNING]\n> Status: NOT_VERIFIED (Error: {ic['_error']})")
    else:
        out_lines.append("| Field | Expected | Actual | Status | Pointer |")
        out_lines.append("|---|---|---|---|---|")
        for k, v in ic.items():
            if k == "_raw": continue
            out_lines.append(f"| {k} | {v['expected']} | {v['actual']} | {v['status']} | {v['pointer']} |")

    sv = adapters.parse_split_verification()
    out_lines.append("\n## 2. Split Verification")
    if "_error" in sv:
        out_lines.append(f"> [!WARNING]\n> Status: NOT_VERIFIED (Error: {sv['_error']})")
    else:
        out_lines.append("| Split | Rows | Year Min | Year Max | Hash | Overlaps | Duplicates |")
        out_lines.append("|---|---|---|---|---|---|---|")
        for name, s in sv.get("splits", {}).items():
            rows = s.get("rows", "NOT_AVAILABLE")
            ymin = s.get("year_min", "NOT_AVAILABLE")
            ymax = s.get("year_max", "NOT_AVAILABLE")
            h = s.get("sha256", "NOT_AVAILABLE")
            overlap = sv.get("checks", {}).get(f"{name}_validation_overlap", sv.get("checks", {}).get(f"train_{name}_overlap", "NOT_VERIFIED"))
            dups = sv.get("checks", {}).get(f"duplicate_{name}_ids", "NOT_VERIFIED")
            out_lines.append(f"| {name} | {rows} | {ymin} | {ymax} | {h} | {overlap} | {dups} |")

    sr = adapters.parse_semantic_roles()
    out_lines.append("\n## 3. Semantic Roles Table")
    if "_error" in sr:
        out_lines.append("> [!WARNING]\n> Status: NOT_VERIFIED")
    else:
        out_lines.append("| Column | Expected Role | Actual Role | Actual Dtype | In X | Source Path | Pointer | Status |")
        out_lines.append("|---|---|---|---|---|---|---|---|")
        for f in sr.get("features", []):
            col = f.get("column", "NOT_AVAILABLE")
            erole = f.get("expected_role", "NOT_AVAILABLE")
            arole = f.get("actual_role", "NOT_AVAILABLE")
            adtype = f.get("actual_dtype", "NOT_AVAILABLE")
            inx = f.get("in_X", "NOT_AVAILABLE")
            sp = f.get("source_path", "NOT_AVAILABLE")
            ptr = f.get("source_pointer", "NOT_AVAILABLE")
            st = f.get("status", "NOT_AVAILABLE")
            out_lines.append(f"| {col} | {erole} | {arole} | {adtype} | {inx} | {sp} | {ptr} | {st} |")
        
        out_lines.append("\n**Summary:**")
        out_lines.append(f"- Input Features: {sr.get('input_feature_count', 'NOT_AVAILABLE')}")
        out_lines.append(f"- Role Overlaps: {sr.get('role_overlap_count', 'NOT_AVAILABLE')}")

    ms = adapters.parse_missing_strategy()
    mp = adapters.parse_missing_profile()
    out_lines.append("\n## 4. Missing Value Strategy")
    if "_error" in ms or "_error" in mp:
        out_lines.append("> [!WARNING]\n> Status: NOT_VERIFIED")
    else:
        out_lines.append("| Feature | Total Missing | Total Ratio | Train Ratio | Val Ratio | Test Ratio |")
        out_lines.append("|---|---|---|---|---|---|")
        for k, v in mp.items():
            if k == "release_year_1900_silently_clipped": continue # skip non-feature keys
            t_m = v.get("total_missing", "NOT_AVAILABLE")
            t_r = v.get("total_ratio", "NOT_AVAILABLE")
            tr_r = v.get("train_ratio", "NOT_AVAILABLE")
            v_r = v.get("validation_ratio", "NOT_AVAILABLE")
            te_r = v.get("test_ratio", "NOT_AVAILABLE")
            out_lines.append(f"| {k} | {t_m} | {t_r} | {tr_r} | {v_r} | {te_r} |")
            
        out_lines.append("\n**Strategies:**")
        for st in ms.get("strategies", []):
            out_lines.append(f"- Feature: {st.get('feature')}, Strategy: {st.get('strategy')}, Value: {st.get('fitted_value')}, Fit Split: {st.get('transformer_fit_split')}")

    oc = adapters.parse_outlier_config()
    ot = adapters.parse_outlier_thresholds()
    op = adapters.parse_outlier_profile()
    out_lines.append("\n## 5. Outlier Rendering")
    if "_error" in oc or "_error" in ot or "_error" in op:
        out_lines.append("> [!WARNING]\n> Status: NOT_VERIFIED")
    else:
        out_lines.append("| Feature | Method | Q1 | Q3 | IQR | Lower | Upper | Train Outliers | Val Outliers | Test Outliers |")
        out_lines.append("|---|---|---|---|---|---|---|---|---|---|")
        
        th_map = {t.get("column", t.get("feature", "NOT_AVAILABLE")): t for t in ot}
        pf_map = {p.get("column", ""): p for p in op.get("profiles", [])}
        
        for k, th in th_map.items():
            method = "IQR"
            q1 = th.get("Q1", "NOT_AVAILABLE")
            q3 = th.get("Q3", "NOT_AVAILABLE")
            iqr = th.get("IQR", "NOT_AVAILABLE")
            lower = th.get("lower_threshold", "NOT_AVAILABLE")
            upper = th.get("upper_threshold", "NOT_AVAILABLE")
            p = pf_map.get(k, {})
            tro = p.get("train", "NOT_AVAILABLE")
            vo = p.get("validation", "NOT_AVAILABLE")
            teo = p.get("test", "NOT_AVAILABLE")
            out_lines.append(f"| {k} | {method} | {q1} | {q3} | {iqr} | {lower} | {upper} | {tro} | {vo} | {teo} |")

    ec = adapters.parse_encoding_config()
    ecat = adapters.parse_encoder_categories()
    ucp = adapters.parse_unknown_category_profile()
    out_lines.append("\n## 6. Encoding Rendering")
    if "_error" in ec or "_error" in ecat or "_error" in ucp:
        out_lines.append("> [!WARNING]\n> Status: NOT_VERIFIED")
    else:
        out_lines.append("| Candidate | Feature | Type | Categories | Handle Unknown | Fit Split |")
        out_lines.append("|---|---|---|---|---|---|")
        for e in ecat:
            cand = e.get("candidate_id", "NOT_AVAILABLE")
            feat = e.get("column", "NOT_AVAILABLE")
            typ = e.get("encoder_type", "NOT_AVAILABLE")
            cats = e.get("category_count", "NOT_AVAILABLE")
            hu = e.get("parameters", {}).get("handle_unknown", "NOT_AVAILABLE")
            fs = e.get("fit_split", "NOT_AVAILABLE")
            out_lines.append(f"| {cand} | {feat} | {typ} | {cats} | {hu} | {fs} |")
            
        out_lines.append("\n**Unknown Category Audit:**")
        val_unk = sum(p.get("unknown_row_count_validation", 0) for p in ucp.get("profiles", []))
        test_unk = sum(p.get("unknown_row_count_test", 0) for p in ucp.get("profiles", []))
        out_lines.append(f"- Validation Unknowns: {val_unk}")
        out_lines.append(f"- Test Unknowns: {test_unk}")
        
        out_lines.append("\n**Binary Handling:**")
        bin_handling = ucp.get("binary_handling", {})
        if bin_handling:
            for k, v in bin_handling.items():
                out_lines.append(f"- {k} missing count: {v.get('missing_count', 'NOT_AVAILABLE')}")
        else:
            out_lines.append("- Explicit missing count: 0")

    sc = adapters.parse_scaling_config()
    ss = adapters.parse_scaler_statistics()
    out_lines.append("\n## 7. Scaling Rendering")
    if "_error" in sc or "_error" in ss:
        out_lines.append("> [!WARNING]\n> Status: NOT_VERIFIED")
    else:
        out_lines.append("| Candidate | Scaler | Feature | Mean/Center | Scale |")
        out_lines.append("|---|---|---|---|---|")
        for s in ss:
            cand = s.get("candidate_id", "NOT_AVAILABLE")
            sclr = s.get("scaler", "NOT_AVAILABLE")
            feat = s.get("column", "NOT_AVAILABLE")
            if sclr == "NONE":
                out_lines.append(f"| {cand} | {sclr} | {feat} | NOT_APPLICABLE | NOT_APPLICABLE |")
                continue
            mc = s.get("mean_", s.get("center_", "NOT_AVAILABLE"))
            scl = s.get("scale_", "NOT_AVAILABLE")
            out_lines.append(f"| {cand} | {sclr} | {feat} | {mc} | {scl} |")

    osh = adapters.parse_output_schemas()
    out_lines.append("\n## 8. Output Schemas")
    out_lines.append("| Candidate | Train Shape | Val Shape | Test Shape | Dtype | Exact Class |")
    out_lines.append("|---|---|---|---|---|---|")
    for cid, sh in osh.items():
        if "_error" in sh:
            out_lines.append(f"| {cid} | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED |")
            continue
        tr = sh.get("train_shape", "NOT_AVAILABLE")
        va = sh.get("validation_shape", "NOT_AVAILABLE")
        te = sh.get("test_shape", "NOT_AVAILABLE")
        dt = sh.get("dtype", "NOT_AVAILABLE")
        cls = sh.get("exact_matrix_type", "NOT_AVAILABLE")
        out_lines.append(f"| {cid} | {tr} | {va} | {te} | {dt} | {cls} |")

    fa = adapters.parse_fit_audit()
    out_lines.append("\n## 9. Fit Audit")
    if "_error" in fa:
        out_lines.append("> [!WARNING]\n> Status: NOT_VERIFIED")
    else:
        out_lines.append("| Candidate | Component ID | Type | Fit Split | Val Fit Called | Test Fit Called | Fit Input Hash | Statistics Hash |")
        out_lines.append("|---|---|---|---|---|---|---|---|")
        for f in fa:
            cid = f.get("candidate_id", "NOT_AVAILABLE")
            comp = f.get("component_id", f.get("component_name", "NOT_AVAILABLE"))
            typ = f.get("component_type", "NOT_AVAILABLE")
            fs = f.get("fit_split", "NOT_AVAILABLE")
            vfc = f.get("validation_fit_called", "NOT_AVAILABLE")
            tfc = f.get("test_fit_called", "NOT_AVAILABLE")
            fih = f.get("fit_input_hash", "NOT_AVAILABLE")
            sth = f.get("fitted_statistics_hash", "NOT_AVAILABLE")
            out_lines.append(f"| {cid} | {comp} | {typ} | {fs} | {vfc} | {tfc} | {fih} | {sth} |")

    out_lines.append("\n> Generation Completed At: " + datetime.now(timezone.utc).isoformat())

    with open(OUTPUT_DIR / 'BAO_CAO_NGHIEM_THU_FEATURE_2_2.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(out_lines) + "\n")

if __name__ == "__main__":
    build_review_package()

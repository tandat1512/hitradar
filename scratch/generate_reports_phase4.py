import os, json

REPORT_DIR = r"E:\Dự án 1 hitrada\Output epic2"
LOCAL_DIR = r"E:\Dự án 1 hitrada\hitradar\7.ML\7.9.explainability\local"
DEP_DIR = r"E:\Dự án 1 hitrada\hitradar\7.ML\7.9.explainability\dependence"

def rj(path):
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

# Data
exps = rj(os.path.join(LOCAL_DIR, "local_explanations.json"))
dep_summ = rj(os.path.join(DEP_DIR, "shap_dependence_summary.json"))
local_man = rj(os.path.join(LOCAL_DIR, "local_explanation_manifest.json"))
ck = rj(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.9.explainability\checkpoints", "feature_2_6_phase_4_checkpoint.json"))

# LOCAL_EXPLANATION_REPORT.md
local_report = f"""# Local SHAP Explanation Report (Phase 4/5)
**Model**: EXP24-XGB-FINAL-001
**Total Cases Analyzed**: {local_man['local_case_count']}
**Additivity Pass Rate**: {local_man['additivity_pass_rate'] * 100:.1f}%

## 1. Case Summary
"""
for e in exps[:5]:  # Top 5 to keep it concise
    local_report += f"### {e['case_id']} ({e['category']})\n"
    local_report += f"- **Track ID**: {e['track_id']}\n"
    local_report += f"- **Prediction**: {e['y_pred_raw']:.4f} (True: {e['y_true']:.4f})\n"
    local_report += f"- **Interpretation**: {e['interpretation']}\n\n"

with open(os.path.join(REPORT_DIR, "LOCAL_EXPLANATION_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(local_report)

# DEPENDENCE_PLOTS_REPORT.md
dep_report = f"""# SHAP Dependence & Category Contribution Report (Phase 4/5)
**Sample Size**: 5000 canonical

## 1. Analyzed Features
"""
for d in dep_summ:
    dep_report += f"### Feature: {d['feature']}\n"
    dep_report += f"- **Observed**: {d['observed_association']}\n"
    dep_report += f"- **Disclaimer**: {d['interpretation_limitation']}\n\n"

with open(os.path.join(REPORT_DIR, "DEPENDENCE_PLOTS_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(dep_report)

# FEATURE_2_6_PHASE_4_REPORT.md
phase4_report = f"""# Feature 2.6 Phase 4 Summary Report
**Phase**: 4/5 (Local Explanation & Dependence Plots)
**Champion**: EXP24-XGB-FINAL-001
**Status**: {ck['phase_status']}

## 1. Execution Evidence
- Local cases selected deterministically: {ck['local_case_policy_valid']} ({ck['local_case_count']} cases)
- Local additivity valid: {ck['local_additivity_complete']} (Rate: {ck['local_additivity_pass_rate']*100}%)
- Waterfall plots generated: {ck['local_plot_count']}
- Dependence features generated: {ck['dependence_feature_count']}
- Global SHAP recomputed: {ck['global_shap_recomputed']}
- Causal claims made: NO

## 2. Next Steps
Proceed to Phase 5: SHAP Serving Integration & Artifact Manifest Closure.
"""
with open(os.path.join(REPORT_DIR, "FEATURE_2_6_PHASE_4_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(phase4_report)

print("Markdown reports generated successfully in Output epic2.")

import os
import json

files = [
    r"Output epic2\F 2.5\BAO_CAO_NGHIEM_THU_FEATURE_2_5.md",
    r"Output epic2\F 2.5\BUSINESS_METRICS_REPORT.md",
    r"Output epic2\F 2.5\FEATURE_2_5_PHASE_1_REPORT.md",
    r"Output epic2\F 2.5\FEATURE_2_5_PHASE_2_REPORT.md",
    r"Output epic2\F 2.5\FEATURE_2_5_PHASE_3_REPORT.md",
    r"Output epic2\F 2.5\FEATURE_2_5_PHASE_4_REPORT.md",
    r"Output epic2\F 2.5\FINAL_TEST_EVALUATION_REPORT.md",
    r"Output epic2\F 2.5\POPULARITY_BUCKET_ERROR_REPORT.md",
    r"Output epic2\F 2.5\RESIDUAL_ANALYSIS_REPORT.md",
    r"Output epic2\F 2.5\TEMPORAL_ROBUSTNESS_REPORT.md",
    r"Output epic2\BAO_CAO_NGHIEM_THU_FEATURE_2_6.md",
    r"Output epic2\CLOSURE_GATE_REPORT_FEATURE_2_6.md",
    r"Output epic2\DEPENDENCE_PLOTS_REPORT.md",
    r"Output epic2\EXPLAIN_ONE_PREDICTION_REPORT.md",
    r"Output epic2\FEATURE_2_6_COMPLETION_REPORT.md",
    r"Output epic2\FEATURE_2_6_INPUT_REPORT.md",
    r"Output epic2\FEATURE_2_6_PHASE_1_REPORT.md",
    r"Output epic2\FEATURE_2_6_PHASE_2_REPORT.md",
    r"Output epic2\FEATURE_2_6_PHASE_3_REPORT.md",
    r"Output epic2\FEATURE_2_6_PHASE_4_REPORT.md",
    r"Output epic2\FEATURE_2_6_VALIDATION_REPORT.md",
    r"Output epic2\GLOBAL_EXPLANATION_REPORT.md",
    r"Output epic2\LOCAL_EXPLANATION_REPORT.md",
    r"Output epic2\SHAP_BACKGROUND_REPORT.md",
    r"Output epic2\SHAP_COMPUTATION_REPORT.md"
]

res = {}
base = r"E:\Dự án 1 hitrada"
for f in files:
    p = os.path.join(base, f)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as file:
            res[f] = file.read()
    else:
        res[f] = "MISSING"

with open(r"E:\Dự án 1 hitrada\hitradar\scratch\all_reports.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

lengths = {k: len(v) for k, v in res.items()}
print("Total files:", len(res))
print("Total characters:", sum(lengths.values()))

import os, json, pytest, glob
import pandas as pd
import numpy as np

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EXP_DIR = os.path.join(REPO_ROOT, "7.ML", "7.9.explainability")
LOCAL_DIR = os.path.join(EXP_DIR, "local")
DEP_DIR = os.path.join(EXP_DIR, "dependence")

def get_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_local_case_selection_matches_policy_limit():
    cases = get_json(os.path.join(LOCAL_DIR, "local_explanation_case_selection.json"))
    assert len(cases) > 0, "No local cases selected"
    assert len(cases) <= 27, f"Expected at most 27 cases, got {len(cases)}"
    
    # Check deterministic selection properties
    categories = [c["category"] for c in cases]
    assert "largest_absolute_error" in categories
    assert len(set(categories)) >= 2, "Should have multiple categories of local cases"

def test_all_selected_cases_exist_in_test_set():
    cases = get_json(os.path.join(LOCAL_DIR, "local_explanation_case_selection.json"))
    track_ids = {c["track_id"] for c in cases}
    
    df_preds = pd.read_parquet(os.path.join(REPO_ROOT, "7.ML", "7.8.model_evaluation", "predictions", "final_test_predictions.parquet"))
    test_track_ids = set(df_preds["track_id"].values)
    
    missing = track_ids - test_track_ids
    assert len(missing) == 0, f"Cases not in test set: {missing}"

def test_local_additivity_tolerance():
    add_val = get_json(os.path.join(LOCAL_DIR, "local_additivity_validation.json"))
    assert len(add_val) > 0, "No additivity validation found"
    
    failures = []
    for r in add_val:
        if not r["within_tolerance"] or r["reconstruction_error"] >= 1e-4:
            failures.append(f"{r['track_id']} error {r['reconstruction_error']}")
            
    assert len(failures) == 0, f"Additivity failures: {failures}"

def test_waterfall_assets_exist():
    manifest = get_json(os.path.join(LOCAL_DIR, "local_plot_manifest.json"))
    assert len(manifest) > 0, "No waterfall manifest"
    
    for item in manifest:
        assert os.path.exists(item["path"]), f"Plot missing: {item['path']}"
        assert item["bytes"] > 0, "Plot file empty"

def test_grouped_contributions_map():
    df_long = pd.read_csv(os.path.join(LOCAL_DIR, "local_contributions_long.csv"))
    df_grouped = pd.read_csv(os.path.join(LOCAL_DIR, "local_grouped_contributions.csv"))
    
    assert len(df_long) > 0
    assert len(df_grouped) > 0
    
    # Check that grouped sums match raw sums approximately
    case_sums_long = df_long.groupby("case_id")["shap_value"].sum().to_dict()
    case_sums_grouped = df_grouped.groupby("case_id")["grouped_shap_value"].sum().to_dict()
    
    for case_id in case_sums_long:
        diff = abs(case_sums_long[case_id] - case_sums_grouped.get(case_id, 0.0))
        assert diff < 1e-4, f"Grouping sum mismatch for {case_id}: diff {diff}"

def test_shap_interpretation_text_format():
    exps = get_json(os.path.join(LOCAL_DIR, "local_explanations.json"))
    assert len(exps) > 0, "No explanations found"
    
    causal_words = ["cause", "gây ra", "makes", "changes", "tạo ra sai số"]
    
    for exp in exps:
        interp = exp["interpretation"].lower()
        for w in causal_words:
            assert w not in interp, f"Found causal word '{w}' in interpretation: {interp}"
        assert "chứng minh" in interp or "giải thích" in interp, "Required non-causal disclaimer missing"

def test_dependence_features_selected_from_top():
    dep_sel = get_json(os.path.join(DEP_DIR, "dependence_feature_selection.json"))
    assert len(dep_sel) > 0, "No dependence features selected"
    assert len(dep_sel) <= 8, f"Too many dependence features: {len(dep_sel)}"
    
    df_global = pd.read_csv(os.path.join(EXP_DIR, "global", "shap_global_importance_selected.csv"))
    top10 = df_global.head(10)["selected_feature"].tolist()
    
    for f in dep_sel:
        assert f["feature"] in top10, f"Dependence feature {f['feature']} not in global top 10"

def test_dependence_plots_generated():
    manifest = get_json(os.path.join(DEP_DIR, "shap_dependence_manifest.json"))
    assert manifest["plots_generated"] > 0
    
    summary = get_json(os.path.join(DEP_DIR, "shap_dependence_summary.json"))
    assert len(summary) > 0
    
    for p in summary:
        path = p["plot_path"]
        assert os.path.exists(path), f"Dependence plot missing: {path}"
        assert os.path.getsize(path) > 0, "Plot file empty"
        assert "causality" in p["interpretation_limitation"] or "causal" in p["interpretation_limitation"], "Disclaimer missing"

def test_local_consistency_manifest():
    consist = get_json(os.path.join(LOCAL_DIR, "phase_4_explanation_consistency_check.json"))
    assert consist["local_case_count_matches"]
    assert consist["no_duplicates"]
    assert consist["additivity_valid"]
    assert consist["plot_count_matches"]
    assert not consist["global_shap_recomputed"]
    assert consist["overall_consistent"]

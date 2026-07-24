"""Tests for Feature 2.6 Phase 3 — Global SHAP Explanation."""
import os, json, pytest, subprocess, hashlib
import numpy as np, pandas as pd

REPO_ROOT = subprocess.check_output("git rev-parse --show-toplevel", shell=True).decode().strip()
EXP = os.path.join(REPO_ROOT, "7.ML", "7.9.explainability")
G = os.path.join(EXP, "global")
SV = os.path.join(EXP, "shap_values")
CK = os.path.join(EXP, "checkpoints")

def rj(p):
    with open(p, "r", encoding="utf-8") as f: return json.load(f)
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8192), b""): h.update(b)
    return h.hexdigest()

# ── Source validation ────────────────────────────────────────────────
class TestGlobalSource:
    def test_source_hash_unchanged(self):
        d = rj(os.path.join(G, "global_explanation_source_validation.json"))
        assert d["hash_matches_manifest"] is True
    def test_immutable(self):
        d = rj(os.path.join(G, "global_explanation_source_validation.json"))
        assert d["immutable"] is True
    def test_no_recomputation(self):
        ck = rj(os.path.join(CK, "feature_2_6_phase_3_checkpoint.json"))
        assert ck["shap_recomputed"] is False

# ── Importance tables ────────────────────────────────────────────────
class TestGlobalImportance:
    def test_transformed_csv_exists(self):
        assert os.path.exists(os.path.join(G, "shap_global_importance_transformed.csv"))
    def test_importance_count_matches(self):
        df = pd.read_csv(os.path.join(G, "shap_global_importance_transformed.csv"))
        assert len(df) == 49
    def test_no_nan_importance(self):
        df = pd.read_csv(os.path.join(G, "shap_global_importance_transformed.csv"))
        assert df["mean_abs_shap"].isna().sum() == 0
    def test_no_inf_importance(self):
        df = pd.read_csv(os.path.join(G, "shap_global_importance_transformed.csv"))
        assert not np.isinf(df["mean_abs_shap"]).any()
    def test_ranking_deterministic(self):
        df = pd.read_csv(os.path.join(G, "shap_global_importance_transformed.csv"))
        assert list(df["rank"]) == list(range(1, 50))

# ── Grouped importance ───────────────────────────────────────────────
class TestGroupedImportance:
    def test_selected_csv_exists(self):
        assert os.path.exists(os.path.join(G, "shap_global_importance_selected.csv"))
    def test_raw_family_csv_exists(self):
        assert os.path.exists(os.path.join(G, "shap_global_importance_raw_family.csv"))
    def test_no_duplicate_groups(self):
        df = pd.read_csv(os.path.join(G, "shap_global_importance_selected.csv"))
        assert len(df["selected_feature"].unique()) == len(df)

# ── Importance shares ────────────────────────────────────────────────
class TestImportanceShares:
    def test_shares_sum_to_one_transformed(self):
        df = pd.read_csv(os.path.join(G, "shap_global_importance_transformed.csv"))
        assert abs(df["importance_share"].sum() - 1.0) < 0.001
    def test_shares_sum_to_one_selected(self):
        df = pd.read_csv(os.path.join(G, "shap_global_importance_selected.csv"))
        assert abs(df["importance_share"].sum() - 1.0) < 0.001

# ── Bar plots ────────────────────────────────────────────────────────
class TestGlobalBarPlots:
    def test_bar_transformed_exists(self):
        p = os.path.join(G, "shap_summary_bar_transformed.png")
        assert os.path.exists(p) and os.path.getsize(p) > 0
    def test_bar_selected_exists(self):
        p = os.path.join(G, "shap_summary_bar_selected.png")
        assert os.path.exists(p) and os.path.getsize(p) > 0
    def test_bar_raw_exists(self):
        p = os.path.join(G, "shap_summary_bar_raw_family.png")
        assert os.path.exists(p) and os.path.getsize(p) > 0

# ── Beeswarm ─────────────────────────────────────────────────────────
class TestBeeswarm:
    def test_beeswarm_exists(self):
        p = os.path.join(G, "shap_summary_beeswarm.png")
        assert os.path.exists(p) and os.path.getsize(p) > 0

# ── Global summary ───────────────────────────────────────────────────
class TestGlobalSummary:
    def test_summary_exists(self):
        assert os.path.exists(os.path.join(G, "global_explanation_summary.json"))
    def test_top_features_match_csv(self):
        s = rj(os.path.join(G, "global_explanation_summary.json"))
        df = pd.read_csv(os.path.join(G, "shap_global_importance_transformed.csv"))
        assert s["top_5_transformed"][0]["transformed_feature"] == df.iloc[0]["transformed_feature"]
    def test_no_causal_claims(self):
        s = rj(os.path.join(G, "global_explanation_summary.json"))
        assert "no_causality_statement" in s
        assert "causal" in s["no_causality_statement"].lower()

# ── Governance ───────────────────────────────────────────────────────
class TestPhase3Governance:
    def test_no_training(self):
        ck = rj(os.path.join(CK, "feature_2_6_phase_3_checkpoint.json"))
        assert ck["training_executed"] is False
    def test_no_tuning(self):
        ck = rj(os.path.join(CK, "feature_2_6_phase_3_checkpoint.json"))
        assert ck["tuning_executed"] is False
    def test_champion_unchanged(self):
        manifest = rj(os.path.join(SV, "canonical_shap_values_manifest.json"))
        assert manifest["champion_id"] == "EXP24-XGB-FINAL-001"
    def test_consistency_valid(self):
        c = rj(os.path.join(G, "global_explanation_consistency_check.json"))
        assert c["overall_consistent"] is True

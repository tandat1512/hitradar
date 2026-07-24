"""Tests for Feature 2.6 Phase 1 — All 10 test modules combined."""
import os, json, pytest, hashlib, subprocess, numpy as np, pandas as pd

REPO_ROOT = subprocess.check_output("git rev-parse --show-toplevel", shell=True).decode().strip()
EXP_DIR = os.path.join(REPO_ROOT, "7.ML", "7.9.explainability")
EVAL_DIR = os.path.join(REPO_ROOT, "7.ML", "7.8.model_evaluation")
MT_DIR = os.path.join(REPO_ROOT, "7.ML", "7.7.model_training")
FE_DIR = os.path.join(REPO_ROOT, "7.ML", "7.6.feature_engineering")
M = os.path.join(EXP_DIR, "manifests")
C = os.path.join(EXP_DIR, "configs")
CK = os.path.join(EXP_DIR, "checkpoints")
BG = os.path.join(EXP_DIR, "background")

def rj(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(8192), b""):
            h.update(blk)
    return h.hexdigest()

# ── test_feature_2_6_input_contract ──────────────────────────────────
class TestInputContract:
    def test_f25_gate_valid(self):
        d = rj(os.path.join(M, "feature_2_5_handoff_gate_validation.json"))
        assert d["gate_valid"] is True

    def test_source_feature(self):
        d = rj(os.path.join(M, "feature_2_6_input_validation.json"))
        assert d["source_feature"] == "2.5"

    def test_explainability_owner(self):
        d = rj(os.path.join(M, "feature_2_6_input_validation.json"))
        assert d["explainability_owner"] == "Feature 2.6"

    def test_shap_not_started(self):
        d = rj(os.path.join(M, "feature_2_6_input_validation.json"))
        assert d["shap_status"] == "NOT_STARTED"

    def test_model_selection_locked(self):
        d = rj(os.path.join(M, "feature_2_6_input_validation.json"))
        assert d["model_selection_locked"] is True

# ── test_feature_2_6_champion_identity ───────────────────────────────
class TestChampionIdentity:
    def test_champion_id(self):
        d = rj(os.path.join(M, "champion_explainability_identity_validation.json"))
        assert d["champion_model_id"] == "EXP24-XGB-FINAL-001"

    def test_artifact_exists(self):
        d = rj(os.path.join(M, "champion_explainability_identity_validation.json"))
        assert d["artifact_exists"] is True

    def test_hash_consistent_with_f25(self):
        d = rj(os.path.join(M, "champion_explainability_identity_validation.json"))
        assert d["hash_f25_lock_vs_alias"] is True

    def test_no_identity_conflict(self):
        d = rj(os.path.join(M, "champion_explainability_identity_validation.json"))
        assert d["identity_conflict"] is False

# ── test_feature_2_6_champion_lock ───────────────────────────────────
class TestChampionLock:
    def test_training_not_allowed(self):
        d = rj(os.path.join(M, "champion_explainability_lock.json"))
        assert d["training_allowed"] is False

    def test_tuning_not_allowed(self):
        d = rj(os.path.join(M, "champion_explainability_lock.json"))
        assert d["tuning_allowed"] is False

    def test_reselection_not_allowed(self):
        d = rj(os.path.join(M, "champion_explainability_lock.json"))
        assert d["model_reselection_allowed"] is False

    def test_modification_not_allowed(self):
        d = rj(os.path.join(M, "champion_explainability_lock.json"))
        assert d["artifact_modification_allowed"] is False

# ── test_feature_2_6_dimensions ──────────────────────────────────────
class TestDimensions:
    def test_bundle_input_recorded(self):
        d = rj(os.path.join(M, "feature_2_6_dimension_contract.json"))
        assert d["bundle_input_feature_count"] > 0

    def test_selected_count_recorded(self):
        d = rj(os.path.join(M, "feature_2_6_dimension_contract.json"))
        assert d["selected_engineered_feature_count"] > 0

    def test_matrix_width_recorded(self):
        d = rj(os.path.join(M, "feature_2_6_dimension_contract.json"))
        assert d["model_matrix_width"] > 0

    def test_feature_names_available(self):
        d = rj(os.path.join(M, "feature_2_6_dimension_contract.json"))
        assert d["feature_names_available"] is True

# ── test_feature_2_6_feature_names ───────────────────────────────────
class TestFeatureNames:
    def test_count_matches_width(self):
        names = rj(os.path.join(M, "transformed_feature_names.json"))
        dim = rj(os.path.join(M, "feature_2_6_dimension_contract.json"))
        assert len(names) == dim["model_matrix_width"]

    def test_no_empty_names(self):
        names = rj(os.path.join(M, "transformed_feature_names.json"))
        assert all(len(n) > 0 for n in names)

    def test_no_duplicate_names(self):
        names = rj(os.path.join(M, "transformed_feature_names.json"))
        assert len(names) == len(set(names))

# ── test_feature_2_6_train_source ────────────────────────────────────
class TestTrainSource:
    def test_source_valid(self):
        d = rj(os.path.join(M, "shap_train_source_validation.json"))
        assert d["valid"] is True

    def test_split_label(self):
        d = rj(os.path.join(M, "shap_train_source_validation.json"))
        assert d["split_label"] == "train"

    def test_has_rows(self):
        d = rj(os.path.join(M, "shap_train_source_validation.json"))
        assert d["rows"] > 0

# ── test_feature_2_6_background_sample ───────────────────────────────
class TestBackgroundSample:
    def test_raw_exists(self):
        assert os.path.exists(os.path.join(BG, "shap_background_raw.parquet"))

    def test_actual_rows(self):
        m = rj(os.path.join(M, "shap_background_manifest.json"))
        assert m["raw_rows"] == 1000

    def test_target_excluded(self):
        df = pd.read_parquet(os.path.join(BG, "shap_background_raw.parquet"))
        assert "target_popularity" not in df.columns

    def test_identifier_excluded(self):
        df = pd.read_parquet(os.path.join(BG, "shap_background_raw.parquet"))
        assert "track_id" not in df.columns

# ── test_feature_2_6_background_train_only ───────────────────────────
class TestBackgroundTrainOnly:
    def test_no_validation_overlap(self):
        d = rj(os.path.join(M, "shap_background_distribution.json"))
        assert d["validation_overlap_count"] == 0

    def test_no_test_overlap(self):
        d = rj(os.path.join(M, "shap_background_distribution.json"))
        assert d["test_overlap_count"] == 0

    def test_train_only_verified(self):
        d = rj(os.path.join(M, "shap_background_distribution.json"))
        assert d["train_only_verification"] is True

# ── test_feature_2_6_background_transform ────────────────────────────
class TestBackgroundTransform:
    def test_transformed_exists(self):
        npy = os.path.join(BG, "shap_background_transformed.npy")
        npz = os.path.join(BG, "shap_background_transformed.npz")
        assert os.path.exists(npy) or os.path.exists(npz)

    def test_rows_match_raw(self):
        m = rj(os.path.join(M, "shap_background_manifest.json"))
        assert m["rows_match"] is True

    def test_columns_match_width(self):
        m = rj(os.path.join(M, "shap_background_manifest.json"))
        assert m["columns_match_model_matrix_width"] is True

    def test_no_nan(self):
        m = rj(os.path.join(M, "shap_background_manifest.json"))
        assert m["has_nan"] is False

    def test_no_inf(self):
        m = rj(os.path.join(M, "shap_background_manifest.json"))
        assert m["has_inf"] is False

# ── test_feature_2_6_phase_1_governance ──────────────────────────────
class TestPhase1Governance:
    def test_no_training(self):
        ck = rj(os.path.join(CK, "feature_2_6_phase_1_checkpoint.json"))
        assert ck["training_executed"] is False

    def test_no_tuning(self):
        ck = rj(os.path.join(CK, "feature_2_6_phase_1_checkpoint.json"))
        assert ck["tuning_executed"] is False

    def test_no_model_reselection(self):
        ck = rj(os.path.join(CK, "feature_2_6_phase_1_checkpoint.json"))
        assert ck["model_reselected"] is False

    def test_shap_not_computed(self):
        ck = rj(os.path.join(CK, "feature_2_6_phase_1_checkpoint.json"))
        assert ck["shap_values_computed"] is False

    def test_seed_locked(self):
        cfg = rj(os.path.join(C, "feature_2_6_shap_config.json"))
        assert cfg["random_state"] == 42

    def test_champion_locked(self):
        ck = rj(os.path.join(CK, "feature_2_6_phase_1_checkpoint.json"))
        assert ck["champion_locked"] is True

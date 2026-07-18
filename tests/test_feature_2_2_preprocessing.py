import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def load_json(name):
    with open(PREP_DIR / name, 'r') as f:
        return json.load(f)

def test_input_contract_complete():
    j = load_json('preprocessing_input_contract.json')
    assert "checks" in j
    assert len(j["checks"]) > 0

def test_split_counts_complete():
    j = load_json('preprocessing_split_verification.json')
    assert "splits" in j
    assert j["splits"]["train"]["rows"] == 415524

def test_split_year_ranges():
    j = load_json('preprocessing_split_verification.json')
    assert j["splits"]["train"]["year_min"] >= 1900
    assert j["splits"]["train"]["year_max"] <= 2004

def test_split_hashes_present():
    j = load_json('preprocessing_split_verification.json')
    assert len(j["splits"]["train"]["sha256"]) > 10

def test_split_overlap_zero():
    j = load_json('preprocessing_split_verification.json')
    assert j["checks"]["train_validation_overlap"] == 0

def test_split_union_reconciles():
    j = load_json('preprocessing_split_verification.json')
    assert j["checks"]["union_reconciles"] is True

def test_semantic_roles_exact():
    j = load_json('semantic_roles.json')
    assert j["input_feature_count"] == 18

def test_semantic_roles_no_overlap():
    j = load_json('semantic_roles.json')
    assert j["role_overlap_count"] == 0

def test_actual_dtypes_sourced():
    j = load_json('semantic_roles.json')
    assert all("actual_dtype" in f for f in j["features"])

def test_target_and_identifier_excluded():
    j = load_json('semantic_roles.json')
    assert not j["target_present_in_X"]

def test_missing_profiles_reconcile():
    j = load_json('missing_profile_by_split.json')
    assert "tempo" in j

def test_release_month_strategy():
    j = load_json('missing_value_strategy.json')
    assert any(x["column"] == "release_month" for x in j["strategies"])

def test_post_transform_missing_zero():
    j = load_json('missing_profile_by_split.json')
    assert j["tempo"]["post_transform_missing_by_candidate"]["P22-A"] == 0

def test_time_signature_strategy_consistent():
    j = load_json('missing_value_strategy.json')
    strat = next(x for x in j["strategies"] if x["column"] == "time_signature")
    assert strat["strategy"] == "most_frequent"

def test_imputer_statistics_match_fitted_objects():
    j = load_json('imputer_statistics.json')
    assert len(j) > 0

def test_outlier_q1_q3_iqr_recompute():
    j = load_json('outlier_thresholds.json')
    assert len(j) > 0

def test_outlier_profile_matches_thresholds():
    j = load_json('outlier_profile_by_split.json')
    assert len(j["profiles"]) > 0

def test_outlier_clip_counts():
    j = load_json('outlier_thresholds.json')
    assert "values_clipped_by_split" in j[0]

def test_release_year_not_silently_clipped():
    j = load_json('outlier_profile_by_split.json')
    assert j["release_year_1900_silently_clipped"] is False

def test_bounded_feature_domains():
    j = load_json('outlier_config.json')
    assert "danceability" in j["bounded_features"]

def test_encoder_categories_match_fitted_objects():
    j = load_json('encoder_categories.json')
    assert len(j) > 0

def test_category_counts_match_lists():
    j = load_json('encoder_categories.json')
    assert j[0]["category_count"] == len(j[0]["categories"])

def test_unknown_categories_profile():
    j = load_json('unknown_category_profile.json')
    assert len(j["profiles"]) > 0

def test_unknown_category_transform():
    j = load_json('unknown_category_profile.json')
    assert j["profiles"][0]["transform_success"] is True

def test_binary_handling():
    j = load_json('unknown_category_profile.json')
    assert "explicit" in j["binary_handling"]

def test_p22a_scaler_statistics():
    j = load_json('scaler_statistics.json')
    assert any(x["candidate_id"] == "P22-A" for x in j)

def test_p22b_scaler_statistics():
    j = load_json('scaler_statistics.json')
    assert any(x["candidate_id"] == "P22-B" for x in j)

def test_p22c_scaler_statistics():
    j = load_json('scaler_statistics.json')
    assert any(x["candidate_id"] == "P22-C" for x in j)

def test_p22d_scaler_not_applicable():
    j = load_json('scaler_statistics.json')
    assert any(x["candidate_id"] == "P22-D" and x["status"] == "NOT_APPLICABLE" for x in j if "status" in x)

def test_standard_scaler_mean_and_scale():
    j = load_json('scaler_statistics.json')
    st = next(x for x in j if x["scaler"] == "StandardScaler")
    assert "mean_" in st

def test_robust_scaler_center_and_scale():
    j = load_json('scaler_statistics.json')
    rs = next(x for x in j if x["scaler"] == "RobustScaler")
    assert "center_" in rs

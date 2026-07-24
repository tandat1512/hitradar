import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
EVAL_DIR = os.path.join(BASE_DIR, '7.ML', '7.8.model_evaluation')

def read_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def test_source_prediction_artifact_valid():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("source_prediction_artifact_valid") is True

def test_no_full_test_prediction():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("full_test_model_prediction_executed") is False

def test_residual_formula_valid():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("residual_formula_valid") is True

def test_residual_metric_consistency_valid():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("residual_metric_consistency_valid") is True

def test_residual_statistics_complete():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("residual_statistics_complete") is True

def test_error_magnitude_analysis_complete():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("error_magnitude_analysis_complete") is True

def test_largest_error_cases_complete():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("largest_error_cases_complete") is True

def test_feature_context_join_complete():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("feature_context_join_complete") is True

def test_figures_complete():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("figures_complete") is True

def test_no_shap_executed():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("shap_executed") is False

def test_no_training_tuning():
    chk3 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_3_checkpoint.json'))
    assert chk3.get("training_executed") is False
    assert chk3.get("tuning_executed") is False
    assert chk3.get("champion_changed") is False

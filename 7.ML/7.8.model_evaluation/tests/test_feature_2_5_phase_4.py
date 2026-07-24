import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
EVAL_DIR = os.path.join(BASE_DIR, '7.ML', '7.8.model_evaluation')

def read_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def test_source_prediction_valid():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("source_prediction_valid") is True
    assert chk4.get("source_prediction_unchanged") is True

def test_no_full_test_prediction():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("full_test_model_prediction_executed") is False

def test_temporal_robustness_complete():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("temporal_robustness_complete") is True

def test_bucket_rows_match_test_rows():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("bucket_rows_match_test_rows") is True

def test_regression_to_mean_complete():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("regression_to_mean_analysis_complete") is True

def test_bucket_confusion_complete():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("bucket_confusion_complete") is True

def test_cross_slice_complete():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("cross_slice_complete") is True

def test_figures_complete():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("figures_complete") is True

def test_consistency_check_valid():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("consistency_check_valid") is True

def test_no_training_tuning():
    chk4 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_4_checkpoint.json'))
    assert chk4.get("training_executed") is False
    assert chk4.get("tuning_executed") is False
    assert chk4.get("champion_changed") is False

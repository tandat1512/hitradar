import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
EVAL_DIR = os.path.join(BASE_DIR, '7.ML', '7.8.model_evaluation')

def read_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def test_feature_2_4_gate():
    chk1 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_1_checkpoint.json'))
    assert chk1.get("feature_2_4_gate_valid") is True

def test_champion_lock():
    lock = read_json(os.path.join(EVAL_DIR, 'configs', 'champion_lock_manifest.json'))
    assert lock.get("champion_locked") is True
    assert lock.get("locked_before_test_labels") is True

def test_evaluation_configs():
    assert read_json(os.path.join(EVAL_DIR, 'configs', 'test_evaluation_lock.json')).get("all_evaluation_rules_locked") is True
    assert read_json(os.path.join(EVAL_DIR, 'configs', 'feature_2_5_metric_contract.json')).get("locked") is True

def test_test_opening_manifest():
    mani = read_json(os.path.join(EVAL_DIR, 'manifests', 'test_feature_opening_manifest.json'))
    assert mani.get("test_features_opened") is True
    assert mani.get("test_labels_accessed") is False

def test_no_prediction_generated():
    chk1 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_1_checkpoint.json'))
    assert chk1.get("test_full_prediction_generated") is False
    assert chk1.get("test_metrics_computed") is False

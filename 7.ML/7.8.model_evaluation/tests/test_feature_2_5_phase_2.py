import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
EVAL_DIR = os.path.join(BASE_DIR, '7.ML', '7.8.model_evaluation')

def read_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def test_champion_unchanged():
    chk2 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_2_checkpoint.json'))
    assert chk2.get("champion_artifact_hash_unchanged") is True
    assert chk2.get("champion_changed") is False

def test_evaluation_lock_unchanged():
    chk2 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_2_checkpoint.json'))
    assert chk2.get("evaluation_lock_unchanged") is True

def test_label_unseal_occurred():
    mani = read_json(os.path.join(EVAL_DIR, 'manifests', 'test_label_unseal_manifest.json'))
    assert mani.get("test_labels_accessed") is True

def test_no_training_tuning():
    chk2 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_2_checkpoint.json'))
    assert chk2.get("training_executed") is False
    assert chk2.get("tuning_executed") is False

def test_canonical_prediction_exists():
    chk2 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_2_checkpoint.json'))
    assert chk2.get("test_prediction_complete") is True
    assert chk2.get("canonical_full_test_generation_count") == 1

def test_no_nan_inf():
    chk2 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_2_checkpoint.json'))
    assert chk2.get("no_nan_predictions") is True
    assert chk2.get("no_inf_predictions") is True

def test_metric_recomputation_match():
    chk2 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_2_checkpoint.json'))
    assert chk2.get("metric_recomputation_valid") is True

def test_runner_up_not_evaluated():
    chk2 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_2_checkpoint.json'))
    assert chk2.get("runner_up_test_evaluation_executed") is False

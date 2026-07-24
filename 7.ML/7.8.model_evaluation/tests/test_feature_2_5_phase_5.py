import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
EVAL_DIR = os.path.join(BASE_DIR, '7.ML', '7.8.model_evaluation')
MT_DIR = os.path.join(BASE_DIR, '7.ML', '7.7.model_training')

def read_json(path):
    if not os.path.exists(path): return {}
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def test_phase_audit():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("phase_1_audit_valid") is True
    assert chk5.get("phase_2_audit_valid") is True
    assert chk5.get("phase_3_audit_valid") is True
    assert chk5.get("phase_4_audit_valid") is True

def test_raw_prediction_unchanged():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("source_raw_prediction_unchanged") is True

def test_postprocessing_complete():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("postprocessing_complete") is True

def test_raw_metrics_preserved():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("raw_metrics_preserved") is True

def test_uncertainty_source_valid():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("uncertainty_source_valid") is True
    assert chk5.get("uncertainty_source") == "VALIDATION"

def test_interval_coverage_complete():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("interval_80_complete") is True
    assert chk5.get("interval_90_complete") is True
    assert chk5.get("interval_coverage_complete") is True

def test_final_prediction_artifact_valid():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("final_prediction_artifact_valid") is True

def test_feature_2_6_contract_complete():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("feature_2_6_contract_complete") is True
    contract = read_json(os.path.join(MT_DIR, 'configs', 'feature_2_6_input_contract.json'))
    assert contract.get("model_selection_locked") is True

def test_closure_gate():
    gate = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_closure_gate.json'))
    assert gate.get("feature_2_5_status") == "PASS"
    assert gate.get("feature_2_5_decision") == "ELIGIBLE_FOR_CLOSURE"
    assert gate.get("feature_2_6_gate") == "MAY_BEGIN"

def test_no_training_tuning():
    chk5 = read_json(os.path.join(EVAL_DIR, 'checkpoints', 'feature_2_5_phase_5_checkpoint.json'))
    assert chk5.get("training_executed") is False
    assert chk5.get("tuning_executed") is False
    assert chk5.get("champion_changed") is False

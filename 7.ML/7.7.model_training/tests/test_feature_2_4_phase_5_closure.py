import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
configs_dir = os.path.join(BASE_DIR, 'configs')
metrics_dir = os.path.join(BASE_DIR, 'metrics')
manifests_dir = os.path.join(BASE_DIR, 'manifests')
checkpoints_dir = os.path.join(BASE_DIR, 'session_checkpoints')
registries_dir = os.path.join(BASE_DIR, 'registries')
models_dir = os.path.join(BASE_DIR, 'models')

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def test_champion_selected():
    dec = read_json(os.path.join(configs_dir, 'best_model_decision.json'))
    assert dec['champion_family'] == 'XGBoost'
    assert dec['runner_up_family'] == 'RandomForest'

def test_closure_gate():
    gate = read_json(os.path.join(configs_dir, 'feature_2_4_closure_gate.json'))
    assert gate['feature_2_4_status'] == 'PASS_WITH_WARNINGS'
    assert gate['feature_2_4_decision'] == 'ELIGIBLE_FOR_CLOSURE'
    assert gate['feature_2_5_gate'] == 'MAY_BEGIN'
    assert gate['test_accessed'] is False

def test_feature_2_5_contract():
    con = read_json(os.path.join(configs_dir, 'feature_2_5_input_contract.json'))
    assert con['test_status'] == 'LOCKED_UNTIL_FEATURE_2_5'
    assert con['test_features_accessed_in_feature_2_4'] is False
    assert con['selected_feature_count'] == 31
    assert con['raw_input_feature_count'] == 18

def test_experiment_registry_flags():
    reg = read_json(os.path.join(registries_dir, 'experiment_registry.json'))
    champs = [r for r in reg if r.get('selected_as_champion')]
    runners = [r for r in reg if r.get('selected_as_runner_up')]
    assert len(champs) == 1
    assert len(runners) == 1

def test_champion_bundle_exists():
    assert os.path.exists(os.path.join(models_dir, 'champion_bundle.joblib'))

def test_runner_up_bundle_exists():
    assert os.path.exists(os.path.join(models_dir, 'runner_up_bundle.joblib'))

def test_champion_roundtrip():
    r = read_json(os.path.join(metrics_dir, 'champion_roundtrip_results.json'))
    assert r['pass'] is True

def test_runner_up_roundtrip():
    r = read_json(os.path.join(metrics_dir, 'runner_up_roundtrip_results.json'))
    assert r['pass'] is True

def test_checkpoint_phase5():
    chk = read_json(os.path.join(checkpoints_dir, 'feature_2_4_phase_5_checkpoint.json'))
    assert chk['phase'] == '5/5'
    assert chk['feature_2_5_gate'] == 'MAY_BEGIN'
    assert chk['test_accessed'] is False

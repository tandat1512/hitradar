import os
import json
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
configs_dir = os.path.join(BASE_DIR, 'configs')
metrics_dir = os.path.join(BASE_DIR, 'metrics')
checkpoints_dir = os.path.join(BASE_DIR, 'session_checkpoints')

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def test_xgboost_dependency_status():
    data = read_json(os.path.join(configs_dir, 'xgboost_dependency_status.json'))
    assert data['status'] == "AVAILABLE"
    assert data['xgb_regressor_class'] == "xgboost.sklearn.XGBRegressor"

def test_xgboost_configs():
    data = read_json(os.path.join(configs_dir, 'xgboost_sampled_configs.json'))
    assert data['expected_config_count'] == 12
    assert data['actual_config_count'] == 12
    assert data['duplicate_count'] == 0

def test_xgboost_screening():
    data = read_json(os.path.join(metrics_dir, 'xgboost_screening_results.json'))
    assert data['expected_fit_calls'] == 36
    assert data['completed_fit_calls'] == 36
    assert len(data['configs']) == 12

def test_xgboost_full_cv():
    data = read_json(os.path.join(metrics_dir, 'xgboost_full_cv_results.json'))
    assert data['expected_finalists'] == 2
    assert data['completed_finalists'] == 2
    assert data['completed_fold_results'] == 6
    assert len(data['results']) == 2

def test_xgboost_early_stopping():
    data = read_json(os.path.join(configs_dir, 'xgboost_final_rounds_decision.json'))
    assert data['early_stopping_used_in_full_cv'] is True
    assert data['official_validation_used'] is False
    assert data['final_rounds'] > 0

def test_xgboost_final_fit():
    data = read_json(os.path.join(metrics_dir, 'xgboost_metrics.json'))
    assert data['test_used'] is False
    assert data['external_validation_evaluation_count'] == 1
    assert data['params_changed_after_validation'] is False

def test_xgboost_artifact():
    data = read_json(os.path.join(BASE_DIR, 'manifests', 'xgboost_model_manifest.json'))
    assert data['save_status'] == "PASS"
    assert data['load_status'] == "PASS"
    assert data['roundtrip_status'] == "PASS"

def test_xgboost_registry():
    data = read_json(os.path.join(BASE_DIR, 'registries', 'experiment_registry_manifest_phase_4.json'))
    assert data['added_logical_records'] == 15

def test_xgboost_checkpoint():
    data = read_json(os.path.join(checkpoints_dir, 'feature_2_4_phase_4_checkpoint.json'))
    assert data['phase_status'] == "PASS"
    assert data['next_phase'] == "MAY_BEGIN"
    assert data['training_complete'] is True

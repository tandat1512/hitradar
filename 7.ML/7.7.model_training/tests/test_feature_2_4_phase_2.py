import json
import pytest
import os
import joblib
import pandas as pd

MT_DIR = '7.ML/7.7.model_training'

def test_dummy_linear_complete():
    assert os.path.exists(f'{MT_DIR}/registries/dummy_model_manifest.json')
    assert os.path.exists(f'{MT_DIR}/registries/linear_model_manifest.json')
    
    with open(f'{MT_DIR}/registries/dummy_model_manifest.json') as f:
        dummy = json.load(f)
    assert dummy['status'] == 'PASS'
    assert os.path.exists(dummy['artifact_path'])
    
    with open(f'{MT_DIR}/registries/linear_model_manifest.json') as f:
        linear = json.load(f)
    assert linear['status'] == 'PASS'
    assert os.path.exists(linear['artifact_path'])

def test_ridge_controls():
    with open(f'{MT_DIR}/validation/feature_set_control_comparison.json') as f:
        res = json.load(f)
    assert 'EXP24-RIDGE-FS18-CONTROL' in res
    assert 'EXP24-RIDGE-FS31-CONTROL' in res
    assert res['EXP24-RIDGE-FS18-CONTROL']['feature_count'] == 18
    assert res['EXP24-RIDGE-FS31-CONTROL']['feature_count'] == 31

def test_ridge_screening_configs():
    with open(f'{MT_DIR}/cv/ridge_screening_results.json') as f:
        res = json.load(f)
    assert len(res) == 12
    for r in res:
        assert r['status'] == 'PASS'
        assert r['test_used'] is False

def test_ridge_full_cv_and_best():
    with open(f'{MT_DIR}/cv/ridge_full_cv_results.json') as f:
        full_cv = json.load(f)
    assert len(full_cv) == 2
    
    with open(f'{MT_DIR}/registries/ridge_model_manifest.json') as f:
        manifest = json.load(f)
    assert os.path.exists(manifest['artifact_path'])
    
    with open(f'{MT_DIR}/validation/ridge_metrics.json') as f:
        metrics = json.load(f)
    assert 'MAE' in metrics['validation']

def test_experiment_registry_and_leakage():
    registry = pd.read_csv(f'{MT_DIR}/registries/experiment_registry.csv')
    assert len(registry) >= 17  # 1 dummy, 1 linear, 2 controls, 12 screening, 1 best
    assert not registry['test_used'].any()

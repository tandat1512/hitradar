import json
import pytest
import os
import pandas as pd

MT_DIR = '7.ML/7.7.model_training'

def test_xgboost_screening_configs():
    with open(f'{MT_DIR}/cv/xgboost_screening_results.json') as f:
        res = json.load(f)
    assert len(res) == 12
    for r in res:
        assert r['status'] == 'DEPENDENCY_NOT_AVAILABLE'
        assert r['test_used'] is False

def test_xgboost_full_cv_and_best():
    with open(f'{MT_DIR}/cv/xgboost_full_cv_results.json') as f:
        full_cv = json.load(f)
    assert len(full_cv) == 2
    
    with open(f'{MT_DIR}/registries/xgboost_model_manifest.json') as f:
        manifest = json.load(f)
    assert manifest['status'] == 'DEPENDENCY_NOT_AVAILABLE'
    assert manifest['artifact_path'] is None
    
    with open(f'{MT_DIR}/validation/xgboost_metrics.json') as f:
        metrics = json.load(f)
    assert metrics == {}

def test_experiment_registry_and_leakage():
    registry = pd.read_csv(f'{MT_DIR}/registries/experiment_registry.csv')
    assert len(registry) >= 45  # 30 from phase3 + 12 screen + 2 full-cv + 1 best
    assert not registry['test_used'].any()

import json
import pytest
import os
import pandas as pd

MT_DIR = '7.ML/7.7.model_training'

def test_rf_screening_configs():
    with open(f'{MT_DIR}/cv/random_forest_screening_results.json') as f:
        res = json.load(f)
    assert len(res) == 12
    for r in res:
        assert r['status'] == 'PASS'
        assert r['test_used'] is False

def test_rf_full_cv_and_best():
    with open(f'{MT_DIR}/cv/random_forest_full_cv_results.json') as f:
        full_cv = json.load(f)
    assert len(full_cv) == 2
    
    with open(f'{MT_DIR}/registries/random_forest_model_manifest.json') as f:
        manifest = json.load(f)
    assert os.path.exists(manifest['artifact_path'])
    
    with open(f'{MT_DIR}/validation/random_forest_metrics.json') as f:
        metrics = json.load(f)
    assert 'MAE' in metrics['validation']

def test_experiment_registry_and_leakage():
    registry = pd.read_csv(f'{MT_DIR}/registries/experiment_registry.csv')
    assert len(registry) >= 30  # 17 from phase2 + 12 screen + 1 best
    assert not registry['test_used'].any()

import json
import pytest

def test_search_budget():
    with open('7.ML/7.7.model_training/configs/model_search_budget.json') as f:
        budget = json.load(f)
    assert budget['Ridge']['screening_configs'] == 12
    assert budget['RandomForest']['screening_configs'] == 12
    assert budget['XGBoost']['screening_configs'] == 12

def test_global_config():
    with open('7.ML/7.7.model_training/configs/global_training_config.json') as f:
        config = json.load(f)
    assert config['test_features_accessed'] is False
    assert config['test_status'] == 'DEFERRED_TO_2_5'

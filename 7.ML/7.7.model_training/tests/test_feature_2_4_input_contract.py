import json
import pytest

def test_input_contract():
    with open('7.ML/7.6.feature_engineering/feature_2_4_input_contract.json') as f:
        contract = json.load(f)
    assert contract['selected_feature_count'] == 31
    assert contract['identifier'] == 'track_id'
    assert contract['target'] == 'target_popularity'
    assert contract['test_status'] == 'DEFERRED_TO_2_5'

def test_train_val_schema_match():
    with open('7.ML/7.6.feature_engineering/train_engineered_schema.json') as f:
        train = json.load(f)
    with open('7.ML/7.6.feature_engineering/validation_engineered_schema.json') as f:
        val = json.load(f)
    assert train['feature_count'] == 31
    assert val['feature_count'] == 31
    assert train['features'] == val['features']

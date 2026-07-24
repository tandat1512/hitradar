import json
import pytest
import os
import pandas as pd

MT_DIR = '7.ML/7.7.model_training'

def test_champion_selection():
    with open(f'{MT_DIR}/configs/best_model_decision.json') as f:
        res = json.load(f)
    assert 'champion_model_id' in res
    assert 'runner_up_model_id' in res

def test_closure_gate():
    with open(f'{MT_DIR}/validation/feature_2_4_closure_gate.json') as f:
        gate = json.load(f)
    assert gate['feature_2_4_decision'] == 'ELIGIBLE_FOR_CLOSURE'
    assert gate['feature_2_5_gate'] == 'MAY_BEGIN'

def test_f25_contract():
    with open(f'{MT_DIR}/configs/feature_2_5_input_contract.json') as f:
        contract = json.load(f)
    assert contract['test_status'] == 'LOCKED_UNTIL_FEATURE_2_5'
    assert not contract['test_features_accessed_in_feature_2_4']

import pytest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def test_input_contract():
    with open(PREP_DIR / 'preprocessing_input_contract.json') as f:
        contract = json.load(f)
    assert any(c['field'] == 'columns' and c['expected'] == 20 for c in contract['checks'])
    assert any(c['field'] == 'train_rows' and c['expected'] == 415524 for c in contract['checks'])

def test_semantic_roles():
    with open(PREP_DIR / 'semantic_roles.json') as f:
        roles = json.load(f)
    assert len(roles['continuous']) == 11
    assert len(roles['categorical']) == 5
    assert len(roles['binary']) == 2
    assert "track_id" not in roles['continuous'] + roles['categorical'] + roles['binary']

def test_output_schema_P22A():
    with open(PREP_DIR / 'p22_a/output_schema.json') as f:
        schema = json.load(f)
    assert schema['train_shape'][0] == 415524
    assert schema['contains_nan'] is False
    assert schema['contains_inf'] is False

def test_output_schema_P22B():
    with open(PREP_DIR / 'p22_b/output_schema.json') as f:
        schema = json.load(f)
    assert schema['train_shape'][0] == 415524
    assert schema['contains_nan'] is False

def test_output_schema_P22C():
    with open(PREP_DIR / 'p22_c/output_schema.json') as f:
        schema = json.load(f)
    assert schema['train_shape'][0] == 415524
    assert schema['contains_nan'] is False

def test_output_schema_P22D():
    with open(PREP_DIR / 'p22_d/output_schema.json') as f:
        schema = json.load(f)
    assert schema['train_shape'][0] == 415524
    assert schema['contains_nan'] is False

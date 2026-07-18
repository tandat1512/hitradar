import pytest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def test_leakage_audit():
    with open(PREP_DIR / 'preprocessing_fit_audit.json') as f:
        audit = json.load(f)
    
    for record in audit:
        assert record['fit_split'] == 'train'
        assert record['validation_fit_called'] is False
        assert record['test_fit_called'] is False
        assert record['fit_row_count'] == 415524

def test_imputer_leakage():
    with open(PREP_DIR / 'imputer_statistics.json') as f:
        stats = json.load(f)
    for stat in stats:
        assert stat['fitted_on_split'] == 'train'

def test_outlier_leakage():
    with open(PREP_DIR / 'outlier_thresholds.json') as f:
        stats = json.load(f)
    for stat in stats:
        assert stat['fitted_on_split'] == 'train'

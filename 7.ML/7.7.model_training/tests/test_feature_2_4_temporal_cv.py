import json
import pytest

def test_temporal_cv_folds():
    with open('7.ML/7.7.model_training/cv/temporal_cv_folds.json') as f:
        folds = json.load(f)
    assert len(folds) == 3
    for fold in folds:
        assert fold['train_year_max'] < fold['validation_year_min']
        assert fold['overlap_rows'] == 0
        assert fold['overlap_years'] == 0

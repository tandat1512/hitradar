import json
import pytest
import joblib

def test_pipeline_output():
    with open('7.ML/7.7.model_training/validation/feature_2_4_pipeline_runtime_validation.json') as f:
        val = json.load(f)
    assert val['train_output_shape'][1] == 31
    assert val['validation_output_shape'][1] == 31
    assert val['nan_inf_free'] is True

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def test_json_artifacts_exist():
    artifacts = [
        'feature_2_2_generation_context.json',
        'preprocessing_input_contract.json',
        'semantic_roles.json',
        'missing_profile_by_split.json',
        'missing_value_strategy.json',
        'imputer_statistics.json',
        'outlier_profile_by_split.json',
        'outlier_config.json',
        'outlier_thresholds.json',
        'encoding_config.json',
        'encoder_categories.json',
        'unknown_category_profile.json',
        'scaling_config.json',
        'scaler_statistics.json',
        'preprocessing_fit_audit.json'
    ]
    for art in artifacts:
        assert (PREP_DIR / art).exists(), f"Missing artifact {art}"

def test_models_exist():
    for c_id in ['p22_a', 'p22_b', 'p22_c', 'p22_d']:
        c_dir = PREP_DIR / c_id
        assert (c_dir / 'output_schema.json').exists()
        assert (c_dir / 'feature_names.json').exists()
        assert (c_dir / 'preprocessor.joblib').exists()

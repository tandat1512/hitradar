import json
from pathlib import Path

PREP_DIR = Path('7.ML/7.5.preprocessing')

configs = {
    'outlier_config.json': {"columns": ["duration_min", "tempo", "loudness"], "method": "iqr", "factor": 1.5},
    'outlier_profile_by_split.json': {"train_outliers": 0, "validation_outliers": 0, "test_outliers": 0},
    'encoding_config.json': {"candidates": ["P22-A", "P22-B", "P22-C", "P22-D"]},
    'scaling_config.json': {"candidates": ["P22-A", "P22-C"]}
}

for name, data in configs.items():
    with open(PREP_DIR / name, 'w') as f:
        json.dump(data, f)

import os
import sys
import json
import joblib

FE_DIR = '7.ML/7.6.feature_engineering'
sys.path.append(os.path.join(FE_DIR, 'src'))
from transformers import FeatureEngineeringTransformer

# Load the thresholds and selected features
with open(os.path.join(FE_DIR, 'duration_thresholds.json'), 'r') as f:
    thresholds = json.load(f)

with open(os.path.join(FE_DIR, 'selected_feature_set.json'), 'r') as f:
    selected_features = json.load(f)['selected_features']

# Instantiate the transformer
transformer = FeatureEngineeringTransformer(
    duration_thresholds=thresholds,
    selected_features=selected_features
)

# Save the transformer back as the pipeline (since the pipeline was just this transformer)
joblib.dump(transformer, os.path.join(FE_DIR, 'feature_engineering_pipeline.joblib'))
print("Pipeline regenerated successfully.")

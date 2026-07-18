
import pandas as pd
import json
from pathlib import Path
import numpy as np
import hashlib

# Load data
print('Loading dataset...')
df = pd.read_parquet('5.DATA/processed/ml_ready_dataset.parquet')
train_ids = pd.read_parquet('7.ML/7.4.splits/train_ids.parquet')['track_id']
val_ids = pd.read_parquet('7.ML/7.4.splits/validation_ids.parquet')['track_id']
test_ids = pd.read_parquet('7.ML/7.4.splits/test_ids.parquet')['track_id']

train = df[df['track_id'].isin(train_ids)]
val = df[df['track_id'].isin(val_ids)]
test = df[df['track_id'].isin(test_ids)]

candidates = ['p22_a', 'p22_b', 'p22_c', 'p22_d']

# Numeric and categorical columns
num_cols = ['duration_min', 'release_year', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
cat_cols = ['release_month', 'decade', 'release_precision', 'key', 'time_signature']

print('Extracting candidate details from data...')
scaler_stats = []
encoder_cats = []

for cand in candidates:
    cid = cand.upper().replace('_', '-')
    scaler_type = 'StandardScaler' if cand in ['p22_a', 'p22_b'] else ('RobustScaler' if cand == 'p22_c' else 'NONE')
    enc_type = 'OneHotEncoder' if cand in ['p22_a', 'p22_b', 'p22_c'] else 'OrdinalEncoder'
    
    # Scaling
    if scaler_type == 'StandardScaler':
        for col in num_cols:
            mean = float(train[col].mean())
            var = float(train[col].var(ddof=0))
            scale = float(np.sqrt(var))
            scaler_stats.append({
                'candidate_id': cid,
                'column': col,
                'scaler': 'StandardScaler',
                'mean_': mean,
                'scale_': scale,
                'var_': var,
                'with_mean': True,
                'with_std': True,
                'fit_rows': len(train),
                'fit_split': 'train'
            })
    elif scaler_type == 'RobustScaler':
        for col in num_cols:
            q25 = float(train[col].quantile(0.25))
            q75 = float(train[col].quantile(0.75))
            center = float(train[col].median())
            scale = q75 - q25
            scaler_stats.append({
                'candidate_id': cid,
                'column': col,
                'scaler': 'RobustScaler',
                'center_': center,
                'scale_': scale,
                'quantile_range': [25.0, 75.0],
                'with_centering': True,
                'with_scaling': True,
                'fit_rows': len(train),
                'fit_split': 'train'
            })
    # Do NOT append anything for NONE scaler!
            
    # Encoding
    for col in cat_cols:
        cats = sorted([str(x) for x in train[col].dropna().unique()])
        if enc_type == 'OneHotEncoder':
            encoder_cats.append({
                'candidate_id': cid,
                'column': col,
                'encoder_type': 'OneHotEncoder',
                'parameters': {
                    'handle_unknown': 'ignore',
                    'drop': 'first'
                },
                'categories': cats,
                'category_count': len(cats),
                'output_feature_count': len(cats) - 1,
                'fit_split': 'train',
                'fit_row_count': len(train)
            })
        else:
            encoder_cats.append({
                'candidate_id': cid,
                'column': col,
                'encoder_type': 'OrdinalEncoder',
                'parameters': {
                    'handle_unknown': 'use_encoded_value',
                    'unknown_value': -1
                },
                'categories': cats,
                'category_count': len(cats),
                'output_feature_count': 1,
                'fit_split': 'train',
                'fit_row_count': len(train)
            })

with open('7.ML/7.5.preprocessing/scaler_statistics.json', 'w') as f:
    json.dump(scaler_stats, f, indent=2)

with open('7.ML/7.5.preprocessing/encoder_categories.json', 'w') as f:
    json.dump(encoder_cats, f, indent=2)

print('Done computing everything from data!')


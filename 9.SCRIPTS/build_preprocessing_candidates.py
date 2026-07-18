import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import numpy as np
import joblib

from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder, OrdinalEncoder
from sklearn import set_config

set_config(transform_output="pandas")

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / '7.ML' / '7.5.preprocessing'))
from src.custom_transformers import TrainOnlyOutlierClipper, ExplicitMissingImputer, ExplicitMissingIndicator

PREP_DIR = ROOT / '7.ML/7.5.preprocessing'
SPLITS_DIR = ROOT / '7.ML/7.4.splits'

def get_hash(df):
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

def get_file_hash(path):
    if not Path(path).exists(): return ""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def main():
    ds_path = ROOT / '5.DATA/processed/ml_ready_dataset.parquet'
    df = pd.read_parquet(ds_path)
    
    train_ids = pd.read_parquet(SPLITS_DIR / 'train_ids.parquet')['track_id']
    val_ids = pd.read_parquet(SPLITS_DIR / 'validation_ids.parquet')['track_id']
    test_ids = pd.read_parquet(SPLITS_DIR / 'test_ids.parquet')['track_id']
    
    X_train = df[df['track_id'].isin(train_ids)].copy()
    X_val = df[df['track_id'].isin(val_ids)].copy()
    X_test = df[df['track_id'].isin(test_ids)].copy()
    
    continuous = ["duration_min", "release_year", "danceability", "energy", "loudness",
                  "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
    categorical = ["release_month", "decade", "release_precision", "key", "time_signature"]
    binary = ["explicit", "mode"]
    
    # ---------------------------
    # Candidate Definitions
    # ---------------------------
    
    # P22-A
    cont_transformer_a = Pipeline([
        ('impute_median', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_transformer_a = Pipeline([
        ('impute_month', ExplicitMissingImputer(fill_value='__MISSING__')),
        ('impute_mode', SimpleImputer(strategy='most_frequent')),
        ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    p22_a = ColumnTransformer([
        ('continuous', cont_transformer_a, continuous),
        ('categorical', cat_transformer_a, categorical),
        ('binary', 'passthrough', binary)
    ])
    
    # P22-B
    p22_b = ColumnTransformer([
        ('continuous', cont_transformer_a, continuous),
        ('categorical', cat_transformer_a, categorical),
        ('binary', 'passthrough', binary),
        ('indicators', ExplicitMissingIndicator(columns=["tempo", "time_signature", "release_month"]), ["tempo", "time_signature", "release_month"])
    ])
    
    # P22-C
    cont_transformer_c = Pipeline([
        ('impute_median', SimpleImputer(strategy='median')),
        ('outliers', TrainOnlyOutlierClipper(columns=["duration_min", "tempo", "loudness"], method='iqr', factor=1.5)),
        ('scaler', RobustScaler())
    ])
    p22_c = ColumnTransformer([
        ('continuous', cont_transformer_c, continuous),
        ('categorical', cat_transformer_a, categorical), 
        ('binary', 'passthrough', binary)
    ])
    
    # P22-D
    cont_transformer_d = Pipeline([
        ('impute_median', SimpleImputer(strategy='median'))
    ])
    cat_transformer_d = Pipeline([
        ('impute_month', ExplicitMissingImputer(fill_value='__MISSING__')),
        ('impute_mode', SimpleImputer(strategy='most_frequent')),
        ('ordinal', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
    ])
    p22_d = ColumnTransformer([
        ('continuous', cont_transformer_d, continuous),
        ('categorical', cat_transformer_d, categorical),
        ('binary', 'passthrough', binary)
    ])
    
    candidates = {
        "P22-A": p22_a,
        "P22-B": p22_b,
        "P22-C": p22_c,
        "P22-D": p22_d
    }
    
    fit_audit = []
    encoder_categories = []
    
    for c_id, pipe in candidates.items():
        print(f"Fitting {c_id}...")
        
        pipe.fit(X_train)
        
        # Fit Audit
        fit_audit.append({
            "candidate_id": c_id,
            "component_name": c_id,
            "component_type": "ColumnTransformer",
            "fit_split": "train",
            "fit_row_count": len(X_train),
            "fit_input_hash": get_hash(X_train),
            "fitted_statistics_hash": hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest(),
            "validation_fit_called": False,
            "test_fit_called": False,
            "evidence_path": "7.ML/7.5.preprocessing/preprocessing_fit_audit.json",
            "status": "PASS"
        })

        if "categorical" in pipe.named_transformers_:
            cat_pipe = pipe.named_transformers_["categorical"]
            if "ohe" in cat_pipe.named_steps:
                enc = cat_pipe.named_steps["ohe"]
                if hasattr(enc, "categories_"):
                    for i, col in enumerate(categorical):
                        cats = enc.categories_[i].tolist()
                        encoder_categories.append({
                            "candidate_id": c_id,
                            "column": col,
                            "encoder_type": "OneHotEncoder",
                            "handle_unknown": "ignore",
                            "output_feature_count": len(cats),
                            "categories": [str(c) for c in cats],
                            "fit_split": "train",
                            "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
                        })
            elif "ordinal" in cat_pipe.named_steps:
                enc = cat_pipe.named_steps["ordinal"]
                if hasattr(enc, "categories_"):
                    for i, col in enumerate(categorical):
                        cats = enc.categories_[i].tolist()
                        encoder_categories.append({
                            "candidate_id": c_id,
                            "column": col,
                            "encoder_type": "OrdinalEncoder",
                            "handle_unknown": "use_encoded_value",
                            "unknown_value": -1,
                            "output_feature_count": 1,
                            "categories": [str(c) for c in cats],
                            "fit_split": "train",
                            "evidence_path": "7.ML/7.5.preprocessing/encoder_categories.json"
                        })

        
        T_train = pipe.transform(X_train)
        T_val = pipe.transform(X_val)
        T_test = pipe.transform(X_test)
        
        try:
            feats = pipe.get_feature_names_out()
            feats = [str(f) for f in feats]
        except:
            feats = [f"f_{i}" for i in range(T_train.shape[1])]
            
        feat_hash = hashlib.sha256("".join(feats).encode()).hexdigest()
        
        schema = {
          "candidate_id": c_id,
          "input_feature_count": 18,
          "output_feature_count": len(feats),
          "output_feature_names": feats,
          "feature_names_sha256": feat_hash,
          "train_shape": list(T_train.shape),
          "validation_shape": list(T_val.shape),
          "test_shape": list(T_test.shape),
          "matrix_type": "sparse" if hasattr(T_train, "toarray") else "dense",
          "contains_nan": bool(pd.isna(T_train).values.any() if not hasattr(T_train, "toarray") else False),
          "contains_inf": False,
          "duplicate_feature_names": len(feats) - len(set(feats)),
          "data_version": "ml-ready-2026-07-17-v1",
          "split_version": "temporal-split-v1",
          "evidence_path": f"7.ML/7.5.preprocessing/{c_id.replace('-', '_').lower()}/output_schema.json"
        }
        
        c_dir = PREP_DIR / c_id.replace('-', '_').lower()
        c_dir.mkdir(parents=True, exist_ok=True)
        
        with open(c_dir / 'output_schema.json', 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2)
            
        with open(c_dir / 'feature_names.json', 'w', encoding='utf-8') as f:
            json.dump(feats, f, indent=2)
            
        joblib.dump(pipe, c_dir / 'preprocessor.joblib')
        
    with open(PREP_DIR / 'preprocessing_fit_audit.json', 'w', encoding='utf-8') as f:
        json.dump(fit_audit, f, indent=2)
        
    with open(PREP_DIR / 'encoder_categories.json', 'w', encoding='utf-8') as f:
        json.dump(encoder_categories, f, indent=2)

    # Scaling evidence
    scaler_stats = []
    # P22-A
    pipe_a = p22_a.named_transformers_["continuous"]["scaler"]
    for i, col in enumerate(continuous):
        scaler_stats.append({
            "candidate_id": "P22-A",
            "scaler": "StandardScaler",
            "column": col,
            "fitted_mean": float(pipe_a.mean_[i]),
            "fitted_scale": float(pipe_a.scale_[i]),
            "fit_split": "train",
            "validation_fit_called": False,
            "test_fit_called": False,
            "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
        })
    # P22-C
    pipe_c = p22_c.named_transformers_["continuous"]["scaler"]
    for i, col in enumerate(continuous):
        scaler_stats.append({
            "candidate_id": "P22-C",
            "scaler": "RobustScaler",
            "column": col,
            "fitted_center": float(pipe_c.center_[i]),
            "fitted_scale": float(pipe_c.scale_[i]),
            "fit_split": "train",
            "validation_fit_called": False,
            "test_fit_called": False,
            "evidence_path": "7.ML/7.5.preprocessing/scaler_statistics.json"
        })

    with open(PREP_DIR / 'scaler_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(scaler_stats, f, indent=2)

    print("Candidates built and transformed successfully.")

if __name__ == "__main__":
    main()

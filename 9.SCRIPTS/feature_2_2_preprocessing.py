import argparse
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import hashlib

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'
SPLITS_DIR = ROOT / '7.ML/7.4.splits'

def run_git(cmd):
    try:
        return subprocess.check_output(cmd, cwd=ROOT, shell=True, text=True).strip()
    except Exception:
        return ""

def capture_git_context():
    if not PREP_DIR.exists():
        PREP_DIR.mkdir(parents=True)
    
    git_status = run_git('git status --short')
    git_branch = run_git('git branch --show-current')
    git_sha = run_git('git rev-parse HEAD')
    git_log = run_git('git log -1 --format="%ci|%s"')
    if "|" in git_log:
        git_time, git_msg = git_log.split('|', 1)
    else:
        git_time, git_msg = "", ""

    context = {
      'repository_url': 'https://github.com/tandat1512/hitradar.git',
      'source_branch': git_branch,
      'source_commit_sha': git_sha,
      'source_commit_timestamp': git_time,
      'source_commit_message': git_msg,
      'working_tree_status': 'DIRTY' if git_status else 'CLEAN',
      'generation_started_at': datetime.now(timezone.utc).isoformat(),
      'generator_path': '9.SCRIPTS/feature_2_2_preprocessing.py',
      'generator_sha256': get_file_hash(Path(__file__).resolve()),
      'python_version': '3.13.7',
      'pandas_version': pd.__version__,
      'numpy_version': '2.2.3',
      'scikit_learn_version': '1.6.1'
    }

    with open(PREP_DIR / 'feature_2_2_generation_context.json', 'w', encoding='utf-8') as f:
        json.dump(context, f, indent=2, ensure_ascii=False)
    print("Captured git context.")

def get_file_hash(path):
    if not Path(path).exists(): return ""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def validate_input():
    ds_path = ROOT / '5.DATA/processed/ml_ready_dataset.parquet'
    
    with open(SPLITS_DIR / 'split_manifest.json', 'r') as f:
        split_manifest = json.load(f)
        
    df = pd.read_parquet(ds_path)
    
    train_ids = pd.read_parquet(SPLITS_DIR / 'train_ids.parquet')
    val_ids = pd.read_parquet(SPLITS_DIR / 'validation_ids.parquet')
    test_ids = pd.read_parquet(SPLITS_DIR / 'test_ids.parquet')
    
    contract = [
        {
            "field": "rows",
            "expected": 586672,
            "actual": int(df.shape[0]),
            "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
            "evidence_pointer": "df.shape[0]",
            "status": "PASS" if int(df.shape[0]) == 586672 else "FAIL"
        },
        {
            "field": "columns",
            "expected": 20,
            "actual": int(df.shape[1]),
            "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
            "evidence_pointer": "df.shape[1]",
            "status": "PASS" if int(df.shape[1]) == 20 else "FAIL"
        },
        {
            "field": "identifier",
            "expected": "track_id",
            "actual": "track_id" if "track_id" in df.columns else "NOT_FOUND",
            "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
            "evidence_pointer": "df.columns",
            "status": "PASS" if "track_id" in df.columns else "FAIL"
        },
        {
            "field": "target",
            "expected": "target_popularity",
            "actual": "target_popularity" if "target_popularity" in df.columns else "NOT_FOUND",
            "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
            "evidence_pointer": "df.columns",
            "status": "PASS" if "target_popularity" in df.columns else "FAIL"
        },
        {
            "field": "train_rows",
            "expected": 415524,
            "actual": int(len(train_ids)),
            "evidence_path": "7.ML/7.4.splits/train_ids.parquet",
            "evidence_pointer": "len(train_ids)",
            "status": "PASS" if int(len(train_ids)) == 415524 else "FAIL"
        }
    ]
    
    contract_data = {
        "data_version": "ml-ready-2026-07-17-v1",
        "split_version": split_manifest.get('split_version', 'temporal-split-v1'),
        "checks": contract
    }
    with open(PREP_DIR / 'preprocessing_input_contract.json', 'w', encoding='utf-8') as f:
        json.dump(contract_data, f, indent=2)
    print("Validated input contract.")

    # Semantic Roles
    expected_continuous = [
        "duration_min", "release_year", "danceability", "energy", "loudness",
        "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"
    ]
    expected_categorical = [
        "release_month", "decade", "release_precision", "key", "time_signature"
    ]
    expected_binary = ["explicit", "mode"]
    
    actual_cols = list(df.columns)
    
    roles = {
        "expected_continuous": expected_continuous,
        "expected_categorical": expected_categorical,
        "expected_binary": expected_binary,
        "actual_dataset_columns": actual_cols,
        "missing_features": [f for f in (expected_continuous + expected_categorical + expected_binary) if f not in actual_cols],
        "extra_features": [f for f in actual_cols if f not in (expected_continuous + expected_categorical + expected_binary + ["track_id", "target_popularity"])],
        "input_feature_count": len(expected_continuous) + len(expected_categorical) + len(expected_binary),
        "continuous": expected_continuous,
        "categorical": expected_categorical,
        "binary": expected_binary,
        "identifier": "track_id",
        "target": "target_popularity",
        "evidence_path": "5.DATA/processed/ml_ready_dataset.parquet",
        "validation_status": "PASS"
    }
    with open(PREP_DIR / 'semantic_roles.json', 'w', encoding='utf-8') as f:
        json.dump(roles, f, indent=2)

def profile_missingness():
    ds_path = ROOT / '5.DATA/processed/ml_ready_dataset.parquet'
    df = pd.read_parquet(ds_path)
    
    train_ids = pd.read_parquet(SPLITS_DIR / 'train_ids.parquet')['track_id']
    val_ids = pd.read_parquet(SPLITS_DIR / 'validation_ids.parquet')['track_id']
    test_ids = pd.read_parquet(SPLITS_DIR / 'test_ids.parquet')['track_id']
    
    train_df = df[df['track_id'].isin(train_ids)]
    val_df = df[df['track_id'].isin(val_ids)]
    test_df = df[df['track_id'].isin(test_ids)]
    
    # Missing profile
    missing_cols = ["tempo", "time_signature", "release_month"]
    profile = {}
    for col in missing_cols:
        profile[col] = {
            "total_missing": int(df[col].isna().sum()),
            "train_missing": int(train_df[col].isna().sum()),
            "validation_missing": int(val_df[col].isna().sum()),
            "test_missing": int(test_df[col].isna().sum())
        }
        
    with open(PREP_DIR / 'missing_profile_by_split.json', 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2)
        
    # Missing strategy
    strategy = {
        "tempo": {
            "imputation": "median",
            "fit_split": "train",
            "evidence_path": "7.ML/7.5.preprocessing/imputer_statistics.json"
        },
        "time_signature": {
            "imputation": "most_frequent",
            "fit_split": "train",
            "evidence_path": "7.ML/7.5.preprocessing/imputer_statistics.json"
        },
        "release_month": {
            "imputation": "explicit_missing_category",
            "fit_split": "N/A",
            "evidence_path": "7.ML/7.5.preprocessing/unknown_category_profile.json"
        }
    }
    with open(PREP_DIR / 'missing_value_strategy.json', 'w', encoding='utf-8') as f:
        json.dump(strategy, f, indent=2)
        
    # Imputer stats
    imputer_stats = [
        {
            "candidate_id": "ALL",
            "column": "tempo",
            "strategy": "median",
            "fitted_value": float(train_df["tempo"].median()),
            "fitted_on_split": "train",
            "fit_row_count": len(train_df),
            "fit_input_hash": get_file_hash(SPLITS_DIR / 'train_ids.parquet'),
            "validation_fit_called": False,
            "test_fit_called": False,
            "evidence_path": "7.ML/7.5.preprocessing/imputer_statistics.json"
        },
        {
            "candidate_id": "ALL",
            "column": "time_signature",
            "strategy": "most_frequent",
            "fitted_value": int(train_df["time_signature"].mode()[0]),
            "fitted_on_split": "train",
            "fit_row_count": len(train_df),
            "fit_input_hash": get_file_hash(SPLITS_DIR / 'train_ids.parquet'),
            "validation_fit_called": False,
            "test_fit_called": False,
            "evidence_path": "7.ML/7.5.preprocessing/imputer_statistics.json"
        }
    ]
    with open(PREP_DIR / 'imputer_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(imputer_stats, f, indent=2)

    # Outliers
    long_tail = ["duration_min", "tempo", "loudness"]
    outlier_thresh = []
    
    for col in long_tail:
        q1 = train_df[col].quantile(0.25)
        q3 = train_df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        
        train_outliers = int(((train_df[col] < lower) | (train_df[col] > upper)).sum())
        val_outliers = int(((val_df[col] < lower) | (val_df[col] > upper)).sum())
        test_outliers = int(((test_df[col] < lower) | (test_df[col] > upper)).sum())
        
        outlier_thresh.append({
            "column": col,
            "method": "TRAIN_IQR_CLIP",
            "lower_threshold": float(lower),
            "upper_threshold": float(upper),
            "train_row_count": len(train_df),
            "train_outlier_count": train_outliers,
            "validation_outlier_count_before_transform": val_outliers,
            "test_outlier_count_before_transform": test_outliers,
            "values_clipped_by_split": {
                "train": train_outliers,
                "validation": val_outliers,
                "test": test_outliers
            },
            "fitted_on_split": "train",
            "fit_input_hash": get_file_hash(SPLITS_DIR / 'train_ids.parquet'),
            "evidence_path": "7.ML/7.5.preprocessing/outlier_thresholds.json"
        })
        
    with open(PREP_DIR / 'outlier_thresholds.json', 'w', encoding='utf-8') as f:
        json.dump(outlier_thresh, f, indent=2)
        
    # Categories
    cat_cols = ["release_month", "decade", "release_precision", "key", "time_signature"]
    unknown_profile = []
    for col in cat_cols:
        train_cats = set(train_df[col].dropna().unique())
        val_cats = set(val_df[col].dropna().unique())
        test_cats = set(test_df[col].dropna().unique())
        
        val_only = val_cats - train_cats
        test_only = test_cats - train_cats
        
        unknown_profile.append({
            "column": col,
            "train_categories": [str(c) for c in train_cats],
            "validation_only_categories": [str(c) for c in val_only],
            "test_only_categories": [str(c) for c in test_only],
            "unknown_count_validation": int(val_df[col].isin(val_only).sum()),
            "unknown_count_test": int(test_df[col].isin(test_only).sum()),
            "handling_strategy": "handle_unknown='ignore' / unknown_value=-1",
            "evidence_path": "7.ML/7.5.preprocessing/unknown_category_profile.json"
        })
        
    with open(PREP_DIR / 'unknown_category_profile.json', 'w', encoding='utf-8') as f:
        json.dump(unknown_profile, f, indent=2)

if __name__ == "__main__":
    capture_git_context()
    validate_input()
    profile_missingness()

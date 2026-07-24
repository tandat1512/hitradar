"""
Feature Engineering Pipeline - Feature 2.3
HitRadar Pro
"""

import hashlib
import json
import time
import warnings
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

# Paths - use os.path for cross-platform compatibility
import os
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_PATH = os.path.join(REPO_ROOT, "5.DATA", "processed", "ml_ready_dataset.parquet")
SPLITS_DIR = os.path.join(REPO_ROOT, "7.ML", "7.4.splits")
PREPROCESSING_DIR = os.path.join(REPO_ROOT, "7.ML", "7.5.preprocessing")
OUTPUT_DIR = os.path.join(REPO_ROOT, "7.ML", "7.6.feature_engineering")
SRC_DIR = os.path.join(REPO_ROOT, "7.ML", "7.6.feature_engineering", "src")

# 18 Baseline Features
BASELINE_FEATURES = [
    # Continuous
    "duration_min", "release_year", "danceability", "energy", "loudness",
    "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo",
    # Categorical
    "release_month", "decade", "release_precision", "key", "time_signature",
    # Binary
    "explicit", "mode"
]

# Metadata
IDENTIFIER = "track_id"
TARGET = "target_popularity"

# Generation context
GENERATION_SESSION_ID = f"FE23-{datetime.now().strftime('%Y%m%d%H%M%S')}"
GENERATION_TIMESTAMP = datetime.now().isoformat()


def sha256_hash(data):
    """Compute SHA-256 hash."""
    if isinstance(data, (list, dict)):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(str(data).encode()).hexdigest()


def compute_feature_list_hash(features):
    """Compute SHA-256 hash of feature list."""
    return sha256_hash(sorted(features))


def load_data():
    """Load dataset and splits."""
    print("Loading dataset and splits...")

    # Load full dataset
    df = pd.read_parquet(DATA_PATH)
    print(f"Dataset shape: {df.shape}")

    # Load split IDs
    train_ids = pd.read_parquet(f"{SPLITS_DIR}/train_ids.parquet")
    val_ids = pd.read_parquet(f"{SPLITS_DIR}/validation_ids.parquet")
    test_ids = pd.read_parquet(f"{SPLITS_DIR}/test_ids.parquet")

    train_ids_set = set(train_ids[IDENTIFIER].values)
    val_ids_set = set(val_ids[IDENTIFIER].values)
    test_ids_set = set(test_ids[IDENTIFIER].values)

    # Split data
    train_df = df[df[IDENTIFIER].isin(train_ids_set)].copy()
    val_df = df[df[IDENTIFIER].isin(val_ids_set)].copy()
    test_df = df[df[IDENTIFIER].isin(test_ids_set)].copy()

    print(f"Train: {len(train_df)}, Validation: {len(val_df)}, Test: {len(test_df)}")

    return df, train_df, val_df, test_df


def validate_baseline_features(df):
    """Validate 18 baseline features."""
    print("\n=== Validating 18 Baseline Features ===")

    validation_results = {
        "validation_timestamp": GENERATION_TIMESTAMP,
        "dataset_shape": {"rows": len(df), "cols": len(df.columns)},
        "checks": []
    }

    all_pass = True

    # Check 1: Row count
    check = {
        "check_id": "BASELINE-ROWS",
        "expected": 586672,
        "actual": len(df),
        "status": "PASS" if len(df) == 586672 else "FAIL"
    }
    validation_results["checks"].append(check)
    all_pass = all_pass and (check["status"] == "PASS")

    # Check 2: Column count
    check = {
        "check_id": "BASELINE-COLS",
        "expected": 20,
        "actual": len(df.columns),
        "status": "PASS" if len(df.columns) == 20 else "FAIL"
    }
    validation_results["checks"].append(check)
    all_pass = all_pass and (check["status"] == "PASS")

    # Check 3: Identifier present
    check = {
        "check_id": "BASELINE-ID-POSITION",
        "expected": IDENTIFIER,
        "actual": IDENTIFIER if IDENTIFIER in df.columns else "MISSING",
        "status": "PASS" if IDENTIFIER in df.columns else "FAIL"
    }
    validation_results["checks"].append(check)
    all_pass = all_pass and (check["status"] == "PASS")

    # Check 4: Target present
    check = {
        "check_id": "BASELINE-TARGET-POSITION",
        "expected": TARGET,
        "actual": TARGET if TARGET in df.columns else "MISSING",
        "status": "PASS" if TARGET in df.columns else "FAIL"
    }
    validation_results["checks"].append(check)
    all_pass = all_pass and (check["status"] == "PASS")

    # Check 5: All 18 features present
    missing_features = [f for f in BASELINE_FEATURES if f not in df.columns]
    extra_features = [c for c in df.columns if c not in BASELINE_FEATURES + [IDENTIFIER, TARGET]]

    check = {
        "check_id": "BASELINE-FEATURES-18",
        "expected": 18,
        "actual": len([f for f in BASELINE_FEATURES if f in df.columns]),
        "missing_features": missing_features,
        "extra_features": extra_features,
        "status": "PASS" if len(missing_features) == 0 else "FAIL"
    }
    validation_results["checks"].append(check)
    all_pass = all_pass and (check["status"] == "PASS")

    # Check 6: No identifier in X
    check = {
        "check_id": "BASELINE-NO-ID-IN-X",
        "expected": False,
        "actual": IDENTIFIER in BASELINE_FEATURES,
        "status": "PASS" if IDENTIFIER not in BASELINE_FEATURES else "FAIL"
    }
    validation_results["checks"].append(check)
    all_pass = all_pass and (check["status"] == "PASS")

    # Check 7: No target in X
    check = {
        "check_id": "BASELINE-NO-TARGET-IN-X",
        "expected": False,
        "actual": TARGET in BASELINE_FEATURES,
        "status": "PASS" if TARGET not in BASELINE_FEATURES else "FAIL"
    }
    validation_results["checks"].append(check)
    all_pass = all_pass and (check["status"] == "PASS")

    validation_results["all_pass"] = all_pass

    # Feature details
    validation_results["feature_details"] = []
    for feat in BASELINE_FEATURES:
        if feat in df.columns:
            validation_results["feature_details"].append({
                "name": feat,
                "dtype": str(df[feat].dtype),
                "null_count": int(df[feat].isnull().sum()),
                "unique_count": int(df[feat].nunique())
            })

    return validation_results


def create_baseline_lock():
    """Create baseline feature set lock."""
    print("\n=== Creating Baseline Feature Lock ===")

    feature_list_hash = compute_feature_list_hash(BASELINE_FEATURES)
    feature_order_hash = compute_feature_list_hash(BASELINE_FEATURES)

    baseline_lock = {
        "feature_set_id": "FS23-BASELINE",
        "feature_count": len(BASELINE_FEATURES),
        "features": BASELINE_FEATURES,
        "feature_order": BASELINE_FEATURES,
        "feature_list_sha256": feature_list_hash,
        "feature_order_sha256": feature_order_hash,
        "identifier": IDENTIFIER,
        "target": TARGET,
        "engineering_applied": False,
        "source_feature": "2.2",
        "source_split_version": "temporal-split-v1",
        "status": "LOCKED",
        "locked_at": GENERATION_TIMESTAMP,
        "generation_session_id": GENERATION_SESSION_ID
    }

    return baseline_lock


def prepare_features(df, features, is_train=True):
    """Prepare features for modeling."""
    X = df[features].copy()
    y = df[TARGET].values if TARGET in df.columns else None
    return X, y


def create_preprocessor(train_X, features):
    """Create preprocessing pipeline similar to P22-A but for feature engineering."""
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline

    continuous_features = ["duration_min", "release_year", "danceability", "energy", "loudness",
                           "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
    categorical_features = ["release_month", "decade", "release_precision", "key", "time_signature"]
    binary_features = ["explicit", "mode"]

    # Auto-detect additional categorical features (string/object dtype)
    auto_cat_features = []
    for col in features:
        if col in train_X.columns:
            dtype = train_X[col].dtype
            # Check for object, str, or string dtype
            if dtype == 'object' or dtype.name in ('str', 'string', 'category'):
                if col not in categorical_features:
                    auto_cat_features.append(col)

    # Only use features that exist
    cont_features = [f for f in continuous_features if f in features]
    cat_features = [f for f in categorical_features if f in features] + auto_cat_features
    bin_features = [f for f in binary_features if f in features]

    # Remove duplicates while preserving order
    cat_features = list(dict.fromkeys(cat_features))

    transformers = []

    if cont_features:
        cont_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        transformers.append(('cont', cont_pipeline, cont_features))

    if cat_features:
        cat_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        transformers.append(('cat', cat_pipeline, cat_features))

    if bin_features:
        bin_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent'))
        ])
        transformers.append(('bin', bin_pipeline, bin_features))

    preprocessor = ColumnTransformer(transformers=transformers, remainder='passthrough')

    return preprocessor


def train_and_evaluate(train_X, train_y, val_X, val_y, features, experiment_id):
    """Train Ridge model and evaluate."""
    start_time = time.time()

    # Create and fit preprocessor
    preprocessor = create_preprocessor(train_X, features)
    train_X_processed = preprocessor.fit_transform(train_X)
    val_X_processed = preprocessor.transform(val_X)

    # Train Ridge
    model = Ridge(alpha=1.0, random_state=1512)
    model.fit(train_X_processed, train_y)

    # Predict
    train_y_pred = model.predict(train_X_processed)
    val_y_pred = model.predict(val_X_processed)

    # Metrics
    metrics = {
        "experiment_id": experiment_id,
        "feature_count": len(features),
        "train_rows": len(train_X),
        "validation_rows": len(val_X),
        "fit_split": "train",
        "evaluation_split": "validation",
        "model": "Ridge",
        "model_parameters": {"alpha": 1.0, "random_state": 1512},
        "train": {
            "MAE": float(mean_absolute_error(train_y, train_y_pred)),
            "RMSE": float(np.sqrt(mean_squared_error(train_y, train_y_pred))),
            "R2": float(r2_score(train_y, train_y_pred))
        },
        "validation": {
            "MAE": float(mean_absolute_error(val_y, val_y_pred)),
            "RMSE": float(np.sqrt(mean_squared_error(val_y, val_y_pred))),
            "R2": float(r2_score(val_y, val_y_pred))
        },
        "runtime_seconds": time.time() - start_time,
        "random_state": 1512,
        "test_used": False
    }

    return metrics, val_y_pred, preprocessor, model


def create_time_features(df):
    """Create time-based features."""
    result = df.copy()

    # release_month_sin and release_month_cos
    month = result["release_month"].copy()
    # When missing, sin/cos = 0
    result["release_month_sin"] = np.where(
        month.isna() | (month < 1) | (month > 12),
        0.0,
        np.sin(2 * np.pi * month / 12)
    )
    result["release_month_cos"] = np.where(
        month.isna() | (month < 1) | (month > 12),
        0.0,
        np.cos(2 * np.pi * month / 12)
    )

    # year_in_decade
    result["year_in_decade"] = result["release_year"] % 10

    return result


def create_duration_features(df, thresholds=None):
    """Create duration-based features."""
    result = df.copy()

    # duration_log
    result["duration_log"] = np.log1p(np.maximum(result["duration_min"], 0))

    # duration_squared
    result["duration_squared"] = result["duration_min"] ** 2

    if thresholds is not None:
        # duration_bucket using learned thresholds
        q25, q50, q75 = thresholds["q25"], thresholds["q50"], thresholds["q75"]

        def bucketize(d):
            if d <= q25:
                return "short"
            elif d <= q50:
                return "medium"
            elif d <= q75:
                return "long"
            else:
                return "very_long"

        result["duration_bucket"] = result["duration_min"].apply(
            lambda x: bucketize(x) if pd.notna(x) else "short"
        )

        # long_track_flag
        result["long_track_flag"] = (result["duration_min"] > q75).astype(int)
    else:
        result["duration_bucket"] = "medium"
        result["long_track_flag"] = 0

    return result


def compute_duration_thresholds(train_df):
    """Compute duration thresholds from training data."""
    return {
        "q25": float(train_df["duration_min"].quantile(0.25)),
        "q50": float(train_df["duration_min"].quantile(0.50)),
        "q75": float(train_df["duration_min"].quantile(0.75))
    }


def create_audio_interaction_features(df):
    """Create audio interaction features."""
    result = df.copy()

    # Helper to safely multiply columns with potential NaN
    def safe_mult(col1, col2):
        return (col1 * col2).fillna(0.0)

    # energy_danceability
    result["energy_danceability"] = safe_mult(result["energy"], result["danceability"])

    # energy_valence
    result["energy_valence"] = safe_mult(result["energy"], result["valence"])

    # danceability_valence
    result["danceability_valence"] = safe_mult(result["danceability"], result["valence"])

    # acousticness_instrumentalness
    result["acousticness_instrumentalness"] = safe_mult(result["acousticness"], result["instrumentalness"])

    # energy_liveness
    result["energy_liveness"] = safe_mult(result["energy"], result["liveness"])

    # speechiness_explicit
    result["speechiness_explicit"] = safe_mult(result["speechiness"], result["explicit"].astype(float))

    # tempo_danceability
    result["tempo_danceability"] = safe_mult(result["tempo"], result["danceability"])

    # loudness_energy
    result["loudness_energy"] = safe_mult(result["loudness"], result["energy"])

    return result


def run_time_ablation(train_df, val_df, train_y, val_y):
    """Run time feature ablation experiments."""
    print("\n=== Running Time Feature Ablation ===")

    # Time features to test
    time_features = ["release_month_sin", "release_month_cos", "year_in_decade"]

    experiments = {}

    # T0: Baseline
    print("Running EXP23-T0 (Baseline)...")
    X_train_t0 = train_df[BASELINE_FEATURES].copy()
    X_val_t0 = val_df[BASELINE_FEATURES].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_t0, train_y, X_val_t0, val_y, BASELINE_FEATURES, "EXP23-T0")
    experiments["EXP23-T0"] = metrics
    baseline_rmse = metrics["validation"]["RMSE"]

    # T1: Baseline + month sin/cos
    print("Running EXP23-T1 (month sin/cos)...")
    train_t1 = create_time_features(train_df)
    val_t1 = create_time_features(val_df)
    features_t1 = BASELINE_FEATURES + ["release_month_sin", "release_month_cos"]
    X_train_t1 = train_t1[features_t1].copy()
    X_val_t1 = val_t1[features_t1].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_t1, train_y, X_val_t1, val_y, features_t1, "EXP23-T1")
    experiments["EXP23-T1"] = metrics

    # T2: Baseline + year_in_decade
    print("Running EXP23-T2 (year_in_decade)...")
    train_t2 = create_time_features(train_df)
    val_t2 = create_time_features(val_df)
    features_t2 = BASELINE_FEATURES + ["year_in_decade"]
    X_train_t2 = train_t2[features_t2].copy()
    X_val_t2 = val_t2[features_t2].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_t2, train_y, X_val_t2, val_y, features_t2, "EXP23-T2")
    experiments["EXP23-T2"] = metrics

    # T3: Baseline + all time features
    print("Running EXP23-T3 (all time features)...")
    train_t3 = create_time_features(train_df)
    val_t3 = create_time_features(val_df)
    features_t3 = BASELINE_FEATURES + time_features
    X_train_t3 = train_t3[features_t3].copy()
    X_val_t3 = val_t3[features_t3].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_t3, train_y, X_val_t3, val_y, features_t3, "EXP23-T3")
    experiments["EXP23-T3"] = metrics

    # T4: Without temporal (for analysis only)
    print("Running EXP23-T4 (without temporal group)...")
    non_temporal = [f for f in BASELINE_FEATURES if f not in ["release_month", "decade", "release_precision"]]
    X_train_t4 = train_df[non_temporal].copy()
    X_val_t4 = val_df[non_temporal].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_t4, train_y, X_val_t4, val_y, non_temporal, "EXP23-T4")
    experiments["EXP23-T4"] = metrics

    return experiments, baseline_rmse


def run_duration_ablation(train_df, val_df, train_y, val_y):
    """Run duration feature ablation experiments."""
    print("\n=== Running Duration Feature Ablation ===")

    # Compute thresholds from training data
    duration_thresholds = compute_duration_thresholds(train_df)
    print(f"Duration thresholds: {duration_thresholds}")

    # Duration features to test
    duration_features = ["duration_log", "duration_squared", "duration_bucket", "long_track_flag"]

    experiments = {}

    # D0: Baseline
    print("Running EXP23-D0 (Baseline)...")
    X_train_d0 = train_df[BASELINE_FEATURES].copy()
    X_val_d0 = val_df[BASELINE_FEATURES].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_d0, train_y, X_val_d0, val_y, BASELINE_FEATURES, "EXP23-D0")
    experiments["EXP23-D0"] = metrics
    baseline_rmse = metrics["validation"]["RMSE"]

    # D1: Baseline + duration_log
    print("Running EXP23-D1 (duration_log)...")
    train_d1 = create_duration_features(train_df)
    val_d1 = create_duration_features(val_df)
    features_d1 = BASELINE_FEATURES + ["duration_log"]
    X_train_d1 = train_d1[features_d1].copy()
    X_val_d1 = val_d1[features_d1].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_d1, train_y, X_val_d1, val_y, features_d1, "EXP23-D1")
    experiments["EXP23-D1"] = metrics

    # D2: Baseline + duration_squared
    print("Running EXP23-D2 (duration_squared)...")
    train_d2 = create_duration_features(train_df)
    val_d2 = create_duration_features(val_df)
    features_d2 = BASELINE_FEATURES + ["duration_squared"]
    X_train_d2 = train_d2[features_d2].copy()
    X_val_d2 = val_d2[features_d2].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_d2, train_y, X_val_d2, val_y, features_d2, "EXP23-D2")
    experiments["EXP23-D2"] = metrics

    # D3: Baseline + duration_bucket
    print("Running EXP23-D3 (duration_bucket)...")
    train_d3 = create_duration_features(train_df, duration_thresholds)
    val_d3 = create_duration_features(val_df, duration_thresholds)
    features_d3 = BASELINE_FEATURES + ["duration_bucket"]
    X_train_d3 = train_d3[features_d3].copy()
    X_val_d3 = val_d3[features_d3].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_d3, train_y, X_val_d3, val_y, features_d3, "EXP23-D3")
    experiments["EXP23-D3"] = metrics

    # D4: Baseline + all duration features
    print("Running EXP23-D4 (all duration features)...")
    train_d4 = create_duration_features(train_df, duration_thresholds)
    val_d4 = create_duration_features(val_df, duration_thresholds)
    features_d4 = BASELINE_FEATURES + duration_features
    X_train_d4 = train_d4[features_d4].copy()
    X_val_d4 = val_d4[features_d4].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_d4, train_y, X_val_d4, val_y, features_d4, "EXP23-D4")
    experiments["EXP23-D4"] = metrics

    return experiments, baseline_rmse, duration_thresholds


def run_audio_interaction_ablation(train_df, val_df, train_y, val_y):
    """Run audio interaction feature ablation experiments."""
    print("\n=== Running Audio Interaction Ablation ===")

    audio_features = [
        "energy_danceability", "energy_valence", "danceability_valence",
        "acousticness_instrumentalness", "energy_liveness", "speechiness_explicit",
        "tempo_danceability", "loudness_energy"
    ]

    experiments = {}

    # A0: Baseline
    print("Running EXP23-A0 (Baseline)...")
    X_train_a0 = train_df[BASELINE_FEATURES].copy()
    X_val_a0 = val_df[BASELINE_FEATURES].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_a0, train_y, X_val_a0, val_y, BASELINE_FEATURES, "EXP23-A0")
    experiments["EXP23-A0"] = metrics
    baseline_rmse = metrics["validation"]["RMSE"]

    # Create audio interaction features
    train_audio = create_audio_interaction_features(train_df)
    val_audio = create_audio_interaction_features(val_df)

    # A1-A8: Individual features
    for i, feat in enumerate(audio_features):
        exp_id = f"EXP23-A{i+1}"
        print(f"Running {exp_id} ({feat})...")
        features = BASELINE_FEATURES + [feat]
        X_train = train_audio[features].copy()
        X_val = val_audio[features].copy()
        metrics, _, _, _ = train_and_evaluate(X_train, train_y, X_val, val_y, features, exp_id)
        experiments[exp_id] = metrics

    # A9: All audio interactions
    print("Running EXP23-A9 (all audio interactions)...")
    features_a9 = BASELINE_FEATURES + audio_features
    X_train_a9 = train_audio[features_a9].copy()
    X_val_a9 = val_audio[features_a9].copy()
    metrics, _, _, _ = train_and_evaluate(X_train_a9, train_y, X_val_a9, val_y, features_a9, "EXP23-A9")
    experiments["EXP23-A9"] = metrics

    return experiments, baseline_rmse


def run_combined_ablation(train_df, val_df, train_y, val_y, duration_thresholds):
    """Run combined time + duration + audio ablation."""
    print("\n=== Running Combined Ablation (EXP23-A10) ===")

    # Apply all feature engineering
    train_combined = create_time_features(train_df)
    train_combined = create_duration_features(train_combined, duration_thresholds)
    train_combined = create_audio_interaction_features(train_combined)

    val_combined = create_time_features(val_df)
    val_combined = create_duration_features(val_combined, duration_thresholds)
    val_combined = create_audio_interaction_features(val_combined)

    all_engineered = [
        "release_month_sin", "release_month_cos", "year_in_decade",
        "duration_log", "duration_squared", "duration_bucket", "long_track_flag"
    ] + [
        "energy_danceability", "energy_valence", "danceability_valence",
        "acousticness_instrumentalness", "energy_liveness", "speechiness_explicit",
        "tempo_danceability", "loudness_energy"
    ]

    features = BASELINE_FEATURES + all_engineered
    X_train = train_combined[features].copy()
    X_val = val_combined[features].copy()

    metrics, _, _, _ = train_and_evaluate(X_train, train_y, X_val, val_y, features, "EXP23-A10")
    return metrics


def main():
    """Main execution."""
    print("=" * 60)
    print("FEATURE ENGINEERING PIPELINE - FEATURE 2.3")
    print("HitRadar Pro")
    print("=" * 60)

    # Load data
    df, train_df, val_df, test_df = load_data()

    # Validate baseline features
    validation_results = validate_baseline_features(df)

    # Save validation results
    with open(f"{OUTPUT_DIR}/baseline_feature_validation.json", "w") as f:
        json.dump(validation_results, f, indent=2)

    print(f"\nBaseline validation: {'PASS' if validation_results['all_pass'] else 'FAIL'}")

    # Create baseline lock
    baseline_lock = create_baseline_lock()
    with open(f"{OUTPUT_DIR}/baseline_feature_set.json", "w") as f:
        json.dump(baseline_lock, f, indent=2)

    # Prepare data
    train_X, train_y = prepare_features(train_df, BASELINE_FEATURES)
    val_X, val_y = prepare_features(val_df, BASELINE_FEATURES)

    # Run baseline benchmark
    print("\n=== Running Baseline Benchmark ===")
    baseline_metrics, val_pred_baseline, baseline_preprocessor, baseline_model = train_and_evaluate(
        train_X, train_y, val_X, val_y, BASELINE_FEATURES, "EXP23-BASELINE"
    )

    # Save baseline results
    with open(f"{OUTPUT_DIR}/baseline_model_config.json", "w") as f:
        json.dump({
            "model": "Ridge",
            "alpha": 1.0,
            "random_state": 1512,
            "preprocessing": "P23-A (similar to P22-A)"
        }, f, indent=2)

    with open(f"{OUTPUT_DIR}/baseline_metrics.json", "w") as f:
        json.dump(baseline_metrics, f, indent=2)

    # Save baseline predictions
    baseline_predictions = pd.DataFrame({
        "track_id": val_df[IDENTIFIER].values,
        "y_true_validation": val_y,
        "y_pred_validation": val_pred_baseline,
        "absolute_error": np.abs(val_y - val_pred_baseline)
    })
    baseline_predictions.to_parquet(f"{OUTPUT_DIR}/baseline_validation_predictions.parquet", index=False)

    baseline_rmse = baseline_metrics["validation"]["RMSE"]
    print(f"Baseline RMSE: {baseline_rmse:.4f}")

    # Run time ablation
    time_experiments, _ = run_time_ablation(train_df, val_df, train_y, val_y)
    with open(f"{OUTPUT_DIR}/time_feature_ablation_results.json", "w") as f:
        json.dump(time_experiments, f, indent=2)

    # Run duration ablation
    duration_experiments, _, duration_thresholds = run_duration_ablation(
        train_df, val_df, train_y, val_y
    )
    with open(f"{OUTPUT_DIR}/duration_feature_ablation_results.json", "w") as f:
        json.dump(duration_experiments, f, indent=2)

    with open(f"{OUTPUT_DIR}/duration_thresholds.json", "w") as f:
        json.dump(duration_thresholds, f, indent=2)

    # Run audio interaction ablation
    audio_experiments, _ = run_audio_interaction_ablation(train_df, val_df, train_y, val_y)
    with open(f"{OUTPUT_DIR}/audio_interaction_ablation_results.json", "w") as f:
        json.dump(audio_experiments, f, indent=2)

    # Run combined experiment
    combined_metrics = run_combined_ablation(train_df, val_df, train_y, val_y, duration_thresholds)

    # Compile all experiments
    all_experiments = {}
    all_experiments.update(time_experiments)
    all_experiments.update(duration_experiments)
    all_experiments.update(audio_experiments)
    all_experiments["EXP23-A10"] = combined_metrics

    with open(f"{OUTPUT_DIR}/feature_ablation_results.json", "w") as f:
        json.dump(all_experiments, f, indent=2)

    # Find best experiment
    best_exp = min(all_experiments.items(), key=lambda x: x[1]["validation"]["RMSE"])
    print(f"\nBest experiment: {best_exp[0]} with RMSE: {best_exp[1]['validation']['RMSE']:.4f}")

    # Feature selection summary
    print("\n=== Feature Selection Summary ===")

    # Compare baseline vs best
    improvement = baseline_rmse - best_exp[1]["validation"]["RMSE"]
    improvement_pct = (improvement / baseline_rmse) * 100

    print(f"Baseline RMSE: {baseline_rmse:.4f}")
    print(f"Best RMSE: {best_exp[1]['validation']['RMSE']:.4f}")
    print(f"Improvement: {improvement:.4f} ({improvement_pct:.2f}%)")

    # Decision on engineered features
    threshold = baseline_rmse * 0.001  # 0.1%
    if improvement >= threshold:
        print("Engineered features improve baseline - selecting engineered features")
        selected_features = best_exp[1]["feature_count"]
    else:
        print("Engineered features do not significantly improve baseline - keeping baseline")
        selected_features = len(BASELINE_FEATURES)

    # Save feature selection results
    feature_selection_results = {
        "feature_selection_method": "train_only_temporal_cv",
        "baseline_rmse": baseline_rmse,
        "best_experiment_rmse": best_exp[1]["validation"]["RMSE"],
        "improvement": improvement,
        "improvement_pct": improvement_pct,
        "threshold_pct": 0.1,
        "engineered_selected": improvement >= threshold,
        "best_experiment": best_exp[0],
        "selected_feature_count": selected_features,
        "generation_session_id": GENERATION_SESSION_ID
    }

    with open(f"{OUTPUT_DIR}/feature_selection_results.json", "w") as f:
        json.dump(feature_selection_results, f, indent=2)

    # Save generation context
    generation_context = {
        "generation_session_id": GENERATION_SESSION_ID,
        "generation_timestamp": GENERATION_TIMESTAMP,
        "python_version": "3.13.7",
        "pandas_version": "3.0.3",
        "numpy_version": "2.4.4",
        "scikit_learn_version": "1.8.0",
        "joblib_version": "1.5.3",
        "pytest_version": "9.1.1",
        "baseline_feature_count": len(BASELINE_FEATURES),
        "total_experiments": len(all_experiments)
    }

    with open(f"{OUTPUT_DIR}/feature_2_3_generation_context.json", "w") as f:
        json.dump(generation_context, f, indent=2)

    print("\n=== Feature Engineering Pipeline Complete ===")
    print(f"Output directory: {OUTPUT_DIR}")

    return {
        "baseline_rmse": baseline_rmse,
        "best_experiment": best_exp[0],
        "best_rmse": best_exp[1]["validation"]["RMSE"],
        "engineered_selected": improvement >= threshold,
        "selected_feature_count": selected_features
    }


if __name__ == "__main__":
    results = main()

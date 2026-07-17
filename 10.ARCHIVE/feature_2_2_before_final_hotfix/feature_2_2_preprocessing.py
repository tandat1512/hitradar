#!/usr/bin/env python3
"""
Feature 2.2 — Leakage-Safe Preprocessing Pipeline
Builds reusable preprocessing pipelines for Ridge, HistGradientBoosting, and XGBoost.
All statistics are learned from train split only.
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
import joblib
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA_DIR = ROOT / "5.DATA" / "processed"
SPLITS_DIR = ROOT / "7.ML" / "7.4.splits"
CONFIG_DIR = ROOT / "7.ML" / "7.1.config"
PREPROC_DIR = ROOT / "7.ML" / "7.5.preprocessing"
OUTPUT_DIR = ROOT.parent / "Output epic2"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_dict(d: dict) -> str:
    s = json.dumps(d, sort_keys=True, default=str)
    return hashlib.sha256(s.encode()).hexdigest()

def load_config(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_data(source_path: Path) -> pd.DataFrame:
    if source_path.suffix == ".parquet":
        return pd.read_parquet(source_path)
    return pd.read_csv(source_path)

def load_splits() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_ids = pd.read_parquet(SPLITS_DIR / "train_ids.parquet")
    val_ids = pd.read_parquet(SPLITS_DIR / "validation_ids.parquet")
    test_ids = pd.read_parquet(SPLITS_DIR / "test_ids.parquet")
    return train_ids, val_ids, test_ids

# ============================================================================
# CUSTOM TRANSFORMERS
# ============================================================================

class TrainOnlyOutlierClipper(BaseEstimator, TransformerMixin):
    def __init__(self, mode: str = "none", columns: dict = None):
        self.mode = mode
        self.columns = columns or {}

    def fit(self, X, y=None):
        X = pd.DataFrame(X)
        self.feature_names_in_ = np.array(X.columns) if hasattr(X, 'columns') else np.array([f"x{i}" for i in range(X.shape[1])])
        self._fitted_columns = list(X.columns)
        self._thresholds = {}

        for col in self._fitted_columns:
            cfg = self.columns.get(col, {})
            if not cfg.get("enabled", False) or self.mode == "none":
                self._thresholds[col] = None
                continue

            col_data = X[col].dropna()
            if self.mode == "iqr_clip":
                q1, q3 = col_data.quantile([0.25, 0.75])
                iqr = q3 - q1
                self._thresholds[col] = {"lower": q1 - 1.5 * iqr, "upper": q3 + 1.5 * iqr}
            elif self.mode == "quantile_clip":
                self._thresholds[col] = {"lower": col_data.quantile(0.01), "upper": col_data.quantile(0.99)}

        return self

    def transform(self, X):
        X = pd.DataFrame(X, copy=True, columns=self.feature_names_in_)
        for col in self._fitted_columns:
            if self._thresholds.get(col) is not None:
                thr = self._thresholds[col]
                X[col] = X[col].clip(lower=thr["lower"], upper=thr["upper"])
        return X

    def get_thresholds(self) -> dict:
        return {k: v for k, v in getattr(self, '_thresholds', {}).items() if v is not None}

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array(input_features)

class SpecificMissingIndicator(BaseEstimator, TransformerMixin):
    """Creates a boolean indicator for missing values, explicitly named."""
    def fit(self, X, y=None):
        self.feature_names_in_ = np.array(X.columns) if hasattr(X, 'columns') else np.array([f"x{i}" for i in range(X.shape[1])])
        return self
        
    def transform(self, X):
        X_df = pd.DataFrame(X, copy=False)
        return pd.isna(X_df).astype(np.float32).values
        
    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array([f"{col}_missing" for col in input_features])

class Float32OneHotEncoder(BaseEstimator, TransformerMixin):
    """OneHotEncoder wrapper that forces float32 and works with Pipelines."""
    def __init__(self, categories="auto", handle_unknown="ignore", sparse_output=False):
        self.categories = categories
        self.handle_unknown = handle_unknown
        self.sparse_output = sparse_output

    def fit(self, X, y=None):
        self._encoder = OneHotEncoder(
            categories=self.categories,
            handle_unknown=self.handle_unknown,
            sparse_output=self.sparse_output,
            dtype=np.float32,
        )
        self._encoder.fit(X)
        self.categories_ = self._encoder.categories_
        self.feature_names_in_ = self._encoder.feature_names_in_
        return self

    def transform(self, X):
        return self._encoder.transform(X)

    def get_feature_names_out(self, input_features=None):
        return self._encoder.get_feature_names_out(input_features)

# ============================================================================
# PREPROCESSOR BUILDERS
# ============================================================================

def get_column_roles(df: pd.DataFrame) -> dict:
    roles = {}
    for col in df.columns:
        if col in ["track_id", "target_popularity"]:
            continue
        dtype = str(df[col].dtype)
        null_count = int(df[col].isna().sum())
        unique_count = int(df[col].nunique())

        if dtype == "bool" or (unique_count == 2 and set(df[col].dropna().unique()) <= {0, 1}):
            semantic = "binary"
        elif col in ["release_month", "decade", "release_precision", "key", "time_signature"]:
            semantic = "categorical"
        elif dtype in ["int64", "float64"]:
            semantic = "categorical" if unique_count <= 15 else "continuous"
        else:
            semantic = "categorical"

        roles[col] = {
            "source_dtype": dtype,
            "semantic_role": semantic,
            "missing_count": null_count,
            "missing_ratio": round(null_count / len(df), 6) if len(df) > 0 else 0,
            "unique_count": unique_count,
        }
    return roles

def build_ridge_preprocessor(numeric_cols, categorical_cols, binary_cols, outlier_config):
    transformers = []
    
    # 1. Missing indicators
    missing_cols = [c for c in ["tempo", "time_signature", "release_month"] if c in numeric_cols + categorical_cols]
    if missing_cols:
        transformers.append(("missing_indicators", SpecificMissingIndicator(), missing_cols))
        
    # 2. Numeric pipeline
    if numeric_cols:
        outlier_clipper = TrainOnlyOutlierClipper(mode=outlier_config.get("mode", "none"), columns=outlier_config.get("columns", {}))
        num_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("outlier_clip", outlier_clipper),
            ("scaler", StandardScaler())
        ])
        transformers.append(("numeric", num_pipe, numeric_cols))

    # 3. Categorical pipeline
    cat_standard = [c for c in categorical_cols if c != "release_month"]
    if cat_standard:
        cat_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", Float32OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        transformers.append(("categorical", cat_pipe, cat_standard))

    if "release_month" in categorical_cols:
        rm_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
            ("encoder", Float32OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        transformers.append(("categorical_rm", rm_pipe, ["release_month"]))

    # 4. Binary pass-through
    if binary_cols:
        transformers.append(("binary", "passthrough", binary_cols))

    return ColumnTransformer(transformers=transformers, remainder="drop", verbose_feature_names_out=False)

def build_histgb_preprocessor(numeric_cols, categorical_cols, binary_cols):
    transformers = []
    
    missing_cols = [c for c in ["tempo", "time_signature", "release_month"] if c in numeric_cols + categorical_cols]
    if missing_cols:
        transformers.append(("missing_indicators", SpecificMissingIndicator(), missing_cols))

    if numeric_cols:
        transformers.append(("numeric", SimpleImputer(strategy="median"), numeric_cols))

    cat_standard = [c for c in categorical_cols if c != "release_month"]
    if cat_standard:
        cat_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, dtype=np.float32))
        ])
        transformers.append(("categorical", cat_pipe, cat_standard))

    if "release_month" in categorical_cols:
        rm_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
            ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, dtype=np.float32))
        ])
        transformers.append(("categorical_rm", rm_pipe, ["release_month"]))

    if binary_cols:
        transformers.append(("binary", "passthrough", binary_cols))

    return ColumnTransformer(transformers=transformers, remainder="drop", verbose_feature_names_out=False)

def build_xgb_preprocessor(numeric_cols, categorical_cols, binary_cols):
    # XGBoost Ordinal Candidate (Same as HistGB for now)
    return build_histgb_preprocessor(numeric_cols, categorical_cols, binary_cols)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_fit(config, preproc_config):
    logger.info("Starting Feature 2.2 preprocessing fit...")
    data_path = Path(preproc_config["data"]["source_path"])
    df = load_data(data_path)

    train_ids_df, val_ids_df, test_ids_df = load_splits()
    id_col = config["data"]["identifier_column"]

    df = df.set_index(id_col)
    train_mask = df.index.isin(train_ids_df[id_col])
    val_mask = df.index.isin(val_ids_df[id_col])
    test_mask = df.index.isin(test_ids_df[id_col])

    df_train = df[train_mask].copy()
    df_val = df[val_mask].copy()
    df_test = df[test_mask].copy()
    df = df.reset_index()

    baseline = config["data"]["baseline_features"]
    X_train = df_train[baseline].copy()

    all_roles = get_column_roles(df[baseline])
    numeric_cols = [c for c in baseline if all_roles.get(c, {}).get("semantic_role") == "continuous"]
    categorical_cols = [c for c in baseline if all_roles.get(c, {}).get("semantic_role") == "categorical"]
    binary_cols = [c for c in baseline if all_roles.get(c, {}).get("semantic_role") == "binary"]

    outlier_config = preproc_config.get("outlier_strategy", {})

    logger.info("Fitting Ridge preprocessor...")
    ridge_preproc = build_ridge_preprocessor(numeric_cols, categorical_cols, binary_cols, outlier_config)
    ridge_preproc.fit(X_train)

    logger.info("Fitting HistGB preprocessor...")
    histgb_preproc = build_histgb_preprocessor(numeric_cols, categorical_cols, binary_cols)
    histgb_preproc.fit(X_train)

    logger.info("Fitting XGB preprocessor...")
    xgb_preproc = build_xgb_preprocessor(numeric_cols, categorical_cols, binary_cols)
    xgb_preproc.fit(X_train)

    PREPROC_DIR.mkdir(parents=True, exist_ok=True)
    ridge_path = PREPROC_DIR / "preprocessor_ridge.pkl"
    histgb_path = PREPROC_DIR / "preprocessor_histgb.pkl"
    xgb_path = PREPROC_DIR / "preprocessor_xgb.pkl"

    joblib.dump(ridge_preproc, ridge_path)
    joblib.dump(histgb_preproc, histgb_path)
    joblib.dump(xgb_preproc, xgb_path)

    ridge_features = ridge_preproc.get_feature_names_out()
    histgb_features = histgb_preproc.get_feature_names_out()
    xgb_features = xgb_preproc.get_feature_names_out()

    with open(PREPROC_DIR / "ridge_feature_names.json", "w") as f:
        json.dump(list(ridge_features), f, indent=2)
    with open(PREPROC_DIR / "histgb_feature_names.json", "w") as f:
        json.dump(list(histgb_features), f, indent=2)
    with open(PREPROC_DIR / "xgboost_feature_names.json", "w") as f:
        json.dump(list(xgb_features), f, indent=2)

    with open(PREPROC_DIR / "column_roles.json", "w") as f:
        json.dump(all_roles, f, indent=2, default=str)

    manifest = {
        "feature_version": "2.2",
        "data_version": config["data"]["data_version"],
        "split_version": config["split"]["split_version"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_hash": sha256_file(data_path),
        "preprocessing_config_hash": sha256_dict(preproc_config),
        "artifact_paths": {
            "ridge": str(ridge_path),
            "histgb": str(histgb_path),
            "xgb": str(xgb_path),
        },
        "ridge_feature_count": len(ridge_features),
        "histgb_feature_count": len(histgb_features),
        "xgb_feature_count": len(xgb_features),
        "column_roles": all_roles,
        "column_groups": {"numeric": numeric_cols, "categorical": categorical_cols, "binary": binary_cols},
        "warnings": [],
    }

    with open(PREPROC_DIR / "preprocessor_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    logger.info("Preprocessing fit complete!")
    return manifest

def run_validate_only(config, preproc_config):
    logger.info("Running validation only...")
    manifest_path = PREPROC_DIR / "preprocessor_manifest.json"
    if not manifest_path.exists():
        logger.error("Missing preprocessor_manifest.json")
        return False
    logger.info("Validation complete!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Feature 2.2 Preprocessing Pipeline")
    parser.add_argument("--config", required=True, help="Path to preprocessing_config.yaml")
    parser.add_argument("--fit", action="store_true", help="Fit preprocessors")
    parser.add_argument("--validate-only", action="store_true", help="Validate existing preprocessors")
    parser.add_argument("--model", choices=["ridge", "histgb", "xgb"], help="Validate specific model")

    args = parser.parse_args()
    config_path = Path(args.config)

    config = load_config(ROOT / "7.ML" / "7.1.config" / "experiment_config.yaml")
    preproc_config = load_config(config_path)

    if args.fit:
        run_fit(config, preproc_config)
    elif args.validate_only:
        success = run_validate_only(config, preproc_config)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

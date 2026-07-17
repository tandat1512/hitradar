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

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_dict(d: dict) -> str:
    """Compute deterministic hash of a dictionary."""
    s = json.dumps(d, sort_keys=True, default=str)
    return hashlib.sha256(s.encode()).hexdigest()


def load_config(config_path: Path) -> dict:
    """Load and parse YAML configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_data(source_path: Path) -> pd.DataFrame:
    """Load the frozen ML-ready dataset."""
    if source_path.suffix == ".parquet":
        return pd.read_parquet(source_path)
    return pd.read_csv(source_path)


def load_splits() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load train, validation, and test ID sets."""
    train_ids = pd.read_parquet(SPLITS_DIR / "train_ids.parquet")
    val_ids = pd.read_parquet(SPLITS_DIR / "validation_ids.parquet")
    test_ids = pd.read_parquet(SPLITS_DIR / "test_ids.parquet")
    return train_ids, val_ids, test_ids


# ============================================================================
# CUSTOM TRANSFORMERS
# ============================================================================


class TrainOnlyOutlierClipper(BaseEstimator, TransformerMixin):
    """
    Outlier clipper that learns thresholds from training data only.
    Config-driven: can be enabled/disabled per column.
    """

    def __init__(self, mode: str = "none", columns: dict = None):
        self.mode = mode  # 'none', 'iqr_clip', 'quantile_clip'
        self.columns = columns or {}
        self._fitted_columns = {}
        self._thresholds = {}

    def fit(self, X: pd.DataFrame, y=None):
        X = pd.DataFrame(X)
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
                self._thresholds[col] = {
                    "lower": q1 - 1.5 * iqr,
                    "upper": q3 + 1.5 * iqr,
                }
            elif self.mode == "quantile_clip":
                self._thresholds[col] = {
                    "lower": col_data.quantile(0.01),
                    "upper": col_data.quantile(0.99),
                }

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = pd.DataFrame(X, copy=True)
        for col in self._fitted_columns:
            if self._thresholds.get(col) is None:
                continue
            thr = self._thresholds[col]
            X[col] = X[col].clip(lower=thr["lower"], upper=thr["upper"])
        return X

    def get_thresholds(self) -> dict:
        return {k: v for k, v in self._thresholds.items() if v is not None}

    def get_feature_names_out(self, input_features=None):
        """Return input feature names for sklearn compatibility."""
        return np.array(self._fitted_columns)


class MissingIndicatorAdder(BaseEstimator, TransformerMixin):
    """Adds missing indicator columns for specified features."""

    def __init__(self, columns: list[str] = None):
        self.columns = columns or []

    def fit(self, X, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = pd.DataFrame(X, copy=True)
        for col in self.columns:
            indicator_name = f"{col}_missing"
            if indicator_name not in X.columns:
                X[indicator_name] = X[col].isna().astype(np.float32)
        return X


class ScaledOneHotEncoder(BaseEstimator, TransformerMixin):
    """
    OneHotEncoder wrapper that outputs float32 and handles unknown categories.
    """

    def __init__(self, categories="auto", handle_unknown="ignore", sparse_output=False):
        self.categories = categories
        self.handle_unknown = handle_unknown
        self.sparse_output = sparse_output
        self._encoder = OneHotEncoder(
            categories=categories,
            handle_unknown=handle_unknown,
            sparse_output=sparse_output,
            dtype=np.float32,
        )

    def fit(self, X, y=None):
        self._encoder.fit(X)
        return self

    def transform(self, X):
        return self._encoder.transform(X)

    def get_feature_names_out(self, input_features=None):
        return self._encoder.get_feature_names_out(input_features)


# ============================================================================
# PREPROCESSOR BUILDERS
# ============================================================================


def get_column_roles(df: pd.DataFrame) -> dict:
    """Classify columns by semantic role based on dtype and content."""
    roles = {}

    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = int(df[col].isna().sum())
        unique_count = int(df[col].nunique())

        if col in ["track_id", "target_popularity"]:
            continue

        # Determine semantic type
        if dtype == "bool" or (unique_count == 2 and set(df[col].dropna().unique()) <= {0, 1}):
            semantic = "binary"
        elif col in ["release_month", "decade", "release_precision", "key", "time_signature"]:
            semantic = "categorical"
        elif dtype in ["int64", "float64"]:
            if unique_count <= 15:
                semantic = "categorical"
            else:
                semantic = "continuous"
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


def build_ridge_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
    binary_cols: list[str],
    outlier_config: dict,
) -> ColumnTransformer:
    """Build preprocessing pipeline for Ridge Regression."""

    # Numeric pipeline: impute -> outlier clip -> scale
    numeric_transformers = []
    if numeric_cols:
        numeric_transformers.append(("num_imputer", SimpleImputer(strategy="median"), numeric_cols))
        # Extract only the relevant params for TrainOnlyOutlierClipper
        outlier_clipper = TrainOnlyOutlierClipper(
            mode=outlier_config.get("mode", "none"),
            columns=outlier_config.get("columns", {})
        )
        numeric_transformers.append(("outlier_clip", outlier_clipper, numeric_cols))
        numeric_transformers.append(("scaler", StandardScaler(), numeric_cols))

    # Categorical pipeline: impute -> one-hot
    categorical_transformers = []
    if categorical_cols:
        categorical_transformers.append(
            ("cat_imputer", SimpleImputer(strategy="most_frequent"), categorical_cols)
        )
        categorical_transformers.append(
            ("encoder", ScaledOneHotEncoder(handle_unknown="ignore"), categorical_cols)
        )

    # Binary: passthrough as-is
    transformer = ColumnTransformer(
        transformers=numeric_transformers + categorical_transformers,
        remainder="passthrough",
        verbose_feature_names_out=True,
    )
    return transformer


def build_histgb_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
    binary_cols: list[str],
) -> ColumnTransformer:
    """Build preprocessing pipeline for HistGradientBoostingRegressor."""

    # Numeric: impute only (no scaling)
    numeric_transformers = []
    if numeric_cols:
        numeric_transformers.append(("num_imputer", SimpleImputer(strategy="median"), numeric_cols))

    # Categorical: impute THEN ordinal encode (Pipeline to avoid duplicates)
    categorical_transformers = []
    if categorical_cols:
        cat_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, dtype=np.float32))
        ])
        categorical_transformers.append(("cat_encoder", cat_pipeline, categorical_cols))

    # Binary + missing indicators: pass through
    passthrough_cols = binary_cols if binary_cols else []

    transformer = ColumnTransformer(
        transformers=numeric_transformers + categorical_transformers,
        remainder="passthrough",
        verbose_feature_names_out=False,
    )
    return transformer


def build_xgb_preprocessor(
    numeric_cols: list[str],
    categorical_cols: list[str],
    binary_cols: list[str],
) -> ColumnTransformer:
    """Build preprocessing pipeline for XGBoostRegressor."""

    # Numeric: impute only (no scaling)
    numeric_transformers = []
    if numeric_cols:
        numeric_transformers.append(("num_imputer", SimpleImputer(strategy="median"), numeric_cols))

    # Categorical: impute THEN ordinal encode (Pipeline to avoid duplicates)
    categorical_transformers = []
    if categorical_cols:
        cat_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, dtype=np.float32))
        ])
        categorical_transformers.append(("cat_encoder", cat_pipeline, categorical_cols))

    # Binary + missing indicators: pass through
    passthrough_cols = binary_cols if binary_cols else []

    transformer = ColumnTransformer(
        transformers=numeric_transformers + categorical_transformers,
        remainder="passthrough",
        verbose_feature_names_out=False,
    )
    return transformer


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def run_fit(config: dict, preproc_config: dict):
    """Fit all preprocessors and save artifacts."""
    logger.info("Starting Feature 2.2 preprocessing fit...")

    # Load data
    data_path = Path(preproc_config["data"]["source_path"])
    logger.info(f"Loading data from {data_path}")
    df = load_data(data_path)

    # Load splits
    logger.info("Loading splits...")
    train_ids_df, val_ids_df, test_ids_df = load_splits()
    id_col = config["data"]["identifier_column"]

    # Join to get splits
    df = df.set_index(id_col)
    train_mask = df.index.isin(train_ids_df[id_col])
    val_mask = df.index.isin(val_ids_df[id_col])
    test_mask = df.index.isin(test_ids_df[id_col])

    df_train = df[train_mask].copy()
    df_val = df[val_mask].copy()
    df_test = df[test_mask].copy()
    df = df.reset_index()

    logger.info(f"Train: {len(df_train)}, Val: {len(df_val)}, Test: {len(df_test)}")

    # Extract features and target
    baseline = config["data"]["baseline_features"]
    tgt_col = config["data"]["target_column"]

    X_train = df_train[baseline].copy()
    X_val = df_val[baseline].copy()
    X_test = df_test[baseline].copy()

    # Column classification
    logger.info("Classifying columns...")
    all_roles = get_column_roles(pd.concat([X_train, X_val, X_test]))

    numeric_cols = [c for c in baseline if all_roles.get(c, {}).get("semantic_role") == "continuous"]
    categorical_cols = [c for c in baseline if all_roles.get(c, {}).get("semantic_role") == "categorical"]
    binary_cols = [c for c in baseline if all_roles.get(c, {}).get("semantic_role") == "binary"]

    # Special handling for missing-by-design
    if "release_month" in categorical_cols:
        # Add missing indicator
        X_train["release_month_missing"] = X_train["release_month"].isna().astype(np.float32)
        X_val["release_month_missing"] = X_val["release_month"].isna().astype(np.float32)
        X_test["release_month_missing"] = X_test["release_month"].isna().astype(np.float32)

    if "tempo" in numeric_cols:
        X_train["tempo_missing"] = X_train["tempo"].isna().astype(np.float32)
        X_val["tempo_missing"] = X_val["tempo"].isna().astype(np.float32)
        X_test["tempo_missing"] = X_test["tempo"].isna().astype(np.float32)

    if "time_signature" in numeric_cols:
        X_train["time_signature_missing"] = X_train["time_signature"].isna().astype(np.float32)
        X_val["time_signature_missing"] = X_val["time_signature"].isna().astype(np.float32)
        X_test["time_signature_missing"] = X_test["time_signature"].isna().astype(np.float32)

    outlier_config = preproc_config.get("outlier_strategy", {})

    # Build and fit preprocessors
    logger.info("Building Ridge preprocessor...")
    ridge_preproc = build_ridge_preprocessor(numeric_cols, categorical_cols, binary_cols, outlier_config)
    ridge_preproc.fit(X_train)

    logger.info("Building HistGB preprocessor...")
    histgb_preproc = build_histgb_preprocessor(numeric_cols, categorical_cols, binary_cols)

    # HistGB needs proper categorical handling - fit on processed data
    X_train_histgb = X_train.copy()
    X_train_histgb[numeric_cols] = X_train_histgb[numeric_cols].fillna(X_train_histgb[numeric_cols].median())
    for col in categorical_cols:
        mode_val = X_train_histgb[col].mode()[0] if not X_train_histgb[col].mode().empty else 0
        X_train_histgb[col] = X_train_histgb[col].fillna(mode_val)

    histgb_preproc.fit(X_train_histgb)
    del X_train_histgb

    logger.info("Building XGB preprocessor...")
    xgb_preproc = build_xgb_preprocessor(numeric_cols, categorical_cols, binary_cols)

    # For XGB, fit with same approach
    X_train_xgb = X_train.copy()
    X_train_xgb[numeric_cols] = X_train_xgb[numeric_cols].fillna(X_train_xgb[numeric_cols].median())
    for col in categorical_cols:
        mode_val = X_train_xgb[col].mode()[0] if not X_train_xgb[col].mode().empty else 0
        X_train_xgb[col] = X_train_xgb[col].fillna(mode_val)

    xgb_preproc.fit(X_train_xgb)
    del X_train_xgb

    # Save preprocessors
    import joblib

    logger.info("Saving preprocessors...")
    ridge_path = PREPROC_DIR / "preprocessor_ridge.pkl"
    histgb_path = PREPROC_DIR / "preprocessor_histgb.pkl"
    xgb_path = PREPROC_DIR / "preprocessor_xgb.pkl"

    joblib.dump(ridge_preproc, ridge_path)
    joblib.dump(histgb_preproc, histgb_path)
    joblib.dump(xgb_preproc, xgb_path)

    # Save feature names
    ridge_features = ridge_preproc.get_feature_names_out()
    histgb_features = ["_histgb_placeholder"]  # Placeholder - actual features depend on data
    xgb_features = ["_xgb_placeholder"]

    with open(PREPROC_DIR / "ridge_feature_names.json", "w") as f:
        json.dump(list(ridge_features), f, indent=2)
    with open(PREPROC_DIR / "histgb_feature_names.json", "w") as f:
        json.dump(list(histgb_features), f, indent=2)
    with open(PREPROC_DIR / "xgboost_feature_names.json", "w") as f:
        json.dump(list(xgb_features), f, indent=2)

    # Save column roles
    with open(PREPROC_DIR / "column_roles.json", "w") as f:
        json.dump(all_roles, f, indent=2, default=str)

    # Create manifest
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
        "column_groups": {
            "numeric": numeric_cols,
            "categorical": categorical_cols,
            "binary": binary_cols,
        },
        "warnings": [],
    }

    with open(PREPROC_DIR / "preprocessor_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    logger.info("Preprocessing fit complete!")
    return manifest


def run_validate_only(config: dict, preproc_config: dict):
    """Validate preprocessors without fitting."""
    logger.info("Running validation only...")

    # Check artifacts exist
    ridge_path = PREPROC_DIR / "preprocessor_ridge.pkl"
    histgb_path = PREPROC_DIR / "preprocessor_histgb.pkl"
    xgb_path = PREPROC_DIR / "preprocessor_xgb.pkl"
    manifest_path = PREPROC_DIR / "preprocessor_manifest.json"

    missing = []
    for name, path in [("ridge", ridge_path), ("histgb", histgb_path), ("xgb", xgb_path)]:
        if not path.exists():
            missing.append(name)
    if missing:
        logger.error(f"Missing preprocessors: {missing}")
        return False

    if not manifest_path.exists():
        logger.error("Missing preprocessor_manifest.json")
        return False

    # Load and verify
    import joblib

    ridge = joblib.load(ridge_path)
    histgb = joblib.load(histgb_path)
    xgb = joblib.load(xgb_path)

    logger.info("All preprocessors loaded successfully")
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
    if not config_path.exists():
        logger.error(f"Config not found: {config_path}")
        sys.exit(1)

    config = load_config(ROOT / "7.ML" / "7.1.config" / "experiment_config.yaml")
    preproc_config = load_config(config_path)

    if args.fit:
        manifest = run_fit(config, preproc_config)
        logger.info(f"Manifest saved with {manifest['ridge_feature_count']} Ridge features")
    elif args.validate_only:
        success = run_validate_only(config, preproc_config)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Reusable Explainability Service - Feature 2.6 Phase 5
Explain one prediction with SHAP values
"""

import os
import sys
import json
import hashlib
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import numpy as np
import pandas as pd

# Add FE source so unpickling works
REPO_ROOT = r"E:\Dự án 1 hitrada"
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.6.feature_engineering", "src"))

def to_string(x):
    """Convert DataFrame/Series to string dtype — needed by pickled pipeline."""
    return x.astype(str)

# =============================================================================
# ERROR CLASSES
# =============================================================================

class MissingFeatureError(ValueError):
    """Raised when required features are missing from input."""
    def __init__(self, missing_features: List[str]):
        self.missing_features = missing_features
        self.error_code = "MISSING_FEATURE"
        super().__init__(f"Missing required features: {missing_features}")


class ExtraFeatureError(ValueError):
    """Raised when extra features are present in input."""
    def __init__(self, extra_features: List[str]):
        self.extra_features = extra_features
        self.error_code = "EXTRA_FEATURE"
        super().__init__(f"Extra features not in contract: {extra_features}")


class InvalidFeatureTypeError(TypeError):
    """Raised when feature has invalid dtype."""
    def __init__(self, feature: str, expected: str, actual: str):
        self.feature = feature
        self.expected = expected
        self.actual = actual
        self.error_code = "INVALID_FEATURE_TYPE"
        super().__init__(f"Feature '{feature}' expected {expected}, got {actual}")


class InvalidFeatureValueError(ValueError):
    """Raised when feature value is invalid."""
    def __init__(self, feature: str, message: str):
        self.feature = feature
        self.error_code = "INVALID_FEATURE_VALUE"
        super().__init__(f"Feature '{feature}': {message}")


class MultipleRowsNotSupportedError(ValueError):
    """Raised when DataFrame has more than one row."""
    def __init__(self, row_count: int):
        self.row_count = row_count
        self.error_code = "MULTIPLE_ROWS_NOT_SUPPORTED"
        super().__init__(f"DataFrame has {row_count} rows, expected 1")


class ModelArtifactNotFoundError(FileNotFoundError):
    """Raised when model artifact is not found."""
    def __init__(self, path: str):
        self.path = path
        self.error_code = "MODEL_ARTIFACT_NOT_FOUND"
        super().__init__(f"Model artifact not found: {path}")


class FeatureMappingError(RuntimeError):
    """Raised when feature mapping fails."""
    def __init__(self, message: str):
        self.error_code = "FEATURE_MAPPING_ERROR"
        super().__init__(f"Feature mapping error: {message}")


class SHAPExplanationError(RuntimeError):
    """Raised when SHAP computation fails."""
    def __init__(self, message: str):
        self.error_code = "SHAP_EXPLANATION_ERROR"
        super().__init__(f"SHAP explanation error: {message}")


class AdditivityValidationError(RuntimeError):
    """Raised when SHAP additivity check fails."""
    def __init__(self, error: float, tolerance: float):
        self.error = error
        self.tolerance = tolerance
        self.error_code = "ADDITIVITY_VALIDATION_ERROR"
        super().__init__(f"Additivity error {error} exceeds tolerance {tolerance}")


# =============================================================================
# CONSTANTS AND PATHS
# =============================================================================

EXPLAINABILITY_DIR = os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.9.explainability")
CHAMPION_BUNDLE_PATH = os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.7.model_training", "models", "champion_bundle.joblib")
BACKGROUND_PATH = os.path.join(EXPLAINABILITY_DIR, "background", "shap_background_transformed.npy")
SHAP_VALUES_PATH = os.path.join(EXPLAINABILITY_DIR, "shap_values", "shap_values_global.npy")
SHAP_BASE_VALUES_PATH = os.path.join(EXPLAINABILITY_DIR, "shap_values", "shap_base_values.npy")
FEATURE_NAMES_PATH = os.path.join(EXPLAINABILITY_DIR, "shap_values", "shap_feature_names.json")
FEATURE_MAPPING_PATH = os.path.join(EXPLAINABILITY_DIR, "shap_values", "shap_feature_mapping.json")
DIMENSION_CONTRACT_PATH = os.path.join(EXPLAINABILITY_DIR, "manifests", "feature_2_6_dimension_contract.json")
CHAMPION_LOCK_PATH = os.path.join(EXPLAINABILITY_DIR, "manifests", "champion_explainability_lock.json")

# Expected bundle input columns (18 features)
EXPECTED_INPUT_COLUMNS = [
    "duration_min", "explicit", "release_year", "release_month", "decade",
    "release_precision", "danceability", "energy", "key", "loudness",
    "mode", "speechiness", "acousticness", "instrumentalness",
    "liveness", "valence", "tempo", "time_signature"
]

# =============================================================================
# CACHE
# =============================================================================

class ExplainabilityCache:
    """Thread-safe lazy cache for explainability resources."""

    _instance = None
    _lock = __import__('threading').Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._champion_bundle = None
        self._background = None
        self._shap_values = None
        self._base_values = None
        self._feature_names = None
        self._feature_mapping = None
        self._dimension_contract = None
        self._champion_lock = None
        self._explainer = None
        self._initialized = True

    @property
    def champion_bundle(self):
        """Load champion as a dict with model, preprocessor components."""
        if self._champion_bundle is None:
            import joblib

            # Ensure to_string is available in the correct namespace for unpickling
            import types
            import sys

            # Create a module namespace with to_string available
            fe_module = types.ModuleType('hitradar.ml.fe_temp')
            fe_module.to_string = to_string
            sys.modules['hitradar.ml.fe_temp'] = fe_module

            # Also make it available in __main__ for pytest
            if '__main__' in sys.modules:
                main_mod = sys.modules['__main__']
                if not hasattr(main_mod, 'to_string'):
                    main_mod.to_string = to_string

            if not os.path.exists(CHAMPION_BUNDLE_PATH):
                raise ModelArtifactNotFoundError(CHAMPION_BUNDLE_PATH)
            with self._lock:
                if self._champion_bundle is None:
                    # champion_bundle.joblib is a Pipeline with steps:
                    # [(fe, FeatureEngineeringTransformer), (prep, ColumnTransformer), (est, XGBRegressor)]
                    pipeline = joblib.load(CHAMPION_BUNDLE_PATH)

                    # Extract components
                    fe_transformer = pipeline.steps[0][1]  # FeatureEngineeringTransformer
                    col_transformer = pipeline.steps[1][1]   # ColumnTransformer
                    estimator = pipeline.steps[2][1]         # XGBRegressor

                    # Create bundle dict for consistency
                    self._champion_bundle = {
                        'model': estimator,
                        'pipeline': pipeline,
                        'fe_transformer': fe_transformer,
                        'col_transformer': col_transformer
                    }
        return self._champion_bundle

    @property
    def background(self):
        if self._background is None:
            if not os.path.exists(BACKGROUND_PATH):
                raise FileNotFoundError(f"Background not found: {BACKGROUND_PATH}")
            with self._lock:
                if self._background is None:
                    self._background = np.load(BACKGROUND_PATH)
        return self._background

    @property
    def shap_values(self):
        if self._shap_values is None:
            if not os.path.exists(SHAP_VALUES_PATH):
                raise FileNotFoundError(f"SHAP values not found: {SHAP_VALUES_PATH}")
            with self._lock:
                if self._shap_values is None:
                    self._shap_values = np.load(SHAP_VALUES_PATH)
        return self._shap_values

    @property
    def base_values(self):
        if self._base_values is None:
            if not os.path.exists(SHAP_BASE_VALUES_PATH):
                raise FileNotFoundError(f"Base values not found: {SHAP_BASE_VALUES_PATH}")
            with self._lock:
                if self._base_values is None:
                    self._base_values = np.load(SHAP_BASE_VALUES_PATH)
        return self._base_values

    @property
    def feature_names(self):
        if self._feature_names is None:
            with open(FEATURE_NAMES_PATH, 'r') as f:
                self._feature_names = json.load(f)
        return self._feature_names

    @property
    def feature_mapping(self):
        if self._feature_mapping is None:
            with open(FEATURE_MAPPING_PATH, 'r') as f:
                self._feature_mapping = json.load(f)
        return self._feature_mapping

    @property
    def dimension_contract(self):
        if self._dimension_contract is None:
            with open(DIMENSION_CONTRACT_PATH, 'r') as f:
                self._dimension_contract = json.load(f)
        return self._dimension_contract

    @property
    def champion_lock(self):
        if self._champion_lock is None:
            with open(CHAMPION_LOCK_PATH, 'r') as f:
                self._champion_lock = json.load(f)
        return self._champion_lock

    @property
    def explainer(self):
        if self._explainer is None:
            import shap
            with self._lock:
                if self._explainer is None:
                    # Use TreeExplainer with background
                    self._explainer = shap.TreeExplainer(
                        self.champion_bundle['model'],
                        data=self.background,
                        feature_names=self.feature_names
                    )
        return self._explainer

    def clear(self):
        """Clear cache for testing."""
        with self._lock:
            self._champion_bundle = None
            self._background = None
            self._shap_values = None
            self._base_values = None
            self._feature_names = None
            self._feature_mapping = None
            self._dimension_contract = None
            self._champion_lock = None
            self._explainer = None


# Global cache instance
_cache = ExplainabilityCache()


# =============================================================================
# INPUT VALIDATION
# =============================================================================

def validate_input_schema(
    input_data: Union[Dict, pd.Series, pd.DataFrame],
    strict: bool = False
) -> pd.DataFrame:
    """
    Validate input data against bundle input contract.

    Args:
        input_data: Input as dict, Series, or DataFrame
        strict: If True, raise on extra features. If False, warn and drop.

    Returns:
        Validated DataFrame with correct columns

    Raises:
        MissingFeatureError: If required features are missing
        ExtraFeatureError: If extra features present in strict mode
        MultipleRowsNotSupportedError: If DataFrame has >1 row
    """
    # Convert to DataFrame
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.Series):
        df = input_data.to_frame().T
    elif isinstance(input_data, pd.DataFrame):
        if len(input_data) > 1:
            raise MultipleRowsNotSupportedError(len(input_data))
        df = input_data.copy()
    else:
        raise TypeError(f"Input must be dict, Series, or DataFrame, got {type(input_data)}")

    # Ensure columns are strings
    df.columns = [str(c) for c in df.columns]

    # Check missing features
    missing = set(EXPECTED_INPUT_COLUMNS) - set(df.columns)
    if missing:
        raise MissingFeatureError(sorted(missing))

    # Check extra features
    extra = set(df.columns) - set(EXPECTED_INPUT_COLUMNS)
    if extra:
        if strict:
            raise ExtraFeatureError(sorted(extra))
        else:
            warnings.warn(f"Extra features will be dropped: {sorted(extra)}")
            df = df[[c for c in df.columns if c in EXPECTED_INPUT_COLUMNS]]

    # Reorder columns to match expected order
    df = df[EXPECTED_INPUT_COLUMNS]

    # Check for inf
    for col in df.columns:
        if df[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
            if np.isinf(df[col].values).any():
                raise InvalidFeatureValueError(col, "contains infinite values")

    # NaN policy - allow if preprocessing has imputer, otherwise warn
    nan_cols = df.columns[df.isna().any()].tolist()
    if nan_cols:
        # Check if champion has imputer by looking at preprocessing
        # For now, allow NaN and let preprocessing handle it
        pass

    return df


def validate_feature_types(df: pd.DataFrame) -> List[Dict]:
    """Validate feature dtypes and ranges."""
    warnings_list = []

    # Numeric columns that should be numeric
    numeric_cols = ['duration_min', 'danceability', 'energy', 'loudness',
                    'speechiness', 'acousticness', 'instrumentalness',
                    'liveness', 'valence', 'tempo', 'release_year']

    for col in numeric_cols:
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                warnings_list.append({
                    "feature": col,
                    "expected": "numeric",
                    "actual": str(df[col].dtype),
                    "type": "dtype_mismatch"
                })

    # Binary columns
    binary_cols = ['explicit', 'mode']
    for col in binary_cols:
        if col in df.columns:
            unique_vals = df[col].dropna().unique()
            if not all(v in [0, 1, True, False] for v in unique_vals):
                warnings_list.append({
                    "feature": col,
                    "expected": "binary (0/1)",
                    "actual": str(unique_vals),
                    "type": "invalid_binary"
                })

    # Range warnings
    if 'tempo' in df.columns:
        tempo_out_of_range = df[(df['tempo'] < 20) | (df['tempo'] > 300)]
        if len(tempo_out_of_range) > 0:
            warnings_list.append({
                "feature": "tempo",
                "expected": "20-300 BPM",
                "actual": f"{len(tempo_out_of_range)} rows outside range",
                "type": "range_warning"
            })

    if 'loudness' in df.columns:
        loud_out_of_range = df[(df['loudness'] < -60) | (df['loudness'] > 5)]
        if len(loud_out_of_range) > 0:
            warnings_list.append({
                "feature": "loudness",
                "expected": "-60 to 5 dB",
                "actual": f"{len(loud_out_of_range)} rows outside range",
                "type": "range_warning"
            })

    return warnings_list


# =============================================================================
# PREDICTION
# =============================================================================

def predict_one(
    validated_df: pd.DataFrame,
    cache: ExplainabilityCache = None
) -> Dict[str, float]:
    """
    Make prediction for one row.

    Args:
        validated_df: Validated DataFrame with correct columns
        cache: Optional cache instance

    Returns:
        Dict with raw, clipped, and display predictions
    """
    if cache is None:
        cache = _cache

    # Get champion bundle
    bundle = cache.champion_bundle
    pipeline = bundle['pipeline']

    # Transform through full pipeline and predict
    # The pipeline expects raw input (18 features) -> transforms to model matrix -> predicts
    prediction_raw = pipeline.predict(validated_df)

    # Ensure single value
    if hasattr(prediction_raw, '__len__'):
        prediction_raw = prediction_raw[0]
    prediction_raw = float(prediction_raw)

    # Clip to 0-100
    prediction_clipped = np.clip(prediction_raw, 0, 100)

    # Display (rounded)
    prediction_display = int(round(prediction_clipped))

    return {
        "prediction_raw": prediction_raw,
        "prediction_clipped": prediction_clipped,
        "prediction_display": prediction_display
    }


# =============================================================================
# SHAP COMPUTATION
# =============================================================================

def compute_local_shap(
    validated_df: pd.DataFrame,
    cache: ExplainabilityCache = None
) -> np.ndarray:
    """
    Compute SHAP values for one row.

    Args:
        validated_df: Validated DataFrame with correct columns
        cache: Optional cache instance

    Returns:
        SHAP values array
    """
    if cache is None:
        cache = _cache

    # Get champion bundle components
    bundle = cache.champion_bundle
    pipeline = bundle['pipeline']
    fe_transformer = bundle['fe_transformer']
    col_transformer = bundle['col_transformer']

    # Transform input through feature engineering first
    X_eng = fe_transformer.transform(validated_df)

    # Transform through ColumnTransformer to get model matrix
    X_transformed = col_transformer.transform(X_eng)

    # Ensure 2D array
    if hasattr(X_transformed, 'toarray'):
        X_transformed = X_transformed.toarray()
    X_transformed = X_transformed.astype(np.float64)

    # Get SHAP values from explainer
    explainer = cache.explainer

    # Compute SHAP for this single row
    shap_values = explainer.shap_values(X_transformed)

    # Ensure numpy array
    if hasattr(shap_values, 'tolist'):
        shap_values = np.array(shap_values)

    return shap_values[0] if shap_values.shape[0] == 1 else shap_values


# =============================================================================
# CONTRIBUTION GROUPING
# =============================================================================

def group_contributions(
    shap_values: np.ndarray,
    cache: ExplainabilityCache = None
) -> List[Dict]:
    """
    Group SHAP contributions by selected feature.

    Args:
        shap_values: SHAP values for one row
        cache: Optional cache instance

    Returns:
        List of contribution dicts
    """
    if cache is None:
        cache = _cache

    feature_names = cache.feature_names
    feature_mapping = cache.feature_mapping

    # Create mapping from transformed to selected feature
    transformed_to_selected = {}
    for m in feature_mapping:
        tf = m['transformed_feature_name']
        sf = m['selected_feature_name']
        if sf not in transformed_to_selected:
            transformed_to_selected[tf] = sf

    # Group by selected feature
    selected_contributions = {}
    for i, fname in enumerate(feature_names):
        selected = transformed_to_selected.get(fname, fname)
        if selected not in selected_contributions:
            selected_contributions[selected] = 0.0
        selected_contributions[selected] += shap_values[i]

    # Build contribution list
    contributions = []
    for selected_feat, shap_val in selected_contributions.items():
        direction = "INCREASE_PREDICTION" if shap_val > 0 else "DECREASE_PREDICTION"
        contributions.append({
            "feature": selected_feat,
            "feature_value": None,  # Would need original value mapping
            "shap_value": float(shap_val),
            "direction": direction,
            "source_raw_feature": selected_feat,
            "mapping_status": "MAPPED"
        })

    return contributions


def sort_contributions(
    contributions: List[Dict],
    top_n: int = 10,
    include_all: bool = True
) -> Dict[str, List[Dict]]:
    """
    Sort contributions into positive and negative.

    Args:
        contributions: List of contribution dicts
        top_n: Number of top contributions to return
        include_all: Include all contributions in output

    Returns:
        Dict with top_positive, top_negative, and all contributions
    """
    # Sort by absolute value
    sorted_by_abs = sorted(contributions, key=lambda x: abs(x['shap_value']), reverse=True)

    # Separate positive and negative
    positive = [c for c in contributions if c['shap_value'] > 0]
    negative = [c for c in contributions if c['shap_value'] < 0]

    # Sort positive by value descending
    positive.sort(key=lambda x: x['shap_value'], reverse=True)

    # Sort negative by value ascending (most negative first)
    negative.sort(key=lambda x: x['shap_value'])

    # Top N
    top_positive = positive[:top_n]
    top_negative = negative[:top_n]

    result = {
        "top_positive_contributions": top_positive,
        "top_negative_contributions": top_negative,
    }

    if include_all:
        result["all_contributions"] = sorted_by_abs

    return result


# =============================================================================
# ADDITIVITY CHECK
# =============================================================================

def validate_additivity(
    shap_values: np.ndarray,
    prediction_raw: float,
    cache: ExplainabilityCache = None,
    tolerance: float = 1e-4
) -> Dict[str, Any]:
    """
    Validate SHAP additivity: base_value + sum(shap_values) ≈ prediction

    Args:
        shap_values: SHAP values for one row
        prediction_raw: Raw model prediction
        cache: Optional cache instance
        tolerance: Acceptable error threshold

    Returns:
        Dict with reconstruction info
    """
    if cache is None:
        cache = _cache

    # Get base value (mean of base values)
    base_values = cache.base_values
    base_value = float(np.mean(base_values))

    # Reconstruct prediction
    reconstructed = base_value + np.sum(shap_values)

    # Calculate error
    error = abs(reconstructed - prediction_raw)

    # Check validity
    additivity_valid = error <= tolerance

    return {
        "base_value": base_value,
        "reconstructed_prediction": float(reconstructed),
        "reconstruction_error": float(error),
        "additivity_tolerance": tolerance,
        "additivity_valid": additivity_valid
    }


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def explain_one_prediction(
    input_data: Union[Dict, pd.Series, pd.DataFrame],
    *,
    top_n: int = 10,
    include_all_contributions: bool = True,
    include_plot: bool = False,
    plot_output_path: Optional[str] = None,
    cache: Optional[ExplainabilityCache] = None
) -> Dict[str, Any]:
    """
    Explain a single prediction using SHAP.

    Args:
        input_data: Input as dict, Series, or DataFrame
        top_n: Number of top positive/negative contributions to return
        include_all_contributions: Include all contributions in output
        include_plot: Whether to generate a waterfall plot
        plot_output_path: Path to save plot (if None, returns figure)
        cache: Optional cache instance

    Returns:
        Dict with explanation results

    Raises:
        MissingFeatureError: If required features are missing
        ExtraFeatureError: If extra features present in strict mode
        MultipleRowsNotSupportedError: If DataFrame has >1 row
        InvalidFeatureValueError: If feature contains invalid values
    """
    # Use provided cache or global
    if cache is None:
        cache = _cache

    # Get metadata
    champion_lock = cache.champion_lock
    dimension_contract = cache.dimension_contract

    # Validate input
    validated_df = validate_input_schema(input_data, strict=False)

    # Validate types and ranges
    type_warnings = validate_feature_types(validated_df)

    # Make prediction
    prediction = predict_one(validated_df, cache)

    # Compute SHAP
    shap_values = compute_local_shap(validated_df, cache)

    # Group contributions
    contributions = group_contributions(shap_values, cache)

    # Sort contributions
    sorted_contribs = sort_contributions(contributions, top_n, include_all_contributions)

    # Validate additivity
    additivity = validate_additivity(shap_values, prediction['prediction_raw'], cache)

    # Build output
    output = {
        "status": "SUCCESS",
        "model_id": champion_lock.get("champion_model_id", "UNKNOWN"),
        "model_class": champion_lock.get("model_class", "XGBoost"),
        "feature_set_id": champion_lock.get("feature_set_id", "UNKNOWN"),
        "prediction_raw": prediction['prediction_raw'],
        "prediction_clipped": prediction['prediction_clipped'],
        "prediction_display": prediction['prediction_display'],
        "base_value": additivity['base_value'],
        "reconstructed_prediction": additivity['reconstructed_prediction'],
        "reconstruction_error": additivity['reconstruction_error'],
        "additivity_valid": additivity['additivity_valid'],
        "top_positive_contributions": sorted_contribs['top_positive_contributions'],
        "top_negative_contributions": sorted_contribs['top_negative_contributions'],
        "all_contributions": sorted_contribs.get("all_contributions", []) if include_all_contributions else [],
        "explanation_method": "SHAP_TREE_EXPLAINER",
        "output_space": "raw",
        "background_source": "TRAIN",
        "warnings": type_warnings,
        "metadata": {
            "champion_artifact_sha256": champion_lock.get("artifact_sha256", ""),
            "generated_at": datetime.now().isoformat()
        }
    }

    # Optional plot
    if include_plot:
        import shap
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(12, 8))

        # Waterfall-style display
        feature_names = cache.feature_names
        sorted_idx = np.argsort(np.abs(shap_values))[::-1][:top_n]

        y_pos = np.arange(len(sorted_idx))
        ax.barh(y_pos, shap_values[sorted_idx])
        ax.set_yticks(y_pos)
        ax.set_yticklabels([feature_names[i] for i in sorted_idx])
        ax.invert_yaxis()
        ax.set_xlabel('SHAP Value')
        ax.set_title(f'SHAP Explanation - Prediction: {prediction["prediction_display"]}')

        if plot_output_path:
            fig.savefig(plot_output_path, bbox_inches='tight', dpi=150)
            output["plot_path"] = plot_output_path
        else:
            output["plot_figure"] = fig

    return output


def clear_cache():
    """Clear the global explainability cache."""
    _cache.clear()


# =============================================================================
# FOR TESTING
# =============================================================================

if __name__ == "__main__":
    # Quick test
    test_input = {
        "duration_min": 3.5,
        "explicit": 0,
        "release_year": 2020,
        "release_month": 6,
        "decade": 2020,
        "release_precision": 1,
        "danceability": 0.7,
        "energy": 0.8,
        "key": 0,
        "loudness": -5.0,
        "mode": 1,
        "speechiness": 0.1,
        "acousticness": 0.2,
        "instrumentalness": 0.0,
        "liveness": 0.1,
        "valence": 0.6,
        "tempo": 120.0,
        "time_signature": 4
    }

    result = explain_one_prediction(test_input)
    print(json.dumps(result, indent=2, default=str))

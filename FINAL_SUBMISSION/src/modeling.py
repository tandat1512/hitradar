"""Model pipelines shared by Notebook 06 and deployment validation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from src.features import (
    BASELINE_CATEGORICAL_FEATURES,
    BASELINE_NUMERIC_FEATURES,
    FeatureBuilder,
    RANDOM_STATE,
    SELECTED_ENGINEERED_CATEGORICAL_FEATURES,
    SELECTED_ENGINEERED_NUMERIC_FEATURES,
    get_model_features,
)


MODEL_NAMES = ("Linear Regression", "Random Forest", "XGBoost")


def build_preprocessor(
    include_engineered: bool, include_time: bool = True
) -> ColumnTransformer:
    """Build encoding/scaling for the exact declared experiment contract."""
    model_features = get_model_features(
        include_engineered=include_engineered, include_time=include_time
    )
    numeric_pool = BASELINE_NUMERIC_FEATURES + SELECTED_ENGINEERED_NUMERIC_FEATURES
    categorical_pool = (
        BASELINE_CATEGORICAL_FEATURES + SELECTED_ENGINEERED_CATEGORICAL_FEATURES
    )
    numeric_features = [feature for feature in numeric_pool if feature in model_features]
    categorical_features = [
        feature for feature in categorical_pool if feature in model_features
    ]

    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=True),
            ),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def _make_estimator(model_name: str):
    if model_name == "Linear Regression":
        return LinearRegression()
    if model_name == "Random Forest":
        return RandomForestRegressor(
            n_estimators=60,
            max_depth=16,
            min_samples_leaf=8,
            max_features=0.75,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    if model_name == "XGBoost":
        return XGBRegressor(
            n_estimators=260,
            learning_rate=0.05,
            max_depth=7,
            min_child_weight=5,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="reg:squarederror",
            tree_method="hist",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
    raise ValueError(f"Unsupported model: {model_name}")


def build_model_pipeline(
    model_name: str,
    include_engineered: bool = True,
    include_time: bool = True,
) -> Pipeline:
    return Pipeline(
        [
            ("features", FeatureBuilder(include_engineered=include_engineered)),
            (
                "preprocessing",
                build_preprocessor(include_engineered, include_time=include_time),
            ),
            ("model", _make_estimator(model_name)),
        ]
    )


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred)),
    }


def regression_metric_variants(y_true, y_pred) -> dict[str, dict[str, float]]:
    """Report unconstrained model quality and production-range quality separately."""
    raw = np.asarray(y_pred, dtype=float)
    return {
        "Raw": regression_metrics(y_true, raw),
        "Clipped [0,100]": regression_metrics(y_true, np.clip(raw, 0.0, 100.0)),
    }


def transformed_feature_importance(pipeline: Pipeline) -> pd.DataFrame:
    feature_names = pipeline.named_steps["preprocessing"].get_feature_names_out()
    model = pipeline.named_steps["model"]
    if hasattr(model, "feature_importances_"):
        importance = np.asarray(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        importance = np.abs(np.asarray(model.coef_, dtype=float)).ravel()
    else:
        raise TypeError("Final estimator does not expose feature importance or coefficients.")
    return (
        pd.DataFrame({"Feature": feature_names, "Importance": importance})
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )


def grouped_feature_importance(pipeline: Pipeline) -> pd.DataFrame:
    """Aggregate one-hot levels back to their original pre-encoding feature."""
    detailed = transformed_feature_importance(pipeline)
    preprocessor = pipeline.named_steps["preprocessing"]
    numeric = list(preprocessor.transformers_[0][2])
    categorical = list(preprocessor.transformers_[1][2])

    def original_feature(encoded_name: str) -> str:
        if encoded_name in numeric:
            return encoded_name
        matches = [name for name in categorical if encoded_name.startswith(f"{name}_")]
        return max(matches, key=len) if matches else encoded_name

    detailed["Feature Group"] = detailed["Feature"].map(original_feature)
    return (
        detailed.groupby("Feature Group", as_index=False)["Importance"]
        .sum()
        .sort_values("Importance", ascending=False)
        .reset_index(drop=True)
    )

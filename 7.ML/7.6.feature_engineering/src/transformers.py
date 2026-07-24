"""
Feature Engineering Transformers for Feature 2.3
HitRadar Pro
"""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class FeatureEngineeringTransformer(BaseEstimator, TransformerMixin):
    """Transformer for creating engineered features."""

    def __init__(self, duration_thresholds, selected_features):
        self.duration_thresholds = duration_thresholds
        self.selected_features = selected_features
        self.baseline_features = [
            "duration_min", "release_year", "danceability", "energy", "loudness",
            "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo",
            "release_month", "decade", "release_precision", "key", "time_signature",
            "explicit", "mode"
        ]
        self.q25 = duration_thresholds["q25"]
        self.q50 = duration_thresholds["q50"]
        self.q75 = duration_thresholds["q75"]

    def fit(self, X, y=None):
        """No fitting needed for feature engineering."""
        return self

    def transform(self, X):
        """Transform features by adding engineered features."""
        result = X.copy()

        # Time features
        if "release_month_sin" in self.selected_features or "release_month_cos" in self.selected_features:
            month = result["release_month"]
            result["release_month_sin"] = np.where(
                month.isna() | (month < 1) | (month > 12),
                0.0, np.sin(2 * np.pi * month / 12)
            )
            result["release_month_cos"] = np.where(
                month.isna() | (month < 1) | (month > 12),
                0.0, np.cos(2 * np.pi * month / 12)
            )

        if "year_in_decade" in self.selected_features:
            result["year_in_decade"] = result["release_year"] % 10

        # Duration features
        if "duration_log" in self.selected_features:
            result["duration_log"] = np.log1p(np.maximum(result["duration_min"], 0))

        if "duration_squared" in self.selected_features:
            result["duration_squared"] = result["duration_min"] ** 2

        # Audio interactions
        def safe_mult(col1, col2):
            return (col1 * col2).fillna(0.0)

        if "energy_danceability" in self.selected_features:
            result["energy_danceability"] = safe_mult(result["energy"], result["danceability"])

        if "energy_valence" in self.selected_features:
            result["energy_valence"] = safe_mult(result["energy"], result["valence"])

        if "danceability_valence" in self.selected_features:
            result["danceability_valence"] = safe_mult(result["danceability"], result["valence"])

        if "acousticness_instrumentalness" in self.selected_features:
            result["acousticness_instrumentalness"] = safe_mult(result["acousticness"], result["instrumentalness"])

        if "energy_liveness" in self.selected_features:
            result["energy_liveness"] = safe_mult(result["energy"], result["liveness"])

        if "speechiness_explicit" in self.selected_features:
            result["speechiness_explicit"] = safe_mult(result["speechiness"], result["explicit"].astype(float))

        if "tempo_danceability" in self.selected_features:
            result["tempo_danceability"] = safe_mult(result["tempo"], result["danceability"])

        if "loudness_energy" in self.selected_features:
            result["loudness_energy"] = safe_mult(result["loudness"], result["energy"])

        return result[self.selected_features]

    def get_feature_names_out(self):
        """Return selected feature names."""
        return self.selected_features

    def get_duration_thresholds(self):
        """Return duration thresholds."""
        return self.duration_thresholds

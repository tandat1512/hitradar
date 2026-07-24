"""
Test Feature 2.6 - explain_one_prediction additivity
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add paths
REPO_ROOT = r"E:\Dự án 1 hitrada"
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.9.explainability", "services"))
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.6.feature_engineering", "src"))

def to_string(x):
    return x.astype(str)

import explain_prediction as ep


class TestAdditivity:
    """Test SHAP additivity validation."""

    @pytest.fixture
    def valid_input(self):
        """Valid input DataFrame."""
        return pd.DataFrame([{
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
        }])

    def test_additivity_validation(self, valid_input):
        """Additivity validation should work."""
        shap_values = ep.compute_local_shap(valid_input)
        prediction = ep.predict_one(valid_input)

        additivity = ep.validate_additivity(
            shap_values,
            prediction["prediction_raw"]
        )

        assert "base_value" in additivity
        assert "reconstructed_prediction" in additivity
        assert "reconstruction_error" in additivity
        assert "additivity_valid" in additivity

    def test_additivity_valid(self, valid_input):
        """Additivity should be valid within tolerance."""
        shap_values = ep.compute_local_shap(valid_input)
        prediction = ep.predict_one(valid_input)

        additivity = ep.validate_additivity(
            shap_values,
            prediction["prediction_raw"],
            tolerance=1e-3
        )

        assert additivity["additivity_valid"] is True

    def test_additivity_error_small(self, valid_input):
        """Additivity error should be small."""
        shap_values = ep.compute_local_shap(valid_input)
        prediction = ep.predict_one(valid_input)

        additivity = ep.validate_additivity(
            shap_values,
            prediction["prediction_raw"]
        )

        # Error should be very small (less than 0.001)
        assert additivity["reconstruction_error"] < 1e-3


class TestAdditivityTolerance:
    """Test additivity tolerance handling."""

    @pytest.fixture
    def valid_input(self):
        """Valid input DataFrame."""
        return pd.DataFrame([{
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
        }])

    def test_custom_tolerance(self, valid_input):
        """Custom tolerance should work."""
        shap_values = ep.compute_local_shap(valid_input)
        prediction = ep.predict_one(valid_input)

        # Very small tolerance should pass
        additivity = ep.validate_additivity(
            shap_values,
            prediction["prediction_raw"],
            tolerance=1e-2
        )

        assert additivity["additivity_valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

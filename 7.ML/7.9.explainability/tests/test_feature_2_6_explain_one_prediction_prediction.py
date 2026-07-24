"""
Test Feature 2.6 - explain_one_prediction prediction output
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


class TestPredictionOutput:
    """Test prediction output validation."""

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

    def test_prediction_returns_dict(self, valid_input):
        """Prediction should return dict with raw, clipped, display."""
        result = ep.predict_one(valid_input)

        assert isinstance(result, dict)
        assert "prediction_raw" in result
        assert "prediction_clipped" in result
        assert "prediction_display" in result

    def test_prediction_raw_finite(self, valid_input):
        """Prediction raw should be finite."""
        result = ep.predict_one(valid_input)

        assert np.isfinite(result["prediction_raw"])

    def test_prediction_clipped_range(self, valid_input):
        """Prediction clipped should be in [0, 100]."""
        result = ep.predict_one(valid_input)

        assert 0 <= result["prediction_clipped"] <= 100

    def test_prediction_display_int(self, valid_input):
        """Prediction display should be integer."""
        result = ep.predict_one(valid_input)

        assert isinstance(result["prediction_display"], (int, np.integer))

    def test_prediction_deterministic(self, valid_input):
        """Prediction should be deterministic."""
        result1 = ep.predict_one(valid_input)
        result2 = ep.predict_one(valid_input)

        assert result1["prediction_raw"] == result2["prediction_raw"]


class TestPredictionWithDifferentInputs:
    """Test prediction with different input values."""

    def test_prediction_low_value(self):
        """Test prediction for low popularity input."""
        valid_input = pd.DataFrame([{
            "duration_min": 0.5,
            "explicit": 0,
            "release_year": 1950,
            "release_month": 1,
            "decade": 1950,
            "release_precision": 1,
            "danceability": 0.1,
            "energy": 0.1,
            "key": 0,
            "loudness": -60.0,
            "mode": 1,
            "speechiness": 0.0,
            "acousticness": 0.9,
            "instrumentalness": 0.9,
            "liveness": 0.9,
            "valence": 0.1,
            "tempo": 50.0,
            "time_signature": 4
        }])

        result = ep.predict_one(valid_input)
        assert 0 <= result["prediction_clipped"] <= 100

    def test_prediction_high_value(self):
        """Test prediction for high popularity input."""
        valid_input = pd.DataFrame([{
            "duration_min": 3.5,
            "explicit": 1,
            "release_year": 2023,
            "release_month": 12,
            "decade": 2020,
            "release_precision": 1,
            "danceability": 0.9,
            "energy": 0.9,
            "key": 0,
            "loudness": 0.0,
            "mode": 1,
            "speechiness": 0.5,
            "acousticness": 0.1,
            "instrumentalness": 0.0,
            "liveness": 0.1,
            "valence": 0.9,
            "tempo": 180.0,
            "time_signature": 4
        }])

        result = ep.predict_one(valid_input)
        assert 0 <= result["prediction_clipped"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

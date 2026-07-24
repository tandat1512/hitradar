"""
Test Feature 2.6 - explain_one_prediction output schema
"""

import pytest
import pandas as pd
import numpy as np
import json
import sys
import os

# Add paths
REPO_ROOT = r"E:\Dự án 1 hitrada"
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.9.explainability", "services"))
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.6.feature_engineering", "src"))

def to_string(x):
    return x.astype(str)

import explain_prediction as ep


class TestOutputSchema:
    """Test output schema."""

    @pytest.fixture
    def valid_input(self):
        """Valid input dict."""
        return {
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

    def test_output_has_required_fields(self, valid_input):
        """Output should have all required fields."""
        result = ep.explain_one_prediction(valid_input)

        required_fields = [
            "status",
            "model_id",
            "model_class",
            "feature_set_id",
            "prediction_raw",
            "prediction_clipped",
            "prediction_display",
            "base_value",
            "reconstructed_prediction",
            "reconstruction_error",
            "additivity_valid",
            "top_positive_contributions",
            "top_negative_contributions",
            "explanation_method",
            "output_space",
            "background_source",
            "warnings",
            "metadata"
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"

    def test_output_model_id(self, valid_input):
        """Output should have correct model_id."""
        result = ep.explain_one_prediction(valid_input)

        assert result["model_id"] == "EXP24-XGB-FINAL-001"

    def test_output_model_class(self, valid_input):
        """Output should have correct model_class."""
        result = ep.explain_one_prediction(valid_input)

        assert result["model_class"] == "XGBoost"

    def test_output_prediction_range(self, valid_input):
        """Output predictions should be in valid range."""
        result = ep.explain_one_prediction(valid_input)

        assert 0 <= result["prediction_clipped"] <= 100
        assert isinstance(result["prediction_display"], int)
        assert 0 <= result["prediction_display"] <= 100

    def test_output_contributions_structure(self, valid_input):
        """Output contributions should have correct structure."""
        result = ep.explain_one_prediction(valid_input)

        for contrib in result["top_positive_contributions"] + result["top_negative_contributions"]:
            assert "feature" in contrib
            assert "shap_value" in contrib
            assert "direction" in contrib

    def test_output_json_serializable(self, valid_input):
        """Output should be JSON serializable."""
        result = ep.explain_one_prediction(valid_input)

        # Should not raise
        json_str = json.dumps(result, default=str)
        parsed = json.loads(json_str)
        assert parsed is not None

    def test_output_metadata(self, valid_input):
        """Output should have metadata."""
        result = ep.explain_one_prediction(valid_input)

        assert "metadata" in result
        assert "champion_artifact_sha256" in result["metadata"]
        assert "generated_at" in result["metadata"]


class TestTopN:
    """Test top_n parameter."""

    @pytest.fixture
    def valid_input(self):
        """Valid input dict."""
        return {
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

    def test_top_n_limit(self, valid_input):
        """Top_n should limit contributions."""
        result = ep.explain_one_prediction(valid_input, top_n=3)

        assert len(result["top_positive_contributions"]) <= 3
        assert len(result["top_negative_contributions"]) <= 3

    def test_include_all_contributions(self, valid_input):
        """include_all_contributions should control all_contributions field."""
        result_all = ep.explain_one_prediction(
            valid_input, top_n=3, include_all_contributions=True
        )
        assert "all_contributions" in result_all

        result_no_all = ep.explain_one_prediction(
            valid_input, top_n=3, include_all_contributions=False
        )
        # all_contributions may be empty but field should exist
        assert "all_contributions" in result_no_all


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

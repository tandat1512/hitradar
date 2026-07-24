"""
Test Feature 2.6 - explain_one_prediction error handling
"""

import pytest
import pandas as pd
import sys
import os

# Add paths
REPO_ROOT = r"E:\Dự án 1 hitrada"
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.9.explainability", "services"))
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.6.feature_engineering", "src"))

def to_string(x):
    return x.astype(str)

import explain_prediction as ep


class TestMissingFeatureError:
    """Test MissingFeatureError."""

    def test_missing_feature_raises(self):
        """Missing required feature should raise MissingFeatureError."""
        test_input = {
            "duration_min": 3.5,
            # Missing other features
        }

        with pytest.raises(ep.MissingFeatureError):
            ep.validate_input_schema(test_input)

    def test_missing_feature_has_attributes(self):
        """MissingFeatureError should have missing_features attribute."""
        test_input = {
            "duration_min": 3.5,
            "explicit": 0,
        }

        try:
            ep.validate_input_schema(test_input)
        except ep.MissingFeatureError as e:
            assert hasattr(e, "missing_features")
            assert hasattr(e, "error_code")
            assert e.error_code == "MISSING_FEATURE"


class TestExtraFeatureError:
    """Test ExtraFeatureError."""

    def test_extra_feature_raises_strict(self):
        """Extra feature should raise ExtraFeatureError in strict mode."""
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
            "time_signature": 4,
            "extra_col": 999
        }

        with pytest.raises(ep.ExtraFeatureError):
            ep.validate_input_schema(test_input, strict=True)


class TestMultipleRowsError:
    """Test MultipleRowsNotSupportedError."""

    def test_multiple_rows_raises(self):
        """Multiple rows should raise MultipleRowsNotSupportedError."""
        test_df = pd.DataFrame([
            {"duration_min": 3.5, "explicit": 0, "release_year": 2020, "release_month": 6,
             "decade": 2020, "release_precision": 1, "danceability": 0.7, "energy": 0.8,
             "key": 0, "loudness": -5.0, "mode": 1, "speechiness": 0.1, "acousticness": 0.2,
             "instrumentalness": 0.0, "liveness": 0.1, "valence": 0.6, "tempo": 120.0, "time_signature": 4},
            {"duration_min": 4.0, "explicit": 1, "release_year": 2019, "release_month": 3,
             "decade": 2010, "release_precision": 1, "danceability": 0.6, "energy": 0.7,
             "key": 1, "loudness": -6.0, "mode": 0, "speechiness": 0.2, "acousticness": 0.3,
             "instrumentalness": 0.1, "liveness": 0.2, "valence": 0.5, "tempo": 110.0, "time_signature": 4},
        ])

        with pytest.raises(ep.MultipleRowsNotSupportedError):
            ep.validate_input_schema(test_df)


class TestInvalidFeatureValueError:
    """Test InvalidFeatureValueError."""

    def test_inf_raises(self):
        """Inf should raise InvalidFeatureValueError."""
        test_input = {
            "duration_min": float('inf'),
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

        with pytest.raises(ep.InvalidFeatureValueError):
            ep.validate_input_schema(test_input)

    def test_invalid_feature_value_has_attributes(self):
        """InvalidFeatureValueError should have feature and error_code."""
        test_input = {
            "duration_min": float('inf'),
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

        try:
            ep.validate_input_schema(test_input)
        except ep.InvalidFeatureValueError as e:
            assert hasattr(e, "feature")
            assert hasattr(e, "error_code")
            assert e.error_code == "INVALID_FEATURE_VALUE"


class TestCacheClear:
    """Test cache clearing."""

    def test_clear_cache(self):
        """clear_cache should work without error."""
        # Should not raise
        ep.clear_cache()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

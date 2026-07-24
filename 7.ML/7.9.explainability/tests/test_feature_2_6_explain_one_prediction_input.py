"""
Test Feature 2.6 - explain_one_prediction input validation
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

# Define to_string for unpickling
def to_string(x):
    return x.astype(str)

import explain_prediction as ep


class TestDictInput:
    """Test dict input validation."""

    def test_dict_input_valid(self):
        """Valid dict input should work."""
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

        result = ep.validate_input_schema(test_input)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert list(result.columns) == ep.EXPECTED_INPUT_COLUMNS

    def test_dict_input_missing_feature(self):
        """Missing required feature should raise MissingFeatureError."""
        test_input = {
            "duration_min": 3.5,
            "explicit": 0,
            "release_year": 2020,
            # Missing other features
        }

        with pytest.raises(ep.MissingFeatureError) as exc_info:
            ep.validate_input_schema(test_input)
        assert "missing_features" in exc_info.value.__dict__

    def test_dict_input_extra_feature(self):
        """Extra feature should warn in non-strict mode."""
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
            "extra_feature": 999  # Extra
        }

        # Should warn but not raise in non-strict mode
        with pytest.warns(UserWarning):
            result = ep.validate_input_schema(test_input, strict=False)
        assert "extra_feature" not in result.columns

    def test_dict_input_extra_feature_strict(self):
        """Extra feature should raise in strict mode."""
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
            "extra_feature": 999
        }

        with pytest.raises(ep.ExtraFeatureError):
            ep.validate_input_schema(test_input, strict=True)


class TestSeriesInput:
    """Test pandas Series input validation."""

    def test_series_input_valid(self):
        """Valid Series input should work."""
        test_series = pd.Series({
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
        })

        result = ep.validate_input_schema(test_series)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1


class TestDataFrameInput:
    """Test pandas DataFrame input validation."""

    def test_dataframe_one_row_valid(self):
        """Valid one-row DataFrame should work."""
        test_df = pd.DataFrame([{
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

        result = ep.validate_input_schema(test_df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    def test_dataframe_multiple_rows_rejected(self):
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


class TestFeatureTypeValidation:
    """Test feature type validation."""

    def test_inf_rejected(self):
        """Inf values should raise InvalidFeatureValueError."""
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

    def test_negative_inf_rejected(self):
        """Negative inf should raise InvalidFeatureValueError."""
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
            "loudness": float('-inf'),
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


class TestFeatureTypeWarnings:
    """Test feature type warnings."""

    def test_binary_invalid_warning(self):
        """Invalid binary values should generate warning."""
        test_input = {
            "duration_min": 3.5,
            "explicit": 2,  # Invalid binary
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

        df = ep.validate_input_schema(test_input)
        warnings = ep.validate_feature_types(df)
        binary_warnings = [w for w in warnings if w.get('type') == 'invalid_binary']
        assert len(binary_warnings) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

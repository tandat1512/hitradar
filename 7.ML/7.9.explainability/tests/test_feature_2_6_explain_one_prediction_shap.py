"""
Test Feature 2.6 - explain_one_prediction SHAP computation
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


class TestSHAPComputation:
    """Test SHAP computation in function."""

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

    def test_shap_returns_array(self, valid_input):
        """SHAP computation should return numpy array."""
        shap_values = ep.compute_local_shap(valid_input)

        assert isinstance(shap_values, np.ndarray)

    def test_shap_shape_matches_features(self, valid_input):
        """SHAP values should match feature count."""
        cache = ep._cache
        feature_count = len(cache.feature_names)

        shap_values = ep.compute_local_shap(valid_input)

        assert len(shap_values) == feature_count

    def test_shap_finite(self, valid_input):
        """SHAP values should be finite."""
        shap_values = ep.compute_local_shap(valid_input)

        assert np.all(np.isfinite(shap_values))


class TestContributionsGrouping:
    """Test contribution grouping."""

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

    def test_group_contributions(self, valid_input):
        """Group contributions should work."""
        shap_values = ep.compute_local_shap(valid_input)
        contributions = ep.group_contributions(shap_values)

        assert isinstance(contributions, list)
        assert len(contributions) > 0

        # Check structure
        for c in contributions:
            assert "feature" in c
            assert "shap_value" in c
            assert "direction" in c

    def test_sort_contributions(self, valid_input):
        """Sort contributions should work."""
        shap_values = ep.compute_local_shap(valid_input)
        contributions = ep.group_contributions(shap_values)
        sorted_contribs = ep.sort_contributions(contributions, top_n=5)

        assert "top_positive_contributions" in sorted_contribs
        assert "top_negative_contributions" in sorted_contribs

        # Positive should be sorted descending
        pos = sorted_contribs["top_positive_contributions"]
        if len(pos) > 1:
            for i in range(len(pos) - 1):
                assert pos[i]["shap_value"] >= pos[i + 1]["shap_value"]

    def test_top_n_respected(self, valid_input):
        """Top_n should limit results."""
        shap_values = ep.compute_local_shap(valid_input)
        contributions = ep.group_contributions(shap_values)
        sorted_contribs = ep.sort_contributions(contributions, top_n=3, include_all=True)

        assert len(sorted_contribs["top_positive_contributions"]) <= 3
        assert len(sorted_contribs["top_negative_contributions"]) <= 3


class TestFeatureMapping:
    """Test feature mapping."""

    def test_feature_names_loaded(self):
        """Feature names should be loaded from cache."""
        cache = ep._cache
        feature_names = cache.feature_names

        assert isinstance(feature_names, list)
        assert len(feature_names) > 0

    def test_feature_mapping_loaded(self):
        """Feature mapping should be loaded from cache."""
        cache = ep._cache
        feature_mapping = cache.feature_mapping

        assert isinstance(feature_mapping, list)
        assert len(feature_mapping) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

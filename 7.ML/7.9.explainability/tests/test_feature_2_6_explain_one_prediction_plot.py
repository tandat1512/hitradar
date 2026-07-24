"""
Test Feature 2.6 - explain_one_prediction optional plot
"""

import pytest
import pandas as pd
import os
import sys

# Add paths
REPO_ROOT = r"E:\Dự án 1 hitrada"
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.9.explainability", "services"))
sys.path.insert(0, os.path.join(REPO_ROOT, "hitradar", "7.ML", "7.6.feature_engineering", "src"))

def to_string(x):
    return x.astype(str)

import explain_prediction as ep


class TestOptionalPlot:
    """Test optional plot generation."""

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

    def test_no_plot_by_default(self, valid_input):
        """By default, no plot should be generated."""
        result = ep.explain_one_prediction(valid_input, include_plot=False)

        # Should not have plot fields
        assert "plot_path" not in result
        assert "plot_figure" not in result

    def test_plot_output_path(self, valid_input, tmp_path):
        """Plot should be saved to path if provided."""
        plot_path = str(tmp_path / "test_plot.png")

        result = ep.explain_one_prediction(
            valid_input,
            include_plot=True,
            plot_output_path=plot_path
        )

        assert "plot_path" in result
        assert result["plot_path"] == plot_path
        assert os.path.exists(plot_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

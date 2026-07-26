"""
test_psi.py — PSI (Population Stability Index) computation tests.
Feature 2.9 Phase 3/5.
"""
from __future__ import annotations

import numpy as np
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from model_monitor import compute_psi


class TestPSI:
    def test_identical_distributions_psi_zero(self):
        """PSI should be ~0 when current exactly matches expected proportions."""
        # Both bins ≈50% each; current is uniform 0.5 → PSI ≈ 0
        current = [0.25] * 500 + [0.75] * 500
        bins = [0.0, 0.5, 1.0]
        # 0.25 lands in bin 0, 0.75 lands in bin 1 → proportions ≈ [0.5, 0.5]
        expected_props = [0.5, 0.5]
        result = compute_psi(current, [], bins, expected_proportions=expected_props)
        assert result["psi"] is not None
        assert result["psi"] < 0.01  # near-zero
        assert result["status"] == "COMPUTED"

    def test_shifted_distribution_psi_positive(self):
        """PSI should be > 0 when distributions differ."""
        current = [0.1] * 500 + [0.9] * 500  # shifted high
        expected = [0.5] * 1000
        bins = [0.0, 0.3, 0.6, 1.0]
        result = compute_psi(current, expected, bins)
        assert result["psi"] is not None
        assert result["psi"] > 0
        assert result["status"] == "COMPUTED"

    def test_not_enough_data(self):
        """PSI should return NOT_ENOUGH_DATA for fewer than 10 values."""
        current = [0.5] * 5
        bins = [0.0, 0.5, 1.0]
        result = compute_psi(current, [], bins)
        assert result["psi"] is None
        assert result["status"] == "NOT_ENOUGH_DATA"

    def test_fixed_bins_used(self):
        """PSI result should indicate fixed bin policy."""
        bins = [0.0, 0.25, 0.5, 0.75, 1.0]
        result = compute_psi([0.3] * 200, [], bins, expected_proportions=[0.0, 1.0, 0.0, 0.0])
        assert result["bin_policy"] == "fixed_from_baseline"

    def test_epsilon_prevents_log_zero(self):
        """PSI should not raise on near-zero probability bins."""
        current = [0.1] * 1000
        bins = [0.0, 0.1, 0.2, 0.3, 1.0]  # some bins may have zero count
        result = compute_psi(current, [], bins, expected_proportions=[1.0, 0.0, 0.0, 0.0])
        assert result["status"] == "COMPUTED"
        assert result["psi"] is not None

    def test_sample_size_ok_flag(self):
        """PSI result should reflect sample size."""
        current = list(np.random.beta(5, 5, 200))
        bins = [0.0, 0.25, 0.5, 0.75, 1.0]
        result = compute_psi(current, [], bins, expected_proportions=[0.0, 1.0, 0.0, 0.0])
        assert result["sample_size_ok"] is True  # 200 >= 100

    def test_nan_filtered(self):
        """NaN values should be filtered before PSI computation."""
        # Need >= 10 valid values for PSI to compute
        current = [0.5, 0.6, np.nan, 0.7, 0.4, 0.55, 0.65, 0.45, 0.58, 0.62, 0.52, np.nan]
        bins = [0.0, 0.3, 0.6, 1.0]
        result = compute_psi(current, [], bins, expected_proportions=[0.5, 0.5, 0.0])
        assert result["current_n"] == 10
        assert result["status"] == "COMPUTED"

    def test_empty_bins_handled(self):
        """Empty bins should be handled with epsilon replacement."""
        current = [0.01] * 1000  # almost all in first bin
        bins = [0.0, 0.1, 0.5, 1.0]
        result = compute_psi(current, [], bins, expected_proportions=[1.0, 0.0, 0.0])
        assert result["empty_bin_handling"] == "epsilon_replacement"
        assert result["status"] == "COMPUTED"

    def test_returns_bin_edges(self):
        """PSI result should include bin edges for auditability."""
        bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        result = compute_psi([0.3] * 150, [], bins, expected_proportions=[0.0, 1.0, 0.0, 0.0, 0.0])
        assert result["bin_edges"] == bins
        assert result["bin_count"] == len(bins) - 1

    def test_expected_data_missing_returns_none(self):
        """PSI should return EXPECTED_DATA_MISSING when no expected data or proportions."""
        current = [0.5] * 100
        bins = [0.0, 0.5, 1.0]
        result = compute_psi(current, [], bins)
        assert result["psi"] is None
        assert result["status"] == "EXPECTED_DATA_MISSING"

    def test_explicit_proportions_used_directly(self):
        """Explicit proportions should bypass heuristic and be used directly."""
        # 100% in first bin, expected is 0% in first bin → high PSI
        current = [0.01] * 200
        bins = [0.0, 0.5, 1.0]
        result = compute_psi(current, [], bins, expected_proportions=[0.0, 1.0])
        assert result["psi"] is not None
        assert result["psi"] > 0.5  # large divergence

    def test_invalid_proportions_length(self):
        """PSI should return INVALID_PROPORTIONS when proportions length mismatches bins."""
        current = [0.5] * 100
        bins = [0.0, 0.5, 1.0]  # 2 bins
        result = compute_psi(current, [], bins, expected_proportions=[0.33, 0.33, 0.34])  # 3 values
        assert result["psi"] is None
        assert result["status"] == "INVALID_PROPORTIONS"

    def test_psi_known_values(self):
        """PSI with known distributions: identical distributions give PSI ≈ 0."""
        # Same distribution in both current and expected → PSI = 0
        data = [0.15] * 500 + [0.85] * 500
        bins = [0.0, 0.3, 0.6, 1.0]
        result = compute_psi(data, data, bins)
        assert result["psi"] is not None
        assert result["psi"] < 0.001

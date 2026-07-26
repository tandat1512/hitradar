"""
test_tvd.py — Total Variation Distance (TVD) computation tests.
Feature 2.9 Phase 3/5.
"""
from __future__ import annotations

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from model_monitor import compute_tvd


class TestTVD:
    def test_identical_distributions_tvd_zero(self):
        """TVD should be 0 when distributions are identical."""
        current = {"A": 500, "B": 500}
        expected = {"A": 500, "B": 500}
        result = compute_tvd(current, expected)
        assert result["tvd"] == 0.0
        assert result["status"] == "COMPUTED"

    def test_max_tvd_is_half(self):
        """Maximum TVD (1.0) occurs for maximally disjoint distributions."""
        current = {"A": 500, "B": 500}
        expected = {"C": 500, "D": 500}
        result = compute_tvd(current, expected)
        assert result["tvd"] == 1.0
        # A and B are in current but not expected → unseen
        assert set(result["unseen_categories"]) == {"A", "B"}

    def test_unseen_categories_detected(self):
        """Unseen categories (in current but not expected) should be flagged."""
        current = {"A": 700, "C": 300}
        expected = {"A": 500, "B": 500}
        result = compute_tvd(current, expected)
        assert "C" in result["unseen_categories"]
        assert result["unseen_rate"] > 0

    def test_null_baseline_frequencies_ignored(self):
        """Null baseline frequencies are treated as unseen (zero frequency)."""
        current = {"A": 500, "B": 500}
        expected = {"A": None, "B": None}
        result = compute_tvd(current, expected)
        # Both categories treated as unseen → current 100% unseen → TVD = 0.5
        assert result["tvd"] == 0.5
        assert result["status"] == "COMPUTED"

    def test_partial_null_baseline(self):
        """Null in expected counts should not crash."""
        current = {"A": 600, "B": 400}
        expected = {"A": 500, "B": None}
        result = compute_tvd(current, expected)
        assert result["tvd"] is not None
        assert result["status"] == "COMPUTED"

    def test_missing_categories_in_expected(self):
        """Categories in current but not expected count as unseen."""
        current = {"A": 400, "B": 300, "C": 300}
        expected = {"A": 500, "B": 500}
        result = compute_tvd(current, expected)
        assert "C" in result["unseen_categories"]

    def test_tvd_bounded_0_to_1(self):
        """TVD must always be in [0, 1.0]."""
        for _ in range(20):
            import random
            current = {"A": random.randint(100, 900),
                       "B": random.randint(100, 900),
                       "C": random.randint(0, 200)}
            expected = {"A": 500, "B": 500}
            result = compute_tvd(current, expected)
            if result["tvd"] is not None:
                assert 0 <= result["tvd"] <= 1.0

    def test_empty_current(self):
        """Empty current distribution should return valid result."""
        current = {}
        expected = {"A": 500, "B": 500}
        result = compute_tvd(current, expected)
        assert result["unseen_count"] == 0
        assert result["status"] in ("COMPUTED", "BASELINE_UNAVAILABLE")

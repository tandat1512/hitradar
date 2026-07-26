"""
Tests for config fingerprint computation (full/scientific/execution).
Feature 2.9 Phase 2 — test_feature_2_9_config_fingerprint.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.fingerprints import compute_config_fingerprints


class TestComputeConfigFingerprints:
    """Tests for config fingerprint computation."""

    def test_returns_all_three_hashes(self):
        """Returns three hashes: full, scientific, execution."""
        config = {
            "mode": "train",
            "allow_training": True,
            "model_type": "random_forest",
            "n_estimators": 100,
        }
        result = compute_config_fingerprints(config)
        assert "full_config_hash" in result
        assert "scientific_config_hash" in result
        assert "execution_config_hash" in result

    def test_full_hash_is_sha256(self):
        """full_config_hash is a 64-char SHA-256 hex string."""
        result = compute_config_fingerprints({"key": "value"})
        h = result["full_config_hash"]
        assert isinstance(h, str)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_scientific_hash_is_sha256(self):
        """scientific_config_hash is a 64-char SHA-256 hex string."""
        result = compute_config_fingerprints({"key": "value"})
        h = result["scientific_config_hash"]
        assert isinstance(h, str)
        assert len(h) == 64

    def test_execution_hash_is_sha256(self):
        """execution_config_hash is a 64-char SHA-256 hex string."""
        result = compute_config_fingerprints({"key": "value"})
        h = result["execution_config_hash"]
        assert isinstance(h, str)
        assert len(h) == 64

    def test_identical_config_same_hashes(self):
        """Same config produces same hashes."""
        config = {"mode": "validate", "n_estimators": 50}
        r1 = compute_config_fingerprints(config)
        r2 = compute_config_fingerprints(config)
        assert r1["full_config_hash"] == r2["full_config_hash"]
        assert r1["scientific_config_hash"] == r2["scientific_config_hash"]
        assert r1["execution_config_hash"] == r2["execution_config_hash"]

    def test_different_config_different_full_hash(self):
        """Different config produces different full_config_hash."""
        r1 = compute_config_fingerprints({"n_estimators": 50})
        r2 = compute_config_fingerprints({"n_estimators": 100})
        assert r1["full_config_hash"] != r2["full_config_hash"]

    def test_different_scientific_params_different_full_hash(self):
        """Different scientific params change full_config_hash."""
        r1 = compute_config_fingerprints({"n_estimators": 50, "model_type": "rf"})
        r2 = compute_config_fingerprints({"n_estimators": 100, "model_type": "rf"})
        assert r1["full_config_hash"] != r2["full_config_hash"]

    def test_config_key_order_independent(self):
        """Hash is independent of dict key ordering."""
        r1 = compute_config_fingerprints({"a": 1, "b": 2, "c": 3})
        r2 = compute_config_fingerprints({"c": 3, "a": 1, "b": 2})
        assert r1["full_config_hash"] == r2["full_config_hash"]

    def test_full_hash_includes_execution_params(self):
        """full_config_hash includes execution parameters."""
        r1 = compute_config_fingerprints({"n_estimators": 50, "fail_fast": False})
        r2 = compute_config_fingerprints({"n_estimators": 50, "fail_fast": True})
        assert r1["full_config_hash"] != r2["full_config_hash"]

    def test_empty_config_produces_valid_hashes(self):
        """Empty config produces valid SHA-256 hashes."""
        result = compute_config_fingerprints({})
        for key in ["full_config_hash", "scientific_config_hash", "execution_config_hash"]:
            h = result[key]
            assert len(h) == 64
            assert all(c in "0123456789abcdef" for c in h)

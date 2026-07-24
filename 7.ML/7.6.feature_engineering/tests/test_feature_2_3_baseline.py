"""
Tests for baseline feature validation (Feature 2.3).

Validates that:
  - Exactly 18 baseline features are defined.
  - No identifier or target columns appear in the feature list.
  - Status is LOCKED.
  - SHA-256 hash is stable across the canonical ordering.
  - All expected baseline features are present.
"""

import pytest
import hashlib
import json


def sha256_of_list(lst):
    """Compute SHA-256 hash of a list."""
    return hashlib.sha256(json.dumps(lst, sort_keys=True).encode()).hexdigest()


class TestBaselineFeatureCount:
    """Tests for baseline feature count."""

    def test_baseline_feature_count_is_18(self, baseline_feature_set):
        assert baseline_feature_set["feature_count"] == 18

    def test_baseline_features_list_length(self, baseline_feature_set):
        assert len(baseline_feature_set["features"]) == 18

    def test_baseline_feature_order_length(self, baseline_feature_set):
        assert len(baseline_feature_set["feature_order"]) == 18


class TestBaselineFeatureIdentity:
    """Tests that identifier and target are not in the feature list."""

    def test_track_id_not_in_features(self, baseline_feature_set):
        features = baseline_feature_set["features"]
        assert "track_id" not in features

    def test_target_not_in_features(self, baseline_feature_set):
        features = baseline_feature_set["features"]
        assert "target_popularity" not in features

    def test_identifier_field_present(self, baseline_feature_set):
        assert baseline_feature_set["identifier"] == "track_id"

    def test_target_field_present(self, baseline_feature_set):
        assert baseline_feature_set["target"] == "target_popularity"


class TestBaselineFeatureStatus:
    """Tests for baseline feature set status."""

    def test_status_is_locked(self, baseline_feature_set):
        assert baseline_feature_set["status"] == "LOCKED"

    def test_engineering_applied_false(self, baseline_feature_set):
        assert baseline_feature_set["engineering_applied"] is False

    def test_source_feature_is_2_2(self, baseline_feature_set):
        assert baseline_feature_set["source_feature"] == "2.2"


class TestBaselineFeatureHash:
    """Tests for baseline feature SHA-256 hash stability."""

    def test_stored_sha256_matches_computed(
        self, baseline_feature_set, expected_baseline_features, baseline_sha256
    ):
        computed = sha256_of_list(expected_baseline_features)
        assert computed == baseline_feature_set["feature_list_sha256"]

    def test_feature_list_and_order_hashes_match(self, baseline_feature_set):
        assert (
            baseline_feature_set["feature_list_sha256"]
            == baseline_feature_set["feature_order_sha256"]
        )

    def test_hash_matches_canonical(self, baseline_feature_set, baseline_sha256):
        assert baseline_feature_set["feature_list_sha256"] == baseline_sha256


class TestBaselineFeatureContent:
    """Tests that all expected baseline features are present."""

    @pytest.mark.parametrize(
        "feature",
        [
            "duration_min",
            "release_year",
            "danceability",
            "energy",
            "loudness",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "release_month",
            "decade",
            "release_precision",
            "key",
            "time_signature",
            "explicit",
            "mode",
        ],
    )
    def test_expected_feature_present(self, baseline_feature_set, feature):
        features = baseline_feature_set["features"]
        assert feature in features, f"Expected baseline feature '{feature}' not found"

    def test_all_expected_features_present(
        self, baseline_feature_set, expected_baseline_features
    ):
        actual = set(baseline_feature_set["features"])
        expected = set(expected_baseline_features)
        assert actual == expected, (
            f"Feature set mismatch.\n"
            f"Missing: {expected - actual}\n"
            f"Extra: {actual - expected}"
        )

    def test_no_duplicate_features(self, baseline_feature_set):
        features = baseline_feature_set["features"]
        assert len(features) == len(set(features)), "Duplicate features found"


class TestBaselineGenerationMetadata:
    """Tests for generation metadata fields."""

    def test_feature_set_id_prefix(self, baseline_feature_set):
        assert baseline_feature_set["feature_set_id"].startswith("FS23-BASELINE")

    def test_generation_session_id_present(self, baseline_feature_set):
        assert "generation_session_id" in baseline_feature_set
        sid = baseline_feature_set["generation_session_id"]
        assert sid.startswith("FE23-")
        assert len(sid) > 5

    def test_locked_at_present(self, baseline_feature_set):
        assert "locked_at" in baseline_feature_set
        locked_at = baseline_feature_set["locked_at"]
        assert locked_at is not None
        assert isinstance(locked_at, str)
        assert "T" in locked_at  # ISO format

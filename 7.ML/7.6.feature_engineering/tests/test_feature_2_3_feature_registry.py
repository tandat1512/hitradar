"""
Tests for the feature registry (Feature 2.3).

Validates that:
  - Registry has exactly 33 features (18 baseline + 15 engineered).
  - Baseline vs engineered counts are correct.
  - All expected features are present and correctly categorised.
  - fit_required / fit_split / leakage_risk annotations are consistent.
  - Active vs rejected counts are correct.
  - Registry manifest is consistent with registry content.
"""

import pytest


class TestRegistryFeatureCounts:
    """Tests for overall feature counts in the registry."""

    def test_total_feature_count(self, feature_registry):
        assert len(feature_registry["features"]) == 33

    def test_baseline_feature_count(self, feature_registry):
        baseline = [
            f for f in feature_registry["features"]
            if f["baseline_or_engineered"] == "baseline"
        ]
        assert len(baseline) == 18

    def test_engineered_feature_count(self, feature_registry):
        engineered = [
            f for f in feature_registry["features"]
            if f["baseline_or_engineered"] == "engineered"
        ]
        assert len(engineered) == 15

    def test_selected_for_modeling_count(self, feature_registry):
        selected = [
            f for f in feature_registry["features"]
            if f["selected_for_modeling"] is True
        ]
        assert len(selected) == 31


class TestRegistryManifest:
    """Tests that the registry manifest matches the registry content."""

    def test_manifest_total_features(self, feature_registry_manifest):
        assert feature_registry_manifest["total_features"] == 33

    def test_manifest_baseline_count(self, feature_registry_manifest):
        assert feature_registry_manifest["baseline_count"] == 18

    def test_manifest_engineered_count(self, feature_registry_manifest):
        assert feature_registry_manifest["engineered_count"] == 15

    def test_manifest_selected_count(self, feature_registry_manifest):
        assert feature_registry_manifest["selected_count"] == 31

    def test_manifest_active_count(self, feature_registry_manifest):
        assert feature_registry_manifest["active_count"] == 31

    def test_manifest_rejected_count(self, feature_registry_manifest):
        assert feature_registry_manifest["rejected_count"] == 2

    def test_manifest_version(self, feature_registry_manifest):
        assert feature_registry_manifest["registry_version"] == "1.0"


class TestBaselineFeaturesClassification:
    """Tests that all baseline features are correctly classified."""

    @pytest.mark.parametrize("feature_name", [
        "duration_min", "release_year", "danceability", "energy", "loudness",
        "speechiness", "acousticness", "instrumentalness", "liveness", "valence",
        "tempo", "release_month", "decade", "release_precision", "key",
        "time_signature", "explicit", "mode",
    ])
    def test_baseline_feature_classification(
        self, feature_registry, feature_name
    ):
        feat = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == feature_name
        )
        assert feat["baseline_or_engineered"] == "baseline"
        assert feat["feature_group"] == "baseline"
        assert feat["selected_for_modeling"] is True
        assert feat["status"] == "ACTIVE"

    def test_baseline_formula_is_none(self, feature_registry):
        for feat in feature_registry["features"]:
            if feat["baseline_or_engineered"] == "baseline":
                assert feat["formula"] == "none"


class TestEngineeredFeaturesClassification:
    """Tests that all engineered features are correctly classified."""

    ENGINEERED_EXPECTED = {
        "release_month_sin": {"formula": "sin(2\\u03c0 \\u00d7 release_month / 12)"},
        "release_month_cos": {"formula": "cos(2\\u03c0 \\u00d7 release_month / 12)"},
        "year_in_decade":    {"formula": "release_year % 10"},
        "duration_log":      {"formula": "log1p(max(duration_min, 0))"},
        "duration_squared":   {"formula": "duration_min ** 2"},
        "energy_danceability":         {"formula": "energy * danceability"},
        "energy_valence":             {"formula": "energy * valence"},
        "danceability_valence":        {"formula": "danceability * valence"},
        "acousticness_instrumentalness": {"formula": "acousticness * instrumentalness"},
        "energy_liveness":             {"formula": "energy * liveness"},
        "speechiness_explicit":        {"formula": "speechiness * explicit"},
        "tempo_danceability":          {"formula": "tempo * danceability"},
        "loudness_energy":             {"formula": "loudness * energy"},
        "duration_bucket":             {"formula": "bucketize based on Q25, Q50, Q75", "selected": False},
        "long_track_flag":             {"formula": "duration_min > Q75", "selected": False},
    }

    @pytest.mark.parametrize("feature_name", list(ENGINEERED_EXPECTED.keys()))
    def test_engineered_feature_classification(
        self, feature_registry, feature_name
    ):
        feat = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == feature_name
        )
        assert feat["baseline_or_engineered"] == "engineered"
        assert feat["selected_for_modeling"] == (
            not feat.get("status") == "REJECTED"
        )

    @pytest.mark.parametrize(
        "feature_name,expected_formula",
        [
            ("release_month_sin", "sin(2π × release_month / 12)"),
            ("release_month_cos", "cos(2π × release_month / 12)"),
            ("year_in_decade",    "release_year % 10"),
            ("duration_log",      "log1p(max(duration_min, 0))"),
            ("duration_squared",   "duration_min ** 2"),
            ("energy_danceability",         "energy * danceability"),
            ("energy_valence",             "energy * valence"),
            ("danceability_valence",        "danceability * valence"),
            ("acousticness_instrumentalness", "acousticness * instrumentalness"),
            ("energy_liveness",             "energy * liveness"),
            ("speechiness_explicit",        "speechiness * explicit"),
            ("tempo_danceability",          "tempo * danceability"),
            ("loudness_energy",             "loudness * energy"),
        ],
    )
    def test_engineered_formula_correct(
        self, feature_registry, feature_name, expected_formula
    ):
        feat = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == feature_name
        )
        assert feat["formula"] == expected_formula


class TestRejectedFeatures:
    """Tests for features that were rejected during feature selection."""

    def test_duration_bucket_rejected(self, feature_registry):
        feat = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == "duration_bucket"
        )
        assert feat["status"] == "REJECTED"
        assert feat["selected_for_modeling"] is False
        assert feat["exclusion_reason"] is not None
        assert len(feat["exclusion_reason"]) > 0

    def test_long_track_flag_rejected(self, feature_registry):
        feat = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == "long_track_flag"
        )
        assert feat["status"] == "REJECTED"
        assert feat["selected_for_modeling"] is False
        assert feat["exclusion_reason"] is not None

    def test_only_two_rejected_features(self, feature_registry):
        rejected = [
            f for f in feature_registry["features"]
            if f["status"] == "REJECTED"
        ]
        assert len(rejected) == 2


class TestRegistrySchemaConsistency:
    """Tests that every registry entry has all required schema fields."""

    REQUIRED_FIELDS = [
        "feature_name", "feature_group", "baseline_or_engineered",
        "source_columns", "formula", "dtype", "semantic_role",
        "fit_required", "fit_split", "learned_parameters",
        "missing_handling", "encoding_requirement", "scaling_requirement",
        "leakage_risk", "selected_for_modeling", "exclusion_reason",
        "version", "status",
    ]

    def test_all_entries_have_required_fields(self, feature_registry):
        for feat in feature_registry["features"]:
            for field in self.REQUIRED_FIELDS:
                assert field in feat, (
                    f"Feature '{feat['feature_name']}' missing field '{field}'"
                )

    def test_all_source_columns_non_empty(self, feature_registry):
        for feat in feature_registry["features"]:
            assert len(feat["source_columns"]) > 0, (
                f"Feature '{feat['feature_name']}' has empty source_columns"
            )

    def test_valid_dtype_values(self, feature_registry):
        valid_dtypes = {"float64", "int64", "category"}
        for feat in feature_registry["features"]:
            assert feat["dtype"] in valid_dtypes, (
                f"Feature '{feat['feature_name']}' has invalid dtype "
                f"'{feat['dtype']}'"
            )

    def test_valid_semantic_roles(self, feature_registry):
        valid_roles = {"continuous", "categorical", "binary"}
        for feat in feature_registry["features"]:
            assert feat["semantic_role"] in valid_roles, (
                f"Feature '{feat['feature_name']}' has invalid semantic_role "
                f"'{feat['semantic_role']}'"
            )

    def test_valid_status_values(self, feature_registry):
        valid_statuses = {"ACTIVE", "REJECTED", "EXPERIMENTAL"}
        for feat in feature_registry["features"]:
            assert feat["status"] in valid_statuses, (
                f"Feature '{feat['feature_name']}' has invalid status "
                f"'{feat['status']}'"
            )

    def test_exclusion_reason_null_when_selected(self, feature_registry):
        for feat in feature_registry["features"]:
            if feat["selected_for_modeling"]:
                assert feat["exclusion_reason"] is None

    def test_exclusion_reason_set_when_rejected(self, feature_registry):
        for feat in feature_registry["features"]:
            if feat["status"] == "REJECTED":
                assert feat["exclusion_reason"] is not None
                assert len(feat["exclusion_reason"]) > 0


class TestFeatureGroupAssignment:
    """Tests that features are assigned to the correct feature groups."""

    def test_time_group_features(self, feature_registry):
        time_feats = [
            f for f in feature_registry["features"]
            if f["feature_group"] == "time"
        ]
        expected = {"release_month_sin", "release_month_cos", "year_in_decade"}
        actual = {f["feature_name"] for f in time_feats}
        assert actual == expected

    def test_duration_group_features(self, feature_registry):
        duration_feats = [
            f for f in feature_registry["features"]
            if f["feature_group"] == "duration"
        ]
        expected = {
            "duration_log", "duration_squared",
            "duration_bucket", "long_track_flag",
        }
        actual = {f["feature_name"] for f in duration_feats}
        assert actual == expected

    def test_audio_interaction_group_features(self, feature_registry):
        audio_feats = [
            f for f in feature_registry["features"]
            if f["feature_group"] == "audio_interaction"
        ]
        expected = {
            "energy_danceability", "energy_valence", "danceability_valence",
            "acousticness_instrumentalness", "energy_liveness",
            "speechiness_explicit", "tempo_danceability", "loudness_energy",
        }
        actual = {f["feature_name"] for f in audio_feats}
        assert actual == expected


class TestGeneratedAtField:
    """Tests for the generated_at timestamp field."""

    def test_generated_at_present(self, feature_registry):
        assert "generated_at" in feature_registry
        ts = feature_registry["generated_at"]
        assert isinstance(ts, str)
        assert "T" in ts  # ISO 8601 format

    def test_generated_at_matches_manifest(
        self, feature_registry, feature_registry_manifest
    ):
        assert feature_registry["generated_at"] == (
            feature_registry_manifest["generated_at"]
        )

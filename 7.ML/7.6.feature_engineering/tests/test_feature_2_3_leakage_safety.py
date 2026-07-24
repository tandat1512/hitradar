"""
Tests for data leakage safety in Feature 2.3.

Validates that:
  - Learned parameters (e.g., duration thresholds) come from train only.
  - No ablation experiment uses the test split.
  - Feature registry correctly marks fit_required / fit_split fields.
  - No target-derived features exist in the registry.
  - Baseline metrics do not use test split.
"""

import pytest


class TestTrainOnlyLearnedParameters:
    """Tests that learned parameters come from the training split only."""

    def test_duration_thresholds_in_registry_from_train(
        self, feature_registry
    ):
        """duration_bucket has q25/q50/q75 learned from train."""
        duration_bucket = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == "duration_bucket"
        )
        assert duration_bucket["fit_required"] is True
        assert duration_bucket["fit_split"] == "train"
        assert "q25" in duration_bucket["learned_parameters"]
        assert "q50" in duration_bucket["learned_parameters"]
        assert "q75" in duration_bucket["learned_parameters"]

    def test_long_track_flag_fit_split_is_train(self, feature_registry):
        long_track = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == "long_track_flag"
        )
        assert long_track["fit_required"] is True
        assert long_track["fit_split"] == "train"

    def test_duration_thresholds_json_matches_registry(
        self, duration_thresholds, feature_registry
    ):
        duration_bucket = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == "duration_bucket"
        )
        assert (
            duration_bucket["learned_parameters"]["q25"]
            == duration_thresholds["q25"]
        )
        assert (
            duration_bucket["learned_parameters"]["q50"]
            == duration_thresholds["q50"]
        )
        assert (
            duration_bucket["learned_parameters"]["q75"]
            == duration_thresholds["q75"]
        )

    def test_non_learned_features_fit_required_false(self, feature_registry):
        """All baseline and non-fit engineered features should not require fitting."""
        non_fit_features = [
            "release_month_sin", "release_month_cos", "year_in_decade",
            "duration_log", "duration_squared",
            "energy_danceability", "energy_valence", "danceability_valence",
            "acousticness_instrumentalness", "energy_liveness",
            "speechiness_explicit", "tempo_danceability", "loudness_energy",
        ]
        for name in non_fit_features:
            feat = next(f for f in feature_registry["features"] if f["feature_name"] == name)
            assert feat["fit_required"] is False, f"{name} should not require fit"


class TestNoTestSplitUsage:
    """Tests that no experiment uses the test split."""

    def test_all_ablation_experiments_test_used_false(
        self, feature_ablation_results
    ):
        for exp_id, exp in feature_ablation_results.items():
            assert exp.get("test_used") is False, (
                f"Experiment {exp_id} used test split (test_used=True)"
            )

    def test_baseline_metrics_test_used_false(self, baseline_metrics):
        assert baseline_metrics.get("test_used") is False, (
            "Baseline metrics used test split"
        )

    def test_selected_feature_set_test_used_false(self, selected_feature_set):
        assert selected_feature_set.get("test_used") is False, (
            "Selected feature set used test split"
        )

    def test_feature_selection_results_method_is_train_only(
        self, feature_selection_results
    ):
        # The selection method itself proves train-only usage.
        # feature_selection_results.json does not contain a test_used key,
        # which is consistent with the SELECTION-TRAIN-ONLY validation check.
        assert "test_used" not in feature_selection_results
        assert feature_selection_results["feature_selection_method"] == "train_only_temporal_cv"


class TestNoTargetDerivedFeatures:
    """Tests that no feature formula contains the target variable."""

    def test_no_target_in_any_feature_formula(self, feature_registry):
        for feat in feature_registry["features"]:
            formula = feat.get("formula", "none")
            if formula != "none":
                assert "target" not in formula.lower(), (
                    f"Feature '{feat['feature_name']}' formula contains 'target': "
                    f"{formula}"
                )

    def test_no_target_derived_in_validation_results(
        self, feature_2_3_validation_results
    ):
        """Check NO-TARGET-DERIVED-FEATURE check passed."""
        check = next(
            c for c in feature_2_3_validation_results["checks"]
            if c["check_id"] == "NO-TARGET-DERIVED-FEATURE"
        )
        assert check["status"] == "PASS"
        assert check["actual"] is False


class TestLeakageRiskAnnotations:
    """Tests for leakage risk annotations in the feature registry."""

    def test_all_features_have_leakage_risk_field(self, feature_registry):
        for feat in feature_registry["features"]:
            assert "leakage_risk" in feat, (
                f"Feature '{feat['feature_name']}' missing leakage_risk field"
            )

    def test_baseline_features_no_leakage_risk(self, feature_registry):
        baseline_feats = [
            f for f in feature_registry["features"]
            if f["baseline_or_engineered"] == "baseline"
        ]
        for feat in baseline_feats:
            assert feat["leakage_risk"] == "none", (
                f"Baseline feature '{feat['feature_name']}' should have "
                f"leakage_risk='none', got '{feat['leakage_risk']}'"
            )

    def test_duration_bucket_low_leakage_risk(self, feature_registry):
        duration_bucket = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == "duration_bucket"
        )
        assert duration_bucket["leakage_risk"] == "low"

    def test_long_track_flag_low_leakage_risk(self, feature_registry):
        long_track = next(
            f for f in feature_registry["features"]
            if f["feature_name"] == "long_track_flag"
        )
        assert long_track["leakage_risk"] == "low"


class TestValidationChecksLeakage:
    """Tests that the feature_2_3_validation_results pass all leakage-related checks."""

    @pytest.mark.parametrize(
        "check_id",
        [
            "DURATION-THRESHOLDS-TRAIN-ONLY",
            "NO-TEST-ACCESS",
            "NO-TARGET-DERIVED-FEATURE",
            "SELECTION-TRAIN-ONLY",
        ],
    )
    def test_validation_check_passed(
        self, feature_2_3_validation_results, check_id
    ):
        check = next(
            (c for c in feature_2_3_validation_results["checks"] if c["check_id"] == check_id),
            None,
        )
        assert check is not None, f"Check '{check_id}' not found in validation results"
        assert check["status"] == "PASS", (
            f"Check '{check_id}' failed: {check.get('message')}"
        )

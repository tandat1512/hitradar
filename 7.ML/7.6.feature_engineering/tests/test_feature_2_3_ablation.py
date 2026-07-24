"""
Tests for ablation experiment results (Feature 2.3).

Validates that:
  - All expected experiment groups (T, D, A) are present.
  - Each experiment has required fields.
  - Experiments used for selection do not touch test.
  - Baseline reference is consistent with baseline_metrics.
  - Improvement is computed and is positive for the selected set.
"""

import pytest


class TestAblationExperimentCoverage:
    """Tests that all expected ablation experiment groups are present."""

    def test_time_experiments_present(self, feature_ablation_results):
        time_exps = ["EXP23-T0", "EXP23-T1", "EXP23-T2", "EXP23-T3", "EXP23-T4"]
        for exp_id in time_exps:
            assert exp_id in feature_ablation_results, (
                f"Time experiment '{exp_id}' not found"
            )

    def test_duration_experiments_present(self, feature_ablation_results):
        duration_exps = ["EXP23-D0", "EXP23-D1", "EXP23-D2", "EXP23-D3", "EXP23-D4"]
        for exp_id in duration_exps:
            assert exp_id in feature_ablation_results, (
                f"Duration experiment '{exp_id}' not found"
            )

    def test_audio_experiments_present(self, feature_ablation_results):
        # A0-A10 (11 audio interaction experiments)
        audio_exps = [f"EXP23-A{i}" for i in range(11)]
        for exp_id in audio_exps:
            assert exp_id in feature_ablation_results, (
                f"Audio experiment '{exp_id}' not found"
            )

    def test_total_experiment_count(self, feature_ablation_results):
        # 5 time + 5 duration + 11 audio = 21
        assert len(feature_ablation_results) == 21


class TestExperimentStructure:
    """Tests that each experiment has all required fields."""

    @pytest.fixture
    def required_fields(self):
        return [
            "experiment_id", "feature_count", "train_rows", "validation_rows",
            "fit_split", "evaluation_split", "model", "model_parameters",
            "train", "validation", "runtime_seconds", "random_state", "test_used",
        ]

    @pytest.mark.parametrize("exp_id", [
        "EXP23-T0", "EXP23-D0", "EXP23-A0",
    ])
    def test_experiment_has_required_fields(
        self, feature_ablation_results, required_fields, exp_id
    ):
        exp = feature_ablation_results[exp_id]
        for field in required_fields:
            assert field in exp, f"Experiment {exp_id} missing field '{field}'"


class TestExperimentMetrics:
    """Tests for the structure of train/validation metrics within experiments."""

    def test_train_metrics_have_required_fields(self, feature_ablation_results):
        required = {"MAE", "RMSE", "R2"}
        for exp_id, exp in feature_ablation_results.items():
            assert required.issubset(exp["train"].keys()), (
                f"{exp_id} train metrics missing fields"
            )

    def test_validation_metrics_have_required_fields(self, feature_ablation_results):
        required = {"MAE", "RMSE", "R2"}
        for exp_id, exp in feature_ablation_results.items():
            assert required.issubset(exp["validation"].keys()), (
                f"{exp_id} validation metrics missing fields"
            )

    def test_mae_positive(self, feature_ablation_results):
        for exp_id, exp in feature_ablation_results.items():
            assert exp["train"]["MAE"] >= 0, f"{exp_id} train MAE is negative"
            assert exp["validation"]["MAE"] >= 0, f"{exp_id} val MAE is negative"

    def test_rmse_positive(self, feature_ablation_results):
        for exp_id, exp in feature_ablation_results.items():
            assert exp["train"]["RMSE"] >= 0, f"{exp_id} train RMSE is negative"
            assert exp["validation"]["RMSE"] >= 0, f"{exp_id} val RMSE is negative"

    def test_runtime_positive(self, feature_ablation_results):
        for exp_id, exp in feature_ablation_results.items():
            assert exp["runtime_seconds"] >= 0, (
                f"{exp_id} runtime is negative"
            )

    def test_random_state_consistent(self, feature_ablation_results):
        random_states = {exp["random_state"] for exp in feature_ablation_results.values()}
        assert len(random_states) == 1, "random_state is not consistent across experiments"


class TestExperimentSplits:
    """Tests for experiment split consistency."""

    def test_all_experiments_fit_on_train(self, feature_ablation_results):
        for exp_id, exp in feature_ablation_results.items():
            assert exp["fit_split"] == "train", (
                f"{exp_id} fit_split is not 'train'"
            )

    def test_all_experiments_eval_on_validation(self, feature_ablation_results):
        for exp_id, exp in feature_ablation_results.items():
            assert exp["evaluation_split"] == "validation", (
                f"{exp_id} evaluation_split is not 'validation'"
            )

    def test_all_experiments_use_ridge_model(self, feature_ablation_results):
        for exp_id, exp in feature_ablation_results.items():
            assert exp["model"] == "Ridge", (
                f"{exp_id} model is not 'Ridge'"
            )

    def test_row_counts_consistent(self, feature_ablation_results):
        for exp_id, exp in feature_ablation_results.items():
            assert exp["train_rows"] == 415524, (
                f"{exp_id} train_rows should be 415524, got {exp['train_rows']}"
            )
            assert exp["validation_rows"] == 85272, (
                f"{exp_id} validation_rows should be 85272, "
                f"got {exp['validation_rows']}"
            )


class TestBaselineReference:
    """Tests that the T0 time experiment matches standalone baseline metrics."""

    def test_baseline_experiment_matches_baseline_metrics(
        self, feature_ablation_results, baseline_metrics
    ):
        # The baseline metrics file corresponds to EXP23-T0 (18-feature baseline)
        baseline_exp = feature_ablation_results["EXP23-T0"]
        assert baseline_exp["train"]["MAE"] == pytest.approx(
            baseline_metrics["train"]["MAE"], rel=1e-9
        )
        assert baseline_exp["train"]["RMSE"] == pytest.approx(
            baseline_metrics["train"]["RMSE"], rel=1e-9
        )
        assert baseline_exp["validation"]["MAE"] == pytest.approx(
            baseline_metrics["validation"]["MAE"], rel=1e-9
        )
        assert baseline_exp["validation"]["RMSE"] == pytest.approx(
            baseline_metrics["validation"]["RMSE"], rel=1e-9
        )


class TestFeatureSelectionResults:
    """Tests for the feature selection results artifact."""

    def test_selection_method_is_train_only_temporal_cv(
        self, feature_selection_results
    ):
        assert (
            feature_selection_results["feature_selection_method"]
            == "train_only_temporal_cv"
        )

    def test_best_experiment_is_EXP23_A10(self, feature_selection_results):
        assert feature_selection_results["best_experiment"] == "EXP23-A10"

    def test_best_experiment_exists_in_ablation(
        self, feature_selection_results, feature_ablation_results
    ):
        best = feature_selection_results["best_experiment"]
        assert best in feature_ablation_results, (
            f"Best experiment '{best}' not found in ablation results"
        )

    def test_best_rmse_improvement_is_positive(self, feature_selection_results):
        improvement = feature_selection_results["improvement"]
        assert improvement > 0, (
            f"Improvement should be positive, got {improvement}"
        )

    def test_improvement_pct_reasonable(self, feature_selection_results):
        pct = feature_selection_results["improvement_pct"]
        assert 0 < pct < 50, (
            f"Improvement percentage {pct} seems unreasonable"
        )

    def test_best_rmse_better_than_baseline(
        self, feature_selection_results, baseline_metrics
    ):
        assert feature_selection_results["best_experiment_rmse"] < (
            baseline_metrics["validation"]["RMSE"]
        )

    def test_engineered_features_were_selected(self, feature_selection_results):
        assert feature_selection_results["engineered_selected"] is True

    def test_selected_feature_count_reasonable(self, feature_selection_results):
        count = feature_selection_results["selected_feature_count"]
        assert 18 <= count <= 33, (
            f"Selected feature count {count} outside expected range"
        )


class TestAblationValidationResults:
    """Tests for ablation-related checks in feature_2_3_validation_results."""

    def test_ablations_complete_check_passed(
        self, feature_2_3_validation_results
    ):
        check = next(
            c for c in feature_2_3_validation_results["checks"]
            if c["check_id"] == "ABLATION-COMPLETE"
        )
        assert check["status"] == "PASS"

    def test_time_experiments_valid_check_passed(
        self, feature_2_3_validation_results
    ):
        check = next(
            c for c in feature_2_3_validation_results["checks"]
            if c["check_id"] == "TIME-FEATURES-VALID"
        )
        assert check["status"] == "PASS"

    def test_audio_experiments_valid_check_passed(
        self, feature_2_3_validation_results
    ):
        check = next(
            c for c in feature_2_3_validation_results["checks"]
            if c["check_id"] == "AUDIO-FEATURES-VALID"
        )
        assert check["status"] == "PASS"

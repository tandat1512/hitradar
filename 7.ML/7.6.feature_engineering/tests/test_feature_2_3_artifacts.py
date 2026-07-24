"""
Tests for artifact integrity (Feature 2.3).

Validates that:
  - All expected artifact files exist on disk.
  - Artifact files are non-empty.
  - SHA-256 hashes are 64-character hex strings.
  - All JSON artifacts are valid (parseable) and contain required top-level fields.
  - Feature order SHA-256 matches across artifacts.
  - Feature 2.4 input contract is consistent with selected features.
"""

import json
import os
import pytest


class TestArtifactFilePresence:
    """Tests that all expected artifact files exist."""

    EXPECTED_ARTIFACTS = [
        "baseline_feature_set.json",
        "baseline_feature_validation.json",
        "baseline_metrics.json",
        "baseline_model_config.json",
        "baseline_validation_predictions.parquet",
        "duration_feature_ablation_results.json",
        "duration_thresholds.json",
        "feature_2_3_generation_context.json",
        "feature_2_3_validation_results.json",
        "feature_2_4_input_contract.json",
        "feature_ablation_results.json",
        "feature_engineering_pipeline.joblib",
        "feature_engineering_pipeline_manifest.json",
        "feature_registry.csv",
        "feature_registry.json",
        "feature_registry_manifest.json",
        "feature_selection_results.json",
        "mood_cluster_status.json",
        "selected_feature_set.json",
        "train_engineered_schema.json",
        "validation_engineered_schema.json",
    ]

    @pytest.mark.parametrize("artifact_name", EXPECTED_ARTIFACTS)
    def test_artifact_exists(self, output_dir, artifact_name):
        path = os.path.join(output_dir, artifact_name)
        assert os.path.isfile(path), f"Artifact not found: {artifact_name}"

    @pytest.mark.parametrize("artifact_name", EXPECTED_ARTIFACTS)
    def test_artifact_non_empty(self, output_dir, artifact_name):
        path = os.path.join(output_dir, artifact_name)
        size = os.path.getsize(path)
        assert size > 0, f"Artifact is empty: {artifact_name}"


class TestJsonArtifactsValidity:
    """Tests that all JSON artifact files are valid and parseable."""

    JSON_ARTIFACTS = [
        "baseline_feature_set.json",
        "baseline_feature_validation.json",
        "baseline_metrics.json",
        "baseline_model_config.json",
        "duration_thresholds.json",
        "feature_2_3_generation_context.json",
        "feature_2_3_validation_results.json",
        "feature_2_4_input_contract.json",
        "feature_ablation_results.json",
        "feature_engineering_pipeline_manifest.json",
        "feature_registry.json",
        "feature_registry_manifest.json",
        "feature_selection_results.json",
        "mood_cluster_status.json",
        "selected_feature_set.json",
        "train_engineered_schema.json",
        "validation_engineered_schema.json",
    ]

    @pytest.mark.parametrize("artifact_name", JSON_ARTIFACTS)
    def test_json_artifact_parseable(self, output_dir, artifact_name):
        path = os.path.join(output_dir, artifact_name)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data is not None, f"Artifact parsed as None: {artifact_name}"

    @pytest.mark.parametrize("artifact_name", JSON_ARTIFACTS)
    def test_json_artifact_is_dict(self, output_dir, artifact_name):
        path = os.path.join(output_dir, artifact_name)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict), (
            f"Artifact root should be a dict: {artifact_name}"
        )


class TestSha256Hashes:
    """Tests that SHA-256 hash fields are well-formed."""

    def test_baseline_feature_set_sha256_length(
        self, baseline_feature_set
    ):
        sha = baseline_feature_set["feature_list_sha256"]
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)

    def test_baseline_feature_order_sha256_length(
        self, baseline_feature_set
    ):
        sha = baseline_feature_set["feature_order_sha256"]
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)

    def test_pipeline_manifest_sha256_length(
        self, feature_engineering_pipeline_manifest
    ):
        sha = feature_engineering_pipeline_manifest["pipeline_sha256"]
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)

    def test_feature_2_4_input_contract_sha256_length(
        self, feature_2_4_input_contract
    ):
        sha = feature_2_4_input_contract["feature_order_sha256"]
        assert len(sha) == 64
        assert all(c in "0123456789abcdef" for c in sha)


class TestFeatureOrderConsistency:
    """Tests that feature order hashes are consistent across artifacts."""

    def test_selected_feature_order_sha256_consistent(
        self, selected_feature_set, feature_2_4_input_contract
    ):
        sha_selected = selected_feature_set["feature_order_sha256"]
        sha_contract = feature_2_4_input_contract["feature_order_sha256"]
        assert sha_selected == sha_contract, (
            "feature_order_sha256 mismatch between selected_feature_set.json "
            "and feature_2_4_input_contract.json"
        )


class TestFeature2_4InputContract:
    """Tests for the Feature 2.4 input contract artifact."""

    def test_contract_source_feature_is_2_3(
        self, feature_2_4_input_contract
    ):
        assert feature_2_4_input_contract["source_feature"] == "2.3"

    def test_contract_target_is_target_popularity(
        self, feature_2_4_input_contract
    ):
        assert feature_2_4_input_contract["target"] == "target_popularity"

    def test_contract_identifier_is_track_id(
        self, feature_2_4_input_contract
    ):
        assert feature_2_4_input_contract["identifier"] == "track_id"

    def test_contract_selected_feature_count_is_31(
        self, feature_2_4_input_contract
    ):
        assert feature_2_4_input_contract["selected_feature_count"] == 31

    def test_contract_selected_feature_order_count_is_31(
        self, feature_2_4_input_contract
    ):
        assert len(feature_2_4_input_contract["selected_feature_order"]) == 31

    def test_contract_selected_feature_order_matches_selected_set(
        self, feature_2_4_input_contract, selected_feature_set
    ):
        contract_order = feature_2_4_input_contract["selected_feature_order"]
        # selected_feature_set.json uses "selected_features" key for the ordered list
        set_order = selected_feature_set["selected_features"]
        assert contract_order == set_order

    def test_contract_pipeline_path_in_manifest(
        self, feature_2_4_input_contract, feature_engineering_pipeline_manifest
    ):
        contract_path = feature_2_4_input_contract["pipeline_path"]
        manifest_path = feature_engineering_pipeline_manifest["pipeline_path"]
        # Both should reference the same pipeline file (same basename)
        assert os.path.basename(contract_path) == os.path.basename(manifest_path)

    def test_contract_pipeline_sha256_matches_manifest(
        self, feature_2_4_input_contract, feature_engineering_pipeline_manifest
    ):
        assert (
            feature_2_4_input_contract["pipeline_sha256"]
            == feature_engineering_pipeline_manifest["pipeline_sha256"]
        )

    def test_contract_row_counts_present(self, feature_2_4_input_contract):
        assert feature_2_4_input_contract["train_rows"] == 415524
        assert feature_2_4_input_contract["validation_rows"] == 85272
        assert feature_2_4_input_contract["test_rows"] == 85876

    def test_contract_test_status_is_deferred(
        self, feature_2_4_input_contract
    ):
        assert feature_2_4_input_contract["test_status"] == "DEFERRED_TO_2_5"

    def test_contract_model_training_owner_is_feature_2_4(
        self, feature_2_4_input_contract
    ):
        assert feature_2_4_input_contract["model_training_owner"] == "Feature 2.4"

    def test_contract_validation_schema_valid(
        self, feature_2_4_input_contract
    ):
        schema = feature_2_4_input_contract["validation_schema"]
        assert schema["train_shape"] == [415524, 31]
        assert schema["validation_shape"] == [85272, 31]
        assert schema["features_match"] is True


class TestValidationResultsChecks:
    """Tests for the feature_2_3_validation_results artifact structure."""

    def test_validation_results_has_required_fields(
        self, feature_2_3_validation_results
    ):
        required = [
            "validation_timestamp", "total_checks", "passed",
            "failed", "warnings", "checks",
        ]
        for field in required:
            assert field in feature_2_3_validation_results, (
                f"Missing field '{field}' in validation_results"
            )

    def test_all_validation_checks_passed(self, feature_2_3_validation_results):
        assert feature_2_3_validation_results["failed"] == 0
        assert feature_2_3_validation_results["passed"] == 22
        assert feature_2_3_validation_results["total_checks"] == 22

    def test_each_check_has_required_fields(self, feature_2_3_validation_results):
        required = ["check_id", "expected", "actual", "evidence_path",
                    "evidence_pointer", "status", "message"]
        for check in feature_2_3_validation_results["checks"]:
            for field in required:
                assert field in check, (
                    f"Check '{check.get('check_id')}' missing field '{field}'"
                )

    def test_each_check_status_is_pass(self, feature_2_3_validation_results):
        for check in feature_2_3_validation_results["checks"]:
            assert check["status"] == "PASS", (
                f"Check '{check['check_id']}' status is '{check['status']}'"
            )

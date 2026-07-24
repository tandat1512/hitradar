"""
Tests for report generation (Feature 2.3).

Validates that:
  - All validation checks in feature_2_3_validation_results have PASS status.
  - Report-level assertions (total checks, passed/failed counts) are consistent.
  - All artifact paths referenced in validation checks exist.
  - No warnings or failures are present.
  - Validation timestamp is a valid ISO-8601 string.
"""

import json
import os
import pytest


class TestReportStructure:
    """Tests for the overall structure of feature_2_3_validation_results.json."""

    def test_validation_timestamp_is_iso_format(self, feature_2_3_validation_results):
        ts = feature_2_3_validation_results["validation_timestamp"]
        assert isinstance(ts, str)
        assert "T" in ts, "validation_timestamp should be ISO-8601 format"
        # Should contain date and time parts
        date_part, time_part = ts.split("T")
        assert "-" in date_part
        assert ":" in time_part

    def test_total_checks_count(self, feature_2_3_validation_results):
        checks = feature_2_3_validation_results["checks"]
        assert feature_2_3_validation_results["total_checks"] == len(checks)
        assert len(checks) == 22

    def test_passed_count_matches_pass_checks(
        self, feature_2_3_validation_results
    ):
        passed = sum(1 for c in feature_2_3_validation_results["checks"]
                      if c["status"] == "PASS")
        assert feature_2_3_validation_results["passed"] == passed

    def test_failed_count_matches_fail_checks(
        self, feature_2_3_validation_results
    ):
        failed = sum(1 for c in feature_2_3_validation_results["checks"]
                     if c["status"] == "FAIL")
        assert feature_2_3_validation_results["failed"] == failed

    def test_warnings_count(self, feature_2_3_validation_results):
        warnings = sum(1 for c in feature_2_3_validation_results["checks"]
                        if c["status"] == "WARNING")
        assert feature_2_3_validation_results["warnings"] == warnings


class TestReportSummary:
    """Tests for the summary-level assertions of the report."""

    def test_all_checks_passed(self, feature_2_3_validation_results):
        assert feature_2_3_validation_results["failed"] == 0, (
            "Some checks failed"
        )

    def test_no_warnings(self, feature_2_3_validation_results):
        assert feature_2_3_validation_results["warnings"] == 0, (
            "Some checks produced warnings"
        )

    def test_all_22_checks_passed(self, feature_2_3_validation_results):
        assert feature_2_3_validation_results["passed"] == 22, (
            f"Expected 22 passed checks, got "
            f"{feature_2_3_validation_results['passed']}"
        )

    def test_passed_plus_failed_equals_total(
        self, feature_2_3_validation_results
    ):
        vr = feature_2_3_validation_results
        assert vr["passed"] + vr["failed"] == vr["total_checks"]


class TestReportCheckCoverage:
    """Tests that all expected check IDs are present in the report."""

    EXPECTED_CHECK_IDS = [
        "BASELINE-COUNT-18",
        "BASELINE-NO-ID",
        "BASELINE-NO-TARGET",
        "BASELINE-LOCKED",
        "BASELINE-HASH-STABLE",
        "TRAIN-VAL-SCHEMA-MATCH",
        "TIME-FEATURES-VALID",
        "DURATION-THRESHOLDS-TRAIN-ONLY",
        "AUDIO-FEATURES-VALID",
        "MOOD-CLUSTER-TRAIN-ONLY-OR-NA",
        "NO-TARGET-DERIVED-FEATURE",
        "NO-TEST-ACCESS",
        "NO-UNEXPECTED-NAN",
        "NO-INF",
        "NO-DUPLICATE-FEATURE-NAMES",
        "ABLATION-COMPLETE",
        "SELECTION-TRAIN-ONLY",
        "SELECTED-SET-LOCKED",
        "REGISTRY-COMPLETE",
        "PIPELINE-SAVE-LOAD",
        "FEATURE-ORDER-STABLE",
        "FEATURE-2-4-CONTRACT-COMPLETE",
    ]

    @pytest.mark.parametrize("check_id", EXPECTED_CHECK_IDS)
    def test_check_id_present(self, feature_2_3_validation_results, check_id):
        check_ids = [c["check_id"] for c in feature_2_3_validation_results["checks"]]
        assert check_id in check_ids, f"Expected check '{check_id}' not found in report"

    def test_no_extra_check_ids(self, feature_2_3_validation_results):
        actual_ids = {c["check_id"] for c in feature_2_3_validation_results["checks"]}
        expected_ids = set(self.EXPECTED_CHECK_IDS)
        assert actual_ids == expected_ids, (
            f"Unexpected check IDs: {actual_ids - expected_ids}"
        )


class TestReportCheckAssertions:
    """Per-check assertions for key validation checks."""

    def test_baseline_count_check(self, feature_2_3_validation_results):
        check = next(c for c in feature_2_3_validation_results["checks"]
                     if c["check_id"] == "BASELINE-COUNT-18")
        assert check["expected"] == 18
        assert check["actual"] == 18
        assert check["status"] == "PASS"

    def test_baseline_locked_check(self, feature_2_3_validation_results):
        check = next(c for c in feature_2_3_validation_results["checks"]
                     if c["check_id"] == "BASELINE-LOCKED")
        assert check["expected"] == "LOCKED"
        assert check["actual"] == "LOCKED"
        assert check["status"] == "PASS"

    def test_baseline_hash_stable_check(self, feature_2_3_validation_results):
        check = next(c for c in feature_2_3_validation_results["checks"]
                     if c["check_id"] == "BASELINE-HASH-STABLE")
        sha = "823ced641e09acf862ea3d186a92e35a6a1456aa4f4285f3aefa22e5f7b69e6c"
        assert check["expected"] == sha
        assert check["actual"] == sha
        assert check["status"] == "PASS"

    def test_registry_complete_check(self, feature_2_3_validation_results):
        check = next(c for c in feature_2_3_validation_results["checks"]
                     if c["check_id"] == "REGISTRY-COMPLETE")
        assert check["expected"] == 33
        assert check["actual"] == 33
        assert check["status"] == "PASS"

    def test_train_val_schema_match_check(self, feature_2_3_validation_results):
        check = next(c for c in feature_2_3_validation_results["checks"]
                     if c["check_id"] == "TRAIN-VAL-SCHEMA-MATCH")
        assert check["actual"] == check["expected"]
        assert check["status"] == "PASS"

    def test_selection_train_only_check(self, feature_2_3_validation_results):
        check = next(c for c in feature_2_3_validation_results["checks"]
                     if c["check_id"] == "SELECTION-TRAIN-ONLY")
        assert check["actual"] == "train_only_temporal_cv, test_used=False"
        assert check["status"] == "PASS"

    def test_selected_set_locked_check(self, feature_2_3_validation_results):
        check = next(c for c in feature_2_3_validation_results["checks"]
                     if c["check_id"] == "SELECTED-SET-LOCKED")
        assert check["expected"] == "LOCKED"
        assert check["actual"] == "LOCKED"
        assert check["status"] == "PASS"


class TestReportEvidencePaths:
    """Tests that evidence paths referenced in the report actually exist."""

    def test_all_referenced_artifacts_exist(self, output_dir, feature_2_3_validation_results):
        missing = []
        for check in feature_2_3_validation_results["checks"]:
            # evidence_path may list multiple files separated by commas
            paths_str = check.get("evidence_path", "")
            for artifact_name in paths_str.replace(" ", "").split(","):
                artifact_name = artifact_name.strip()
                if artifact_name:
                    path = os.path.join(output_dir, artifact_name)
                    if not os.path.isfile(path):
                        missing.append(artifact_name)
        assert not missing, f"Evidence artifacts not found: {missing}"


class TestReportMessageQuality:
    """Tests that check messages are informative and non-empty."""

    def test_all_checks_have_non_empty_message(
        self, feature_2_3_validation_results
    ):
        for check in feature_2_3_validation_results["checks"]:
            assert "message" in check
            assert isinstance(check["message"], str)
            assert len(check["message"]) > 0, (
                f"Check '{check['check_id']}' has empty message"
            )

    def test_all_checks_have_evidence_pointer(
        self, feature_2_3_validation_results
    ):
        for check in feature_2_3_validation_results["checks"]:
            assert "evidence_pointer" in check
            assert isinstance(check["evidence_pointer"], str)
            assert len(check["evidence_pointer"]) > 0, (
                f"Check '{check['check_id']}' has empty evidence_pointer"
            )

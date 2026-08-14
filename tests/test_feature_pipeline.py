"""Round-4 tests for reproducibility, temporal governance and packaging."""

from __future__ import annotations

import importlib.util
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
import zipfile

import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "9.SCRIPTS"))

from submission_sanitizer import scan_public_tree  # noqa: E402

from src.evaluation import (  # noqa: E402
    DEVELOPMENT_SCOPE,
    EVALUATION_SCOPE_LABEL,
    FINAL_TEST_SCOPE,
    FIT_SCOPE_LABEL,
    select_validation_winner,
    temporal_masks,
)
from src.features import (  # noqa: E402
    CANDIDATE_ENGINEERED_FEATURES,
    CLUSTER_FEATURES,
    DROPPED_ENGINEERED_FEATURE_REASONS,
    MODEL_FEATURES,
    RAW_INPUT_FEATURES,
    RECOMMENDATION_FEATURES,
    SELECTED_ENGINEERED_FEATURES,
    FeatureBuilder,
    TARGET_ASSOCIATION_SCOPE,
    audit_feature_dependencies,
    build_feature_contract,
    candidate_target_associations,
    selection_train_association_index,
    validate_selected_engineered_features,
)
from src.prediction_policy import (  # noqa: E402
    FINAL_HOLDOUT_MAX_YEAR,
    OBSERVED_DATA_MAX_YEAR,
    PRODUCT_SUPPORT_END_YEAR,
    prediction_support_status,
)


def file_sha256(path: Path) -> str:
    checksum = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def sample_frame() -> pd.DataFrame:
    rows = []
    for index, year in enumerate([1998, 2004, 2012, 2017, 2018, 2020]):
        rows.append(
            {
                "duration_min": 2.5 + index * 0.4,
                "explicit": bool(index % 2),
                "release_year": year,
                "release_month": float(index + 1),
                "release_precision": "day",
                "danceability": 0.3 + index * 0.08,
                "energy": 0.35 + index * 0.08,
                "key": index,
                "loudness": -13.0 + index,
                "mode": index % 2,
                "speechiness": 0.04 + index * 0.01,
                "acousticness": 0.55 - index * 0.05,
                "instrumentalness": index * 0.02,
                "liveness": 0.1 + index * 0.02,
                "valence": 0.25 + index * 0.1,
                "tempo": 75.0 + index * 18.0,
                "time_signature": 4.0,
            }
        )
    return pd.DataFrame(rows)[RAW_INPUT_FEATURES]


class FeatureContractTest(unittest.TestCase):
    def test_candidates_executable_and_selected_valid(self):
        raw = sample_frame()
        builder = FeatureBuilder().fit(raw.iloc[:5])
        candidates = builder.transform_candidates(raw)
        selected = builder.transform(raw)
        self.assertTrue(set(CANDIDATE_ENGINEERED_FEATURES).issubset(candidates.columns))
        self.assertGreaterEqual(len(SELECTED_ENGINEERED_FEATURES), 12)
        self.assertTrue(validate_selected_engineered_features(selected)["Status"].eq("PASS").all())

    def test_selection_is_candidates_minus_explicit_drops(self):
        expected = [
            feature
            for feature in CANDIDATE_ENGINEERED_FEATURES
            if feature not in DROPPED_ENGINEERED_FEATURE_REASONS
        ]
        self.assertEqual(SELECTED_ENGINEERED_FEATURES, expected)
        self.assertTrue(all("selection-train audit" in reason for reason in DROPPED_ENGINEERED_FEATURE_REASONS.values()))
        self.assertTrue(all("development-data audit" not in reason for reason in DROPPED_ENGINEERED_FEATURE_REASONS.values()))

    def test_feature_contract_is_exact(self):
        contract = build_feature_contract()
        self.assertEqual(contract["candidate_engineered_features"], CANDIDATE_ENGINEERED_FEATURES)
        self.assertEqual(contract["selected_engineered_features"], SELECTED_ENGINEERED_FEATURES)
        self.assertEqual(contract["model_features"], MODEL_FEATURES)
        self.assertEqual(contract["cluster_features"], CLUSTER_FEATURES)
        self.assertEqual(contract["recommendation_features"], RECOMMENDATION_FEATURES)

    def test_dependency_leakage_audit_is_executable(self):
        audit = audit_feature_dependencies()
        self.assertEqual(set(audit["Feature"]), set(CANDIDATE_ENGINEERED_FEATURES))
        self.assertTrue(audit["Status"].eq("PASS").all())

    def test_train_statistics_are_immutable_and_target_independent(self):
        raw = sample_frame()
        builder = FeatureBuilder().fit(raw.iloc[:5], np.arange(5))
        before = builder.get_learned_statistics()
        builder.transform(raw.iloc[[5]].assign(energy=0.0, danceability=0.0))
        self.assertEqual(before, builder.get_learned_statistics())
        changed_y = FeatureBuilder().fit(raw.iloc[:5], np.arange(5)[::-1])
        self.assertEqual(before, changed_y.get_learned_statistics())

    @staticmethod
    def _association_inputs():
        raw = sample_frame()
        frame = raw.copy()
        frame["target_popularity"] = [12.0, 20.0, 35.0, 48.0, 62.0, 79.0]
        builder = FeatureBuilder().fit(raw.loc[raw["release_year"] <= 2017])
        return frame, builder.transform_candidates(raw)

    def test_target_association_uses_selection_train_only(self):
        frame, candidates = self._association_inputs()
        index = selection_train_association_index(frame)
        self.assertTrue((frame.loc[index, "release_year"] <= 2017).all())
        evidence = candidate_target_associations(frame, candidates)
        self.assertTrue(evidence["Target Association Scope"].eq(TARGET_ASSOCIATION_SCOPE).all())
        self.assertTrue(evidence["Target Association Rows"].eq(len(index)).all())

    def test_validation_target_changes_do_not_change_candidate_association(self):
        frame, candidates = self._association_inputs()
        original = candidate_target_associations(frame, candidates)
        modified = frame.copy()
        modified.loc[modified["release_year"] == 2018, "target_popularity"] = -99999
        pd.testing.assert_frame_equal(original, candidate_target_associations(modified, candidates))

    def test_final_target_changes_do_not_change_candidate_association(self):
        frame, candidates = self._association_inputs()
        original = candidate_target_associations(frame, candidates)
        modified = frame.copy()
        modified.loc[modified["release_year"] >= 2019, "target_popularity"] = 99999
        pd.testing.assert_frame_equal(original, candidate_target_associations(modified, candidates))

    def test_later_raw_distribution_changes_do_not_change_audit_builder_stats(self):
        raw = sample_frame()
        scope = raw["release_year"] <= 2017
        baseline = FeatureBuilder().fit(raw.loc[scope]).get_learned_statistics()
        validation_changed = raw.copy()
        validation_changed.loc[validation_changed["release_year"] == 2018, ["energy", "tempo"]] = [0.0, 1.0]
        final_changed = raw.copy()
        final_changed.loc[final_changed["release_year"] >= 2019, ["energy", "tempo"]] = [1.0, 300.0]
        self.assertEqual(baseline, FeatureBuilder().fit(validation_changed.loc[scope]).get_learned_statistics())
        self.assertEqual(baseline, FeatureBuilder().fit(final_changed.loc[scope]).get_learned_statistics())


class TemporalProtocolTest(unittest.TestCase):
    def test_final_test_is_disjoint_from_selection_and_validation(self):
        raw = sample_frame()
        masks = temporal_masks(raw)
        self.assertFalse((masks["selection_train"] & masks["validation"]).any())
        self.assertFalse((masks["development"] & masks["final_test"]).any())
        self.assertTrue((raw.loc[masks["selection_train"], "release_year"] <= 2017).all())
        self.assertTrue((raw.loc[masks["validation"], "release_year"] == 2018).all())
        self.assertTrue((raw.loc[masks["final_test"], "release_year"] >= 2019).all())

    def test_winner_selection_accepts_validation_only(self):
        rows = []
        for experiment, rmse in [("Baseline With-Time", 2.0), ("Engineered With-Time", 1.5)]:
            rows.append({"Experiment":experiment, "Model":"XGBoost",
                         "Prediction Variant":"Clipped [0,100]", "MAE":rmse-0.1,
                         "RMSE":rmse, "R2":0.2, "Fit Scope":FIT_SCOPE_LABEL,
                         "Evaluation Scope":EVALUATION_SCOPE_LABEL})
        winner = select_validation_winner(pd.DataFrame(rows))
        self.assertEqual(winner["Experiment"], "Engineered With-Time")

    def test_winner_selection_rejects_final_test_metrics(self):
        invalid = pd.DataFrame([{"Experiment":"A", "Model":"XGBoost",
            "Prediction Variant":"Clipped [0,100]", "MAE":1.0, "RMSE":1.0,
            "R2":0.0, "Fit Scope":FIT_SCOPE_LABEL, "Evaluation Scope":"final test"}])
        with self.assertRaises(ValueError):
            select_validation_winner(invalid)

    def test_production_artifacts_prove_lock_refit_and_one_test_evaluation(self):
        model_dir = ROOT / "4.MODELS" / "hitradar_popularity"
        eval_dir = ROOT / "4.MODELS" / "4.2.evaluation"
        metrics = json.loads((model_dir / "final_test_metrics.json").read_text(encoding="utf-8"))
        lock = json.loads((model_dir / "selection_winner_lock.json").read_text(encoding="utf-8"))
        selection = pd.read_csv(eval_dir / "model_selection_validation_metrics.csv")
        self.assertTrue(selection["Fit Scope"].eq(FIT_SCOPE_LABEL).all())
        self.assertTrue(selection["Evaluation Scope"].eq(EVALUATION_SCOPE_LABEL).all())
        self.assertEqual(metrics["selection_winner_experiment"], lock["selection_winner_experiment"])
        self.assertEqual(metrics["selection_winner_model"], lock["selection_winner_model"])
        self.assertEqual(metrics["final_refit_scope"], DEVELOPMENT_SCOPE)
        self.assertEqual(metrics["feature_builder_fit_rows"], metrics["final_refit_rows"])
        self.assertEqual(metrics["final_test_scope"], FINAL_TEST_SCOPE)
        self.assertEqual(metrics["final_test_evaluation_count"], 1)
        self.assertTrue(metrics["winner_locked_before_final_test"])
        self.assertLess(metrics["winner_locked_at_utc"], metrics["final_test_evaluated_at_utc"])


class TemporalCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "5.UNG_DUNG" / "validation" / "temporal_year_coverage.json"
        cls.coverage = json.loads(cls.path.read_text(encoding="utf-8"))
        cls.years = pd.read_parquet(
            ROOT / "5.DATA" / "processed" / "ml_ready_dataset.parquet",
            columns=["release_year"],
        )["release_year"].astype(int)

    def test_temporal_year_coverage_generated_from_data(self):
        self.assertEqual(self.coverage["total_rows"], len(self.years))
        self.assertEqual(self.coverage["min_release_year"], int(self.years.min()))
        self.assertEqual(self.coverage["max_release_year"], int(self.years.max()))
        expected = {str(int(k)): int(v) for k, v in self.years.value_counts().sort_index().items()}
        self.assertEqual(self.coverage["rows_by_year"], expected)

    def test_final_holdout_max_year_matches_data(self):
        holdout = self.years.loc[self.years >= 2019]
        self.assertEqual(self.coverage["final_temporal_holdout"]["rows"], len(holdout))
        self.assertEqual(self.coverage["final_temporal_holdout"]["max_year"], int(holdout.max()))
        self.assertEqual(FINAL_HOLDOUT_MAX_YEAR, int(holdout.max()))

    def test_product_support_cutoff_is_separate_from_data_max_year(self):
        self.assertEqual(PRODUCT_SUPPORT_END_YEAR, 2020)
        self.assertEqual(self.coverage["product_support_end_year"], PRODUCT_SUPPORT_END_YEAR)
        self.assertEqual(OBSERVED_DATA_MAX_YEAR, self.coverage["max_release_year"])
        self.assertLess(PRODUCT_SUPPORT_END_YEAR, OBSERVED_DATA_MAX_YEAR)


class EnvironmentEvidenceTest(unittest.TestCase):
    def test_public_hotfix_test_evidence_uses_portable_python_path(self):
        evidence = json.loads(
            (ROOT / "5.UNG_DUNG" / "validation" / "public_path_hotfix_test_results.json").read_text(
                encoding="utf-8"
            )
        )
        executable = evidence["python_executable"]
        self.assertTrue(executable.startswith("<PROJECT_ROOT>"))
        self.assertIn(".venv_round4", executable)
        self.assertIsNone(re.match(r"^[A-Za-z]:[\\/]", executable))

    def test_round4_environment_validation_passed(self):
        evidence = json.loads((ROOT / "5.UNG_DUNG" / "validation" / "round4_environment_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(evidence["requirements_install_status"], "PASS")
        self.assertTrue(evidence["python_version"].startswith("3.12."))
        self.assertEqual(evidence["fastapi_testclient_smoke"], "PASS")

    def test_requirements_http_client_pin_matches_validated_environment(self):
        requirements = (ROOT / "5.UNG_DUNG" / "5.3.config" / "requirements.txt").read_text(encoding="utf-8")
        evidence = json.loads((ROOT / "5.UNG_DUNG" / "validation" / "round4_environment_validation.json").read_text(encoding="utf-8"))
        expected_pin = f"{evidence['http_client_package']}=={evidence['http_client_version']}"
        self.assertIn(expected_pin, requirements.splitlines())
        self.assertEqual(evidence["pip_index_httpx2_version_verified"], evidence["http_client_version"])


class DeploymentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline_path = ROOT / "4.MODELS" / "hitradar_popularity" / "popularity_pipeline.joblib"
        cls.pipeline = joblib.load(cls.pipeline_path)
        api_path = ROOT / "5.UNG_DUNG" / "5.1.backend_api" / "api.py"
        spec = importlib.util.spec_from_file_location("hitradar_round2_api_test", api_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.client = TestClient(module.app)
        cls.raw = sample_frame().iloc[-1].to_dict()

    def test_health_means_artifacts_loaded(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["model_ready"] and payload["cluster_ready"] and payload["recommender_ready"])
        self.assertFalse(payload["load_errors"])

    def test_valid_predict_and_direct_parity(self):
        response = self.client.post("/predict", json=self.raw)
        self.assertEqual(response.status_code, 200, response.text)
        direct = float(np.clip(self.pipeline.predict(pd.DataFrame([self.raw])[RAW_INPUT_FEATURES])[0], 0, 100))
        self.assertAlmostEqual(response.json()["predicted_popularity"], direct, places=3)

    def test_2020_prediction_is_within_product_support(self):
        raw = dict(self.raw, release_year=2020)
        response = self.client.post("/predict", json=raw)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertFalse(response.json()["temporal_extrapolation"])
        self.assertEqual(response.json()["prediction_support_status"], "within_product_support")
        self.assertFalse(prediction_support_status(2020)["temporal_extrapolation"])

    def test_2026_prediction_returns_temporal_extrapolation_warning(self):
        raw = dict(self.raw, release_year=2026)
        response = self.client.post("/predict", json=raw)
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertTrue(payload["temporal_extrapolation"])
        self.assertEqual(payload["prediction_support_status"], "temporal_extrapolation")
        self.assertTrue(payload["support_note"].strip())
        self.assertEqual(payload["product_support_end_year"], PRODUCT_SUPPORT_END_YEAR)
        self.assertEqual(payload["observed_data_max_year"], OBSERVED_DATA_MAX_YEAR)
        self.assertEqual(payload["final_holdout_max_year"], FINAL_HOLDOUT_MAX_YEAR)
        self.assertNotIn("evaluated_end_year", payload)

    def test_temporal_warning_does_not_change_prediction_value(self):
        raw = dict(self.raw, release_year=2026)
        response = self.client.post("/predict", json=raw)
        direct = float(np.clip(self.pipeline.predict(pd.DataFrame([raw])[RAW_INPUT_FEATURES])[0], 0, 100))
        self.assertAlmostEqual(response.json()["predicted_popularity"], direct, places=3)

    def test_invalid_normalized_and_engineered_inputs_rejected(self):
        invalid = dict(self.raw, energy=1.5)
        self.assertEqual(self.client.post("/predict", json=invalid).status_code, 422)
        engineered = dict(self.raw, dance_energy=0.5)
        self.assertEqual(self.client.post("/predict", json=engineered).status_code, 422)

    def test_cluster_accepts_only_audio_contract(self):
        cluster_payload = {feature: self.raw[feature] for feature in CLUSTER_FEATURES}
        response = self.client.post("/cluster", json=cluster_payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIsInstance(response.json()["cluster"], int)

    def test_recommendation_errors_and_self_exclusion(self):
        self.assertEqual(self.client.get("/recommend/not-a-real-track?n=5").status_code, 404)
        self.assertEqual(self.client.get("/recommend/not-a-real-track?n=0").status_code, 422)
        bundle = joblib.load(ROOT / "4.MODELS" / "hitradar_secondary" / "content_recommender.joblib")
        query_id = str(bundle.track_ids[0])
        response = self.client.get(f"/recommend/{query_id}?n=5")
        self.assertEqual(response.status_code, 200, response.text)
        returned = {row["track_id"] for row in response.json()["recommendations"]}
        self.assertNotIn(query_id, returned)

    def test_final_pipeline_reload_parity(self):
        reloaded = joblib.load(self.pipeline_path)
        frame = pd.DataFrame([self.raw])[RAW_INPUT_FEATURES]
        self.assertTrue(np.allclose(self.pipeline.predict(frame), reloaded.predict(frame)))

    def test_streamlit_has_exactly_four_tabs(self):
        app_path = ROOT / "5.UNG_DUNG" / "5.2.frontend" / "streamlit_app.py"
        app_test = AppTest.from_file(str(app_path)).run(timeout=40)
        self.assertFalse(app_test.exception)
        self.assertEqual(
            [tab.label for tab in app_test.tabs],
            ["Overview", "Popularity Prediction", "Song Clustering", "Similar Songs"],
        )

    def test_streamlit_2026_warning_visible_and_2020_warning_absent(self):
        app_path = ROOT / "5.UNG_DUNG" / "5.2.frontend" / "streamlit_app.py"
        app_test = AppTest.from_file(str(app_path)).run(timeout=40)
        self.assertFalse(app_test.exception)
        self.assertEqual([warning.value for warning in app_test.warning], [])
        release_year = next(item for item in app_test.number_input if item.label == "Release year")
        future_app = release_year.set_value(2026).run(timeout=40)
        self.assertFalse(future_app.exception)
        warnings = [warning.value for warning in future_app.warning]
        self.assertEqual(len(warnings), 1)
        self.assertIn("product support cutoff", warnings[0])
        self.assertIn("temporal extrapolation", warnings[0])
        self.assertEqual(PRODUCT_SUPPORT_END_YEAR, 2020)


class FinalSubmissionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.submission = ROOT / "FINAL_SUBMISSION"
        cls.files_scanned, cls.path_findings = scan_public_tree(cls.submission)
        cls.sanitization = json.loads(
            (cls.submission / "evidence" / "public_evidence_sanitization.json").read_text(encoding="utf-8")
        )
        cls.manifest = json.loads((cls.submission / "SUBMISSION_MANIFEST.json").read_text(encoding="utf-8"))

    def finding_categories(self) -> set[str]:
        return {item["matched_path_category"] for item in self.path_findings}

    def test_final_report_does_not_claim_historically_never_seen(self):
        report = (ROOT / "FINAL_SUBMISSION" / "FINAL_AUDIT_REPORT.md").read_text(encoding="utf-8").lower()
        prohibited = [
            "completely unseen test set",
            "untouched throughout the entire project",
            "historically never seen",
        ]
        self.assertFalse(any(phrase in report for phrase in prohibited))

    def test_final_report_contains_holdout_history_caveat(self):
        report = (ROOT / "FINAL_SUBMISSION" / "FINAL_AUDIT_REPORT.md").read_text(encoding="utf-8").lower()
        self.assertIn("not used for corrected round-2 winner selection", report)
        self.assertIn("inspected during an earlier development iteration", report)

    def test_final_submission_has_no_legacy_prefixed_files(self):
        submission = ROOT / "FINAL_SUBMISSION"
        prohibited = ("HOTFIX_", "OUTPUT_", "BEFORE_", "BACKUP_")
        offenders = [path.name for path in submission.rglob("*") if path.is_file() and path.name.upper().startswith(prohibited)]
        self.assertEqual(offenders, [])

    def test_final_submission_manifest_files_exist(self):
        submission = ROOT / "FINAL_SUBMISSION"
        required = [
            "README_FINAL_SUBMISSION.md", "FINAL_AUDIT_REPORT.md", "GIT_EVIDENCE.md",
            "notebooks/05_feature_engineering.ipynb", "notebooks/06_machine_learning.ipynb",
            "notebooks/07_ai_deployment.ipynb", "src/features.py", "src/evaluation.py",
            "src/modeling.py", "src/secondary_tasks.py", "src/prediction_policy.py",
            "deployment/api.py", "deployment/prediction.py", "deployment/streamlit_app.py",
            "evidence/candidate_feature_evaluation.csv", "evidence/round4_test_results.json",
            "evidence/round4_end_to_end_validation.json", "evidence/temporal_year_coverage.json",
            "evidence/round4_environment_validation.json", "evidence/round4_notebook_execution_status.json",
            "evidence/public_evidence_sanitization.json",
            "evidence/public_path_hotfix_test_results.json",
            "tests/test_feature_pipeline.py",
            "SUBMISSION_MANIFEST.json",
        ]
        missing = [relative for relative in required if not (submission / relative).is_file()]
        self.assertEqual(missing, [])

    def test_final_readme_has_no_control_characters(self):
        text = (ROOT / "FINAL_SUBMISSION" / "README_FINAL_SUBMISSION.md").read_text(encoding="utf-8")
        forbidden = [character for character in text if ord(character) < 32 and character not in "\n\r\t"]
        self.assertEqual(forbidden, [])

    def test_final_readme_declares_snapshot_semantics(self):
        text = (ROOT / "FINAL_SUBMISSION" / "README_FINAL_SUBMISSION.md").read_text(encoding="utf-8")
        self.assertIn("submission/evidence snapshot", text)
        self.assertIn("canonical HitRadar repository", text)
        self.assertIn("not standalone runnable", text)

    def test_final_readme_canonical_commands_are_literal(self):
        text = (ROOT / "FINAL_SUBMISSION" / "README_FINAL_SUBMISSION.md").read_text(encoding="utf-8")
        expected = [
            "py -3.12 -m venv .venv_round4",
            r".\.venv_round4\Scripts\python -m pip install -r .\5.UNG_DUNG\5.3.config\requirements.txt",
            r".\.venv_round4\Scripts\python .\scratch\execute_notebook.py .\3.NOTEBOOKS\3.7.demo\07_ai_deployment.ipynb",
            r".\.venv_round4\Scripts\python .\9.SCRIPTS\run_round4_tests.py",
        ]
        for command in expected:
            self.assertIn(command, text)

    def test_manifest_declares_non_standalone_snapshot(self):
        manifest = json.loads((ROOT / "FINAL_SUBMISSION" / "SUBMISSION_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["package_type"], "submission_evidence_snapshot")
        self.assertFalse(manifest["standalone_runnable"])
        self.assertTrue(manifest["canonical_repository_required"])
        self.assertTrue(manifest["external_artifacts_required"])

    def test_git_evidence_is_truthful_for_workspace_state(self):
        evidence = (ROOT / "FINAL_SUBMISSION" / "GIT_EVIDENCE.md").read_text(encoding="utf-8")
        report = (ROOT / "FINAL_SUBMISSION" / "FINAL_AUDIT_REPORT.md").read_text(encoding="utf-8")
        if (ROOT / ".git").exists():
            self.assertIn("git status", evidence.lower())
        else:
            self.assertIn("Git metadata was not present", evidence)
            self.assertNotIn("Git status: PASS", report)

    def test_shap_status_matches_inspected_requirements(self):
        status = json.loads((ROOT / "FINAL_SUBMISSION" / "evidence" / "shap_requirement_status.json").read_text(encoding="utf-8"))
        report = (ROOT / "FINAL_SUBMISSION" / "FINAL_AUDIT_REPORT.md").read_text(encoding="utf-8")
        self.assertEqual(status["decision"], "not_added_optional_advanced_item")
        self.assertIn("SHAP was not added", report)

    def test_public_submission_contains_no_windows_absolute_paths(self):
        self.assertNotIn("windows_absolute", self.finding_categories())

    def test_public_submission_contains_no_user_profile_paths(self):
        self.assertNotIn("windows_user_profile", self.finding_categories())

    def test_public_submission_contains_no_codex_cache_paths(self):
        self.assertNotIn("local_runtime_cache_marker", self.finding_categories())

    def test_public_submission_contains_no_downloads_paths(self):
        self.assertNotIn("local_downloads_marker", self.finding_categories())

    def test_public_submission_contains_no_unix_local_home_or_tmp_paths(self):
        self.assertNotIn("unix_local_home_or_temp", self.finding_categories())

    def test_public_environment_json_uses_placeholder_paths(self):
        public_environment = json.loads(
            (self.submission / "evidence" / "round4_environment_validation.json").read_text(encoding="utf-8")
        )
        self.assertTrue(public_environment["python_executable"].startswith("<PROJECT_ROOT>"))
        self.assertTrue(public_environment["install_log"].startswith("5.UNG_DUNG/"))

    def test_public_install_log_is_sanitized(self):
        public_log = (self.submission / "evidence" / "round4_environment_install.log").read_text(encoding="utf-8")
        self.assertIn("<PROJECT_ROOT>", public_log)
        self.assertIn("<LOCAL_USER_CACHE>", public_log)
        self.assertEqual(self.path_findings, [])

    def test_public_and_private_evidence_are_truthfully_distinguished(self):
        self.assertTrue(self.sanitization["tracked_evidence_sanitized"])
        self.assertTrue(self.sanitization["private_raw_evidence_excluded"])
        self.assertTrue(self.sanitization["evidence_checksums"])
        for item in self.sanitization["evidence_checksums"]:
            self.assertTrue(item["private_raw_copy_available_locally"])
            self.assertTrue(item["tracked_public_copy_sanitized"])
            self.assertTrue(item["unchanged_during_generation"])
            if not item["mutable_after_generation"]:
                self.assertEqual(
                    file_sha256(ROOT / item["canonical_file"]),
                    item["tracked_sanitized_sha256"],
                )

    def test_public_sanitization_report_passes(self):
        self.assertEqual(self.sanitization["status"], "PASS")
        self.assertTrue(self.sanitization["public_submission_scan_passed"])
        self.assertEqual(self.sanitization["remaining_sensitive_absolute_paths"], [])
        self.assertEqual(self.sanitization["files_scanned"], self.files_scanned)

    def test_manifest_generated_after_sanitization(self):
        self.assertTrue(self.manifest["public_path_sanitization"])
        self.assertTrue(self.manifest["tracked_evidence_sanitized"])
        self.assertTrue(self.manifest["private_raw_evidence_excluded"])
        for item in self.manifest["files"]:
            self.assertEqual(file_sha256(self.submission / item["path"]), item["sha256"])

    def test_public_sanitization_does_not_change_model_checksum(self):
        model = self.sanitization["model_integrity"]
        self.assertTrue(model["model_unchanged"])
        self.assertEqual(model["model_sha256_before"], model["model_sha256_after"])
        self.assertEqual(
            file_sha256(ROOT / "4.MODELS" / "hitradar_popularity" / "popularity_pipeline.joblib"),
            model["model_sha256_after"],
        )

    def test_public_sanitization_does_not_change_final_metrics(self):
        model = self.sanitization["model_integrity"]
        self.assertTrue(model["final_metrics_unchanged"])
        self.assertEqual(model["final_metrics_sha256_before"], model["final_metrics_sha256_after"])
        self.assertEqual(
            file_sha256(ROOT / "4.MODELS" / "hitradar_popularity" / "final_test_metrics.json"),
            model["final_metrics_sha256_after"],
        )


class FinalReviewGovernanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb02_path = ROOT / "3.NOTEBOOKS" / "3.2.postgresql" / "02_postgresql_pipeline.ipynb"
        cls.nb02 = json.loads(cls.nb02_path.read_text(encoding="utf-8"))
        cls.notebook_text = "\n".join(
            "".join(cell.get("source", [])) for cell in cls.nb02["cells"]
        )
        validator_path = ROOT / "9.SCRIPTS" / "validate_public_repository.py"
        spec = importlib.util.spec_from_file_location("final_review_path_validator", validator_path)
        cls.validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.validator)

    def test_path_scanner_detects_ansi_and_json_escaped_windows_paths(self):
        ansi_traceback = (
            "\x1b[36mFile \x1b[39m\x1b[32m"
            r"e:\Dự án 1 hitrada\.venv\Lib\site-packages\psycopg2\__init__.py"
            "\x1b[39m"
        )
        escaped_json_path = r'D:\\Hitradar\\hitradar-main\\file.json'
        self.assertIn("windows_absolute", self.validator.scan_text(ansi_traceback))
        self.assertIn("windows_absolute", self.validator.scan_text(escaped_json_path))
        self.assertEqual(self.validator.scan_text("<PROJECT_ROOT>/file.json"), {})

    def test_nb02_is_clean_and_explicitly_unexecuted(self):
        self.assertTrue(self.nb02_path.is_file())
        code_cells = [cell for cell in self.nb02["cells"] if cell["cell_type"] == "code"]
        self.assertTrue(code_cells)
        self.assertTrue(all(cell.get("execution_count") is None for cell in code_cells))
        self.assertEqual(sum(len(cell.get("outputs", [])) for cell in code_cells), 0)
        self.assertFalse(any(
            output.get("output_type") == "error"
            for cell in code_cells for output in cell.get("outputs", [])
        ))

    def test_nb02_credentials_are_environment_only(self):
        forbidden = (
            r"POSTGRES_PASSWORD['\"]?\s*,\s*['\"]123456",
            r"password\s*=\s*['\"]123456['\"]",
        )
        for pattern in forbidden:
            self.assertNotRegex(self.notebook_text, pattern)
        self.assertIn(
            'os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD")',
            self.notebook_text,
        )
        self.assertIn("password=password", self.notebook_text)

    def test_nb02_status_wording_and_path_hygiene(self):
        lowered = self.notebook_text.lower()
        self.assertIn("not re-executed", lowered)
        self.assertIn("no successful postgresql execution is claimed", lowered)
        notebook_scan = self.validator.scan_text(self.validator.scan_path_text(self.nb02_path))
        self.assertEqual(notebook_scan, {})

    def test_nb02_status_evidence_is_truthful(self):
        evidence = json.loads(
            (ROOT / "5.UNG_DUNG" / "validation" / "nb02_postgresql_execution_status.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(evidence["final_hotfix_execution"], "not_reexecuted")
        self.assertFalse(evidence["successful_execution_claimed"])
        self.assertEqual(evidence["saved_error_outputs"], 0)
        self.assertFalse(evidence["hardcoded_password_fallback"])
        self.assertTrue(evidence["prior_postgresql_evidence_retained"])
        self.assertEqual(evidence["status"], "DOCUMENTED_LIMITATION")

    def test_shap_evidence_has_no_stale_zero_byte_docx_status(self):
        evidence = json.loads(
            (ROOT / "5.UNG_DUNG" / "validation" / "shap_requirement_status.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(evidence["decision"], "not_added_optional_advanced_item")
        self.assertFalse(evidence["shap_added"])
        docx_sources = [item for item in evidence["sources_inspected"] if item["path"].endswith(".docx")]
        self.assertEqual(len(docx_sources), 4)
        current_docx = [item for item in docx_sources if item["path"].startswith("6.TAI_LIEU/")]
        self.assertEqual(len(current_docx), 3)
        self.assertTrue(all(item["status"] == "valid_current_deliverable" for item in current_docx))
        self.assertFalse(any("zero_byte" in item["status"] for item in current_docx))


class CanonicalDatabaseNotebookGovernanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        validator_path = ROOT / "9.SCRIPTS" / "validate_public_repository.py"
        spec = importlib.util.spec_from_file_location("canonical_database_path_validator", validator_path)
        cls.validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.validator)

        cls.notebooks = {}
        for path in sorted((ROOT / "3.NOTEBOOKS").rglob("*.ipynb")):
            notebook = json.loads(path.read_text(encoding="utf-8"))
            source = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])
            if "psycopg2.connect" in source:
                cls.notebooks[path.relative_to(ROOT).as_posix()] = (path, notebook, source)

    def test_all_canonical_database_notebooks_have_safe_credentials_and_outputs(self):
        required = {
            "3.NOTEBOOKS/3.2.postgresql/02_postgresql_pipeline.ipynb",
            "3.NOTEBOOKS/3.3.lam_sach_python/02_feature_1_4_clean_validation.ipynb",
            "3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb",
        }
        self.assertTrue(required.issubset(self.notebooks))
        self.assertEqual(len(self.notebooks), 11)

        auth_markers = ("password authentication failed", "fe_sendauth", "no password supplied")
        for relative, (path, notebook, source) in self.notebooks.items():
            with self.subTest(notebook=relative):
                self.assertNotIn("123456", source)
                self.assertNotRegex(source, r"password\s*=\s*['\"][^'\"]+['\"]")
                self.assertNotRegex(source, r"get\s*\(\s*['\"]PGPASSWORD['\"]\s*,")
                self.assertIn(
                    'os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD")',
                    source,
                )
                self.assertIn("password=password", source)

                for cell in notebook["cells"]:
                    for output in cell.get("outputs", []):
                        output_text = json.dumps(output, ensure_ascii=False).lower()
                        self.assertFalse(
                            output.get("output_type") == "error"
                            and any(marker in output_text for marker in auth_markers)
                        )
                        self.assertFalse(any(marker in output_text for marker in auth_markers))

                notebook_scan = self.validator.scan_text(self.validator.scan_path_text(path))
                self.assertEqual(notebook_scan, {})

    def test_database_notebook_status_and_failed_connection_state_are_truthful(self):
        for relative, (_, _, source) in self.notebooks.items():
            with self.subTest(notebook=relative):
                lowered = source.lower()
                self.assertIn("not re-executed", lowered)
                self.assertRegex(
                    lowered,
                    r"no (?:new )?successful (?:postgresql|database) execution is claimed",
                )

        failed_connection_notebooks = {
            "3.NOTEBOOKS/3.1.hieu_du_lieu/01_data_understanding.ipynb",
            "3.NOTEBOOKS/3.3.lam_sach_python/02_feature_1_4_clean_validation.ipynb",
            "3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb",
        }
        for relative in failed_connection_notebooks:
            _, notebook, _ = self.notebooks[relative]
            connection_cells = [
                cell for cell in notebook["cells"]
                if cell.get("cell_type") == "code"
                and "psycopg2.connect" in "".join(cell.get("source", []))
            ]
            self.assertTrue(connection_cells)
            for cell in connection_cells:
                self.assertIsNone(cell.get("execution_count"))
                self.assertEqual(cell.get("outputs", []), [])

        # Useful non-error tables/plots remain, with their provenance documented above.
        for relative in (
            "3.NOTEBOOKS/3.3.lam_sach_python/02_feature_1_4_clean_validation.ipynb",
            "3.NOTEBOOKS/3.4.eda/01_data_understanding.ipynb",
        ):
            _, notebook, _ = self.notebooks[relative]
            retained = [
                output for cell in notebook["cells"] for output in cell.get("outputs", [])
                if output.get("output_type") != "error"
            ]
            self.assertGreater(len(retained), 0)


class FinalRepositoryHygieneTest(unittest.TestCase):
    @staticmethod
    def git_files() -> list[str]:
        output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        return [item for item in output.decode("utf-8").split("\0") if item]

    def test_selected_engineered_feature_count_is_exactly_fourteen(self):
        self.assertEqual(len(CANDIDATE_ENGINEERED_FEATURES), 16)
        self.assertEqual(len(SELECTED_ENGINEERED_FEATURES), 14)

    def test_forbidden_runtime_artifacts_are_not_tracked(self):
        tracked = self.git_files()
        forbidden_exact = {
            "5.DATA/processed/ml_ready_dataset.csv",
            "5.DATA/processed/ml_ready_dataset.parquet",
            "5.DATA/processed/features_engineered.parquet",
            "5.UNG_DUNG/5.3.config/.env",
        }
        offenders = [
            item for item in tracked
            if item in forbidden_exact
            or (item.startswith("4.MODELS/") and item.lower().endswith(".joblib"))
        ]
        self.assertEqual(offenders, [])

    def test_external_artifact_checksums_use_relative_paths_and_match_local_files(self):
        registry = json.loads(
            (ROOT / "FINAL_SUBMISSION" / "evidence" / "external_artifact_checksums.json").read_text(encoding="utf-8")
        )
        self.assertGreaterEqual(len(registry), 6)
        for item in registry:
            relative = Path(item["canonical_path"])
            self.assertFalse(relative.is_absolute())
            local = ROOT / relative
            if local.is_file():
                self.assertEqual(file_sha256(local), item["sha256"])

    def test_repository_wide_sensitive_path_scan_passes(self):
        validator_path = ROOT / "9.SCRIPTS" / "validate_public_repository.py"
        spec = importlib.util.spec_from_file_location("public_repository_validator", validator_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.validate(ROOT)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["files_with_findings"], 0)

    def test_project_management_files_are_nonzero_and_readable(self):
        project_dir = ROOT / "7.QUAN_LY_DU_AN"
        for name in ("Daily_Standup_Log.xlsx", "Sprint_Backlog.xlsx", "Task_Tracker.xlsx"):
            path = project_dir / name
            self.assertGreater(path.stat().st_size, 0)
            with zipfile.ZipFile(path) as archive:
                self.assertIn("xl/workbook.xml", archive.namelist())
                self.assertGreater(len(archive.read("xl/workbook.xml")), 0)
        retrospective = (project_dir / "Retrospective_Notes.md").read_text(encoding="utf-8")
        self.assertIn("Retrospective reconstruction", retrospective)

    def test_docx_deliverables_are_nonzero_valid_containers(self):
        report_dir = ROOT / "6.TAI_LIEU" / "6.1.bao_cao"
        for name in ("bao_cao_tong_hop.docx", "huong_dan_su_dung.docx", "phu_luc_ky_thuat.docx"):
            path = report_dir / name
            self.assertGreater(path.stat().st_size, 0)
            with zipfile.ZipFile(path) as archive:
                self.assertIn("word/document.xml", archive.namelist())
                self.assertGreater(len(archive.read("word/document.xml")), 0)

    def test_only_canonical_root_notebooks_are_presented(self):
        self.assertFalse((ROOT / "05_feature_engineering.ipynb").exists())
        self.assertFalse((ROOT / "06_machine_learning.ipynb").exists())
        self.assertFalse((ROOT / "07_ai_deployment.ipynb").exists())
        for relative in (
            "3.NOTEBOOKS/3.5.feature_engineering/05_feature_engineering.ipynb",
            "3.NOTEBOOKS/3.6.modeling/06_machine_learning.ipynb",
            "3.NOTEBOOKS/3.7.demo/07_ai_deployment.ipynb",
        ):
            self.assertTrue((ROOT / relative).is_file())

    def test_no_unjustified_zero_byte_tracked_placeholders(self):
        offenders = []
        for relative in self.git_files():
            path = ROOT / relative
            if path.is_file() and path.stat().st_size == 0 and path.name != "__init__.py":
                offenders.append(relative)
        self.assertEqual(offenders, [])

    def test_nb06_is_classified_as_preserved_and_not_retrained(self):
        evidence = json.loads(
            (ROOT / "5.UNG_DUNG" / "validation" / "round4_notebook_execution_status.json").read_text(encoding="utf-8")
        )
        nb06 = next(item for item in evidence["notebooks"] if item["notebook"] == "06_machine_learning.ipynb")
        self.assertEqual(nb06["round4_execution"], "preserved_round2_execution_not_retrained")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Notebook 06 was preserved from the previous validated execution and was not retrained", readme)

    def test_readme_test_count_matches_current_suite(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        match = re.search(r"latest final repository suite records (\d+) tests", text, flags=re.IGNORECASE)
        self.assertIsNotNone(match)
        test_cases = [
            value for value in globals().values()
            if isinstance(value, type)
            and issubclass(value, unittest.TestCase)
            and value.__module__ == __name__
        ]
        expected = sum(
            unittest.defaultTestLoader.loadTestsFromTestCase(test_case).countTestCases()
            for test_case in test_cases
        )
        self.assertEqual(int(match.group(1)), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)

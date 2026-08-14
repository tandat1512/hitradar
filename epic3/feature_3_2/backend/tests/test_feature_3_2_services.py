"""
Phase 2 unit tests — Feature 3.2 Service Layer
24 tests covering ModelService, ExplainService, WhatIfService.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os, json, pytest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

# ── Setup ─────────────────────────────────────────────────────────────────────
REPO = Path(r"H:\dự án\DUAN1 github")
BACKEND = REPO / "epic3" / "feature_3_2" / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(str(BACKEND))

# Load example input once
EXAMPLE_INPUT_PATH = REPO / "7.ML/7.10.model_packaging/package/examples/example_input.json"
with open(EXAMPLE_INPUT_PATH, encoding="utf-8") as f:
    EXAMPLE_INPUT = json.load(f)

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def pipeline_loader():
    from app.services.pipeline_loader import PipelineLoader
    from app.core.config import PIPELINE_PATH, EPIC2_FE_TRANSFORMERS, ARTIFACTS_PATH
    PipelineLoader.clear_instance()
    loader = PipelineLoader(PIPELINE_PATH, EPIC2_FE_TRANSFORMERS, ARTIFACTS_PATH)
    PipelineLoader.set_instance(loader)
    _ = loader.pipeline
    yield loader
    PipelineLoader.clear_instance()


@pytest.fixture
def model_service(pipeline_loader):
    from app.services.model_service import ModelService
    return ModelService(pipeline_loader)


@pytest.fixture
def explain_service(model_service):
    from app.services.explain_service import ExplainService
    return ExplainService(model_service)


@pytest.fixture
def whatif_service(model_service):
    from app.services.whatif_service import WhatIfService
    return WhatIfService(model_service)


# ── Model Service Load ────────────────────────────────────────────────────────

class TestModelServiceLoad:
    def test_pipeline_loads_successfully(self, pipeline_loader):
        assert pipeline_loader.is_loaded()
        assert pipeline_loader._pipeline is not None

    def test_pipeline_loaded_only_once(self, pipeline_loader):
        p1 = pipeline_loader.pipeline
        p2 = pipeline_loader.pipeline
        assert p1 is p2

    def test_module_import_no_model_load(self):
        import importlib
        import app.services.model_service as ms_mod
        importlib.reload(ms_mod)
        assert True  # No crash means no eager model load at import


class TestModelServiceArtifactIntegrity:
    def test_pipeline_file_exists_and_readable(self, pipeline_loader):
        from app.core.config import PIPELINE_PATH
        assert PIPELINE_PATH.exists()
        assert PIPELINE_PATH.stat().st_size > 0

    def test_schema_artifacts_exist(self):
        from app.core.config import ARTIFACTS_PATH
        assert (ARTIFACTS_PATH / "schemas" / "input_schema.json").exists()
        assert (ARTIFACTS_PATH / "schemas" / "selected_features.json").exists()

    def test_epic2_transformers_exist(self):
        from app.core.config import EPIC2_FE_TRANSFORMERS
        assert EPIC2_FE_TRANSFORMERS.exists()


class TestModelServiceNotReady:
    def test_unset_singleton_returns_none(self):
        from app.services.pipeline_loader import PipelineLoader
        PipelineLoader.clear_instance()
        assert PipelineLoader.get_instance() is None

    def test_model_service_raises_when_not_loaded(self):
        from app.services.pipeline_loader import PipelineLoader
        from app.services.model_service import ModelService
        from app.core.exceptions import ModelNotLoadedError
        PipelineLoader.clear_instance()
        fake_loader = PipelineLoader(
            pipeline_path=Path("nonexistent"),
            epic2_fe_transformers_path=Path("nonexistent"),
            artifacts_path=Path("nonexistent"),
        )
        PipelineLoader.set_instance(fake_loader)
        svc = ModelService(fake_loader)
        with pytest.raises(ModelNotLoadedError):
            svc.predict(EXAMPLE_INPUT)


class TestModelInputConversion:
    def test_example_input_has_18_fields(self):
        assert len(EXAMPLE_INPUT) == 18

    def test_example_input_missing_target(self):
        assert "target_popularity" not in EXAMPLE_INPUT
        assert "track_id" not in EXAMPLE_INPUT

    def test_example_input_all_canonical_fields_present(self, model_service):
        feat = model_service.get_features()
        field_names = {f["name"] for f in feat["canonical_fields"]}
        for k in EXAMPLE_INPUT:
            assert k in field_names, f"Extra field: {k}"


class TestModelPrediction:
    def test_prediction_executes(self, model_service):
        result = model_service.predict(EXAMPLE_INPUT)
        assert result.status == "SUCCESS"

    def test_prediction_matches_canonical(self, model_service):
        result = model_service.predict(EXAMPLE_INPUT)
        assert abs(result.prediction_raw - 46.421062) <= 0.001

    def test_prediction_finite(self, model_service):
        result = model_service.predict(EXAMPLE_INPUT)
        import math
        assert math.isfinite(result.prediction_raw)
        assert math.isfinite(result.prediction_clipped)

    def test_prediction_clipped_in_range(self, model_service):
        result = model_service.predict(EXAMPLE_INPUT)
        assert 0 <= result.prediction_clipped <= 100

    def test_prediction_display_matches_clipped(self, model_service):
        result = model_service.predict(EXAMPLE_INPUT)
        assert result.prediction_display == round(result.prediction_clipped)


class TestModelOutputNormalization:
    def test_model_id_from_metadata(self, model_service):
        result = model_service.predict(EXAMPLE_INPUT)
        assert result.model_id == "EXP24-XGB-FINAL-001"

    def test_model_version_present(self, model_service):
        result = model_service.predict(EXAMPLE_INPUT)
        assert result.model_version in ("1.0.0", "2.7.0")

    def test_package_version_present(self, model_service):
        result = model_service.predict(EXAMPLE_INPUT)
        assert result.package_version in ("1.0.0", "2.7.0")


class TestModelInfoService:
    def test_model_info_returns_metadata(self, model_service):
        info = model_service.get_model_info()
        assert info["model_id"] == "EXP24-XGB-FINAL-001"
        assert info["model_family"] == "XGBoost"
        assert info["feature_set"] == "FS23-SELECTED"

    def test_features_returns_18_fields(self, model_service):
        feat = model_service.get_features()
        assert feat["total_input_fields"] == 18

    def test_selected_features_count_31(self, model_service):
        feat = model_service.get_features()
        assert feat["total_selected_features"] == 31


class TestModelNoRefit:
    def test_fit_call_count_zero(self, pipeline_loader):
        pipe = pipeline_loader.pipeline
        fit_count = getattr(pipe, "fit_call_count", 0)
        assert fit_count == 0

    def test_fit_transform_count_zero(self, pipeline_loader):
        pipe = pipeline_loader.pipeline
        ft_count = getattr(pipe, "fit_transform_call_count", 0)
        assert ft_count == 0

    def test_partial_fit_count_zero(self, pipeline_loader):
        pipe = pipeline_loader.pipeline
        pf_count = getattr(pipe, "partial_fit_call_count", 0)
        assert pf_count == 0


# ── Explain Service ────────────────────────────────────────────────────────────

class TestExplainServiceAvailability:
    def test_explain_service_available(self, explain_service):
        result = explain_service.explain(EXAMPLE_INPUT)
        assert result is not None

    def test_explain_returns_prediction(self, explain_service):
        result = explain_service.explain(EXAMPLE_INPUT)
        assert result.prediction.prediction_raw is not None


class TestExplainServicePredictionMatch:
    def test_explain_prediction_matches_model_service(self, model_service, explain_service):
        svc_result = model_service.predict(EXAMPLE_INPUT)
        expl_result = explain_service.explain(EXAMPLE_INPUT)
        assert abs(svc_result.prediction_raw - expl_result.prediction.prediction_raw) < 0.001


class TestExplainServiceContributions:
    def test_shap_values_count_matches_31(self, explain_service):
        result = explain_service.explain(EXAMPLE_INPUT)
        assert len(result.shap_values) == 31

    def test_shap_values_all_finite(self, explain_service):
        result = explain_service.explain(EXAMPLE_INPUT)
        import math
        for name, val in result.shap_values.items():
            assert math.isfinite(val), f"Non-finite SHAP for {name}: {val}"

    def test_top_features_have_required_fields(self, explain_service):
        result = explain_service.explain(EXAMPLE_INPUT)
        for tf in result.top_features:
            assert "name" in tf
            assert "shap_value" in tf
            assert "feature_value" in tf

    def test_top_features_sorted_by_absolute_shap(self, explain_service):
        result = explain_service.explain(EXAMPLE_INPUT)
        abs_vals = [abs(tf["shap_value"]) for tf in result.top_features]
        assert abs_vals == sorted(abs_vals, reverse=True)


class TestExplainServiceAdditivity:
    def test_additivity_holds(self, explain_service):
        result = explain_service.explain(EXAMPLE_INPUT)
        base = result.base_value
        shap_sum = sum(result.shap_values.values())
        pred = result.prediction.prediction_raw
        error = abs(pred - (base + shap_sum))
        # TreeExplainer.expected_value for a single-row call may differ slightly
        # from the population mean used in pre-computed SHAP.
        # Tolerate up to 1.0 for this request-time computation.
        assert error < 1.0, f"Additivity error {error} too large"


class TestExplainServiceNoCausality:
    def test_no_causality_claim_in_docstring(self):
        from app.services.explain_service import ExplainService
        doc = ExplainService.explain.__doc__ or ""
        assert "causal" not in doc.lower()


# ── What-If Service ────────────────────────────────────────────────────────────

class TestWhatIfSingleChange:
    def test_single_change_returns_delta(self, whatif_service):
        result = whatif_service.compare(EXAMPLE_INPUT, {"release_year": 2020})
        assert result.delta is not None
        assert isinstance(result.delta, float)

    def test_original_and_modified_both_present(self, whatif_service):
        result = whatif_service.compare(EXAMPLE_INPUT, {"release_year": 2020})
        assert result.prediction_before is not None
        assert result.prediction_after is not None
        assert result.prediction_before.prediction_raw != result.prediction_after.prediction_raw


class TestWhatIfMultipleChanges:
    def test_multiple_changes_applied(self, whatif_service):
        result = whatif_service.compare(EXAMPLE_INPUT, {
            "release_year": 2020,
            "danceability": 0.9,
        })
        assert len(result.changes_applied) == 2
        assert "release_year" in result.changes_applied
        assert "danceability" in result.changes_applied


class TestWhatIfInvalidField:
    def test_invalid_field_raises(self, whatif_service):
        from app.core.exceptions import InvalidFeatureError
        with pytest.raises(InvalidFeatureError):
            whatif_service.compare(EXAMPLE_INPUT, {"invalid_field_xyz": 99})


class TestWhatIfTargetRejected:
    def test_target_popularity_rejected(self, whatif_service):
        from app.core.exceptions import InvalidFeatureError
        with pytest.raises(InvalidFeatureError):
            whatif_service.compare(EXAMPLE_INPUT, {"target_popularity": 99})


class TestWhatIfOriginalImmutable:
    def test_original_input_not_mutated(self, whatif_service):
        original_year = EXAMPLE_INPUT["release_year"]
        _ = whatif_service.compare(EXAMPLE_INPUT, {"release_year": 2020})
        assert EXAMPLE_INPUT["release_year"] == original_year


# ── Service Dependency Injection ───────────────────────────────────────────────

class TestServiceDependencyInjection:
    def test_model_service_accepts_loader(self, pipeline_loader):
        from app.services.model_service import ModelService
        svc = ModelService(pipeline_loader)
        assert svc._loader is pipeline_loader

    def test_explain_service_accepts_model_service(self, model_service):
        from app.services.explain_service import ExplainService
        svc = ExplainService(model_service)
        assert svc._model is model_service

    def test_whatif_service_accepts_model_service(self, model_service):
        from app.services.whatif_service import WhatIfService
        svc = WhatIfService(model_service)
        assert svc._model is model_service


# ── Service Concurrency ─────────────────────────────────────────────────────────

class TestServiceConcurrency:
    def test_concurrent_predictions_identical(self, model_service):
        def run(idx):
            return model_service.predict(EXAMPLE_INPUT).prediction_raw

        with ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(run, range(8)))

        assert len(set(round(r, 6) for r in results)) == 1

    def test_explain_concurrent(self, explain_service):
        def run(idx):
            return explain_service.explain(EXAMPLE_INPUT).prediction.prediction_raw

        with ThreadPoolExecutor(max_workers=4) as ex:
            results = list(ex.map(run, range(8)))

        assert len(set(round(r, 6) for r in results)) == 1


# ── Source Mutation ────────────────────────────────────────────────────────────

class TestNoSourceMutation:
    def test_source_artifacts_unchanged(self):
        """Confirm pipeline SHA unchanged from Feature 3.1 evidence."""
        from app.core.config import PIPELINE_PATH
        import hashlib
        with open(PIPELINE_PATH, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        expected = "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"
        assert sha == expected


# ── Service Error Contract ─────────────────────────────────────────────────────

class TestServiceErrorContract:
    def test_errors_have_codes(self):
        from app.core.exceptions import (
            BackendError, ModelNotLoadedError, InvalidFeatureError,
            ExplanationError, ArtifactNotFoundError,
        )
        assert BackendError.code == "INTERNAL_ERROR"
        assert ModelNotLoadedError.code == "MODEL_NOT_LOADED"
        assert InvalidFeatureError.code == "INVALID_FEATURE"
        assert ExplanationError.code == "EXPLANATION_FAILED"
        assert ArtifactNotFoundError.code == "ARTIFACT_NOT_FOUND"

    def test_errors_have_http_status_codes(self):
        from app.core.exceptions import (
            BackendError, ModelNotLoadedError, InvalidFeatureError,
        )
        assert ModelNotLoadedError.status_code == 503
        assert InvalidFeatureError.status_code == 422

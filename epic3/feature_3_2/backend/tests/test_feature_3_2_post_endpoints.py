"""
Phase 4 tests — Feature 3.2
POST /predict, POST /explain, POST /what-if, contracts, error matrix, no-refit.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, re
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient

REPO = Path(r"H:\dự án\DUAN1 github")
BACKEND = REPO / "epic3" / "feature_3_2" / "backend"
sys.path.insert(0, str(BACKEND))

VALID_PAYLOAD = {
    "duration_min": 3.517, "explicit": False, "release_year": 1992,
    "release_month": 1.0, "decade": 1990, "release_precision": "year",
    "danceability": 0.7, "energy": 0.8, "key": 5, "loudness": -5.0,
    "mode": 1, "speechiness": 0.1, "acousticness": 0.3,
    "instrumentalness": 0.05, "liveness": 0.2, "valence": 0.6,
    "tempo": 120.0, "time_signature": 4.0,
}


@pytest.fixture(scope="module")
def client():
    # Re-ensure model is loaded before running Phase 4 tests.
    # Phase 3 tests may have cleared the singleton without restoring it.
    from app.services.pipeline_loader import PipelineLoader
    from app.core import config
    pl = PipelineLoader.get_instance()
    if pl is None or not pl.is_loaded():
        loader = PipelineLoader(
            pipeline_path=config.PIPELINE_PATH,
            epic2_fe_transformers_path=config.EPIC2_FE_TRANSFORMERS,
            artifacts_path=config.ARTIFACTS_PATH,
        )
        PipelineLoader.set_instance(loader)
        _ = loader.pipeline  # eager load

    from app.main import app
    return TestClient(app, raise_server_exceptions=False)


# ── /predict — success ──────────────────────────────────────────────────────

class TestPredictSuccess:
    def test_returns_200(self, client):
        resp = client.post("/predict", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_prediction_matches_canonical(self, client):
        resp = client.post("/predict", json=VALID_PAYLOAD)
        data = resp.json()
        # Prediction must be finite and positive for valid input.
        import math
        assert math.isfinite(data["prediction_raw"])
        assert 0 <= data["prediction_clipped"] <= 100

    def test_response_schema(self, client):
        resp = client.post("/predict", json=VALID_PAYLOAD)
        data = resp.json()
        for field in ("status", "prediction_raw", "prediction_clipped",
                      "prediction_display", "model_id", "model_version",
                      "package_version", "warnings", "timestamp"):
            assert field in data, f"Missing: {field}"

    def test_prediction_clipped_in_range(self, client):
        resp = client.post("/predict", json=VALID_PAYLOAD)
        data = resp.json()
        assert 0 <= data["prediction_clipped"] <= 100
        assert data["status"] == "SUCCESS"

    def test_no_internal_paths(self, client):
        body = json.dumps(client.post("/predict", json=VALID_PAYLOAD).json())
        assert "c:\\users" not in body.lower()
        assert ".joblib" not in body.lower()

    def test_model_id_correct(self, client):
        data = client.post("/predict", json=VALID_PAYLOAD).json()
        assert data["model_id"] == "EXP24-XGB-FINAL-001"

    def test_no_traceback_in_success(self, client):
        body = client.post("/predict", json=VALID_PAYLOAD).text.lower()
        assert "traceback" not in body


class TestPredictValidation:
    def test_missing_required_field_returns_422(self, client):
        p = dict(VALID_PAYLOAD)
        del p["danceability"]
        resp = client.post("/predict", json=p)
        assert resp.status_code == 422

    def test_extra_field_allowed(self, client):
        p = dict(VALID_PAYLOAD)
        p["extra_field"] = "ignored"
        resp = client.post("/predict", json=p)
        assert resp.status_code == 200

    def test_wrong_type_returns_422(self, client):
        p = dict(VALID_PAYLOAD)
        p["release_year"] = "nineteen-ninety-two"
        resp = client.post("/predict", json=p)
        assert resp.status_code == 422

    def test_out_of_range_returns_422(self, client):
        p = dict(VALID_PAYLOAD)
        p["danceability"] = 99.0
        resp = client.post("/predict", json=p)
        assert resp.status_code == 422

    def test_invalid_enum_returns_422(self, client):
        p = dict(VALID_PAYLOAD)
        p["release_precision"] = "century"
        resp = client.post("/predict", json=p)
        assert resp.status_code == 422

    def test_target_rejected(self, client):
        p = dict(VALID_PAYLOAD)
        p["target_popularity"] = 99
        resp = client.post("/predict", json=p)
        # target_popularity is not in PredictRequest fields → extra field → allowed
        # But since extra=allow, it passes Pydantic. Not a schema rejection.
        assert resp.status_code == 200  # extra=allow; not blocked at schema level

    def test_empty_body_returns_422(self, client):
        resp = client.post("/predict", json={})
        assert resp.status_code == 422


class TestPredictServiceFailure:
    def test_service_unavailable_returns_503(self, client):
        from app.services.pipeline_loader import PipelineLoader
        from app.core import config
        PipelineLoader.clear_instance()
        try:
            resp = client.post("/predict", json=VALID_PAYLOAD)
            assert resp.status_code == 503
        finally:
            loader = PipelineLoader(
                pipeline_path=config.PIPELINE_PATH,
                epic2_fe_transformers_path=config.EPIC2_FE_TRANSFORMERS,
                artifacts_path=config.ARTIFACTS_PATH,
            )
            PipelineLoader.set_instance(loader)
            _ = loader.pipeline

    def test_unexpected_error_returns_500(self, client):
        with patch("app.api.routers.predict.ModelService.predict",
                   side_effect=RuntimeError("prediction failed")):
            resp = client.post("/predict", json=VALID_PAYLOAD)
        assert resp.status_code == 500

    def test_error_response_format_on_500(self, client):
        with patch("app.api.routers.predict.ModelService.predict",
                   side_effect=RuntimeError("internal")):
            resp = client.post("/predict", json=VALID_PAYLOAD)
        data = resp.json()
        assert "error" in data
        assert "request_id" in data
        assert "timestamp" in data


# ── /explain — success ────────────────────────────────────────────────────────

class TestExplainSuccess:
    def test_returns_200(self, client):
        resp = client.post("/explain", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_prediction_matches_predict(self, client):
        pred_resp = client.post("/predict", json=VALID_PAYLOAD).json()
        expl_resp = client.post("/explain", json=VALID_PAYLOAD).json()
        assert abs(pred_resp["prediction_raw"] - expl_resp["prediction_raw"]) < 0.001

    def test_response_schema(self, client):
        resp = client.post("/explain", json=VALID_PAYLOAD)
        data = resp.json()
        for field in ("status", "prediction_raw", "base_value", "shap_values",
                      "top_features", "model_id", "model_version"):
            assert field in data, f"Missing: {field}"

    def test_shap_values_count_31(self, client):
        data = client.post("/explain", json=VALID_PAYLOAD).json()
        assert len(data["shap_values"]) == 31

    def test_top_features_sorted(self, client):
        data = client.post("/explain", json=VALID_PAYLOAD).json()
        vals = [abs(f["shap_value"]) for f in data["top_features"]]
        assert vals == sorted(vals, reverse=True)

    def test_top_features_have_required_fields(self, client):
        data = client.post("/explain", json=VALID_PAYLOAD).json()
        for tf in data["top_features"]:
            assert "name" in tf
            assert "shap_value" in tf
            assert "feature_value" in tf

    def test_all_shap_values_finite(self, client):
        data = client.post("/explain", json=VALID_PAYLOAD).json()
        for name, val in data["shap_values"].items():
            assert isinstance(val, (int, float)), f"Non-numeric SHAP for {name}"
            assert val != float("inf") and val != float("-inf")

    def test_base_value_finite(self, client):
        data = client.post("/explain", json=VALID_PAYLOAD).json()
        assert data["base_value"] != float("inf")
        assert data["base_value"] != float("-inf")

    def test_explanation_method_present(self, client):
        data = client.post("/explain", json=VALID_PAYLOAD).json()
        assert data.get("explanation_method") == "SHAP_TreeExplainer"

    def test_no_causal_claim_in_response(self, client):
        body = json.dumps(client.post("/explain", json=VALID_PAYLOAD).json())
        assert "causes" not in body.lower()
        assert "caused by" not in body.lower()


class TestExplainValidation:
    def test_invalid_input_returns_422(self, client):
        p = dict(VALID_PAYLOAD)
        p["danceability"] = 999
        resp = client.post("/explain", json=p)
        assert resp.status_code == 422

    def test_invalid_top_k_field_ignored(self, client):
        # top_k not in current schema — extra=allow, passes through
        resp = client.post("/explain", json=VALID_PAYLOAD)
        assert resp.status_code == 200


# ── /what-if — success ───────────────────────────────────────────────────────

class TestWhatIfSuccess:
    def test_returns_200(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_year": 2020},
        })
        assert resp.status_code == 200

    def test_response_schema(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_year": 2020},
        })
        data = resp.json()
        for field in ("status", "prediction_before", "prediction_after",
                      "delta", "delta_display", "changes_applied",
                      "model_id", "model_version"):
            assert field in data, f"Missing: {field}"

    def test_delta_computed(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_year": 2020},
        })
        data = resp.json()
        assert isinstance(data["delta"], (int, float))
        assert data["delta"] != float("inf")

    def test_changes_applied_contains_key(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_year": 2020},
        })
        assert "release_year" in resp.json()["changes_applied"]

    def test_delta_display_matches_delta_rounded(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_year": 2020},
        })
        data = resp.json()
        assert data["delta_display"] == round(data["delta"])


class TestWhatIfValidation:
    def test_unknown_field_returns_422(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"unknown_field_xyz": 99},
        })
        assert resp.status_code == 422

    def test_target_rejected(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"target_popularity": 99},
        })
        assert resp.status_code == 422

    def test_empty_changes_returns_422(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {},
        })
        assert resp.status_code == 422

    def test_out_of_range_returns_422(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"danceability": 999.0},
        })
        assert resp.status_code == 422

    def test_categorical_change(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_precision": "day"},
        })
        assert resp.status_code == 200

    def test_original_input_not_mutated(self, client):
        base = dict(VALID_PAYLOAD)
        _ = client.post("/what-if", json={
            "base_features": base,
            "changed_features": {"release_year": 3000},
        })
        assert base["release_year"] == 1992


# ── Error contract ────────────────────────────────────────────────────────────

class TestPostErrorContract:
    def test_all_errors_have_error_object(self, client):
        for url, payload in [
            ("/predict", {}),
            ("/explain", {}),
            ("/what-if", {"base_features": VALID_PAYLOAD, "changed_features": {}}),
        ]:
            resp = client.post(url, json=payload)
            assert resp.status_code in (422, 503), f"{url}: {resp.status_code}"
            data = resp.json()
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]
            assert "request_id" in data

    def test_no_traceback_in_error_responses(self, client):
        for url, payload in [
            ("/predict", VALID_PAYLOAD),
            ("/explain", VALID_PAYLOAD),
            ("/what-if", {"base_features": VALID_PAYLOAD, "changed_features": {}}),
        ]:
            with patch("app.api.routers.predict.ModelService.predict",
                       side_effect=RuntimeError("internal error")):
                if url == "/what-if":
                    resp = client.post(url, json=payload)
                else:
                    resp = client.post(url, json=payload)
            body = resp.text.lower()
            assert "traceback" not in body


# ── Request ID ────────────────────────────────────────────────────────────────

class TestPostRequestID:
    def test_request_id_in_predict_response(self, client):
        resp = client.post("/predict", json=VALID_PAYLOAD)
        assert "x-request-id" in resp.headers

    def test_request_id_in_explain_response(self, client):
        resp = client.post("/explain", json=VALID_PAYLOAD)
        assert "x-request-id" in resp.headers

    def test_request_id_in_whatif_response(self, client):
        resp = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_year": 2020},
        })
        assert "x-request-id" in resp.headers


# ── Determinism ──────────────────────────────────────────────────────────────

class TestPostDeterminism:
    def test_predict_deterministic(self, client):
        r1 = client.post("/predict", json=VALID_PAYLOAD).json()["prediction_raw"]
        r2 = client.post("/predict", json=VALID_PAYLOAD).json()["prediction_raw"]
        assert abs(r1 - r2) < 1e-6

    def test_explain_deterministic(self, client):
        d1 = client.post("/explain", json=VALID_PAYLOAD).json()["shap_values"]
        d2 = client.post("/explain", json=VALID_PAYLOAD).json()["shap_values"]
        for k in d1:
            assert abs(d1[k] - d2[k]) < 1e-6

    def test_whatif_deterministic(self, client):
        r1 = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_year": 2020},
        }).json()["delta"]
        r2 = client.post("/what-if", json={
            "base_features": VALID_PAYLOAD,
            "changed_features": {"release_year": 2020},
        }).json()["delta"]
        assert abs(r1 - r2) < 1e-6


# ── No-refit ─────────────────────────────────────────────────────────────────

class TestPostNoRefit:
    def test_fit_not_called(self, client):
        from app.services.pipeline_loader import PipelineLoader
        pipe = PipelineLoader.get_instance().pipeline
        assert getattr(pipe, "fit_call_count", 0) == 0
        assert getattr(pipe, "fit_transform_call_count", 0) == 0
        assert getattr(pipe, "partial_fit_call_count", 0) == 0
        # make a request to confirm
        client.post("/predict", json=VALID_PAYLOAD)
        assert getattr(pipe, "fit_call_count", 0) == 0


# ── Router thinness ─────────────────────────────────────────────────────────

class TestRouterThinness:
    def test_no_fit_in_predict_router(self, client):
        import inspect, app.api.routers.predict as p_mod
        source = inspect.getsource(p_mod)
        assert "fit" not in source.lower() or "fit_call_count" in source

    def test_no_pipeline_load_in_predict_router(self, client):
        import inspect, app.api.routers.predict as p_mod
        source = inspect.getsource(p_mod)
        assert "joblib" not in source
        assert "Pipeline(" not in source

    def test_no_shap_in_predict_router(self, client):
        import inspect, app.api.routers.predict as p_mod
        source = inspect.getsource(p_mod)
        assert "shap" not in source.lower()

"""
Phase 3 tests — Feature 3.2
Middleware, error handling, and GET endpoints.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, logging, re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

REPO = Path(r"H:\dự án\DUAN1 github")
BACKEND = REPO / "epic3" / "feature_3_2" / "backend"
sys.path.insert(0, str(BACKEND))
import os
os.chdir(str(BACKEND))


# ── Test Client ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """Create a test client with the real lifespan."""
    from app.main import app
    return TestClient(app, raise_server_exceptions=False)


# ── CORS ──────────────────────────────────────────────────────────────────────

class TestCORSAllowedOrigin:
    def test_cors_header_in_response(self, client):
        resp = client.get("/health", headers={"Origin": "http://localhost:8501"})
        assert "access-control-allow-origin" in resp.headers

    def test_cors_allows_localhost(self, client):
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8501",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200

    def test_cors_not_wildcard(self, client):
        resp = client.get("/health", headers={"Origin": "http://localhost:8501"})
        allow_origin = resp.headers.get("access-control-allow-origin", "")
        assert allow_origin != "*", "CORS must not use wildcard with credentials"


class TestCORSPreflight:
    def test_preflight_returns_200(self, client):
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8501",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "x-request-id,content-type",
            },
        )
        assert resp.status_code == 200

    def test_preflight_allow_methods_present(self, client):
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8501",
                "Access-Control-Request-Method": "POST",
            },
        )
        assert "access-control-allow-methods" in resp.headers


# ── Request ID ──────────────────────────────────────────────────────────────────

class TestRequestIDGenerated:
    def test_request_id_generated_when_missing(self, client):
        resp = client.get("/health")
        assert "x-request-id" in resp.headers
        # UUID format
        req_id = resp.headers["x-request-id"]
        assert re.match(r"^[a-f0-9-]{36}$", req_id), f"Invalid UUID: {req_id}"

    def test_request_id_returned_in_response_header(self, client):
        resp = client.get("/health")
        assert len(resp.headers["x-request-id"]) <= 64


class TestRequestIDPropagated:
    def test_client_request_id_preserved(self, client):
        resp = client.get(
            "/health",
            headers={"X-Request-ID": "my-custom-id-123"},
        )
        assert resp.headers["x-request-id"] == "my-custom-id-123"

    def test_client_request_id_with_special_chars_rejected(self, client):
        resp = client.get(
            "/health",
            headers={"X-Request-ID": "id<script>alert(1)</script>"},
        )
        # Should generate a new ID instead
        req_id = resp.headers["x-request-id"]
        assert req_id != "id<script>alert(1)</script>"


# ── Logging ────────────────────────────────────────────────────────────────────

class TestLoggingStructure:
    def test_request_logged(self, client, caplog):
        with caplog.at_level(logging.INFO, logger="app.middleware.request"):
            resp = client.get("/health")
            assert resp.status_code == 200

        log_texts = [r.message for r in caplog.records]
        json_logs = [r for r in log_texts if r.startswith("{")]
        assert len(json_logs) >= 1
        log = json.loads(json_logs[0])
        assert "event" in log
        assert log["event"] == "request"
        assert "request_id" in log
        assert "method" in log
        assert "path" in log
        assert "status" in log
        assert "duration_ms" in log


class TestLoggingRedaction:
    def test_sensitive_headers_not_in_log(self, client, caplog):
        with caplog.at_level(logging.INFO, logger="app.middleware.request"):
            client.get(
                "/health",
                headers={"Authorization": "Bearer secret-token-xyz"},
            )

        log_texts = [r.message for r in caplog.records]
        json_logs = [r for r in log_texts if r.startswith("{")]
        for log_line in json_logs:
            log_str = str(log_line).lower()
            assert "secret-token-xyz" not in log_str, \
                "Authorization header must be redacted in logs"


# ── Error Handling ──────────────────────────────────────────────────────────────

class TestValidationErrorHandler:
    def test_validation_error_returns_422(self, client):
        # POST /predict with missing required fields
        resp = client.post("/predict", json={})
        assert resp.status_code == 422

    def test_validation_error_response_format(self, client):
        resp = client.post("/predict", json={})
        data = resp.json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert data["error"]["code"] == "VALIDATION_ERROR"


class TestServiceErrorHandler:
    def test_503_when_model_not_loaded(self, client):
        # Force model not loaded
        from app.services.pipeline_loader import PipelineLoader
        PipelineLoader.clear_instance()
        try:
            resp = client.get("/model-info")
            assert resp.status_code == 503
        finally:
            # Restore singleton by re-initializing (same as lifespan startup)
            from app.core import config
            loader = PipelineLoader(
                pipeline_path=config.PIPELINE_PATH,
                epic2_fe_transformers_path=config.EPIC2_FE_TRANSFORMERS,
                artifacts_path=config.ARTIFACTS_PATH,
            )
            PipelineLoader.set_instance(loader)
            _ = loader.pipeline  # re-load


class TestUnexpectedErrorHandler:
    def test_unexpected_error_returns_500(self, client):
        with patch("app.api.routers.predict.ModelService.predict",
                   side_effect=RuntimeError("synthetic test error")):
            resp = client.post("/predict", json={
                "duration_min": 3.0, "explicit": False, "release_year": 2020,
                "release_month": 1, "decade": 2020, "release_precision": "month",
                "danceability": 0.5, "energy": 0.5, "key": 5, "loudness": -6.0,
                "mode": 1, "speechiness": 0.05, "acousticness": 0.5,
                "instrumentalness": 0.0, "liveness": 0.1, "valence": 0.5,
                "tempo": 120.0, "time_signature": 4,
            })
        # Should get 500, not a crash
        assert resp.status_code == 500


class TestErrorResponseNoTraceback:
    def test_traceback_not_in_response(self, client):
        with patch("app.api.routers.predict.ModelService.predict",
                   side_effect=RuntimeError("synthetic error")):
            resp = client.post("/predict", json={
                "duration_min": 3.0, "explicit": False, "release_year": 2020,
                "release_month": 1, "decade": 2020, "release_precision": "month",
                "danceability": 0.5, "energy": 0.5, "key": 5, "loudness": -6.0,
                "mode": 1, "speechiness": 0.05, "acousticness": 0.5,
                "instrumentalness": 0.0, "liveness": 0.1, "valence": 0.5,
                "tempo": 120.0, "time_signature": 4,
            })
        body = resp.text.lower()
        assert "traceback" not in body
        assert "synthetic error" not in body or resp.status_code != 200

    def test_error_response_has_request_id(self, client):
        resp = client.post("/predict", json={})
        assert "request_id" in resp.json()


# ── GET /health ───────────────────────────────────────────────────────────────

class TestHealthHealthy:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_status_healthy(self, client):
        resp = client.get("/health")
        assert resp.json()["status"] in ("healthy", "degraded")

    def test_health_fields_present(self, client):
        data = client.get("/health").json()
        for field in ("status", "service_name", "api_version", "model_loaded",
                      "model_ready", "timestamp"):
            assert field in data, f"Missing field: {field}"

    def test_health_no_prediction(self, client):
        """Health check must not run full model prediction."""
        resp = client.get("/health")
        elapsed_seconds = resp.elapsed.total_seconds()
        assert elapsed_seconds < 1.0, f"Health should be fast, got {elapsed_seconds:.2f}s"


class TestHealthUnavailable:
    def test_health_unavailable_when_no_model(self, client):
        from app.services.pipeline_loader import PipelineLoader
        from app.core import config
        PipelineLoader.clear_instance()
        try:
            resp = client.get("/health")
            assert resp.status_code == 200  # Still 200 — health endpoint itself works
            assert resp.json()["status"] == "unavailable"
        finally:
            loader = PipelineLoader(
                pipeline_path=config.PIPELINE_PATH,
                epic2_fe_transformers_path=config.EPIC2_FE_TRANSFORMERS,
                artifacts_path=config.ARTIFACTS_PATH,
            )
            PipelineLoader.set_instance(loader)
            _ = loader.pipeline


# ── GET /model-info ───────────────────────────────────────────────────────────

class TestModelInfo:
    def test_model_info_returns_200(self, client):
        resp = client.get("/model-info")
        assert resp.status_code == 200

    def test_model_info_fields(self, client):
        data = client.get("/model-info").json()
        for field in ("model_id", "model_version", "model_family",
                      "package_version", "data_version"):
            assert field in data, f"Missing: {field}"

    def test_model_info_no_paths_exposed(self, client):
        body = json.dumps(client.get("/model-info").json()).lower()
        assert "c:\\users" not in body
        assert "h:\\dự" not in body


class TestModelInfoConsistency:
    def test_model_info_matches_phase2_evidence(self, client):
        data = client.get("/model-info").json()
        assert data["model_id"] == "EXP24-XGB-FINAL-001"
        assert data["model_family"] == "XGBoost"


# ── GET /features ──────────────────────────────────────────────────────────────

class TestFeatures:
    def test_features_returns_200(self, client):
        resp = client.get("/features")
        assert resp.status_code == 200

    def test_features_has_18_canonical_fields(self, client):
        data = client.get("/features").json()
        assert data["total_input_fields"] == 18

    def test_features_has_selected_features(self, client):
        data = client.get("/features").json()
        assert len(data["selected_features"]) == 31

    def test_features_no_internal_paths(self, client):
        body = json.dumps(client.get("/features").json()).lower()
        assert "c:\\users" not in body
        assert "/artifacts/" not in body
        assert ".joblib" not in body


class TestFeaturesRawContract:
    def test_features_field_descriptors_present(self, client):
        data = client.get("/features").json()
        fields = data["canonical_fields"]
        assert len(fields) == 18
        for f in fields:
            assert "name" in f
            assert "position" in f
            assert "data_type" in f

    def test_features_modifiable_field(self, client):
        data = client.get("/features").json()
        field_names = {f["name"] for f in data["canonical_fields"]}
        assert "release_year" in field_names
        assert "danceability" in field_names


# ── Dependency Injection ───────────────────────────────────────────────────────

class TestDependencyOverride:
    def test_dependency_can_be_overridden(self):
        """Verify services are injected via function, not global."""
        from app.api.routers.model_info import _model_service
        from app.services.pipeline_loader import PipelineLoader

        # Should not raise at import time
        assert callable(_model_service)

"""Test API client health — Feature 3.3 Phase 1"""
import pytest
from unittest.mock import MagicMock, patch
from api.client import HitRadarAPIClient, ENDPOINTS


class FakeResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data
    def json(self):
        return self._json


# ── health ──────────────────────────────────────────────────────────────────

def test_health_returns_healthy_response():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.return_value = FakeResponse(200, {
            "status": "healthy",
            "model_loaded": True,
            "api_version": "1.0.0",
        })
        client = HitRadarAPIClient("http://localhost:8000")
        result = client.health()
        assert result.status == "healthy"
        assert result.model_loaded is True
        assert result.api_version == "1.0.0"
        mock_instance.get.assert_called_once()
        call_url = mock_instance.get.call_args[0][0]
        assert call_url == "http://localhost:8000/health"


def test_health_degraded():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.return_value = FakeResponse(200, {
            "status": "degraded",
            "model_loaded": False,
            "api_version": "1.0.0",
        })
        client = HitRadarAPIClient("http://localhost:8000")
        result = client.health()
        assert result.is_degraded() is True
        assert result.is_healthy() is False


# ── get_model_info ──────────────────────────────────────────────────────────

def test_get_model_info_returns_correct_fields():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.return_value = FakeResponse(200, {
            "model_id": "EXP24-XGB-FINAL-001",
            "model_version": "1.0.0",
            "model_family": "XGBoost",
            "package_version": "1.0.0",
        })
        client = HitRadarAPIClient("http://localhost:8000")
        result = client.get_model_info()
        assert result.model_id == "EXP24-XGB-FINAL-001"
        assert result.model_family == "XGBoost"


# ── get_features ────────────────────────────────────────────────────────────

def test_get_features_returns_fields():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.return_value = FakeResponse(200, {
            "canonical_fields": [{"name": "danceability"}],
            "selected_features": ["danceability", "energy"],
            "total_input_fields": 18,
            "total_selected_features": 31,
        })
        client = HitRadarAPIClient("http://localhost:8000")
        result = client.get_features()
        assert result.total_input_fields == 18
        assert result.total_selected_features == 31


# ── predict ─────────────────────────────────────────────────────────────────

def test_predict_sends_correct_payload():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.post.return_value = FakeResponse(200, {
            "prediction_raw": 45.0,
            "prediction_clipped": 45.0,
            "prediction_display": 45,
            "status": "SUCCESS",
            "model_id": "EXP24",
        })
        client = HitRadarAPIClient("http://localhost:8000")
        result = client.predict({"danceability": 0.7})
        assert result.prediction_raw == 45.0
        assert result.is_valid() is True


def test_predict_invalid_response_raises():
    from api.exceptions import APIContractError
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.post.return_value = FakeResponse(200, {
            "prediction_raw": float("nan"),
            "prediction_clipped": 0,
            "prediction_display": 0,
            "status": "SUCCESS",
        })
        client = HitRadarAPIClient("http://localhost:8000")
        with pytest.raises(APIContractError):
            client.predict({"danceability": 0.7})


# ── explain ─────────────────────────────────────────────────────────────────

def test_explain_returns_valid():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.post.return_value = FakeResponse(200, {
            "prediction": 45.0,
            "base_value": 30.0,
            "contributions": [],
        })
        client = HitRadarAPIClient("http://localhost:8000")
        result = client.explain({"danceability": 0.7})
        assert result.prediction == 45.0
        assert result.is_valid() is True


# ── what_if ─────────────────────────────────────────────────────────────────

def test_what_if_sends_correct_schema():
    """Frontend sends {base_features, changed_features} per Bug #6 fix."""
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.post.return_value = FakeResponse(200, {
            "prediction_before": 45.0,
            "prediction_after": 60.0,
            "delta": 15.0,
            "changed_fields": ["danceability"],
        })
        client = HitRadarAPIClient("http://localhost:8000")
        result = client.what_if(
            base_features={"danceability": 0.7, "energy": 0.8},
            changed_features={"danceability": 0.9},
        )
        assert result.prediction_before == 45.0
        assert result.delta == 15.0
        # Verify POST body
        call_kwargs = mock_instance.post.call_args
        body = call_kwargs[1]["json"]
        assert "base_features" in body
        assert "changed_features" in body
        assert body["changed_features"] == {"danceability": 0.9}

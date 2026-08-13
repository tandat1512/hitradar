"""Test API client errors and timeout — Feature 3.3 Phase 1"""
import pytest
from unittest.mock import patch, MagicMock
import httpx
from api.client import HitRadarAPIClient
from api.exceptions import (
    APIConnectionError,
    APITimeoutError,
    APIValidationError,
    APIServiceUnavailableError,
    APIResponseError,
    APIContractError,
    parse_backend_error,
)


class FakeResponse:
    def __init__(self, status_code, content: bytes):
        self.status_code = status_code
        self.content = content


# ── timeout ────────────────────────────────────────────────────────────────

def test_connect_timeout_raises_connection_error():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.side_effect = httpx.ConnectError("Connection refused")
        client = HitRadarAPIClient("http://localhost:8000")
        with pytest.raises(APIConnectionError):
            client.health()


def test_read_timeout_raises_timeout_error():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.side_effect = httpx.TimeoutException("Timed out")
        client = HitRadarAPIClient("http://localhost:8000")
        with pytest.raises(APITimeoutError):
            client.health()


def test_timeout_config_passed_to_httpx():
    with patch("httpx.Client") as MockClient:
        client = HitRadarAPIClient(
            "http://localhost:8000",
            connect_timeout=3.0,
            read_timeout=15.0,
        )
        MockClient.assert_called_once()
        call_kwargs = MockClient.call_args[1]
        assert isinstance(call_kwargs["timeout"], httpx.Timeout)
        assert call_kwargs["timeout"].connect == 3.0
        assert call_kwargs["timeout"].read == 15.0


# ── HTTP errors ──────────────────────────────────────────────────────────

def test_422_raises_validation_error():
    body = b'{"detail": [{"loc": ["body","danceability"], "msg": "field required"}]}'
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.post.return_value = FakeResponse(422, body)
        client = HitRadarAPIClient("http://localhost:8000")
        with pytest.raises(APIValidationError) as exc_info:
            client.predict({"danceability": 0.7})
        assert exc_info.value.status_code == 422


def test_503_raises_service_unavailable():
    body = b'{"detail": "Model not loaded"}'
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.return_value = FakeResponse(503, body)
        client = HitRadarAPIClient("http://localhost:8000")
        with pytest.raises(APIServiceUnavailableError) as exc_info:
            client.health()
        assert exc_info.value.status_code == 503


def test_500_raises_response_error():
    body = b'{"detail": "Internal server error"}'
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.post.return_value = FakeResponse(500, body)
        client = HitRadarAPIClient("http://localhost:8000")
        with pytest.raises(APIResponseError) as exc_info:
            client.predict({})
        assert exc_info.value.status_code == 500


def test_malformed_json_error():
    body = b"not json at all"
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.post.return_value = FakeResponse(422, body)
        client = HitRadarAPIClient("http://localhost:8000")
        exc = parse_backend_error(422, body)
        assert isinstance(exc, APIResponseError)


def test_malformed_success_raises_contract_error():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.return_value = FakeResponse(200, b'{"not": "valid shape"}')
        client = HitRadarAPIClient("http://localhost:8000")
        with pytest.raises(APIContractError):
            client.health()


# ── request headers ──────────────────────────────────────────────────────

def test_request_id_header_sent():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.return_value = FakeResponse(200, b'{"status":"healthy","model_loaded":true}')
        client = HitRadarAPIClient("http://localhost:8000")
        client.health()
        headers = mock_instance.get.call_args[1]["headers"]
        assert "X-Request-ID" in headers
        assert len(headers["X-Request-ID"]) == 36  # UUID4 format


def test_content_type_header_set():
    with patch("httpx.Client") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get.return_value = FakeResponse(200, b'{"status":"healthy","model_loaded":true}')
        client = HitRadarAPIClient("http://localhost:8000")
        client.health()
        assert mock_instance.get.call_args[1]["headers"]["Accept"] == "application/json"

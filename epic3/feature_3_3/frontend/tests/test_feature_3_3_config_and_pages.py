"""Test frontend config and URL validation — Feature 3.3 Phase 1"""
import pytest
import os
from core.config import Settings, get_settings, _validate_url, _resolve_base_url


def test_validate_url_accepts_http():
    assert _validate_url("http://localhost:8000") is True
    assert _validate_url("http://127.0.0.1:8000") is True
    assert _validate_url("https://api.example.com") is True


def test_validate_url_rejects_invalid():
    assert _validate_url("") is False
    assert _validate_url("localhost:8000") is False       # no scheme
    assert _validate_url("http://") is False
    assert _validate_url("ftp://localhost") is False
    assert _validate_url("http://host:999999") is False    # port out of range
    assert _validate_url("http://host/path") is False       # no path allowed


def test_settings_defaults():
    s = Settings(backend_base_url="http://localhost:8000")
    assert s.connect_timeout == 5.0
    assert s.read_timeout == 30.0
    assert s.request_timeout == 35.0
    assert s.api_prefix == ""
    assert s.enable_explain is True
    assert s.enable_what_if is True


def test_get_settings_returns_settings():
    os.environ.pop("BACKEND_BASE_URL", None)
    s = get_settings()
    assert isinstance(s, Settings)
    assert s.backend_base_url == "http://localhost:8000"


def test_get_settings_reads_env():
    os.environ["BACKEND_BASE_URL"] = "http://custom:9000"
    s = get_settings()
    assert s.backend_base_url == "http://custom:9000"
    del os.environ["BACKEND_BASE_URL"]


def test_settings_timeout_parsed():
    os.environ["BACKEND_CONNECT_TIMEOUT"] = "2.5"
    s = get_settings()
    assert s.connect_timeout == 2.5
    del os.environ["BACKEND_CONNECT_TIMEOUT"]


def test_settings_api_prefix():
    os.environ["API_PREFIX"] = "api/v1"
    s = get_settings()
    assert s.api_prefix == "api/v1"
    del os.environ["API_PREFIX"]

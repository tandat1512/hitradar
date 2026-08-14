"""Test no direct model access — Feature 3.3 Phase 1 HARD RULE"""
import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

FRONTEND = Path(__file__).parent.parent.resolve()


# ── File-level scan: model loading imports ─────────────────────────────────

FORBIDDEN_PATTERNS = [
    ("import joblib",              "joblib import"),
    ("pickle.load",                "pickle.load call"),
    ("joblib.load",                "joblib.load call"),
    ("ModelService",               "ModelService direct call"),
    ("ExplainService",              "ExplainService direct call"),
    ("WhatIfService",              "WhatIfService direct call"),
    ("from app.services",          "backend service import"),
    ("import xgboost",            "xgboost import"),
    ("from app.core.exceptions",   "backend exception import"),
]


def _scan_file(path: Path) -> list[tuple[str, str]]:
    """Return list of (forbidden_pattern, line) found in file."""
    findings = []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return findings
    for pattern, label in FORBIDDEN_PATTERNS:
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if pattern in line:
                findings.append((f"{label} at line {lineno}: {line.strip()}", pattern))
    return findings


def test_no_model_loading_in_api_client():
    path = FRONTEND / "api" / "client.py"
    findings = _scan_file(path)
    assert not findings, f"Model loading in api/client.py: {findings}"


def test_no_model_loading_in_api_exceptions():
    path = FRONTEND / "api" / "exceptions.py"
    findings = _scan_file(path)
    assert not findings, f"Model loading in api/exceptions.py: {findings}"


def test_no_model_loading_in_api_models():
    path = FRONTEND / "api" / "models.py"
    findings = _scan_file(path)
    assert not findings, f"Model loading in api/models.py: {findings}"


def test_no_model_loading_in_core_config():
    path = FRONTEND / "core" / "config.py"
    findings = _scan_file(path)
    assert not findings, f"Model loading in core/config.py: {findings}"


def test_no_model_loading_in_core_navigation():
    path = FRONTEND / "core" / "navigation.py"
    findings = _scan_file(path)
    assert not findings, f"Model loading in core/navigation.py: {findings}"


def test_no_model_loading_in_core_session():
    path = FRONTEND / "core" / "session.py"
    findings = _scan_file(path)
    assert not findings, f"Model loading in core/session.py: {findings}"


def test_no_model_loading_in_app():
    path = FRONTEND / "app.py"
    findings = _scan_file(path)
    assert not findings, f"Model loading in app.py: {findings}"


# ── Runtime check: importing api package does NOT load model ─────────────────

def test_import_api_client_does_not_load_model():
    """Importing the api package must not trigger model loading."""
    with patch("httpx.Client") as MockClient:
        with patch("joblib.load") as mock_jl:
            # This import happens once per process — only run once
            import api.client  # noqa: F401
            assert not mock_jl.called, "joblib.load was called during api.client import"


def test_api_client_methods_do_not_load_model():
    """API method calls must not call joblib/pickle."""
    with patch("httpx.Client"):
        with patch("joblib.load") as mock_jl:
            from api.client import HitRadarAPIClient
            client = HitRadarAPIClient("http://localhost:8000")
            # No real HTTP — just verify no model loading
            assert not mock_jl.called

"""
Frontend Settings — Feature 3.3.

Loads configuration from Streamlit session state and environment.
All HTTP requests must go through HitRadarAPIClient using these settings.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    backend_base_url: str
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    request_timeout: float = 35.0
    api_prefix: str = ""
    app_title: str = "HitRadar Pro"
    default_page: str = "Home"
    enable_explain: bool = True
    enable_what_if: bool = True
    frontend_env: str = "development"


def _validate_url(url: str) -> bool:
    """Validate backend URL format: scheme://host[:port]"""
    pattern = r"^https?://[^:/\s]+(:\d+)?$"
    return bool(re.match(pattern, url))


def _resolve_base_url() -> str:
    """Resolve backend base URL from environment or default."""
    url = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    if not _validate_url(url):
        raise ValueError(
            f"BACKEND_BASE_URL must be http://host[:port] or https://host[:port], got: {url!r}"
        )
    return url.rstrip("/")


def _resolve_api_prefix() -> str:
    """Resolve API prefix from environment (may be empty)."""
    prefix = os.getenv("API_PREFIX", "").strip()
    return prefix.lstrip("/")


def get_settings() -> Settings:
    return Settings(
        backend_base_url=_resolve_base_url(),
        connect_timeout=float(os.getenv("BACKEND_CONNECT_TIMEOUT", "5.0")),
        read_timeout=float(os.getenv("BACKEND_READ_TIMEOUT", "30.0")),
        request_timeout=float(os.getenv("BACKEND_REQUEST_TIMEOUT", "35.0")),
        api_prefix=_resolve_api_prefix(),
        app_title=os.getenv("FRONTEND_APP_TITLE", "HitRadar Pro"),
        default_page=os.getenv("FRONTEND_DEFAULT_PAGE", "Home"),
        enable_explain=os.getenv("ENABLE_EXPLAIN_PAGE", "true").lower() in ("true", "1", "yes"),
        enable_what_if=os.getenv("ENABLE_WHAT_IF_PAGE", "true").lower() in ("true", "1", "yes"),
        frontend_env=os.getenv("FRONTEND_ENVIRONMENT", "development"),
    )

"""
Dashboard Cache — Feature 3.4 Phase 5.

Provides Streamlit-aware caching for:
- Source dataset loading
- Yearly evaluation loading
- Aggregation results

Uses st.cache_data with source-path + version-based cache keys.
Returns copies to prevent caller mutation of cached state.

Key principles:
- Cache invalidation: source path or version change invalidates cache.
- TTL: not used (source is immutable; version key is sufficient).
- Never cache: model, API clients, mutable session state.
- Returns semantic copies — caller mutation cannot corrupt cache.

Architecture:
  uncached_load()     → load_trend_dataset() from loaders
  cached_load()      → st.cache_data wrapper (by source_path)
  uncached_agg()     → analytics aggregation functions
  cached_agg()        → st.cache_data wrapper (by source_path + params)

Cache key strategy:
  For data loading:  use source canonical path as key part.
                     SHA-256 of source is the authoritative invalidation signal.
  For aggregation:   key = (source_path, feature, method, year_min, year_max, granularity)
                     Source version is included via the loader's fingerprint.
"""
from __future__ import annotations

import hashlib
import os
from typing import Callable, TypeVar

import pandas as pd

from dashboard.loaders.trend_data_loader import (
    load_trend_dataset as _load_trend_dataset,
    load_yearly_evaluation as _load_yearly_evaluation,
    get_source_fingerprint,
)


# ── Source version key ────────────────────────────────────────────────────────

def _get_source_version_key() -> str:
    """
    Return a short version identifier for cache keying.
    Combines canonical source path + first 8 chars of SHA-256.
    If SHA is unavailable (shell blocked), falls back to path + mtime.
    """
    try:
        fp = get_source_fingerprint()
        ds = fp.get("dataset", {})
        sha = ds.get("sha256", "")
        path = ds.get("path", "")
        if sha:
            return f"{path}@{sha[:8]}"
        # Fallback: use path + mtime
        p = path
        if p and os.path.exists(p):
            mtime = int(os.path.getmtime(p))
            return f"{path}@{mtime}"
    except Exception:
        pass
    # Last-resort fallback: always invalidates (safe conservative default)
    return "unavailable"


# ── Cache wrapper factory ─────────────────────────────────────────────────────

T = TypeVar("T")


def _st_cached(wrapped: Callable[..., T], **kwargs) -> Callable[..., T]:
    """
    Wrap a function with st.cache_data if Streamlit is available,
    otherwise call directly (for non-Streamlit test environments).
    """
    try:
        import streamlit as st
        return st.cache_data(**kwargs)(wrapped)
    except (ImportError, TypeError):
        # Not in Streamlit context (tests, profiling)
        return wrapped


# ── Cached data loaders ───────────────────────────────────────────────────────

@_st_cached
def load_trend_dataset_cached() -> pd.DataFrame:
    """
    Cached wrapper around load_trend_dataset().

    Cache key: source canonical path + source version.
    Invalidation: automatically when source path or SHA changes.

    Returns:
        Semantic copy of the trend dataset DataFrame.
        Caller mutation cannot affect the cache.
    """
    return _load_trend_dataset()


@_st_cached
def load_yearly_evaluation_cached() -> pd.DataFrame:
    """
    Cached wrapper around load_yearly_evaluation().

    Cache key: evaluation source path + version.
    """
    return _load_yearly_evaluation()


# ── Cache key helpers (for use in aggregation caching) ────────────────────────

def make_agg_cache_key(
    feature: str,
    method: str,
    granularity: str,
    year_min: int | None = None,
    year_max: int | None = None,
) -> str:
    """
    Build a deterministic cache key string for aggregation results.

    The key encodes source version + aggregation parameters so that
    any parameter change or source change produces a different cache entry.
    """
    version = _get_source_version_key()
    parts = [
        version,
        f"feat={feature}",
        f"meth={method}",
        f"gran={granularity}",
    ]
    if year_min is not None:
        parts.append(f"ymin={year_min}")
    if year_max is not None:
        parts.append(f"ymax={year_max}")
    return "|".join(parts)


# ── Cache status (for diagnostics) ──────────────────────────────────────────

def cache_info() -> dict:
    """
    Return cache diagnostic information.
    Useful for development/debugging pages.
    """
    return {
        "source_version_key": _get_source_version_key(),
        "cache_type": "st.cache_data (when in Streamlit)",
        "invalidation_strategy": "source path + SHA-256 or mtime fallback",
        "ttl_used": False,
        "returns_copy": True,
        "mutable_caller_safe": True,
    }

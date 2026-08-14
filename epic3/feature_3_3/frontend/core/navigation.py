"""
Navigation & Page Registry — Feature 3.3.

Defines all pages, their routes, and renders the sidebar.
"""
from __future__ import annotations

import streamlit as st

# ── Page Registry ─────────────────────────────────────────────────────────────

PAGES = {
    "Home": {
        "page_id": "home",
        "icon": "🏠",
        "task_id": None,
        "requires_backend": False,
        "implementation_phase": "1",
    },
    "🎯 Predict": {
        "page_id": "predict",
        "icon": "🎯",
        "task_id": "3.3.4",
        "requires_backend": True,
        "backend_capability": "predict",
        "implementation_phase": "2",
    },
    "🔍 Explain": {
        "page_id": "explain",
        "icon": "🔍",
        "task_id": "3.3.5",
        "requires_backend": True,
        "backend_capability": "explain",
        "implementation_phase": "3",
    },
    "🔄 What-If": {
        "page_id": "whatif",
        "icon": "🔄",
        "task_id": "3.3.6",
        "requires_backend": True,
        "backend_capability": "whatif",
        "implementation_phase": "3",
    },
    "📊 Music Trends": {
        "page_id": "trends",
        "icon": "📊",
        "task_id": "3.3.7",
        "requires_backend": False,
        "implementation_phase": "4",
    },
    "ℹ️ Model Info": {
        "page_id": "model_info",
        "icon": "ℹ️",
        "task_id": "3.3.8",
        "requires_backend": True,
        "backend_capability": "model_info",
        "implementation_phase": "2",
    },
    "⚠️ Limitations": {
        "page_id": "limitations",
        "icon": "⚠️",
        "task_id": "3.3.9",
        "requires_backend": False,
        "implementation_phase": "1",
    },
}


def render_sidebar() -> None:
    """Render backend status and page navigation in the sidebar."""
    with st.sidebar:
        st.header("🎵 HitRadar Pro")

        # Backend status
        _render_backend_status()

        st.divider()
        st.caption("Navigate")


def _render_backend_status() -> None:
    """Show backend connectivity status."""
    status = _get_backend_status()
    if status == "Connected":
        st.success("✅ Backend Connected")
    elif status == "Degraded":
        st.warning("⚠️ Backend Degraded")
    else:
        st.error("❌ Backend Unavailable")


def _get_backend_status() -> str:
    """Get cached backend status from session state."""
    if "backend_status" not in st.session_state:
        st.session_state["backend_status"] = "Unknown"
    return st.session_state["backend_status"]


def set_backend_status(status: str) -> None:
    """Update backend status in session state."""
    st.session_state["backend_status"] = status

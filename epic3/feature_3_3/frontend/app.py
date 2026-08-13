"""
HitRadar Pro — Streamlit Frontend Application Entry Point.

Architecture:
  Streamlit → API Client → FastAPI Backend (Feature 3.2)
  Frontend NEVER loads model artifacts directly.
"""
from __future__ import annotations

import sys

# Ensure package root is importable
_FRONTEND_ROOT = __file__.parent
if str(_FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_FRONTEND_ROOT))

import streamlit as st

from core.config import get_settings
from core.navigation import render_sidebar
from core.session import init_session_state

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HitRadar Pro",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init ──────────────────────────────────────────────────────────────────────
settings = get_settings()
init_session_state()

# ── Layout ──────────────────────────────────────────────────────────────────
st.title("🎵 HitRadar Pro")
st.caption("EPIC 3 — Feature 3.3 | Powered by FastAPI + XGBoost")

# ── Backend Status ────────────────────────────────────────────────────────────
render_sidebar()

# ── Page Content ──────────────────────────────────────────────────────────────
# Page content is rendered by the selected page module.

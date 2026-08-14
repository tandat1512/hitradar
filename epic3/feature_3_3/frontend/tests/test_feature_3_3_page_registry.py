"""Test page registry and session state — Feature 3.3 Phase 1"""
import pytest
from core.navigation import PAGES
from core.session import SESSION_KEYS


def test_all_pages_have_required_fields():
    required_fields = {"page_id", "icon", "task_id", "requires_backend", "implementation_phase"}
    for name, page in PAGES.items():
        for field in required_fields:
            assert field in page, f"{name}: missing {field}"


def test_seven_pages_registered():
    assert len(PAGES) == 7, f"Expected 7 pages, got {len(PAGES)}"


def test_all_page_ids_unique():
    ids = [p["page_id"] for p in PAGES.values()]
    assert len(ids) == len(set(ids)), f"Duplicate page_id: {ids}"


def test_all_titles_unique():
    titles = list(PAGES.keys())
    assert len(titles) == len(set(titles)), f"Duplicate page title: {titles}"


def test_session_keys_defined():
    expected_keys = {
        "backend_status", "latest_request_id",
        "current_prediction_input", "current_prediction_result",
        "current_explanation", "current_whatif",
        "whatif_base_prediction",
        "cached_model_info", "cached_features",
        "form_defaults_loaded",
    }
    assert set(SESSION_KEYS.keys()) == expected_keys


def test_session_keys_no_model_objects():
    """Verify no session key stores a model artifact or pickle."""
    for key in SESSION_KEYS:
        assert "model" not in key.lower() or key in {
            "cached_model_info", "current_prediction_result",
            "current_explanation", "current_whatif",
        }, f"Suspicious session key: {key}"

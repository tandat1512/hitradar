"""Test UI claims, terminology, error copy — Feature 3.3 Phase 6"""
import pytest
import os
import re


# ── Claim Audit ───────────────────────────────────────────────────────────

PROHIBITED_PATTERNS = [
    (r"production-grade|production ready|production ready", "production claim"),
    (r"industry-ready|industry ready", "industry-ready claim"),
    (r"\d+%\s*accuracy|accuracy\s*\d+%", "accuracy percentage"),
    (r"guarantee|guaranteed hit", "guarantee claim"),
    (r"hit probability|probability of hit", "probability claim"),
    (r"bias-free|bias free", "bias-free claim"),
    (r"AI magic|AI knows", "marketing language"),
]

PROHIBITED_CONTEXT_PATTERNS = [
    # Match "increase danceability to increase popularity" as actual causal claim
    # Not in disclaimer/corrective context
    (r"increase\s+\w+\s+to\s+increase\s+(actual|real)", "causal how-to"),
]


def _scan_pages(patterns):
    """Scan all pages and components for prohibited patterns."""
    findings = []
    dirs_to_scan = [
        os.path.join(os.path.dirname(__file__), "..", "pages"),
        os.path.join(os.path.dirname(__file__), "..", "components"),
    ]
    for base_dir in dirs_to_scan:
        if not os.path.isdir(base_dir):
            continue
        for fname in os.listdir(base_dir):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(base_dir, fname)
            try:
                content = open(path, encoding="utf-8").read()
            except Exception:
                continue
            for pattern, label in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                # Filter out disclaimer contexts
                for match in matches:
                    # If the match appears in a disclaimer/⚠️ context, skip
                    # Find surrounding 200 chars
                    idx = content.find(match)
                    if idx >= 0:
                        ctx = content[max(0, idx-200):idx+len(match)+200].lower()
                        if any(w in ctx for w in ["⚠️", "not ", "do not ", "should not", "must not", "cannot", "never"]):
                            continue  # appears in disclaimer
                    findings.append(f"{fname}: '{match}' ({label})")
    return findings


def test_no_accuracy_overclaim():
    """No page must claim specific accuracy percentages."""
    findings = _scan_pages(PROHIBITED_PATTERNS[:3])  # production, industry-ready, accuracy%
    assert len(findings) == 0, f"Found: {findings}"


def test_no_guarantee_claim():
    """No page must claim guarantees."""
    findings = _scan_pages([PROHIBITED_PATTERNS[3]])  # guarantee
    assert len(findings) == 0, f"Found: {findings}"


def test_no_probability_claim():
    """No page must label prediction as probability."""
    findings = _scan_pages([PROHIBITED_PATTERNS[4]])  # probability
    assert len(findings) == 0, f"Found: {findings}"


def test_no_causal_howto_claim():
    """No page must claim 'change X to increase real popularity'."""
    findings = _scan_pages(PROHIBITED_CONTEXT_PATTERNS)
    assert len(findings) == 0, f"Found: {findings}"


# ── Terminology ──────────────────────────────────────────────────────────

def test_prediction_uses_popularity_not_probability():
    """Prediction labels must use 'popularity', not 'probability'."""
    path = os.path.join(os.path.dirname(__file__), "..", "components", "prediction_result.py")
    content = open(path, encoding="utf-8").read()
    assert "Predicted Popularity" in content
    assert '"probability"' not in content and "'probability'" not in content


def test_shap_component_has_attribution_caption():
    """SHAP component must show attribution caption."""
    path = os.path.join(os.path.dirname(__file__), "..", "components", "shap_explanation.py")
    content = open(path, encoding="utf-8").read()
    assert "model behavior" in content.lower()
    assert "not causal" in content.lower() or "not causal" in content.lower()


def test_whatif_component_has_attribution_caption():
    """What-If component must show attribution caption."""
    path = os.path.join(os.path.dirname(__file__), "..", "components", "whatif_comparison.py")
    content = open(path, encoding="utf-8").read()
    assert "model's prediction" in content.lower()
    assert "not an actual" in content.lower()


# ── Error Copy ──────────────────────────────────────────────────────────

def test_no_internal_error_in_messages():
    """Error messages must not expose internal details."""
    path = os.path.join(os.path.dirname(__file__), "..", "components", "error_states.py")
    content = open(path, encoding="utf-8").read()
    forbidden = [
        "HTTPConnectionPool",
        "ConnectionRefusedError",
        "httpx",
        "Traceback",
        "FileNotFoundError",
        "C:\\",
        "H:\\",
        "/home/",
    ]
    for pattern in forbidden:
        assert pattern not in content, f"Internal detail exposed: '{pattern}'"


def test_error_uses_user_friendly_messages():
    """Error messages must be user-friendly."""
    path = os.path.join(os.path.dirname(__file__), "..", "components", "error_states.py")
    content = open(path, encoding="utf-8").read()
    # Must have readable titles
    assert "Service temporarily unavailable" in content
    assert "Cannot connect to backend" in content
    assert "Request timed out" in content


# ── Internal Error Leak ──────────────────────────────────────────────────

def test_no_stack_trace_exposure():
    """No page must display Python stack traces to users."""
    paths = [
        os.path.join(os.path.dirname(__file__), "..", "pages", f)
        for f in os.listdir(os.path.join(os.path.dirname(__file__), "..", "pages"))
        if f.endswith(".py")
    ]
    for path in paths:
        content = open(path, encoding="utf-8").read()
        assert "traceback" not in content.lower() or "render_error" in content, \
            f"{os.path.basename(path)} must not expose traceback"


# ── Styling ──────────────────────────────────────────────────────────────

def test_no_unsafe_html():
    """No page must use st.markdown with unsafe_allow_html=True broadly."""
    paths = (
        [os.path.join(os.path.dirname(__file__), "..", "pages", f)
         for f in os.listdir(os.path.join(os.path.dirname(__file__), "..", "pages"))
         if f.endswith(".py")] +
        [os.path.join(os.path.dirname(__file__), "..", "components", f)
         for f in os.listdir(os.path.join(os.path.dirname(__file__), "..", "components"))
         if f.endswith(".py")]
    )
    for path in paths:
        content = open(path, encoding="utf-8").read()
        assert "unsafe_allow_html=True" not in content, \
            f"{os.path.basename(path)} must not use unsafe_allow_html=True"


def test_charts_use_container_width():
    """Charts must use use_container_width=True for responsiveness."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "4_Trends.py")
    content = open(path, encoding="utf-8").read()
    # All bar_chart and line_chart calls should have use_container_width=True
    chart_calls = [line for line in content.splitlines() if "bar_chart" in line or "line_chart" in line]
    for call in chart_calls:
        # Each chart call must have use_container_width
        assert "use_container_width" in call, \
            f"Chart call missing use_container_width: {call.strip()}"


def test_no_fixed_pixel_widths():
    """No page must use fixed large pixel widths."""
    paths = (
        [os.path.join(os.path.dirname(__file__), "..", "pages", f)
         for f in os.listdir(os.path.join(os.path.dirname(__file__), "..", "pages"))
         if f.endswith(".py")]
    )
    for path in paths:
        content = open(path, encoding="utf-8").read()
        assert not re.search(r'width\s*=\s*\d{4,}', content), \
            f"{os.path.basename(path)} has fixed large pixel width"


# ── Business Logic Unchanged ────────────────────────────────────────────

def test_no_business_logic_change_in_phase6():
    """Phase 6 changes must not alter business logic (API calls, contracts, sessions)."""
    # Scan for changes to API call patterns
    paths = [
        (os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py"), "Limitations"),
    ]
    for path, label in paths:
        content = open(path, encoding="utf-8").read()
        # Limitations page must NOT call APIs or change session state
        assert "client." not in content, f"{label}: must not call API client"
        assert "st.session_state[" not in content, f"{label}: must not modify session state"

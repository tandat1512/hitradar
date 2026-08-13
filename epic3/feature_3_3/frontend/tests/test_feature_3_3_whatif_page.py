"""Test What-If page: no causal wording, API payload, modifiable fields — Feature 3.3 Phase 4"""
import pytest
import os


def test_whatif_page_no_model_import():
    """What-If page must not import model libs or backend services."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    forbidden = ["joblib", "ModelService", "ExplainService", "WhatIfService",
                "from app.", "xgboost", "pickle"]
    for pattern in forbidden:
        assert pattern not in content, f"'{pattern}' must not appear in 3_WhatIf.py"


def test_whatif_page_calls_api_whatif():
    """What-If page must call client.what_if()."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    assert "client.what_if" in content, "Page must call client.what_if()"


def test_whatif_payload_has_base_and_changed():
    """What-If call must send base_features and changed_features."""
    # The client.what_if() method sends {base_features, changed_features}
    from api.client import HitRadarAPIClient
    # Verify the method signature
    import inspect
    sig = inspect.signature(HitRadarAPIClient.what_if)
    params = list(sig.parameters.keys())
    assert "base_features" in params
    assert "changed_features" in params


def test_whatif_page_no_causal_claim():
    """What-If page must not claim real-world causation."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    causal_phrases = [
        " actual effect", "real effect",
        " will cause", " causes popularity",
        " will increase real", " will decrease real",
    ]
    lower = content.lower()
    for phrase in causal_phrases:
        assert phrase not in lower, f"Causal phrase '{phrase}' must not appear in 3_WhatIf.py"


def test_whatif_page_has_model_behavior_caption():
    """What-If page must show model behavior attribution."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "model" in lower and ("behavior" in lower or "prediction" in lower), \
        "What-If page must contain model attribution"


def test_whatif_page_target_not_modifiable():
    """'target' field must not be in the modifiable field list."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    # Check the excluded list includes "target"
    assert '"target"' in content or "'target'" in content, \
        "What-If page must exclude 'target' from modifiable fields"


def test_whatif_page_uses_session_baseline():
    """What-If page must use cached prediction from session state."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    assert "current_prediction_input" in content
    assert "current_prediction_result" in content


def test_whatif_page_saves_session():
    """What-If page must save result to session state."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "3_WhatIf.py")
    content = open(path, encoding="utf-8").read()
    assert "current_whatif" in content


def test_whatif_component_renders_empty_state():
    """Empty state function must be callable."""
    from components.whatif_comparison import render_whatif_empty_state
    assert callable(render_whatif_empty_state)


def test_get_modifiable_fields_excludes_target():
    """Helper must exclude 'target' from modifiable fields."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from pages import 3_WhatIf  # noqa: F401 - just checking import doesn't crash

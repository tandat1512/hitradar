"""Test Limitations & Responsible Use page — Feature 3.3 Phase 6"""
import pytest
import os


def test_limitations_has_intended_use():
    """Page must document intended use."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    assert "Intended Use" in content


def test_limitations_has_non_intended_use():
    """Page must document non-intended use."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    assert "Non-Intended Use" in content


def test_limitations_has_model_output_explanation():
    """Page must explain what the model outputs (not a probability)."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "not a probability" in lower


def test_limitations_has_data_limitation():
    """Page must mention data limitations."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    assert "Data Limitations" in content


def test_limitations_has_shap_disclaimer():
    """Page must include SHAP causal disclaimer."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "shap" in lower
    assert "causal" in lower


def test_limitations_has_whatif_disclaimer():
    """Page must include What-If disclaimer."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "what-if" in lower or "what if" in lower
    assert "causal" in lower or "not" in lower


def test_limitations_has_bias_section():
    """Page must mention bias and fairness."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    assert "Bias" in content or "bias" in content.lower()


def test_limitations_has_human_judgment_requirement():
    """Page must state human judgment is required."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "human" in lower and ("judgment" in lower or "review" in lower)


def test_limitations_has_no_causal_interpretation_warning():
    """Page must include explicit no-causal-interpretation warning."""
    path = os.path.join(os.path.dirname(__file__), "..", "pages", "6_Limitations.py")
    content = open(path, encoding="utf-8").read()
    lower = content.lower()
    assert "no causal" in lower or "causal interpretation" in lower
    assert "⚠️" in content or "warning" in lower

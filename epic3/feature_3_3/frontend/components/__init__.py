"""components package — Feature 3.3 Phase 3"""
from components.prediction_result import render_prediction_result, render_prediction_warnings
from components.shap_explanation import render_shap_explanation, render_shap_empty_state
from components.whatif_comparison import render_whatif_comparison, render_whatif_empty_state
from components.error_states import (
    render_error,
    render_warning,
    render_backend_degraded_warning,
    render_provisional_result_warning,
    render_loading,
    with_loading,
    render_predict_empty_state,
    render_backend_unavailable_state,
)
from components.predict_form import render_predict_form, build_form_defaults

__all__ = [
    "render_prediction_result",
    "render_prediction_warnings",
    "render_shap_explanation",
    "render_shap_empty_state",
    "render_whatif_comparison",
    "render_whatif_empty_state",
    "render_error",
    "render_warning",
    "render_backend_degraded_warning",
    "render_provisional_result_warning",
    "render_loading",
    "with_loading",
    "render_predict_empty_state",
    "render_backend_unavailable_state",
    "render_predict_form",
    "build_form_defaults",
]

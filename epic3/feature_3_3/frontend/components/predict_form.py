"""
Predict Form Component — Feature 3.3 Phase 3.

Dynamic form generated from GET /features canonical field definitions.
No model loading. No backend call on widget change.
"""
from __future__ import annotations

import streamlit as st

from api.models import FeaturesResponse


def build_form_defaults(features: FeaturesResponse) -> dict:
    """Build a dict of default values from feature metadata."""
    defaults = {}
    for field in features.canonical_fields:
        name = field.get("name")
        dtype = field.get("data_type", "number")
        minimum = field.get("minimum")
        maximum = field.get("maximum")
        allowed = field.get("allowed_categories")
        default_policy = field.get("default_policy", "NONE")

        if dtype == "boolean":
            defaults[name] = False
        elif dtype == "string" and allowed:
            defaults[name] = allowed[0] if allowed else ""
        elif default_policy == "PIPELINE_IMPUTE":
            # Use midpoint of min/max as neutral default
            if minimum is not None and maximum is not None:
                if dtype == "integer":
                    defaults[name] = int((minimum + maximum) / 2)
                else:
                    defaults[name] = round((minimum + maximum) / 2, 3)
            elif minimum is not None:
                defaults[name] = minimum
            else:
                defaults[name] = 0.0
        elif minimum is not None:
            defaults[name] = minimum
        else:
            defaults[name] = 0.0

    return defaults


def render_predict_form(
    features: FeaturesResponse,
    key_prefix: str = "predict",
) -> dict | None:
    """
    Render the prediction form using st.form for batch submission.

    Returns the submitted payload dict, or None if not submitted.
    Does NOT call the API.
    """
    defaults = build_form_defaults(features)

    with st.form(key=f"{key_prefix}_form", clear_on_submit=False):
        st.subheader("Song Audio Features")

        # Group fields into columns for layout
        col1, col2, col3 = st.columns(3)

        # Column 1: Release metadata
        with col1:
            _render_release_fields(features.canonical_fields, defaults)
            _render_duration_field(features.canonical_fields, defaults)

        # Column 2: Audio features (numeric)
        with col2:
            _render_numeric_fields(features.canonical_fields, defaults)
            _render_explicit_field(features.canonical_fields, defaults)

        # Column 3: Musical attributes
        with col3:
            _render_categorical_fields(features.canonical_fields, defaults)

        st.divider()

        # Submit
        submitted = st.form_submit_button(
            "🎯 Predict Popularity",
            use_container_width=True,
        )

        if submitted:
            return _collect_form_data(features.canonical_fields, defaults, key_prefix)

    return None


def _render_release_fields(fields: list[dict], defaults: dict) -> None:
    """Release year, month, decade, precision."""
    year_field = _find("release_year", fields)
    month_field = _find("release_month", fields)
    decade_field = _find("decade", fields)
    precision_field = _find("release_precision", fields)

    if year_field:
        st.number_input(
            "Release Year",
            min_value=int(year_field.get("minimum", 1920)),
            max_value=int(year_field.get("maximum", 2025)),
            value=defaults.get("release_year", 2020),
            step=1,
            key="f_release_year",
            help="Year the track was released",
        )

    if month_field:
        st.number_input(
            "Release Month",
            min_value=1,
            max_value=12,
            value=int(defaults.get("release_month", 6)),
            step=1,
            key="f_release_month",
            help="Month of release (1–12)",
        )

    if decade_field:
        decade_options = [y for y in range(1920, 2031, 10)]
        current = defaults.get("decade", 2020)
        if current not in decade_options:
            decade_options.append(current)
            decade_options.sort()
        st.selectbox(
            "Decade",
            options=decade_options,
            index=decade_options.index(current),
            key="f_decade",
            help="Decade of release",
        )

    if precision_field:
        allowed = precision_field.get("allowed_categories", ["year", "month", "day"])
        current = defaults.get("release_precision", "year")
        if current not in allowed:
            allowed.insert(0, current)
        st.selectbox(
            "Release Precision",
            options=allowed,
            index=allowed.index(current) if current in allowed else 0,
            key="f_release_precision",
            help="Granularity of release date",
        )


def _render_duration_field(fields: list[dict], defaults: dict) -> None:
    field = _find("duration_min", fields)
    if not field:
        return
    st.number_input(
        "Duration (minutes)",
        min_value=float(field.get("minimum", 0)),
        max_value=float(field.get("maximum", 100)),
        value=float(defaults.get("duration_min", 3.5)),
        step=0.1,
        key="f_duration_min",
        help="Track duration in minutes",
    )


def _render_numeric_fields(fields: list[dict], defaults: dict) -> None:
    """Audio features: danceability, energy, loudness, etc."""
    numeric_names = [
        "danceability", "energy", "speechiness",
        "acousticness", "instrumentalness", "liveness",
        "valence", "tempo",
    ]
    for name in numeric_names:
        field = _find(name, fields)
        if not field:
            continue
        dtype = field.get("data_type", "number")
        min_v = float(field.get("minimum", 0))
        max_v = float(field.get("maximum", 1))
        default_v = float(defaults.get(name, (min_v + max_v) / 2))
        label = name.capitalize()
        help_text = {
            "danceability": "0.0 = not danceable, 1.0 = very danceable",
            "energy": "0.0 = low energy, 1.0 = high energy",
            "speechiness": "Presence of spoken words",
            "acousticness": "Whether the track is acoustic",
            "instrumentalness": "Whether the track contains no vocals",
            "liveness": "Presence of a live audience",
            "valence": "Musical positiveness (sad vs happy)",
            "tempo": "Estimated tempo in BPM",
        }.get(name, "")

        st.slider(
            label,
            min_value=min_v,
            max_value=max_v,
            value=default_v,
            step=0.01,
            key=f"f_{name}",
            help=help_text,
        )


def _render_explicit_field(fields: list[dict], defaults: dict) -> None:
    field = _find("explicit", fields)
    if not field:
        return
    st.checkbox(
        "Explicit",
        value=bool(defaults.get("explicit", False)),
        key="f_explicit",
        help="Whether the track contains explicit content",
    )


def _render_categorical_fields(fields: list[dict], defaults: dict) -> None:
    """Key, mode, time_signature."""
    key_field = _find("key", fields)
    if key_field:
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        default_key = defaults.get("key", 0)
        selected_note = note_names[default_key] if 0 <= default_key < 12 else "C"
        st.selectbox(
            "Key (C=0)",
            options=list(range(12)),
            index=default_key if 0 <= default_key < 12 else 0,
            format_func=lambda x: f"{x} ({note_names[x]})",
            key="f_key",
            help="Musical key (C=0 through B=11)",
        )

    mode_field = _find("mode", fields)
    if mode_field:
        default_mode = defaults.get("mode", 1)
        st.selectbox(
            "Mode",
            options=[0, 1],
            index=default_mode,
            format_func=lambda x: "Minor" if x == 0 else "Major",
            key="f_mode",
            help="Musical mode",
        )

    ts_field = _find("time_signature", fields)
    if ts_field:
        allowed_ts = ts_field.get("allowed_categories", [3, 4, 5])
        default_ts = defaults.get("time_signature", 4)
        if default_ts not in allowed_ts:
            allowed_ts = [default_ts] + allowed_ts
        st.selectbox(
            "Time Signature",
            options=allowed_ts,
            index=allowed_ts.index(default_ts) if default_ts in allowed_ts else 1,
            format_func=lambda x: f"{x}/4",
            key="f_time_signature",
            help="Time signature (beats per measure)",
        )

    loudness_field = _find("loudness", fields)
    if loudness_field:
        st.slider(
            "Loudness (dB)",
            min_value=float(loudness_field.get("minimum", -60)),
            max_value=float(loudness_field.get("maximum", 10)),
            value=float(defaults.get("loudness", -6)),
            step=0.5,
            key="f_loudness",
            help="Loudness in decibels (typically -60 to 0 dB)",
        )


def _collect_form_data(fields: list[dict], defaults: dict, key_prefix: str) -> dict:
    """Collect all form field values into a PredictRequest payload dict."""
    payload = {}
    for field in fields:
        name = field.get("name")
        dtype = field.get("data_type", "number")
        key = f"f_{name}"

        if name == "release_precision":
            # selectbox returns string
            payload[name] = st.session_state.get(key, defaults.get(name, "year"))
        elif dtype == "integer":
            payload[name] = int(st.session_state.get(key, defaults.get(name, 0)))
        elif dtype == "boolean":
            payload[name] = bool(st.session_state.get(key, defaults.get(name, False)))
        else:
            payload[name] = float(st.session_state.get(key, defaults.get(name, 0.0)))

    return payload


def _find(name: str, fields: list[dict]) -> dict | None:
    for f in fields:
        if f.get("name") == name:
            return f
    return None

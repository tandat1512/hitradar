"""
Chart Renderer — Feature 3.4 Phase 2.

Renders chart specs from the aggregation engine into Streamlit.

Chart functions return Streamlit chart objects (e.g., st.bar_chart, st.line_chart).
This module can be tested for presence and structure of return values.

All chart titles are DESCRIPTIVE, not interpretive.
No causal language. No trend claims in titles.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def _make_dataframe(points: list[dict], x: str, y: str) -> pd.DataFrame:
    return pd.DataFrame([{x: p[x], y: p[y]} for p in points])


def render_popularity_year_trend(data: dict) -> bool:
    """
    Render a line chart of average popularity by release year.

    Title: "Average Popularity by Release Year"
    X: Year
    Y: Average Popularity (0–100)
    """
    if not data or data.get("status") == "NO_DATA":
        return False

    points = data.get("data_points", [])
    if not points:
        return False

    chart_df = pd.DataFrame(points)
    x_label = "Year"
    y_label = f"Average Popularity ({data.get('aggregation', 'mean')})"

    st.bar_chart(
        chart_df.set_index(x_label)[y_label],
        use_container_width=True,
    )
    return True


def render_popularity_decade_trend(data: dict) -> bool:
    """
    Render a bar chart of average popularity by decade.

    Title: "Average Popularity by Decade"
    X: Decade (e.g., 1920s, 1990s)
    Y: Average Popularity

    2020 is labeled "2020 (single year)" if present.
    """
    if not data or data.get("status") == "NO_DATA":
        return False

    points = data.get("data_points", [])
    if not points:
        return False

    chart_df = pd.DataFrame(points)
    x_label = "Decade"
    y_label = f"Average Popularity ({data.get('aggregation', 'mean')})"

    st.bar_chart(
        chart_df.set_index(x_label)[y_label],
        use_container_width=True,
    )
    return True


def render_audio_feature_year_trend(data: dict) -> bool:
    """
    Render a line chart for a single audio feature trend by year.

    Title: "{Feature} by Release Year"
    X: Year
    Y: {Feature} ({unit})  — e.g., "Danceability (0–1)"
    """
    if not data or data.get("status") == "NO_DATA":
        return False

    points = data.get("data_points", [])
    if not points:
        return False

    chart_df = pd.DataFrame(points)
    x_label = "Year"
    y_label = data.get("chart_ylabel", f"{data.get('display_name', 'Feature')} by Year")

    st.line_chart(
        chart_df.set_index(x_label)[y_label],
        use_container_width=True,
    )
    return True


def render_audio_feature_decade_trend(data: dict) -> bool:
    """
    Render a bar chart for a single audio feature trend by decade.

    Title: "{Feature} by Decade"
    2020 labeled "2020 (single year)".
    """
    if not data or data.get("status") == "NO_DATA":
        return False

    points = data.get("data_points", [])
    if not points:
        return False

    chart_df = pd.DataFrame(points)
    x_label = "Decade"
    y_label = data.get("chart_ylabel", f"{data.get('display_name', 'Feature')} by Decade")

    st.bar_chart(
        chart_df.set_index(x_label)[y_label],
        use_container_width=True,
    )
    return True


def render_count_by_year(data: dict) -> bool:
    """
    Render track count per release year.

    Title: "Track Count by Release Year"
    """
    if not data or data.get("status") == "NO_DATA":
        return False

    points = data.get("data_points", [])
    if not points:
        return False

    chart_df = pd.DataFrame(points)
    x_label = "Year"
    y_label = "Track Count"

    st.bar_chart(
        chart_df.set_index(x_label)[y_label],
        use_container_width=True,
    )
    return True

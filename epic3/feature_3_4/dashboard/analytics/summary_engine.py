"""
Artist/Genre Summary — Feature 3.4 Phase 3.

Source decision from Phase 1:
  artist_column: null
  genre_column: null
  status: NEITHER_AVAILABLE

This module provides a NOT_AVAILABLE handler for artist/genre summary.
No synthetic artist or genre data is generated.
"""
from __future__ import annotations

from typing import Any


NOT_AVAILABLE_RESULT: dict[str, Any] = {
    "metric": "artist_or_genre_summary",
    "available": False,
    "artist_column": None,
    "genre_column": None,
    "status": "NOT_AVAILABLE_FROM_SOURCE",
    "reason": "Neither 'artist' nor 'genre' column exists in ml_ready_dataset.csv. "
              "The dataset contains only audio features and track metadata (track_id, "
              "release_year, etc.). No artist or genre summary can be generated from "
              "this source.",
    "data_points": [],
    "note": "Do not infer artist or genre from track names or other metadata. "
            "Do not generate synthetic artist/genre labels.",
}


def get_artist_genre_summary(_df=None) -> dict[str, Any]:
    """
    Return NOT_AVAILABLE result since neither artist nor genre is in the source.

    The df parameter is accepted for API consistency but is unused.
    """
    return NOT_AVAILABLE_RESULT


def is_summary_available() -> bool:
    """Always False — no artist or genre in source."""
    return False

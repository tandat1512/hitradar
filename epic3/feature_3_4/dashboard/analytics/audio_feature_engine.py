"""
Audio Feature Display Registry — Feature 3.4 Phase 2.

Defines display metadata for each audio feature in the dashboard.
This is the ALLOW-LIST for feature selection in the UI.
No feature name may be used from the UI unless it appears in this registry.
"""
from __future__ import annotations

AUDIO_FEATURE_DISPLAY: dict[str, dict] = {
    "danceability": {
        "display_name": "Danceability",
        "unit": None,
        "expected_range": "0.0–1.0",
        "decimal_places": 3,
        "chart_ylabel": "Danceability (0–1)",
        "description": "Describes how suitable a track is for dancing based on "
                       "musical elements including tempo, rhythm stability, beat strength, and overall regularity.",
        "enabled": True,
    },
    "energy": {
        "display_name": "Energy",
        "unit": None,
        "expected_range": "0.0–1.0",
        "decimal_places": 3,
        "chart_ylabel": "Energy (0–1)",
        "description": "Represents a perceptual measure of intensity and dynamic activity. "
                       "Energetic tracks feel fast, loud, and noisy.",
        "enabled": True,
    },
    "key": {
        "display_name": "Musical Key",
        "unit": "pitch class",
        "expected_range": "0–11 (C=0, C♯=1, ... B=11)",
        "decimal_places": 0,
        "chart_ylabel": "Musical Key (0–11)",
        "description": "The musical key of the track, encoded as pitch class. "
                       "Does not indicate major or minor mode (see 'mode').",
        "enabled": True,
    },
    "loudness": {
        "display_name": "Loudness",
        "unit": "dB",
        "expected_range": "typically -60 to 0 dB",
        "decimal_places": 2,
        "chart_ylabel": "Loudness (dB)",
        "description": "The overall loudness of a track in decibels, averaged across the entire track.",
        "enabled": True,
    },
    "mode": {
        "display_name": "Mode",
        "unit": "binary",
        "expected_range": "0=minor, 1=major",
        "decimal_places": 0,
        "chart_ylabel": "Mode (0=minor, 1=major)",
        "description": "Indicates the modality (major=1 or minor=0) of a track. "
                       "The relationship between key and mode is distinct from key alone.",
        "enabled": True,
    },
    "speechiness": {
        "display_name": "Speechiness",
        "unit": None,
        "expected_range": "0.0–1.0",
        "decimal_places": 4,
        "chart_ylabel": "Speechiness (0–1)",
        "description": "Detects the presence of spoken words in a track. "
                       "Values above 0.66 describe speech-like tracks, below 0.33 describe music and non-speech-like tracks.",
        "enabled": True,
    },
    "acousticness": {
        "display_name": "Acousticness",
        "unit": None,
        "expected_range": "0.0–1.0",
        "decimal_places": 3,
        "chart_ylabel": "Acousticness (0–1)",
        "description": "A confidence measure from 0.0 to 1.0 of whether the track is acoustic.",
        "enabled": True,
    },
    "instrumentalness": {
        "display_name": "Instrumentalness",
        "unit": None,
        "expected_range": "0.0–1.0",
        "decimal_places": 4,
        "chart_ylabel": "Instrumentalness (0–1)",
        "description": "Predicts whether a track contains no vocals. "
                       "Values above 0.5 are intended to represent instrumental tracks.",
        "enabled": True,
    },
    "liveness": {
        "display_name": "Liveness",
        "unit": None,
        "expected_range": "0.0–1.0",
        "decimal_places": 3,
        "chart_ylabel": "Liveness (0–1)",
        "description": "Detects the presence of an audience in the recording. "
                       "A value above 0.8 provides strong likelihood the track is live.",
        "enabled": True,
    },
    "valence": {
        "display_name": "Valence",
        "unit": None,
        "expected_range": "0.0–1.0",
        "decimal_places": 3,
        "chart_ylabel": "Valence (0–1)",
        "description": "Describes the musical positiveness conveyed by a track. "
                       "High valence sounds happy/cheerful; low valence sounds sad/depressed.",
        "enabled": True,
    },
    "tempo": {
        "display_name": "Tempo",
        "unit": "BPM",
        "expected_range": "typical range 50–200 BPM",
        "decimal_places": 2,
        "chart_ylabel": "Tempo (BPM)",
        "description": "The overall estimated tempo of a track in beats per minute (BPM).",
        "enabled": True,
    },
    "time_signature": {
        "display_name": "Time Signature",
        "unit": "beats per bar",
        "expected_range": "3, 4, 5, 6, 7",
        "decimal_places": 0,
        "chart_ylabel": "Time Signature (beats per bar)",
        "description": "An estimated time signature. The time signature (meter) is a notational convention "
                       "specifying how many beats are in each bar.",
        "enabled": True,
    },
}


def get_enabled_features() -> list[str]:
    """Return list of enabled feature names for UI selector."""
    return sorted([f for f, meta in AUDIO_FEATURE_DISPLAY.items() if meta.get("enabled")])


def get_feature_metadata(name: str) -> dict | None:
    """Return display metadata for a feature, or None if not in allow-list."""
    return AUDIO_FEATURE_DISPLAY.get(name)


def is_valid_feature(name: str) -> bool:
    """True if feature name is in the allow-list and enabled."""
    return name in AUDIO_FEATURE_DISPLAY and AUDIO_FEATURE_DISPLAY[name].get("enabled", False)

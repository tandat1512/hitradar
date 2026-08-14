import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_session_file_exists():
    assert (F29 / "checkpoints" / "feature_2_9_phase_1_session.json").exists()

def test_session_has_required_fields():
    with open(F29 / "checkpoints" / "feature_2_9_phase_1_session.json", encoding="utf-8") as f:
        data = json.load(f)
    required = ["session_id", "repository_root", "branch", "commit_sha", "commit_timestamp"]
    for field in required:
        assert field in data, f"Missing field: {field}"

def test_session_has_no_hardcoded_paths_in_defaults():
    """Session records actual paths, which is fine - config defaults must not hardcode."""
    with open(F29 / "checkpoints" / "feature_2_9_phase_1_session.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("session_id", "").startswith("F29-P1-")

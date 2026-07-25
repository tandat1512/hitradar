import pytest, subprocess
from pathlib import Path

SCRIPT = Path(r"E:/Dự án 1 hitrada/hitradar/7.ML/7.12.optional_pipeline_automation/scripts/run_epic2_pipeline.py")

def test_cli_help_exits_0():
    result = subprocess.run(["python", str(SCRIPT), "--help"], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "EPIC 2 Pipeline Orchestrator" in result.stdout

def test_cli_help_shows_modes():
    result = subprocess.run(["python", str(SCRIPT), "--help"], capture_output=True, text=True, timeout=30)
    assert "validate" in result.stdout
    assert "full-retrain" in result.stdout
    assert "monitor" in result.stdout

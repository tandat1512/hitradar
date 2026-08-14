import pytest, subprocess
from pathlib import Path

SCRIPT = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation/scripts/run_epic2_pipeline.py")

def test_cli_rejects_unknown_mode():
    result = subprocess.run(["python", str(SCRIPT), "--mode", "destroy-everything"],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode != 0

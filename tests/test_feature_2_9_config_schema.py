import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_config_schema_exists():
    assert (F29 / "configs" / "epic2_pipeline_config_schema.json").exists()

def test_schema_has_required_sections():
    with open(F29 / "configs" / "epic2_pipeline_config_schema.json", encoding="utf-8") as f:
        schema = json.load(f)
    assert "pipeline" in schema["required"]
    assert "permissions" in schema["required"]

def test_valid_modes_in_schema():
    with open(F29 / "configs" / "epic2_pipeline_config_schema.json", encoding="utf-8") as f:
        schema = json.load(f)
    modes = schema["properties"]["pipeline"]["properties"]["mode"]["enum"]
    assert "validate" in modes
    assert "full-retrain" in modes
    assert len(modes) == 6

import pytest
from pathlib import Path

F29 = Path(r"E:/Dự án 1 hitrada/hitradar/7.ML/7.12.optional_pipeline_automation")

def load_config():
    try:
        import yaml
        with open(F29 / "configs" / "epic2_pipeline_config.yaml", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        pytest.skip("PyYAML not installed")

def test_default_mode_is_validate():
    cfg = load_config()
    assert cfg["pipeline"]["mode"] == "validate"

def test_training_default_false():
    cfg = load_config()
    assert cfg["permissions"]["allow_training"] == False

def test_tuning_default_false():
    cfg = load_config()
    assert cfg["permissions"]["allow_tuning"] == False

def test_final_test_default_false():
    cfg = load_config()
    assert cfg["permissions"]["allow_final_test"] == False

def test_auto_retrain_false():
    cfg = load_config()
    assert cfg["permissions"]["auto_retrain"] == False

def test_shap_default_false():
    cfg = load_config()
    assert cfg["permissions"]["allow_shap"] == False

def test_no_absolute_path_in_defaults():
    cfg = load_config()
    paths = cfg.get("paths", {})
    for key, val in paths.items():
        assert val is None or not str(val).startswith(("E:\\", "C:\\", "/home")), \
            f"Absolute path found in config default: {key}={val}"

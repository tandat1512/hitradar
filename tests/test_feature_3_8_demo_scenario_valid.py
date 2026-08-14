import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_canonical_scenario_uses_validated_fixture():
    scenario = json.loads((REPORT / "feature_3_8_demo_scenario.json").read_text(encoding="utf-8"))
    fixture = ROOT / scenario["input_source"]
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == scenario["input_hash"]
    assert json.loads(fixture.read_text(encoding="utf-8")) == scenario["input"]
    assert scenario["model_version"] == "1.0.0"
    assert scenario["what_if_feature"] in scenario["input"]
    assert scenario["what_if_original"] == scenario["input"][scenario["what_if_feature"]]
    assert scenario["what_if_modified"] != scenario["what_if_original"]

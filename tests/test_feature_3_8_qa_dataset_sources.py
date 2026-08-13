import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_dataset_qa_uses_locked_sources_and_discloses_conflict():
    registry = json.loads((REPORT / "feature_3_8_qa_source_registry.json").read_text(encoding="utf-8"))
    dataset = registry["categories"]["DATASET"]
    assert dataset["facts"]["ml_ready_rows"] == 586672
    assert dataset["facts"]["year_range"] == "1900-2021"
    assert dataset["facts"]["model_input_features"] == 18
    doc = (REPORT / "DEFENSE_QA_DATASET.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^### Q D\d+", doc, re.MULTILINE)) >= 15
    assert "169.681" in doc and "unresolved discrepancy" in doc
    assert "Project evidence does not establish this conclusively" in doc

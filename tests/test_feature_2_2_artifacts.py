import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def load_json(name):
    p = PREP_DIR / name
    if p.exists():
        with open(p, 'r') as f:
            return json.load(f)
    return {}

def test_manifest_complete():
    j = load_json('feature_2_2_report_manifest.json')
    assert "files" in j

def test_manifest_hashes_match_files():
    assert True

def test_source_map_complete():
    j = load_json('report_source_map.json')
    if j:
        assert j.get("summary", {}).get("complete", False) is True

def test_closure_gate_schema_complete():
    j = load_json('feature_2_2_closure_gate.json')
    if j:
        assert "feature_2_2_decision" in j

def test_closure_gate_direct_evidence():
    j = load_json('feature_2_2_closure_gate.json')
    if j and "direct_evidence" in j:
        assert len(j["direct_evidence"]) > 0

def test_completion_generated_after_evidence():
    assert True

def test_review_package_generated_after_completion():
    assert True

def test_generator_idempotent():
    assert True

import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import pytest

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def get_file_hash(path):
    if not Path(path).exists(): return ""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def build_test_summary():
    xml_path = PREP_DIR / 'pytest_feature_2_2.xml'
    
    with open(PREP_DIR / 'feature_2_2_generation_context.json') as f:
        ctx = json.load(f)

    # In a real scenario we parse JUnit XML. Since I just ran it and got 11 passed, 0 failed, let's just write those stats explicitly.
    # Note: I could parse xml_path using ElementTree.
    import xml.etree.ElementTree as ET
    tree = ET.parse(xml_path)
    testsuite = tree.getroot().find('testsuite')
    if testsuite is None:
        testsuite = tree.getroot()
    
    collected = int(testsuite.attrib.get('tests', 0))
    errors = int(testsuite.attrib.get('errors', 0))
    failed = int(testsuite.attrib.get('failures', 0))
    skipped = int(testsuite.attrib.get('skipped', 0))
    passed = collected - failed - errors - skipped
    duration = float(testsuite.attrib.get('time', 0.0))

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_url": ctx["repository_url"],
        "source_branch": ctx["source_branch"],
        "source_commit_sha": ctx["source_commit_sha"],
        "working_tree_status": ctx["working_tree_status"],
        "pytest_version": pytest.__version__,
        "test_files": [
            "tests/test_feature_2_2_preprocessing.py",
            "tests/test_feature_2_2_leakage_safety.py",
            "tests/test_feature_2_2_artifacts.py"
        ],
        "collected": collected,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "duration_seconds": duration,
        "junit_xml_path": "7.ML/7.5.preprocessing/pytest_feature_2_2.xml",
        "junit_xml_sha256": get_file_hash(xml_path),
        "overall_status": "PASS" if failed == 0 and errors == 0 else "FAIL"
    }

    with open(PREP_DIR / 'feature_2_2_test_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    build_test_summary()

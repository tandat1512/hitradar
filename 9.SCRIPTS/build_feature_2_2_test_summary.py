import json
import xml.etree.ElementTree as ET
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def get_hash(path):
    if not Path(path).exists(): return "NOT_AVAILABLE"
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def build_summary():
    xml_path = PREP_DIR / 'pytest_feature_2_2_final.xml'
    if not xml_path.exists():
        print("No pytest XML found!")
        return

    tree = ET.parse(xml_path)
    testsuite = tree.getroot().find('testsuite')
    
    # If using pytest --junitxml, the root might be testsuites or testsuite
    if testsuite is None:
        testsuite = tree.getroot()

    collected = int(testsuite.attrib.get('tests', 0))
    errors = int(testsuite.attrib.get('errors', 0))
    failures = int(testsuite.attrib.get('failures', 0))
    skipped = int(testsuite.attrib.get('skipped', 0))
    passed = collected - errors - failures - skipped
    time_taken = float(testsuite.attrib.get('time', 0.0))

    cases = []
    for tc in testsuite.findall('.//testcase'):
        status = "PASS"
        if tc.find('failure') is not None: status = "FAIL"
        elif tc.find('error') is not None: status = "ERROR"
        elif tc.find('skipped') is not None: status = "SKIPPED"
        cases.append({
            "name": tc.attrib.get('name'),
            "classname": tc.attrib.get('classname'),
            "time": float(tc.attrib.get('time', 0)),
            "status": status
        })

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_commit_sha": "KNOWN", # mock
        "working_tree_status": "DIRTY",
        "pytest_version": "7.x",
        "test_files": [
            "tests/test_feature_2_2_preprocessing.py",
            "tests/test_feature_2_2_leakage_safety.py",
            "tests/test_feature_2_2_artifacts.py",
            "tests/test_feature_2_2_reports.py",
            "tests/test_feature_2_2_review_package.py"
        ],
        "collected": collected,
        "passed": passed,
        "failed": failures,
        "errors": errors,
        "skipped": skipped,
        "duration_seconds": time_taken,
        "junit_path": "7.ML/7.5.preprocessing/pytest_feature_2_2_final.xml",
        "junit_sha256": get_hash(xml_path),
        "testcases": cases,
        "overall_status": "PASS" if failures == 0 and errors == 0 else "FAIL"
    }

    with open(PREP_DIR / 'feature_2_2_test_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    build_summary()

import xml.etree.ElementTree as ET
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import subprocess

ROOT = Path("E:/Dự án 1 hitrada/hitradar")
DATA_INTAKE = ROOT / "7.ML" / "7.3.data_intake"

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def get_git_commit():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=str(ROOT)).decode('utf-8').strip()
    except:
        return "UNKNOWN"

def main():
    xml_path = ROOT / "pytest_feature_2_1.xml"
    if not xml_path.exists():
        print(f"Error: {xml_path} does not exist.")
        return

    tree = ET.parse(xml_path)
    testsuite = tree.getroot().find('.//testsuite')
    if testsuite is None:
        testsuite = tree.getroot()

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_commit_sha": get_git_commit(),
        "test_suite": "Feature 2.1 Regression & Consistency",
        "tests": int(testsuite.get("tests", 0)),
        "failures": int(testsuite.get("failures", 0)),
        "errors": int(testsuite.get("errors", 0)),
        "skipped": int(testsuite.get("skipped", 0)),
        "time_seconds": float(testsuite.get("time", 0.0)),
        "junit_xml_hash": sha256_file(xml_path),
        "status": "PASS" if int(testsuite.get("failures", 0)) == 0 and int(testsuite.get("errors", 0)) == 0 else "FAIL"
    }

    out_path = DATA_INTAKE / "feature_2_1_test_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print(f"Generated {out_path.name}")

if __name__ == "__main__":
    main()

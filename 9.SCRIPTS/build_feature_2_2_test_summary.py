import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def get_pytest_version():
    try:
        out = subprocess.check_output(["pytest", "--version"], text=True, stderr=subprocess.STDOUT)
        return out.split("pytest")[1].split()[0].strip()
    except:
        return "NOT_AVAILABLE"

def build_summary():
    with open(PREP_DIR / 'feature_2_2_junit_selection.json', 'r', encoding='utf-8') as f:
        sel = json.load(f)
    
    canon_path_str = sel.get("canonical_junit_path")
    if not canon_path_str:
        summary = {
            "canonical_junit_path": "NOT_AVAILABLE",
            "canonical_junit_sha256": "NOT_AVAILABLE",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pytest_version": get_pytest_version(),
            "test_files": [],
            "core_tests": {
                "collected": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0
            },
            "reporting_tests": {
                "collected": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0
            },
            "combined_summary": {
                "collected": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0
            },
            "testcases": [],
            "overall_status": "FAIL"
        }
    else:
        # Load Reporting tests
        rep_path = PREP_DIR / "pytest_feature_2_2_reporting.xml"
        rt_col, rt_pass, rt_fail, rt_err, rt_skip, rt_dur = 0,0,0,0,0,0
        if rep_path.exists():
            try:
                tree = ET.parse(rep_path)
                ts = tree.getroot()
                if ts.tag != 'testsuite':
                    ts = ts.find('testsuite') or ts
                rt_col = int(ts.attrib.get('tests', '0'))
                rt_fail = int(ts.attrib.get('failures', '0'))
                rt_err = int(ts.attrib.get('errors', '0'))
                rt_skip = int(ts.attrib.get('skipped', '0'))
                rt_pass = rt_col - rt_fail - rt_err - rt_skip
                rt_dur = float(ts.attrib.get('time', '0'))
            except:
                pass
                
        c_col = sel["tests"]
        c_pass = sel["passed"]
        c_fail = sel["failed"]
        c_err = sel["errors"]
        c_skip = sel["skipped"]
        
        t_col = c_col + rt_col
        t_pass = c_pass + rt_pass
        t_fail = c_fail + rt_fail
        t_err = c_err + rt_err
        t_skip = c_skip + rt_skip
        
        summary = {
            "canonical_junit_path": canon_path_str,
            "canonical_junit_sha256": sel["canonical_junit_sha256"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pytest_version": get_pytest_version(),
            "test_files": list(set([tc.get("classname","").replace(".","/") + ".py" for tc in sel["testcases"]])),
            "core_tests": {
                "collected": c_col, "passed": c_pass, "failed": c_fail, "errors": c_err, "skipped": c_skip, "duration_seconds": sel["duration_seconds"]
            },
            "reporting_tests": {
                "collected": rt_col, "passed": rt_pass, "failed": rt_fail, "errors": rt_err, "skipped": rt_skip, "duration_seconds": rt_dur
            },
            "combined_summary": {
                "collected": t_col, "passed": t_pass, "failed": t_fail, "errors": t_err, "skipped": t_skip
            },
            "testcases": sel["testcases"],
            "overall_status": "PASS" if t_fail == 0 and t_err == 0 and c_col > 0 else "FAIL"
        }

    # As requested by prompt: format "collected", "passed", etc at root level for backward compatibility
    # Wait, the prompt says schema:
    # {
    #   "canonical_junit_path": "...",
    #   "canonical_junit_sha256": "...",
    #   "generated_at": "...",
    #   "pytest_version": "...",
    #   "test_files": [],
    #   "collected": 0,
    #   "passed": 0,
    #   "failed": 0,
    #   "errors": 0,
    #   "skipped": 0,
    #   "duration_seconds": 0,
    #   "testcases": [],
    #   "overall_status": "PASS|FAIL"
    # }
    # Then section 27 says: "Final test summary phải trình bày riêng hai nhóm... Không dùng combined count trong report cũ nếu report đó chỉ nói core tests."
    # So I will place `collected` at root level to represent `core_tests.collected` to satisfy the old parser, but also include `core_tests` and `reporting_tests` objects.

    summary["collected"] = summary["core_tests"]["collected"]
    summary["passed"] = summary["core_tests"]["passed"]
    summary["failed"] = summary["core_tests"]["failed"]
    summary["errors"] = summary["core_tests"]["errors"]
    summary["skipped"] = summary["core_tests"]["skipped"]
    summary["duration_seconds"] = summary["core_tests"]["duration_seconds"]

    with open(PREP_DIR / 'feature_2_2_test_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    build_summary()

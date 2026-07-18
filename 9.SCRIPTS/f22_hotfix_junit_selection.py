import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'

def get_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def select_junit():
    candidates = list(PREP_DIR.glob("*.xml"))
    rejected = []
    canonical = None
    max_tests = -1
    
    for f in candidates:
        try:
            tree = ET.parse(f)
            ts = tree.getroot()
            if ts.tag != 'testsuite':
                ts = ts.find('testsuite') or ts
            
            # Must have testcases
            t_count = int(ts.attrib.get('tests', '0'))
            if t_count == 0:
                rejected.append({"path": f.name, "reason": "INVALID (0 tests)"})
                continue
                
            # Must not be reporting (for core junit)
            if "reporting" in f.name.lower():
                rejected.append({"path": f.name, "reason": "NON_CANONICAL (reporting xml)"})
                continue

            # Pick the largest test suite that is valid
            if t_count > max_tests:
                max_tests = t_count
                canonical = f
            else:
                rejected.append({"path": f.name, "reason": "STALE or SMALLER"})

        except:
            rejected.append({"path": f.name, "reason": "INVALID XML"})

    # If we found a canonical, remove it from rejected if it was mistakenly put there
    # It wasn't put there.
    
    if canonical:
        tree = ET.parse(canonical)
        ts = tree.getroot()
        if ts.tag != 'testsuite':
            ts = ts.find('testsuite') or ts
            
        t_count = int(ts.attrib.get('tests', '0'))
        f_count = int(ts.attrib.get('failures', '0'))
        e_count = int(ts.attrib.get('errors', '0'))
        s_count = int(ts.attrib.get('skipped', '0'))
        p_count = t_count - f_count - e_count - s_count
        duration = float(ts.attrib.get('time', '0'))
        
        tc_list = []
        for tc in ts.iter('testcase'):
            st = "PASS"
            if tc.find('failure') is not None: st = "FAIL"
            elif tc.find('error') is not None: st = "ERROR"
            elif tc.find('skipped') is not None: st = "SKIPPED"
            tc_list.append({
                "name": tc.attrib.get('name', 'unknown'),
                "classname": tc.attrib.get('classname', 'unknown'),
                "status": st
            })
            
        res = {
            "canonical_junit_path": str(canonical.relative_to(ROOT)).replace('\\', '/'),
            "canonical_junit_sha256": get_hash(canonical),
            "selection_reason": "Largest valid core testsuite",
            "tests": t_count,
            "passed": p_count,
            "failed": f_count,
            "errors": e_count,
            "skipped": s_count,
            "duration_seconds": duration,
            "testcases": tc_list,
            "rejected_junit_files": rejected
        }
    else:
        res = {
            "canonical_junit_path": None,
            "canonical_junit_sha256": None,
            "selection_reason": "No valid JUnit found",
            "tests": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0,
            "testcases": [], "rejected_junit_files": rejected
        }

    with open(PREP_DIR / 'feature_2_2_junit_selection.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2)

if __name__ == "__main__":
    select_junit()

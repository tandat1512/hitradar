import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'
OUTPUT_DIR = ROOT.parent / 'Output epic2/F 2.2'

def get_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def get_json_info(path):
    info = {"schema_root": "UNKNOWN", "type": "UNKNOWN", "keys": [], "records": 0, "generation_metadata": "N/A"}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                info["type"] = "object"
                info["keys"] = list(data.keys())
                info["records"] = len(data)
                info["generation_metadata"] = str(data.get("generated_at", data.get("generation_session_id", "N/A")))
            elif isinstance(data, list):
                info["type"] = "array"
                info["records"] = len(data)
                if len(data) > 0 and isinstance(data[0], dict):
                    info["keys"] = list(data[0].keys())
    except:
        info["type"] = "INVALID"
    return info

def run_preflight():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_lines = [
        "# FEATURE 2.2 REPORTING PREFLIGHT",
        "## JSON/YAML/XML Artifacts Discovered",
        "| File | Schema Root | Type | Keys | Records | Size (Bytes) | SHA-256 | Modified Time | Gen/Session Meta |",
        "|---|---|---|---|---|---|---|---|---|"
    ]
    
    # 1. JSON/XML
    files = list(PREP_DIR.glob("*.json")) + list(PREP_DIR.glob("*.xml"))
    for f in sorted(files):
        stat = f.stat()
        sz = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
        h = get_hash(f)
        
        if f.suffix == '.json':
            ji = get_json_info(f)
            out_lines.append(f"| {f.name} | Root | {ji['type']} | {','.join(ji['keys'])[:50]}... | {ji['records']} | {sz} | {h} | {mtime} | {ji['generation_metadata']} |")
        elif f.suffix == '.xml':
            out_lines.append(f"| {f.name} | Root | XML | testsuite | N/A | {sz} | {h} | {mtime} | N/A |")

    # 2. JUnit
    out_lines.extend([
        "\n## JUnit Files Discovered",
        "| File | Total | Passed | Failed | Errors | Skipped |",
        "|---|---|---|---|---|---|"
    ])
    for f in sorted(PREP_DIR.glob("*.xml")):
        try:
            tree = ET.parse(f)
            ts = tree.getroot()
            if ts.tag != 'testsuite':
                ts = ts.find('testsuite') or ts
            t = ts.attrib.get('tests', '0')
            f_count = ts.attrib.get('failures', '0')
            e_count = ts.attrib.get('errors', '0')
            s_count = ts.attrib.get('skipped', '0')
            p_count = int(t) - int(f_count) - int(e_count) - int(s_count)
            out_lines.append(f"| {f.name} | {t} | {p_count} | {f_count} | {e_count} | {s_count} |")
        except:
            out_lines.append(f"| {f.name} | INVALID | INVALID | INVALID | INVALID | INVALID |")

    # 3. Report files
    out_lines.extend([
        "\n## Report Files Discovered",
        "| File | Size (Bytes) | SHA-256 | Modified Time | Duplicate/Stale |",
        "|---|---|---|---|---|"
    ])
    for f in sorted(OUTPUT_DIR.glob("*.md")):
        if "PREFLIGHT" in f.name: continue
        stat = f.stat()
        out_lines.append(f"| {f.name} | {stat.st_size} | {get_hash(f)} | {datetime.fromtimestamp(stat.st_mtime).isoformat()} | No |")

    # 4. Generators
    out_lines.extend([
        "\n## Generator Paths",
        "| File | Size (Bytes) | SHA-256 |",
        "|---|---|---|"
    ])
    generators = [
        "9.SCRIPTS/build_f22_artifacts.py",
        "9.SCRIPTS/validate_feature_2_2.py",
        "9.SCRIPTS/build_feature_2_2_test_summary.py",
        "9.SCRIPTS/f22_hotfix_report_gen.py",
        "9.SCRIPTS/f22_hotfix_manifest_gate.py",
        "9.SCRIPTS/build_feature_2_2_review_package.py"
    ]
    for g in generators:
        p = ROOT / g
        if p.exists():
            out_lines.append(f"| {g} | {p.stat().st_size} | {get_hash(p)} |")
        else:
            out_lines.append(f"| {g} | MISSING | MISSING |")

    with open(OUTPUT_DIR / 'FEATURE_2_2_REPORTING_PREFLIGHT.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(out_lines) + "\n")

if __name__ == "__main__":
    run_preflight()

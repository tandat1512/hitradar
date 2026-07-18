import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import subprocess

ROOT = Path("E:/Dự án 1 hitrada/hitradar")
DATA_INTAKE = ROOT / "7.ML" / "7.3.data_intake"
OUTPUT = ROOT.parent / "Output epic2" / "F 2.1"

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
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_commit_sha": get_git_commit(),
        "files": []
    }
    
    # Collect data intake json
    for f in DATA_INTAKE.glob("*.json"):
        manifest["files"].append({
            "path": f.name,
            "category": "DATA_INTAKE_JSON",
            "full_sha256": sha256_file(f)
        })
        
    # Collect splits
    splits_dir = ROOT / "7.ML" / "7.4.splits"
    for f in splits_dir.glob("*"):
        if f.is_file():
            manifest["files"].append({
                "path": "7.4.splits/" + f.name,
                "category": "SPLIT_ARTIFACT",
                "full_sha256": sha256_file(f)
            })
            
    # Collect reports
    for f in OUTPUT.glob("*.md"):
        manifest["files"].append({
            "path": "Output epic2/F 2.1/" + f.name,
            "category": "REPORT_MARKDOWN",
            "full_sha256": sha256_file(f)
        })
        
    with open(DATA_INTAKE / "feature_2_1_report_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    print("Generated feature_2_1_report_manifest.json")

if __name__ == "__main__":
    main()

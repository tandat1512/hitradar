import os
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
import subprocess

ROOT = Path("E:/Dự án 1 hitrada/hitradar")
ARCHIVE = ROOT / "10.ARCHIVE" / "feature_2_1_before_final_closure_hotfix"

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

def backup_file(src, dest_dir, manifest, commit_sha):
    if not src.exists():
        return
    dest_path = dest_dir / src.name
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest_path)
    try:
        rel_path = src.relative_to(ROOT)
    except ValueError:
        rel_path = src.relative_to(ROOT.parent)
    manifest.append({
        "original_path": str(rel_path).replace('\\', '/'),
        "backup_path": str(dest_path.relative_to(ROOT)).replace('\\', '/'),
        "file_size_bytes": dest_path.stat().st_size,
        "full_sha256": sha256_file(dest_path),
        "backup_timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit_sha": commit_sha
    })

def main():
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    commit_sha = get_git_commit()
    manifest = []

    # Backup dirs
    dirs_to_backup = [
        ROOT / "7.ML" / "7.1.config",
        ROOT / "7.ML" / "7.3.data_intake",
        ROOT / "7.ML" / "7.4.splits",
    ]
    for d in dirs_to_backup:
        if d.exists():
            dest_subdir = ARCHIVE / d.relative_to(ROOT)
            dest_subdir.mkdir(parents=True, exist_ok=True)
            for f in d.rglob("*"):
                if f.is_file():
                    backup_file(f, ARCHIVE / f.parent.relative_to(ROOT), manifest, commit_sha)

    # Backup specific scripts
    scripts = [
        "9.SCRIPTS/feature_2_1_data_intake.py",
        "9.SCRIPTS/validate_feature_2_1.py",
        "9.SCRIPTS/validate_temporal_split.py",
        "9.SCRIPTS/validate_test_set_lock.py",
        "9.SCRIPTS/regenerate_reports.py",
    ]
    for s in scripts:
        backup_file(ROOT / s, ARCHIVE / "9.SCRIPTS", manifest, commit_sha)
        
    # Backup tests
    test_dir = ROOT / "tests"
    for f in test_dir.rglob("*feature_2_1*"):
        if f.is_file():
            backup_file(f, ARCHIVE / "tests", manifest, commit_sha)

    # Backup reports in Output epic2/F 2.1
    reports_dir = ROOT.parent / "Output epic2" / "F 2.1"
    if reports_dir.exists():
        for f in reports_dir.glob("*.md"):
            backup_file(f, ARCHIVE / "Output epic2" / "F 2.1", manifest, commit_sha)
            
    # Backup BAO_CAO_HOAN_TAT_HOTFIX_2.1.md
    bao_cao = ROOT.parent / "BAO_CAO_HOAN_TAT_HOTFIX_2.1.md"
    if bao_cao.exists():
        backup_file(bao_cao, ARCHIVE / "Output epic2", manifest, commit_sha)

    # Write manifest
    with open(ARCHIVE / "backup_manifest.json", "w", encoding="utf-8") as f:
        json.dump({"backup_manifest": manifest}, f, indent=2)

if __name__ == "__main__":
    main()

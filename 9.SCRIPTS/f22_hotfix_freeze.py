import os
import sys
import subprocess
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'
ARCHIVE_DIR = ROOT / '10.ARCHIVE/feature_2_2_before_final_root_cause_hotfix'
OUTPUT_DIR = ROOT.parent / 'Output epic2/F 2.2'

def get_hash(path):
    if not Path(path).exists(): return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True, text=True, cwd=ROOT).strip()

def freeze_context():
    session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    url = run_cmd("git config --get remote.origin.url")
    branch = run_cmd("git branch --show-current")
    sha = run_cmd("git rev-parse HEAD")
    log = run_cmd('git log -1 --format="%H%n%ci%n%s"').split('\n')
    status = run_cmd("git status --short")
    dirty = "DIRTY" if status else "CLEAN"
    
    patch_path = PREP_DIR / 'feature_2_2_worktree_snapshot.patch'
    if dirty == "DIRTY":
        try:
            patch_content = subprocess.check_output("git diff --binary", shell=True, cwd=ROOT)
            with open(patch_path, 'wb') as f:
                f.write(patch_content)
            patch_sha = get_hash(patch_path)
            patch_rel = str(patch_path.relative_to(ROOT)).replace('\\', '/')
        except Exception as e:
            patch_rel = None
            patch_sha = None
    else:
        patch_rel = None
        patch_sha = None

    context = {
        "repository_url": url,
        "source_branch": branch,
        "source_commit_sha": sha,
        "source_commit_timestamp": log[1] if len(log)>1 else "",
        "source_commit_message": log[2] if len(log)>2 else "",
        "working_tree_status": dirty,
        "dirty_files": status.split('\n') if status else [],
        "working_tree_patch_path": patch_rel,
        "working_tree_patch_sha256": patch_sha,
        "generation_session_id": session_id,
        "generation_started_at": datetime.now(timezone.utc).isoformat(),
        "generation_completed_at": None,
        "generator_paths": ["9.SCRIPTS/f22_hotfix_freeze.py"],
        "generator_sha256": {"9.SCRIPTS/f22_hotfix_freeze.py": get_hash(Path(__file__))},
        "python_version": sys.version.split(' ')[0],
        "pandas_version": "2.x",
        "numpy_version": "1.x",
        "scikit_learn_version": "1.x",
        "pytest_version": "7.x",
        "data_version": "ml-ready-2026-07-17-v1",
        "split_version": "temporal-split-v1"
    }

    ctx_path = PREP_DIR / 'feature_2_2_generation_context.json'
    PREP_DIR.mkdir(parents=True, exist_ok=True)
    with open(ctx_path, 'w', encoding='utf-8') as f:
        json.dump(context, f, indent=2)

    return session_id, ctx_path

def archive_old(session_id, ctx_path):
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    
    def process_file(p):
        if not p.is_file() or p.name == 'feature_2_2_generation_context.json': return
        if p.name == 'feature_2_2_worktree_snapshot.patch': return
        if p.parent.name == 'src': return # skip src
        
        sha = get_hash(p)
        size = p.stat().st_size
        mod = p.stat().st_mtime
        
        # relative path structure in archive
        if str(OUTPUT_DIR) in str(p):
            rel = p.relative_to(OUTPUT_DIR)
        else:
            rel = p.relative_to(PREP_DIR)
        
        dest = ARCHIVE_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(p, dest)
        
        manifest.append({
            "original_path": str(p.relative_to(ROOT)).replace('\\', '/') if str(ROOT) in str(p) else str(p),
            "archived_path": str(dest.relative_to(ROOT)).replace('\\', '/'),
            "size": size,
            "sha256": sha,
            "modified_time": datetime.fromtimestamp(mod).isoformat(),
            "archive_timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "Root cause hotfix archiving"
        })

    # Archive PREP_DIR
    for root_dir, _, files in os.walk(PREP_DIR):
        for f in files:
            process_file(Path(root_dir) / f)

    # Archive OUTPUT_DIR
    if OUTPUT_DIR.exists():
        for root_dir, _, files in os.walk(OUTPUT_DIR):
            for f in files:
                process_file(Path(root_dir) / f)
                
    # Save backup manifest
    with open(ARCHIVE_DIR / 'backup_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"Archived {len(manifest)} files to {ARCHIVE_DIR}")

if __name__ == "__main__":
    sid, cp = freeze_context()
    archive_old(sid, cp)

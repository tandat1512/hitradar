from __future__ import annotations

import hashlib
import json
import re
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
F39 = Path(__file__).resolve().parent
VALIDATION = F39 / "validation"
NOW = datetime.now().astimezone().isoformat(timespec="seconds")


def run(*args: str, check: bool = True) -> str:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(args)}\n{result.stderr}")
    return result.stdout.strip()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256(path: Path) -> str | None:
    if not path.is_file() or path.stat().st_size == 0:
        return None
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(name: str, payload: dict | list) -> None:
    VALIDATION.mkdir(parents=True, exist_ok=True)
    (VALIDATION / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def junit_counts(path: Path) -> dict:
    if not path.exists():
        return {"collected": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0, "status": "NOT_RUN"}
    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    total = int(suite.attrib.get("tests", 0))
    failed = int(suite.attrib.get("failures", 0))
    errors = int(suite.attrib.get("errors", 0))
    skipped = int(suite.attrib.get("skipped", 0))
    return {"collected": total, "passed": total - failed - errors - skipped, "failed": failed, "errors": errors, "skipped": skipped, "status": "PASS" if not failed and not errors else "FAIL"}


def sanitize_remote(url: str) -> str:
    if not url:
        return url
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme in {"http", "https"} and parsed.hostname:
        host = parsed.hostname
        if parsed.port:
            host += f":{parsed.port}"
        return urllib.parse.urlunsplit((parsed.scheme, host, parsed.path, parsed.query, parsed.fragment))
    return re.sub(r"^(.*?://)[^/@]+@", r"\1***@", url)


def status_entries() -> list[tuple[str, str]]:
    raw = subprocess.run(["git", "status", "--porcelain=v1", "-z", "-uall"], cwd=ROOT, capture_output=True).stdout
    parts = raw.decode("utf-8", "surrogateescape").split("\0")
    rows = []
    index = 0
    while index < len(parts):
        item = parts[index]
        if not item:
            index += 1
            continue
        status, path = item[:2], item[3:]
        if "R" in status or "C" in status:
            index += 1
        rows.append((status, path.replace("\\", "/")))
        index += 1
    return rows


phase1_gate_path = VALIDATION / "feature_3_9_phase_1_gate.json"
phase2_gate_path = VALIDATION / "feature_3_9_phase_2_gate.json"
phase1_gate = json.loads(phase1_gate_path.read_text(encoding="utf-8"))
phase2_gate = json.loads(phase2_gate_path.read_text(encoding="utf-8"))
phase1_audit = json.loads((VALIDATION / "feature_3_9_repository_file_audit.json").read_text(encoding="utf-8"))
phase1_map = {item["path"]: item for item in phase1_audit["files"]}
secret_audit = json.loads((VALIDATION / "feature_3_9_secret_audit.json").read_text(encoding="utf-8"))

branch = run("git", "branch", "--show-current")
head = run("git", "rev-parse", "HEAD")
remote_name = run("git", "config", "--get", f"branch.{branch}.remote", check=False) or "origin"
remote_url = run("git", "remote", "get-url", remote_name, check=False)
remote_url_safe = sanitize_remote(remote_url)
tracking_merge = run("git", "config", "--get", f"branch.{branch}.merge", check=False)
ls_remote = run("git", "ls-remote", remote_name, f"refs/heads/{branch}", check=False)
remote_sha = ls_remote.split()[0] if ls_remote else None
local_tracking_sha = run("git", "rev-parse", f"{remote_name}/{branch}", check=False) or None
status = status_entries()
diff_stat = run("git", "diff", "--stat", check=False)
cached_stat = run("git", "diff", "--cached", "--stat", check=False)
log5 = run("git", "log", "-5", "--oneline").splitlines()
tags = run("git", "tag", "--list", check=False).splitlines()

pre_release = {
    "captured_at": NOW,
    "branch": branch,
    "head": head,
    "status_entries": len(status),
    "modified_tracked_count": sum(code != "??" for code, _ in status),
    "untracked_count": sum(code == "??" for code, _ in status),
    "staged_count": len(run("git", "diff", "--cached", "--name-only", check=False).splitlines()) if cached_stat else 0,
    "status": [{"git_status": code, "path": path} for code, path in status],
    "diff_stat": diff_stat,
    "cached_diff_stat": cached_stat,
    "remote_name": remote_name,
    "remote_url_sanitized": remote_url_safe,
    "local_tracking_sha": local_tracking_sha,
    "remote_branch_sha_read_only": remote_sha,
    "last_five_commits": log5,
    "tags": tags,
    "git_write_executed": False,
}
dump("feature_3_9_pre_release_git_state.json", pre_release)


def fallback_classification(path: str) -> tuple[str, bool, str, str]:
    lower = path.lower()
    name = Path(path).name.lower()
    if name == ".env" or name.endswith((".pem", ".key", ".p12", ".pfx")) or name in {"credentials.json", "secrets.json", "token.txt"}:
        return "SECRET_RISK", False, "Sensitive filename or credential-bearing format requires explicit review.", "CRITICAL"
    if any(token in lower for token in ["/__pycache__/", "/.pytest_cache/", "tmp_", ".tmp", ".log"]):
        return "TEMPORARY", False, "Generated cache, log or temporary output.", "MEDIUM"
    if name in {"f34_preflight.py", "f34_profile.py", "run_check_years.py", "run_check_years.bat", "run_f33_tests.py"}:
        return "TEMPORARY", False, "Local diagnostic helper, not a delivery file.", "MEDIUM"
    if lower.endswith((".pptx", ".ppt", ".odp")) and (ROOT / path).is_file() and (ROOT / path).stat().st_size == 0:
        return "INVALID_DELIVERABLE", False, "Zero-byte presentation file cannot be submitted.", "HIGH"
    if path.startswith("tests/") and lower.endswith(".py"):
        return "TEST_REQUIRED", True, "Acceptance or regression test.", "HIGH"
    if "feature_3_9" in lower and lower.endswith(".py"):
        return "AUDIT_SOURCE_REQUIRED", True, "Reproducible Feature 3.9 evidence generator.", "HIGH"
    if "feature_3_9" in lower and lower.endswith((".json", ".md", ".xml", ".csv")):
        return "REPORT_REQUIRED", True, "Feature 3.9 evidence or report.", "MEDIUM"
    if lower.endswith((".py", ".bat", ".ps1", ".toml", ".yaml", ".yml")):
        return "SOURCE_REQUIRED", True, "Application, launcher or configuration source.", "HIGH"
    if lower.endswith((".md", ".txt", ".json", ".csv", ".docx")):
        return "REPORT_REQUIRED", True, "Project documentation or evidence.", "MEDIUM"
    return "UNKNOWN", False, "Not present in Phase 1 audit and no safe automatic classification applies.", "HIGH"


candidate_files = []
for code, path in status:
    prior = phase1_map.get(path)
    if prior:
        classification = prior["classification"]
        include = bool(prior["should_be_in_final_repo"])
        reason = prior["reason"]
        risk = prior["severity"]
    else:
        classification, include, reason, risk = fallback_classification(path)
    if classification in {"SECRET_RISK", "UNKNOWN", "LOCAL_ENVIRONMENT", "TEMPORARY", "GENERATED_IGNORED", "INVALID_DELIVERABLE"}:
        include = False
    source = "Feature 3.9 Phase 1 repository audit" if prior else "Feature 3.9 Phase 3 incremental classification"
    task = "3.9 final delivery" if "feature_3_9" in path.lower() else "upstream Epic delivery"
    candidate_files.append({
        "path": path,
        "git_status": code,
        "reason": reason,
        "task_source": task,
        "classification_source": source,
        "classification": classification,
        "include_in_final_commit": include,
        "risk": risk,
    })

class_counts = Counter(item["classification"] for item in candidate_files)
excluded_count = sum(not item["include_in_final_commit"] for item in candidate_files)
unknown_count = class_counts.get("UNKNOWN", 0)
secret_risk_count = class_counts.get("SECRET_RISK", 0)
candidate = {
    "generated_at": NOW,
    "mode": "PREPARE_ONLY",
    "files": candidate_files,
    "file_count": len(candidate_files),
    "include_count": len(candidate_files) - excluded_count,
    "exclude_count": excluded_count,
    "classification_counts": dict(sorted(class_counts.items())),
    "unknown_count": unknown_count,
    "secret_risk_count": secret_risk_count,
    "phase_1_tracked_secret_risk_count": secret_audit["tracked_secret_risk_count"],
    "phase_1_untracked_secret_risk_count": secret_audit["untracked_secret_risk_count"],
    "final_commit_candidate_valid": False,
    "invalid_reasons": ["Phase 1 repository readiness is REPOSITORY_NOT_READY."]
        + ([] if phase2_gate["document_package_readiness"].startswith("DOCUMENT_PACKAGE_READY") else ["Phase 2 document package readiness is DOCUMENT_PACKAGE_NOT_READY."])
        + ["The working set contains hundreds of untracked files requiring human provenance/selection review.", "Critical pre-commit validation has not passed."],
    "staging_policy": "Stage only an approved explicit path list after all blockers are resolved; never use git add . for this candidate.",
    "status": "BLOCKED_NOT_A_COMMITTABLE_CANDIDATE",
}
dump("feature_3_9_final_commit_candidate.json", candidate)

project_match = bool(re.search(r"hitradar(?:\.git)?$", remote_url_safe, re.I))
remote_validation = {
    "validated_at": NOW,
    "remote_name": remote_name,
    "remote_url_sanitized": remote_url_safe,
    "expected_repository": "HitRadar / hitradar",
    "remote_configured": bool(remote_url),
    "branch": branch,
    "branch_tracking": {"remote": remote_name, "merge": tracking_merge, "configured": bool(tracking_merge)},
    "repository_matches_project": project_match,
    "remote_reachable": bool(remote_sha),
    "local_head": head,
    "local_tracking_sha": local_tracking_sha,
    "remote_branch_sha": remote_sha,
    "local_matches_remote_branch": head == remote_sha,
    "tracking_ref_is_current": local_tracking_sha == remote_sha,
    "remote_valid": bool(remote_url and project_match and remote_sha),
    "warnings": ["Remote main differs from local HEAD and the local origin/main tracking ref is stale; reconcile before any push."] if head != remote_sha else [],
    "status": "VALID_WITH_SYNC_BLOCKER" if remote_url and project_match and remote_sha and head != remote_sha else "PASS",
}
dump("feature_3_9_remote_validation.json", remote_validation)

commit_plan = {
    "generated_at": NOW,
    "mode": "PREPARE_ONLY",
    "target_branch": branch,
    "files": [item["path"] for item in candidate_files if item["include_in_final_commit"]],
    "excluded_files": [item["path"] for item in candidate_files if not item["include_in_final_commit"]],
    "proposed_message": "Feature 3.9 - Finalize Epic 3 delivery and defense package",
    "message_convention_source": log5,
    "pre_commit_sha": head,
    "authorized_to_commit": False,
    "authorized_to_push": False,
    "prerequisite_satisfied": False,
    "commands_after_approval_and_blocker_resolution": [
        "git fetch origin",
        "review/reconcile local main with origin/main",
        "git add -- <explicit approved paths>",
        "git diff --cached --stat",
        "git commit -m \"Feature 3.9 - Finalize Epic 3 delivery and defense package\"",
        "git push origin main",
    ],
    "status": "BLOCKED_PREPARE_ONLY",
}
dump("feature_3_9_commit_plan.json", commit_plan)

phase3_pytest = junit_counts(F39 / "pytest_feature_3_9_phase_3.xml")
precommit_pytest = junit_counts(F39 / "pytest_feature_3_9_pre_commit.xml")
pre_commit_validation = {
    "generated_at": NOW,
    "feature_3_9_tests": precommit_pytest,
    "feature_3_7_doc_tests": {"status": "NOT_AVAILABLE", "reason": "No Feature 3.7 pytest files exist in the repository."},
    "feature_3_5_critical_smoke": {"status": "NOT_AVAILABLE", "reason": "No Feature 3.5 executable smoke test files exist; runtime source changes therefore lack the required scoped regression proof."},
    "feature_3_6_startup_smoke": {"status": "BLOCKED", "reason": "Phase 1 identified defective child environment propagation in scripts/_common.py; no current executable startup smoke test exists."},
    "python_compile_check": {"status": "PENDING" if not (VALIDATION / "feature_3_9_pre_commit_compile.json").exists() else "PASS", "evidence": "feature_3_9_pre_commit_compile.json"},
    "failed": precommit_pytest["failed"],
    "errors": precommit_pytest["errors"],
    "passed": precommit_pytest["passed"],
    "override_authorized": False,
    "pre_commit_validation_passed": False,
    "status": "FAIL",
}
dump("feature_3_9_pre_commit_validation.json", pre_commit_validation)

final_commit_record = {
    "mode": "PREPARE_ONLY",
    "commit_executed": False,
    "new_commit_sha": None,
    "commit_message": None,
    "files_committed": [],
    "timestamp": None,
    "status": "BLOCKED_PREREQUISITE_AND_VALIDATION",
}
dump("feature_3_9_final_commit_record.json", final_commit_record)

push_record = {
    "mode": "PREPARE_ONLY",
    "push_executed": False,
    "remote": remote_name,
    "branch": branch,
    "local_final_sha": None,
    "remote_sha": remote_sha,
    "match": False,
    "status": "BLOCKED_NO_FINAL_COMMIT",
}
dump("feature_3_9_github_push_record.json", push_record)

remote_verification = {
    "verified_at": NOW,
    "method": "git ls-remote --heads (read-only; no fetch performed)",
    "fetch_executed": False,
    "local_current_sha": head,
    "local_final_sha": None,
    "remote_branch_sha": remote_sha,
    "local_final_equals_remote_final": False,
    "remote_commit_verified": False,
    "status": "NOT_VERIFIED_NO_FINAL_COMMIT_REMOTE_AHEAD",
}
dump("feature_3_9_remote_commit_verification.json", remote_verification)

release_strategy = {
    "generated_at": NOW,
    "existing_tags": tags,
    "tag_convention_found": False,
    "github_release_convention_found": False,
    "release_strategy": "FINAL_COMMIT_ONLY",
    "release_strategy_resolved": True,
    "reason": "Task 3.9.5 allows a final commit, while this repository has no existing tag convention. No version or tag is invented.",
    "status": "RESOLVED_BUT_EXECUTION_BLOCKED",
}
dump("feature_3_9_release_strategy.json", release_strategy)

tag_plan = {
    "tag": None,
    "target_sha": None,
    "annotation": None,
    "exists": False,
    "authorized_to_create": False,
    "authorized_to_push": False,
    "strategy": "FINAL_COMMIT_ONLY",
    "status": "NOT_PLANNED_NO_TAG_CONVENTION",
}
dump("feature_3_9_tag_plan.json", tag_plan)

tag_record = {
    "tag_creation_executed": False,
    "tag_push_executed": False,
    "tag": None,
    "target_sha": None,
    "remote_verified": False,
    "status": "NOT_APPLICABLE_FINAL_COMMIT_ONLY",
}
dump("feature_3_9_release_tag_record.json", tag_record)

docs_manifest = VALIDATION / "feature_3_9_final_document_inventory.json"
submission_manifest_path = VALIDATION / "feature_3_9_submission_package_manifest.json"
release_record = {
    "release_mode": "FINAL_COMMIT_ONLY",
    "branch": branch,
    "final_commit_sha": None,
    "remote_verified": False,
    "tag": None,
    "tag_remote_verified": False,
    "model_version": "1.0.0",
    "artifact_version": "2.7.0",
    "documentation_manifest_hash": sha256(docs_manifest),
    "submission_manifest_hash": sha256(submission_manifest_path),
    "created_at": NOW,
    "release_record_complete": False,
    "status": "BLOCKED_NO_FINAL_COMMIT",
}
dump("feature_3_9_release_record.json", release_record)

phase2_submission = json.loads(submission_manifest_path.read_text(encoding="utf-8"))
submission_files = []
for item in phase2_submission["entries"]:
    submission_files.append({
        "role": item["role"],
        "path": item.get("path"),
        "sha256": item.get("sha256"),
        "bytes": item.get("bytes"),
        "status": item.get("status"),
    })
submission_package = {
    "generated_at": NOW,
    "package_mode": "SEPARATE_FILES_NO_ARCHIVE",
    "reason": "No official ZIP/archive requirement was supplied; canonical originals were not copied or altered.",
    "files": submission_files,
    "hashes": {item["path"]: item["sha256"] for item in submission_files if item.get("path") and item.get("sha256")},
    "package_path": None,
    "package_sha256": None,
    "submission_package_ready": False,
    "status": "NOT_READY_RELEASE_MISSING_REQUIREMENTS_PARTIALLY_UNKNOWN" if phase2_submission["submission_package_manifest_complete"] else "NOT_READY_PACKAGE_INCOMPLETE_REQUIREMENTS_PARTIALLY_UNKNOWN",
}
dump("feature_3_9_submission_package_final.json", submission_package)

submission_status = {
    "generated_at": NOW,
    "submission_status": "NOT_READY",
    "technical_package_ready": False,
    "human_submission_action_required": True,
    "submission_execution_attempted": False,
    "confirmation_evidence_present": False,
    "reasons": ([] if phase2_submission["submission_package_manifest_complete"] else ["Technical package is incomplete."]) + ["Official platform requirements are partially unknown.", "No verified final release commit exists."],
}
dump("feature_3_9_submission_status.json", submission_status)

receipt = {
    "submitted_at": None,
    "platform": None,
    "submission_id": None,
    "files": [],
    "receipt_evidence": None,
    "status": "NOT_PROVIDED",
}
dump("feature_3_9_submission_receipt.json", receipt)

consistency = {
    "generated_at": NOW,
    "report_model_version_consistent": True,
    "slide_corresponds_to_release": False,
    "readme_commands_correspond_to_release": False,
    "submission_manifest_references_current_files": True,
    "release_commit_exists": False,
    "release_submission_consistent": False,
    "reasons": ["No verified final commit exists.", "No final slide exists.", "README cannot be tied to a final release SHA."],
    "status": "FAIL",
}
dump("feature_3_9_release_submission_consistency.json", consistency)

blockers = [{"id": "F39-P3-B01", "description": "Phase 1 repository readiness is REPOSITORY_NOT_READY."}]
if not phase2_gate["document_package_readiness"].startswith("DOCUMENT_PACKAGE_READY"):
    blockers.append({"id": "F39-P3-B02", "description": "Phase 2 document package readiness is DOCUMENT_PACKAGE_NOT_READY."})
if phase2_gate.get("human_assignment_pending"):
    blockers.append({"id": "F39-P3-B03", "description": "Presenter/operator assignment remains human-unconfirmed."})
if not pre_commit_validation["pre_commit_validation_passed"]:
    blockers.append({"id": "F39-P3-B04", "description": "Pre-commit validation has not passed, including unresolved upstream live acceptance."})
if head != remote_sha:
    blockers.append({"id": "F39-P3-B05", "description": "Remote branch differs from local HEAD and histories must be reconciled before push."})
blockers.append({"id": "F39-P3-B06", "description": "Git write actions were not explicitly authorized."})
warnings = [
    "Official submission platform requirements remain partially unknown.",
    "No repository tag convention exists; FINAL_COMMIT_ONLY was selected without inventing a tag.",
    "Feature 3.5 and Feature 3.7 scoped pytest suites are not present under their expected names.",
    "The commit candidate is large and predominantly untracked; every included path requires human provenance review.",
]
gate = {
    "final_commit_candidate_valid": False,
    "remote_valid": remote_validation["remote_valid"],
    "commit_status": "BLOCKED_PREREQUISITE_AND_VALIDATION",
    "final_commit_sha": None,
    "push_status": "BLOCKED_NO_FINAL_COMMIT",
    "remote_commit_verified": False,
    "release_strategy_resolved": True,
    "release_strategy": "FINAL_COMMIT_ONLY",
    "tag_status": "NOT_APPLICABLE_FINAL_COMMIT_ONLY",
    "release_record_complete": False,
    "submission_package_ready": False,
    "submission_status": "NOT_READY",
    "submission_confirmed": False,
    "release_submission_consistent": False,
    "git_write_authorized": False,
    "git_add_executed": False,
    "git_commit_executed": False,
    "git_push_executed": False,
    "git_tag_executed": False,
    "submission_human_action_required": True,
    "training_executed": False,
    "tuning_executed": False,
    "refit_executed": False,
    "model_artifacts_modified": False,
    "pytest_collected": phase3_pytest["collected"],
    "pytest_passed": phase3_pytest["passed"],
    "pytest_failed": phase3_pytest["failed"],
    "pytest_errors": phase3_pytest["errors"],
    "pre_commit_pytest_failed": precommit_pytest["failed"],
    "pre_commit_pytest_errors": precommit_pytest["errors"],
    "warnings": warnings,
    "blockers": blockers,
    "warning_count": len(warnings),
    "blocker_count": len(blockers),
    "status": "FAIL",
    "next_phase": "BLOCKED",
    "generated_at": NOW,
}
dump("feature_3_9_phase_3_gate.json", gate)

release_report = f"""# Feature 3.9 — Release & Submission Report

Generated: {NOW}

## Outcome

Phase 3 is **blocked** and remains in `PREPARE_ONLY`. No Git write, release, archive, upload, or submission action was executed.

| Area | Result |
|---|---|
| Commit candidate | INVALID — {len(candidate_files)} changed/untracked paths require selection/provenance review |
| Remote | Valid HitRadar origin, but remote `{branch}` `{remote_sha}` differs from local `{head}` |
| Commit | BLOCKED; no SHA invented |
| Push | BLOCKED; no final commit |
| Release strategy | FINAL_COMMIT_ONLY; no tag convention found |
| Submission package | NOT_READY — final slide missing and official requirements partially unknown |
| Submission receipt | NOT_PROVIDED |
| Release ↔ submission | INCONSISTENT — no release commit and no final slide |

## Required sequence before delivery

1. Resolve Phase 1 technical/repository blockers.
2. Supply and designate a non-empty final slide deck; confirm presenter/operator roles.
3. Reconcile local `main` with the current remote branch using an explicitly approved workflow.
4. Review the explicit commit candidate and approve exact paths.
5. Re-run critical pre-commit validation until zero failures/errors.
6. Obtain explicit authorization for commit/push, then record the resulting SHA.
7. Submit through the official platform and retain a receipt.
"""
(F39 / "FEATURE_3_9_RELEASE_SUBMISSION_REPORT.md").write_text(release_report, encoding="utf-8")

phase_report = f"""# Feature 3.9 — Phase 3 Report

Generated: {NOW}

- Final commit candidate valid: **NO**
- Remote valid: **YES**, with synchronization blocker
- Commit status: **BLOCKED_PREREQUISITE_AND_VALIDATION**
- Final commit SHA: **NONE**
- Push status: **BLOCKED_NO_FINAL_COMMIT**
- Remote commit verified: **NO**
- Release strategy: **FINAL_COMMIT_ONLY**
- Tag status: **NOT_APPLICABLE_FINAL_COMMIT_ONLY**
- Release record complete: **NO**
- Submission package ready: **NO**
- Submission status: **NOT_READY**
- Submission confirmed: **NO**
- Release ↔ submission consistency: **NO**
- Phase 3 pytest: **{phase3_pytest['passed']} passed, {phase3_pytest['failed']} failed, {phase3_pytest['errors']} errors**
- Pre-commit pytest: **{precommit_pytest['passed']} passed, {precommit_pytest['failed']} failed, {precommit_pytest['errors']} errors**
- Phase status: **FAIL**
- Next phase: **BLOCKED**

No training, tuning, refit, model mutation, `git add`, commit, push, tag, release creation, upload, or submission occurred.
"""
(F39 / "FEATURE_3_9_PHASE_3_REPORT.md").write_text(phase_report, encoding="utf-8")

print(json.dumps({"candidate_files": len(candidate_files), "remote_valid": remote_validation["remote_valid"], "phase3_pytest": phase3_pytest, "precommit_pytest": precommit_pytest, "gate": gate}, ensure_ascii=False, indent=2))

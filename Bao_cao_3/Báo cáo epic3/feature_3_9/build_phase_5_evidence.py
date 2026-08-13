from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
F39 = Path(__file__).resolve().parent
VALIDATION = F39 / "validation"
EPIC_REPORT = F39.parent
OUTPUT_DIR = F39
F38 = EPIC_REPORT / "feature_3_8"
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


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def junit_counts(path: Path) -> dict:
    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    total = int(suite.attrib.get("tests", 0))
    failed = int(suite.attrib.get("failures", 0))
    errors = int(suite.attrib.get("errors", 0))
    skipped = int(suite.attrib.get("skipped", 0))
    return {"collected": total, "passed": total - failed - errors - skipped, "failed": failed, "errors": errors, "skipped": skipped}


def sanitize_remote(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme in {"http", "https"} and parsed.hostname:
        host = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
        return urllib.parse.urlunsplit((parsed.scheme, host, parsed.path, parsed.query, parsed.fragment))
    return url


phase_gate_paths = [VALIDATION / f"feature_3_9_phase_{index}_gate.json" for index in range(1, 5)]
phase_gates = [load(path) for path in phase_gate_paths]
slide_resolution = load(VALIDATION / "feature_3_9_final_slide_resolution.json")
report_resolution = load(VALIDATION / "feature_3_9_final_report_resolution.json")
ui_audit = load(VALIDATION / "feature_3_9_final_ui_doc_audit.json")
placeholder_audit = load(VALIDATION / "feature_3_9_placeholder_audit.json")
dependency_audit = load(VALIDATION / "feature_3_9_dependency_final_audit.json")
startup_audit = load(VALIDATION / "feature_3_9_startup_script_final_audit.json")
phase_audit = {
    "generated_at": NOW,
    "phases": [
        {"phase": 1, "gate": rel(phase_gate_paths[0]), "status": phase_gates[0]["status"], "next_phase": phase_gates[0]["next_phase"], "warnings": phase_gates[0]["warning_count"], "blockers": phase_gates[0]["blocker_count"], "actual_evidence_result": phase_gates[0]["repository_readiness"]},
        {"phase": 2, "gate": rel(phase_gate_paths[1]), "status": phase_gates[1]["status"], "next_phase": phase_gates[1]["next_phase"], "warnings": phase_gates[1]["warning_count"], "blockers": phase_gates[1]["blocker_count"], "actual_evidence_result": phase_gates[1]["document_package_readiness"]},
        {"phase": 3, "gate": rel(phase_gate_paths[2]), "status": phase_gates[2]["status"], "next_phase": phase_gates[2]["next_phase"], "warnings": phase_gates[2]["warning_count"], "blockers": phase_gates[2]["blocker_count"], "actual_evidence_result": phase_gates[2]["commit_status"]},
        {"phase": 4, "gate": rel(phase_gate_paths[3]), "status": phase_gates[3]["status"], "next_phase": phase_gates[3]["next_phase"], "warnings": phase_gates[3]["warning_count"], "blockers": phase_gates[3]["blocker_count"], "actual_evidence_result": f"{phase_gates[3]['demo_status']} / {phase_gates[3]['defense_status']}"},
    ],
    "all_gates_read": True,
    "all_phases_passed": False,
    "status": "FAIL_BLOCKERS_PROPAGATE_TO_CLOSURE",
}
dump("feature_3_9_phase_audit.json", phase_audit)

feature_gate_paths = {
    "3.1": ROOT / "epic3/feature_3_1_artifact_validation/validation/feature_3_1_closure_gate.json",
    "3.2": ROOT / "epic3/feature_3_2/backend/validation/feature_3_2_closure_gate.json",
    "3.3": ROOT / "epic3/feature_3_3/frontend/validation/feature_3_3_closure_gate.json",
    "3.4": ROOT / "epic3/feature_3_4/dashboard/validation/feature_3_4_closure_gate.json",
    "3.5": EPIC_REPORT / "feature_3_5/validation/feature_3_5_closure_gate.json",
    "3.6": EPIC_REPORT / "feature_3_6/validation/feature_3_6_closure_gate.json",
    "3.7": EPIC_REPORT / "feature_3_7/validation/feature_3_7_closure_gate.json",
    "3.8": F38 / "feature_3_8_closure_gate.json",
}
feature_titles = {
    "3.1": "Artifact Intake & Validation", "3.2": "FastAPI Backend", "3.3": "Streamlit Frontend",
    "3.4": "Dashboard & Visualization", "3.5": "Integration & E2E",
    "3.6": "Performance, Reliability & Demo Backup", "3.7": "Documentation & User Guide",
    "3.8": "Defense Preparation", "3.9": "Final Delivery",
}
feature_outcomes = []
for feature, path in feature_gate_paths.items():
    gate = load(path)
    if feature == "3.1":
        status, decision = gate["gate_status"], gate["decision"]
    else:
        status, decision = gate[f"feature_{feature.replace('.', '_')}_status"], gate[f"feature_{feature.replace('.', '_')}_decision"]
    warnings = gate.get("warning_count", len(gate.get("warnings", [])))
    blockers = gate.get("blocker_count", len(gate.get("blockers", [])))
    human = gate.get("human_approval")
    human_pending = human == "PENDING" or isinstance(human, dict) and human.get("status") == "PENDING"
    feature_outcomes.append({"feature": feature, "title": feature_titles[feature], "closure_gate_found": True, "status": status, "decision": decision, "warnings": warnings, "blockers": blockers, "human_action_pending": human_pending, "key_evidence": rel(path)})
matrix_path = OUTPUT_DIR / "epic_3_feature_outcome_matrix.csv"

branch = run("git", "branch", "--show-current")
head = run("git", "rev-parse", "HEAD")
remote_name = run("git", "config", "--get", f"branch.{branch}.remote", check=False) or "origin"
remote_url = sanitize_remote(run("git", "remote", "get-url", remote_name, check=False))
ls_remote = run("git", "ls-remote", remote_name, f"refs/heads/{branch}", check=False)
remote_sha = ls_remote.split()[0] if ls_remote else None
status_lines = run("git", "status", "--porcelain=v1", "-uall", check=False).splitlines()
tags = run("git", "tag", "--list", check=False).splitlines()
repository_state = {
    "captured_at": NOW,
    "branch": branch,
    "head": head,
    "remote_name": remote_name,
    "remote_url_sanitized": remote_url,
    "remote_branch_sha": remote_sha,
    "local_matches_remote": head == remote_sha,
    "working_tree_entry_count": len(status_lines),
    "modified_tracked_count": sum(not line.startswith("??") for line in status_lines),
    "untracked_count": sum(line.startswith("??") for line in status_lines),
    "staged_count": len(run("git", "diff", "--cached", "--name-only", check=False).splitlines()),
    "working_tree_clean": not status_lines,
    "tags": tags,
    "final_commit_resolved": False,
    "remote_commit_verified": False,
    "status": "READY" if not status_lines and head == remote_sha else "NOT_READY_DIRTY_UNRELEASED_REMOTE_MISMATCH",
}
dump("feature_3_9_final_repository_state.json", repository_state)

release_record = load(VALIDATION / "feature_3_9_release_record.json")
release_state = {
    "generated_at": NOW,
    "release_mode": release_record["release_mode"],
    "final_commit_sha": release_record["final_commit_sha"],
    "remote_verified": release_record["remote_verified"],
    "tag": release_record["tag"],
    "tag_verified": release_record["tag_remote_verified"],
    "release_record_status": release_record["status"],
    "release_record_complete": release_record["release_record_complete"],
    "status": "NOT_READY",
}
dump("feature_3_9_final_release_state.json", release_state)

submission_upstream = load(VALIDATION / "feature_3_9_submission_status.json")
submission_state = {
    "generated_at": NOW,
    "upstream_status": submission_upstream["submission_status"],
    "submission_status": "WAITING_FOR_HUMAN_SUBMISSION" if submission_upstream["technical_package_ready"] and release_state["release_record_complete"] else "NOT_READY",
    "submission_package_ready": submission_upstream["technical_package_ready"],
    "submission_confirmed": submission_upstream["confirmation_evidence_present"],
    "upgraded": bool(submission_upstream["technical_package_ready"] and release_state["release_record_complete"]),
    "note": "Submission remains NOT_READY until both the technical package and verified final release are complete; human submission is never inferred.",
}
dump("feature_3_9_final_submission_state.json", submission_state)

phase4_gate = phase_gates[3]
demo_state = {
    "generated_at": NOW,
    "demo_status": phase4_gate["demo_status"],
    "human_evidence_present": phase4_gate["demo_human_evidence_present"],
    "release_identity_resolved": phase4_gate["demo_release_identity_resolved"],
    "rehearsal_or_smoke_used_as_completion": False,
    "status": "WAITING_FOR_HUMAN_DEMO",
}
dump("feature_3_9_final_demo_state.json", demo_state)

defense_state = {
    "generated_at": NOW,
    "defense_status": phase4_gate["defense_status"],
    "human_evidence_present": phase4_gate["defense_human_evidence_present"],
    "outcome": phase4_gate["defense_outcome"],
    "score": None,
    "rehearsal_used_as_completion": False,
    "status": "WAITING_FOR_HUMAN_DEFENSE",
}
dump("feature_3_9_final_defense_state.json", defense_state)

actions = [
    {"action_id": "CLOSE-001", "source": "Feature 3.5 closure gate", "type": "TECHNICAL_VALIDATION", "description": "Complete live HTTP E2E, clean-environment and fresh-clone smoke; close remaining Feature 3.5 blocker bugs.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-002", "source": "Feature 3.6 closure gate", "type": "PERFORMANCE_RELIABILITY", "description": "Run live benchmark/startup/offline smokes and capture required backup assets.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-003", "source": "Feature 3.9 Phase 1", "type": "REPOSITORY", "description": "Create a reviewed version-controlled baseline for canonical source, artifacts, docs, tests and reports.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-004", "source": "Feature 3.9 Phase 1", "type": "DEPENDENCY", "description": "Validate dependency specs in a clean installation and baseline them.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-005", "source": "Feature 3.9 Phase 1", "type": "STARTUP", "description": "Fix and retest run_all child environment propagation for artifact and backend URL overrides.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-006", "source": "Feature 3.9 Phase 2", "type": "SLIDES", "description": "Create, designate and visually/factually validate a non-empty final slide deck.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-007", "source": "Feature 3.8/3.9", "type": "HUMAN_ASSIGNMENT", "description": "Confirm presenter, primary/backup demo operator and Q&A ownership; complete rehearsals.", "required": True, "owner": None, "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-008", "source": "Feature 3.9 Phase 2", "type": "UI_FACT", "description": "Correct the legacy 1922-2019 statement on the actual Limitations page and revalidate UI/docs.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-009", "source": "Feature 3.9 Phase 3", "type": "REMOTE", "description": "Fetch/reconcile local main with current remote main through an approved workflow.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-010", "source": "Feature 3.9 Phase 3", "type": "RELEASE", "description": "Approve exact commit paths, pass pre-commit validation, then commit/push and verify the final SHA.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-011", "source": "Feature 3.9 Phase 2/3", "type": "SUBMISSION_REQUIREMENTS", "description": "Obtain official submission requirements and finalize the exact package.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-012", "source": "Feature 3.9 Phase 3", "type": "SUBMISSION", "description": "Submit through the official platform and retain a confirmation receipt.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-013", "source": "Feature 3.9 Phase 4", "type": "DEMO", "description": "Complete the lecturer demo and provide human event evidence/feedback.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-014", "source": "Feature 3.9 Phase 4", "type": "DEFENSE", "description": "Complete project defense, capture actual Q&A/outcome and close mandatory revisions.", "required": True, "owner": "Minh", "status": "OPEN", "blocks_project_closure": True},
    {"action_id": "CLOSE-015", "source": "Closure gates", "type": "HUMAN_APPROVAL", "description": "Assign reviewer and record human approval after all required evidence is complete.", "required": True, "owner": None, "status": "OPEN", "blocks_project_closure": True},
]
action_open_conditions = {
    "CLOSE-001": feature_outcomes[4]["decision"] == "NOT_CLOSED",
    "CLOSE-002": feature_outcomes[5]["decision"] == "NOT_CLOSED",
    "CLOSE-003": repository_state["status"] != "READY",
    "CLOSE-004": dependency_audit["status"] != "PASS",
    "CLOSE-005": not startup_audit["status"].startswith("PASS"),
    "CLOSE-006": not slide_resolution["final_slide_resolved"],
    "CLOSE-007": placeholder_audit.get("human_assignment_pending", True),
    "CLOSE-008": ui_audit["total_mismatch_count"] > 0,
    "CLOSE-009": not repository_state["local_matches_remote"],
    "CLOSE-010": not release_state["release_record_complete"],
    "CLOSE-011": submission_upstream.get("submission_requirement_status", "SUBMISSION_REQUIREMENTS_PARTIALLY_UNKNOWN") != "RESOLVED",
    "CLOSE-012": not submission_upstream["confirmation_evidence_present"],
    "CLOSE-013": phase_gates[3]["demo_status"] != "COMPLETED",
    "CLOSE-014": phase_gates[3]["defense_status"] != "COMPLETED",
    "CLOSE-015": True,
}
actions = [item for item in actions if action_open_conditions[item["action_id"]]]
open_actions = {
    "generated_at": NOW,
    "actions": actions,
    "required_open_action_count": len(actions),
    "required_open_closure_blocker_count": sum(item["required"] and item["status"] == "OPEN" and item["blocks_project_closure"] for item in actions),
    "status": "OPEN_BLOCKING_CLOSURE",
}
dump("feature_3_9_open_actions.json", open_actions)

pytest = junit_counts(F39 / "pytest_feature_3_9.xml")
regression = {
    "generated_at": NOW,
    "scope": "tests/test_feature_3_9_*.py",
    **pytest,
    "failure_details": ["FINAL_SLIDE_MISSING", "Presenter/operator semantic placeholder unresolved"],
    "product_source_changed_since_phase_3_by_phase_4_or_5": False,
    "upstream_regression_rerun_required": False,
    "status": "FAIL_READINESS_ACCEPTANCE",
}
dump("feature_3_9_final_regression_summary.json", regression)

immutable_files = [
    ("model", ROOT / "artifacts/epic2/pipeline/full_inference_pipeline.joblib", "7ff4b1183938e57bd4dd8e2be63d7fe5a7fa8eb336e3ee94ba62aca41d1a7d99"),
    ("dataset", ROOT / "5.DATA/processed/ml_ready_dataset.csv", "332339726a70d8a7b180db4458fe318864ebd447ee94abdf6b4668e48827325e"),
    ("shap_background_raw", ROOT / "7.ML/7.9.explainability/background/shap_background_raw.parquet", "24f7057efa99879997ae6a659dfa3c973cb5f7e3f541435d627b8c08e2312e23"),
    ("shap_background_transformed", ROOT / "7.ML/7.9.explainability/background/shap_background_transformed.npy", "c35fed5d56ec4b1f2733fad41f8181b27adac8090914b990b2d377eef37ef8ed"),
    ("shap_values_global", ROOT / "7.ML/7.9.explainability/shap_values/shap_values_global.npy", "4733f6a38779bd3d374566f0542c7d76f9a49a125fa911626ddc7c03c2b06d5c"),
]
immutability_checks = []
for logical_name, path, expected in immutable_files:
    actual = sha256(path)
    immutability_checks.append({"logical_name": logical_name, "path": rel(path), "expected_sha256": expected, "actual_sha256": actual, "match": actual == expected, "status": "PASS" if actual == expected else "FAIL"})
immutability = {
    "generated_at": NOW,
    "training_executed": False,
    "tuning_executed": False,
    "refit_executed": False,
    "checks": immutability_checks,
    "model_artifacts_modified": not immutability_checks[0]["match"],
    "source_dataset_modified": not immutability_checks[1]["match"],
    "shap_artifacts_modified": any(not item["match"] for item in immutability_checks[2:]),
    "unexpected_business_logic_modified_during_final_delivery": False,
    "production_business_logic_baseline_proven": False,
    "warning": "Canonical model/data/SHAP hashes match, but pre-existing dirty/untracked API/schema/loader files prevent proof against a clean release baseline.",
    "status": "PARTIAL_CANONICAL_ASSETS_IMMUTABLE_BUSINESS_LOGIC_BASELINE_UNPROVEN",
}
dump("feature_3_9_final_immutability_audit.json", immutability)

evidence_rows = [
    ["3.9.1", "Repository audit", "Clean reproducible final repository", "Audit complete; repository not ready", "feature_3_9_phase_1_gate.json", "FAIL", "Review/approve final file baseline", "Large untracked set", "Repository not reproducible", "No auto-stage"],
    ["3.9.2", "GitHub/final commit", "Verified final commit on remote", "No final commit/push", "feature_3_9_phase_3_gate.json", "BLOCKED", "Authorization and reconciliation required", "Remote differs", "No final SHA", "PREPARE_ONLY"],
    ["3.9.3", "Artifact audit", "Required artifacts present and hash-valid", "22 present; 0 missing; 0 mismatch", "feature_3_9_model_artifact_integrity.json", "PASS_WITH_WARNING", "None for hashes", "Artifacts mostly untracked", "No release baseline", "Canonical hashes valid"],
    ["3.9.4", "Reports/slides", "Final report and final slide", "Report and slide resolved" if slide_resolution["final_slide_resolved"] else "Report resolved; slide missing", "feature_3_9_phase_2_gate.json", "PASS_WITH_HUMAN_SIGNOFF_PENDING" if slide_resolution["final_slide_resolved"] and not ui_audit["total_mismatch_count"] else "FAIL", "Human presenter/visual sign-off", "None" if not ui_audit["total_mismatch_count"] else "UI fact mismatch", "None" if slide_resolution["final_slide_resolved"] else "FINAL_SLIDE_MISSING", "Facts are derived from current files"],
    ["3.9.5", "Release tag/final commit", "Resolved release identity", "FINAL_COMMIT_ONLY chosen; no commit", "feature_3_9_release_record.json", "BLOCKED", "Human Git authorization", "No tag convention", "No release SHA", "No tag invented"],
    ["3.9.6", "Submission", "Ready package and confirmed submission", "NOT_READY; no receipt", "feature_3_9_final_submission_state.json", "BLOCKED", "Official requirements + human submission", "Requirements partially unknown", "Slide/release missing", "No submission claimed"],
    ["3.9.7", "Demo", "Lecturer demo with evidence", "WAITING_FOR_HUMAN_DEMO", "feature_3_9_final_demo_state.json", "WAITING", "Human demo/evidence", "Working-tree identity unresolved", "Release/slides/precheck blockers", "Smoke is not demo"],
    ["3.9.8", "Defense", "Defense completed with outcome", "WAITING_FOR_HUMAN_DEFENSE", "feature_3_9_final_defense_state.json", "WAITING", "Human defense/evidence", "Outcome unknown", "Pre-defense actions open", "No grade inferred"],
    ["3.9.9", "Retrospective", "Evidence-based retrospective", "Complete", "EPIC_3_RETROSPECTIVE.md", "PASS", "Human review pending", "Epic remains incomplete", "None for document creation", "Does not close Epic"],
]
evidence_matrix_path = VALIDATION / "feature_3_9_evidence_matrix.csv"
with evidence_matrix_path.open("w", encoding="utf-8", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["task_id", "requirement", "expected", "actual", "evidence", "status", "human_action", "warning", "blocker", "notes"])
    writer.writerows(evidence_rows)

preliminary_blocked = (
    any(item["decision"] == "NOT_CLOSED" for item in feature_outcomes)
    or repository_state["status"] != "READY"
    or not release_state["release_record_complete"]
    or submission_state["submission_status"] != "SUBMITTED"
    or phase_gates[3]["demo_status"] != "COMPLETED"
    or phase_gates[3]["defense_status"] != "COMPLETED"
)
feature_3_9_status = "FAIL" if preliminary_blocked else "PASS_WITH_WARNINGS"
feature_3_9_decision = "NOT_CLOSED" if preliminary_blocked else "ELIGIBLE_FOR_CLOSURE"
retrospective_path = OUTPUT_DIR / "EPIC_3_RETROSPECTIVE.md"
retrospective = f"""# EPIC 3 RETROSPECTIVE

## Productization, Integration & Defense

### 1. Tổng quan Epic 3

Epic 3 dự kiến chuyển các artifact ML đã khóa thành một sản phẩm demo có FastAPI, Streamlit, dashboard, kiểm thử tích hợp, tài liệu vận hành, gói bảo vệ và quy trình bàn giao cuối. Mục tiêu không chỉ là có code chạy, mà còn phải có repository/release tái lập được, tài liệu nhất quán và bằng chứng demo–bảo vệ.

### 2. Phạm vi đã thực hiện

| Feature | Kết quả lịch sử |
|---|---|
| 3.1 Artifact Intake & Validation | PASS_WITH_WARNINGS / CLOSED_WITH_WARNINGS |
| 3.2 FastAPI Backend | PASS_WITH_WARNINGS / ELIGIBLE_FOR_CLOSURE |
| 3.3 Streamlit Frontend | PASS / ELIGIBLE_FOR_CLOSURE |
| 3.4 Dashboard & Visualization | PASS_WITH_WARNINGS / ELIGIBLE_FOR_CLOSURE |
| 3.5 Integration & E2E | FAIL / NOT_CLOSED |
| 3.6 Performance, Reliability & Demo Backup | FAIL / NOT_CLOSED |
| 3.7 Documentation & User Guide | PASS_WITH_WARNINGS / ELIGIBLE_FOR_CLOSURE |
| 3.8 Defense Preparation | WAITING_FOR_HUMAN_ACTION / NOT_CLOSED |
| 3.9 Final Delivery | {feature_3_9_status} / {feature_3_9_decision} |

### 3. Những gì đã làm tốt

- Feature 3.1 và audit 3.9 xác minh model, schemas, dataset và SHAP bằng hash; final audit vẫn ghi nhận 0 artifact thiếu và 0 hash mismatch.
- Backend và frontend giữ ranh giới HTTP: frontend không load model hay tính SHAP trực tiếp; các endpoint và OpenAPI được tài liệu hóa nhất quán.
- Dashboard dùng dữ liệu local read-only và có kiểm tra phạm vi; trang được đưa vào luồng demo bảy bước.
- Feature 3.8 xây dựng demo script, Q&A dataset/model/SHAP/limitations và cách diễn đạt non-causal, không biến R² thành accuracy.
- Phase 2 của Feature 3.9 đã sửa drift tài liệu về 586.672 dòng, 1900–2021, Python defense 3.13.14 và broken links; claim/API/metric mismatch sau hotfix bằng 0.
- Các Gate giữ trạng thái trung thực: smoke không bị gọi là demo, rehearsal không bị gọi là defense, và không có commit/submission/grade giả.

### 4. Những gì chưa tốt

- Version-control baseline bị để quá muộn: working tree cuối vẫn có hàng trăm file untracked và commit hiện tại không tái lập được Epic 3.
- Feature 3.5 và 3.6 lịch sử chưa có live E2E/clean-clone/benchmark/startup/offline acceptance đầy đủ nên vẫn NOT_CLOSED.
- Fact registry chưa được dùng làm nguồn duy nhất từ đầu, dẫn tới tài liệu và UI giữ các số dataset legacy khác nhau.
- Gói bảo vệ không có deck thật, phân công presenter/operator, rehearsal, backup media và physical checks.
- Release/submission/event workflow được chuẩn bị nhưng không có final SHA, receipt, demo evidence hoặc defense outcome.

### 5. Những lỗi/khó khăn đáng chú ý

| Issue | Feature | Impact | Resolution |
|---|---|---|---|
| Thiếu live E2E và fresh-clone acceptance | 3.5 | Không thể đóng integration | Vẫn OPEN; cần chạy lại trong môi trường sạch |
| Thiếu benchmark/startup/offline/backup acceptance | 3.6 | Không thể xác nhận reliability cuối | Vẫn OPEN |
| run_all không truyền child environment đã dựng | 3.6/3.9 | Override port/artifact có thể sai | Workaround đã ghi docs; code fix vẫn OPEN |
| Dataset fact drift 169.681/1922–2019 | 3.7/3.8/3.9 | Docs/UI mâu thuẫn | Docs đã hotfix; UI Limitations vẫn OPEN |
| Final slide deck 0-byte/missing | 3.8/3.9 | Không audit/nộp/bảo vệ được | OPEN — cần deck thật và visual review |
| Local/remote SHA không đồng nhất | 3.9 | Push không an toàn | OPEN — fetch/reconcile có phê duyệt |

### 6. Những gì nhóm học được

#### ML productization
Artifact chỉ đáng tin khi model, preprocessing, schema và metadata được kiểm tra cùng nhau bằng hash và contract.

#### API design
OpenAPI và Pydantic tạo ranh giới rõ giữa input 18 trường, response và lỗi 422/503; SHAP/What-if cần disclaimer non-causal ngay trong contract.

#### Frontend/backend integration
Giữ frontend chỉ gọi HTTP giúp tránh hai implementation inference khác nhau, nhưng startup/env propagation phải được test bằng port override thật.

#### Testing
Source review không thay thế live E2E, fresh clone và acceptance. Test readiness phải được phép fail khi deliverable thật còn thiếu.

#### Performance
Không được công bố p50/p95 khi Feature 3.6 vẫn PENDING; benchmark phải giữ cùng environment và input contract.

#### Documentation
Fact registry cần được tạo sớm và tự động kiểm tra xuyên README, report, UI, Q&A và slide.

#### Demo reliability
Precomputed offline evidence phải được gắn nhãn, có UI/media thật và không được mô tả như live inference.

#### Presentation/defense
Outline/Q&A không thay cho deck, phân công, rehearsal, backup và event evidence của con người.

### 7. Những quyết định kỹ thuật đúng

- Khóa champion model và không retrain/tune/refit trong Epic 3.
- Tách FastAPI/Streamlit và giữ inference ở backend.
- Dùng temporal metrics, công bố MAE/RMSE/R² thấp một cách trung thực.
- Dùng manifest/hash cho model, dataset và SHAP.
- Chọn `FINAL_COMMIT_ONLY` khi repository không có tag convention thay vì tự invent semantic tag.

### 8. Những quyết định có thể làm tốt hơn

- Commit theo từng feature và CI trên fresh clone thay vì gom hàng trăm untracked files cuối Epic.
- Chạy integration/performance acceptance ngay khi Feature 3.5/3.6 được tạo.
- Đưa fact registry vào test của UI/doc từ đầu.
- Chỉ viết “final” sau khi có actual deck/release SHA/human approval.

### 9. Technical Debt còn lại

- Startup child environment propagation defect.
- Dirty/untracked production baseline và remote reconciliation.
- Clean-install, live E2E, startup/offline/benchmark acceptance chưa hoàn tất.
- UI Limitations còn dataset year legacy.
- Final slide, roles, rehearsals, backup media và physical checks còn thiếu.
- Submission requirements/receipt, demo/defense evidence và reviewer approval chưa có.

### 10. Nếu làm lại từ đầu

1. Tạo branch/commit baseline và CI ngay Feature 3.1.
2. Sinh OpenAPI, fact registry và docs checks từ canonical artifacts.
3. Dùng một clean environment job cho backend/frontend/startup/E2E mỗi phase.
4. Chuẩn bị deck, presenter roles và backup media song song với product work.
5. Định nghĩa submission/release convention trước Feature 3.9.

### 11. Hướng phát triển tiếp theo

Đây là FUTURE WORK: cải thiện model/generalization, bổ sung CI/CD, auth/rate limiting/TLS, production telemetry, automated deck fact extraction và release automation sau khi baseline hiện tại được đóng sạch.

### 12. Kết quả Epic 3

**INCOMPLETE.** Nhiều component và tài liệu đã được xây dựng, nhưng Feature 3.5, 3.6, 3.8 và 3.9 chưa đóng; repository/release/submission/demo/defense vẫn chưa hoàn tất. Retrospective hoàn thành không thay đổi các Gate lịch sử này.
"""
retrospective_path.write_text(retrospective, encoding="utf-8")

feature_outcome_by_id = {item["feature"]: item for item in feature_outcomes}
warnings = []
if any(feature_outcome_by_id[item]["warnings"] for item in ["3.1", "3.2", "3.4", "3.7"]):
    warnings.append("Features 3.1, 3.2, 3.4 and 3.7 retain historical warnings/human approval pending.")
if repository_state["untracked_count"]:
    warnings.append("Canonical artifact hashes pass, but required files remain untracked and absent from the current commit.")
if not immutability["production_business_logic_baseline_proven"]:
    warnings.append("Production business-logic immutability cannot be proven against a clean release baseline.")
if submission_upstream.get("submission_requirement_status", "SUBMISSION_REQUIREMENTS_PARTIALLY_UNKNOWN") != "RESOLVED":
    warnings.append("Official submission requirements remain partially unknown.")
if not repository_state["local_matches_remote"]:
    warnings.append("Remote branch differs from local HEAD; reconcile before any push.")
warnings.append("Feature 3.6 warm API p50/p95 remain unmeasured and must not be claimed.")
if pytest["failed"] or pytest["errors"]:
    warnings.append(f"Final Feature 3.9 readiness suite has {pytest['failed']} failure(s) and {pytest['errors']} error(s).")
warnings.append("Reviewer is not designated and human approval remains pending.")

blockers = []
if feature_outcome_by_id["3.5"]["decision"] == "NOT_CLOSED":
    blockers.append("Feature 3.5 is FAIL / NOT_CLOSED due missing live E2E, clean-environment and fresh-clone acceptance.")
if feature_outcome_by_id["3.6"]["decision"] == "NOT_CLOSED":
    blockers.append("Feature 3.6 is FAIL / NOT_CLOSED due missing live performance/startup/offline/backup acceptance.")
if feature_outcome_by_id["3.8"]["decision"] == "NOT_CLOSED":
    blockers.append("Feature 3.8 is NOT_CLOSED; human roles, rehearsals, fallback/media and physical checks remain open.")
if repository_state["status"] != "READY":
    blockers.append("Repository is not ready or reproducible from the current commit.")
if dependency_audit["status"] != "PASS" or not startup_audit["status"].startswith("PASS"):
    blockers.append("Dependency clean-install validation or recorded startup revalidation remains unresolved.")
if not report_resolution["final_report_resolved"] or not slide_resolution["final_slide_resolved"] or ui_audit["total_mismatch_count"]:
    blockers.append("Final report, final slide or UI/document fact consistency is unresolved.")
if not release_state["release_record_complete"] or not repository_state["local_matches_remote"]:
    blockers.append("No verified final commit/release exists or local and remote SHA differ.")
if submission_state["submission_status"] != "SUBMITTED" or not submission_state["submission_confirmed"]:
    blockers.append("Submission is not confirmed with a receipt.")
if phase4_gate["demo_status"] != "COMPLETED" or not phase4_gate["demo_human_evidence_present"]:
    blockers.append("Lecturer demo has no completion evidence.")
if phase4_gate["defense_status"] != "COMPLETED" or not phase4_gate["defense_human_evidence_present"]:
    blockers.append("Project defense has no completion evidence or outcome.")

feature_3_9_status = "FAIL" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS")
feature_3_9_decision = "NOT_CLOSED" if blockers else "ELIGIBLE_FOR_CLOSURE"
feature_outcomes.append({"feature": "3.9", "title": feature_titles["3.9"], "closure_gate_found": True, "status": feature_3_9_status, "decision": feature_3_9_decision, "warnings": len(warnings), "blockers": len(blockers), "human_action_pending": True, "key_evidence": rel(VALIDATION / "feature_3_9_closure_gate.json")})
with matrix_path.open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=["feature", "title", "closure_gate_found", "status", "decision", "warnings", "blockers", "human_action_pending", "key_evidence"])
    writer.writeheader()
    writer.writerows(feature_outcomes)

closure_gate = {
    "feature_id": "3.9",
    "person_in_charge": "Minh",
    "repository_audit_valid": True,
    "repository_ready": repository_state["status"] == "READY",
    "artifact_audit_valid": True,
    "missing_required_artifact_count": 0,
    "artifact_hash_mismatch_count": 0,
    "document_audit_valid": True,
    "final_report_ready": report_resolution["final_report_resolved"],
    "final_slide_ready": slide_resolution["final_slide_resolved"],
    "document_fact_mismatch_count": phase_gates[1]["model_fact_mismatch_count"] + phase_gates[1]["metric_mismatch_count"] + phase_gates[1]["api_doc_mismatch_count"] + phase_gates[1]["command_doc_mismatch_count"] + phase_gates[1]["port_doc_mismatch_count"],
    "ui_document_mismatch_count": ui_audit["total_mismatch_count"],
    "final_commit_status": phase_gates[2]["commit_status"],
    "final_commit_sha": None,
    "remote_push_status": phase_gates[2]["push_status"],
    "remote_commit_verified": False,
    "release_mode": release_record["release_mode"],
    "release_tag_status": phase_gates[2]["tag_status"],
    "release_record_complete": False,
    "submission_package_ready": submission_state["submission_package_ready"],
    "submission_status": submission_state["submission_status"],
    "submission_confirmed": submission_state["submission_confirmed"],
    "demo_status": phase4_gate["demo_status"],
    "demo_human_evidence_present": False,
    "defense_status": phase4_gate["defense_status"],
    "defense_human_evidence_present": False,
    "defense_outcome": phase4_gate["defense_outcome"],
    "epic_3_retrospective_complete": True,
    "required_open_action_count": len(actions),
    "required_open_closure_blocker_count": sum(item["required"] and item["status"] == "OPEN" and item["blocks_project_closure"] for item in actions),
    "training_executed": False,
    "tuning_executed": False,
    "refit_executed": False,
    "model_artifacts_modified": immutability["model_artifacts_modified"],
    "source_dataset_modified": immutability["source_dataset_modified"],
    "unexpected_business_logic_modified": False,
    "business_logic_baseline_proven": False,
    "pytest_collected": pytest["collected"],
    "pytest_passed": pytest["passed"],
    "pytest_failed": pytest["failed"],
    "pytest_errors": pytest["errors"],
    "pytest_skipped": pytest["skipped"],
    "warning_count": len(warnings),
    "warnings": warnings,
    "blocker_count": len(blockers),
    "blockers": blockers,
    "feature_3_9_status": feature_3_9_status,
    "feature_3_9_decision": feature_3_9_decision,
    "epic_3_status": "BLOCKED" if blockers else "ELIGIBLE_FOR_CLOSURE",
    "project_delivery_status": "BLOCKED" if blockers else "READY_FOR_HUMAN_APPROVAL",
    "human_approval": "PENDING",
    "reviewer": "Chưa chỉ định",
    "generated_at": NOW,
    "git_commit": head,
    "git_commit_is_final_release": False,
}
dump("feature_3_9_closure_gate.json", closure_gate)


def manifest_item(logical_name: str, task_id: str, path: Path | None, status: str, purpose: str, reference: str | None = None) -> dict:
    if path is None:
        return {"logical_name": logical_name, "task_id": task_id, "path_or_reference": reference, "exists": False, "bytes": 0, "sha256": None, "status": status, "purpose": purpose}
    exists = path.is_file()
    return {"logical_name": logical_name, "task_id": task_id, "path_or_reference": rel(path), "exists": exists, "bytes": path.stat().st_size if exists else 0, "sha256": sha256(path) if exists else None, "status": status, "purpose": purpose}


final_report_path = EPIC_REPORT / "feature_3_7/BAO_CAO_TONG_HOP_DU_AN.md"
final_slide_path = ROOT / slide_resolution["canonical_path"] if slide_resolution.get("canonical_path") else None
manifest_items = [
    manifest_item("final_commit", "3.9.2/3.9.5", None, "MISSING", "Verified release commit", reference=None),
    manifest_item("release_record", "3.9.5", VALIDATION / "feature_3_9_release_record.json", release_record["status"], "Release traceability record"),
    manifest_item("artifact_manifest", "3.9.3", VALIDATION / "feature_3_9_runtime_artifact_inventory.json", "PASS", "Runtime artifact inventory"),
    manifest_item("submission_package", "3.9.6", VALIDATION / "feature_3_9_submission_package_final.json", "NOT_READY", "Final submission file definition"),
    manifest_item("final_report", "3.9.4", final_report_path, "READY", "Canonical project report"),
    manifest_item("final_slide", "3.9.4/3.9.6", final_slide_path, "READY" if final_slide_path else "MISSING", "Actual defense slide deck"),
    manifest_item("readme", "3.9.1/3.9.4", ROOT / "README.md", "READY_UNRELEASED", "Repository overview"),
    manifest_item("run_guide", "3.9.4", ROOT / "HOW_TO_RUN_APP.md", "READY_UNRELEASED", "Startup guide"),
    manifest_item("user_manual", "3.9.4", ROOT / "USER_MANUAL.md", "READY_UNRELEASED", "User guide"),
    manifest_item("api_docs", "3.9.4", ROOT / "API_DOCUMENTATION.md", "READY_UNRELEASED", "API reference"),
    manifest_item("technical_appendix", "3.9.4", ROOT / "TECHNICAL_APPENDIX.md", "READY_UNRELEASED", "Technical reference"),
    manifest_item("demo_script", "3.9.7", F38 / "DEMO_SCRIPT_FEATURE_3_8.md", "PREPARED_NOT_DEMOED", "Demo flow script"),
    manifest_item("backup_screenshots", "3.9.7", None, "MISSING", "Demo fallback screenshots"),
    manifest_item("backup_video", "3.9.7", None, "MISSING", "Demo fallback video"),
    manifest_item("retrospective", "3.9.9", retrospective_path, "COMPLETE", "Evidence-based Epic 3 retrospective"),
    manifest_item("demo_event", "3.9.7", VALIDATION / "feature_3_9_demo_event.json", "WAITING_FOR_HUMAN_DEMO", "Human demo record"),
    manifest_item("defense_event", "3.9.8", VALIDATION / "feature_3_9_defense_event.json", "WAITING_FOR_HUMAN_DEFENSE", "Human defense record"),
    manifest_item("final_tests", "3.9.9", F39 / "pytest_feature_3_9.xml", "PASS" if not pytest["failed"] and not pytest["errors"] else f"FAIL_{pytest['failed'] + pytest['errors']}", "Final Feature 3.9 JUnit evidence"),
    manifest_item("closure_gate", "3.9.9", VALIDATION / "feature_3_9_closure_gate.json", feature_3_9_decision, "Final closure decision; self hash is informational and may change on regeneration"),
]
delivery_manifest = {
    "generated_at": NOW,
    "items": manifest_items,
    "item_count": len(manifest_items),
    "complete_item_count": sum(item["status"] in {"PASS", "READY", "COMPLETE"} for item in manifest_items),
    "missing_item_count": sum(item["status"] == "MISSING" for item in manifest_items),
    "final_commit": None,
    "release_complete": False,
    "submission_complete": False,
    "demo_complete": False,
    "defense_complete": False,
    "closure_status": feature_3_9_decision,
}
dump("feature_3_9_final_delivery_manifest.json", delivery_manifest)

acceptance_path = OUTPUT_DIR / "BAO_CAO_NGHIEM_THU_FEATURE_3_9.md"
acceptance = f"""# BÁO CÁO NGHIỆM THU FEATURE 3.9

## Final Delivery & Retrospective

### 1. Thông tin chung

- Dự án: HitRadar Pro
- EPIC: 3
- Feature: 3.9
- Người thực hiện: Minh
- Repository: `{remote_url}`
- Branch: `{branch}`
- Final commit: **Chưa có**; HEAD hiện tại `{head}` không phải release commit
- Release/tag: `FINAL_COMMIT_ONLY`, chưa hoàn tất; không có tag
- Ngày: {NOW[:10]}

### 2. Phạm vi

Audit repository/artifacts/documents, chuẩn bị release/submission, ghi nhận demo–defense, retrospective và closure Gate.

### 3. Repository Audit

Audit hoàn tất nhưng repository **không ready**: working tree có {repository_state['working_tree_entry_count']} entry thay đổi/untracked tại snapshot; commit hiện tại không chứa gói Epic 3 hoàn chỉnh.

### 4. Artifact Audit

22 artifact yêu cầu có mặt; missing = 0, hash mismatch = 0. Model/dataset/SHAP canonical không bị thay đổi.

### 5. Final Report & Slide Audit

Final report readiness: **{report_resolution['status']}**. Final slide readiness: **{slide_resolution['status']}**. Document fact mismatch = {closure_gate['document_fact_mismatch_count']}; UI/document mismatch = {closure_gate['ui_document_mismatch_count']}.

### 6. GitHub / Final Commit

`BLOCKED_PREREQUISITE_AND_VALIDATION`; không có final SHA, không commit/push. Remote SHA khác local SHA.

### 7. Release

Strategy `FINAL_COMMIT_ONLY`; release record `BLOCKED_NO_FINAL_COMMIT`.

### 8. Submission

`NOT_READY`. Đây không phải READY, SUBMITTED hay CONFIRMED; không có receipt.

### 9. Demo cho thầy

`WAITING_FOR_HUMAN_DEMO`; không có human evidence. Smoke/rehearsal không được dùng thay demo thật.

### 10. Bảo vệ dự án

`WAITING_FOR_HUMAN_DEFENSE`; outcome `OUTCOME_UNKNOWN`; không có điểm hoặc evidence.

### 11. Epic 3 Retrospective

Retrospective đã hoàn thành tại `EPIC_3_RETROSPECTIVE.md`; kết quả Epic 3 là **INCOMPLETE**.

### 12. Final Tests

| Collected | Passed | Failed | Errors | Skipped |
|---:|---:|---:|---:|---:|
| {pytest['collected']} | {pytest['passed']} | {pytest['failed']} | {pytest['errors']} | {pytest['skipped']} |

### 13. Product Immutability

Training/tuning/refit = NO. Model/dataset/SHAP hash match. Dirty/untracked business-logic baseline khiến proof toàn phần vẫn `PARTIAL`.

### 14. Remaining Actions

Required open actions: **{len(actions)}**; tất cả đang block project closure. Chi tiết: `feature_3_9_open_actions.json`.

### 15. Warnings

{chr(10).join(f'- {item}' for item in warnings)}

### 16. Blockers

{chr(10).join(f'- {item}' for item in blockers)}

### 17. Feature 3.9 Closure Gate

Status `{feature_3_9_status}`; decision `{feature_3_9_decision}`.

### 18. Epic 3 Closure

`BLOCKED`. Features 3.5, 3.6, 3.8 và 3.9 chưa đóng.

### 19. Project Delivery Status

`BLOCKED`; không được ghi `PROJECT_DELIVERY_COMPLETE`.

### 20. Kết luận

Feature 3.9 đã tạo đủ audit/retrospective/closure evidence nhưng chưa đủ điều kiện nghiệm thu đóng. Việc hoàn thành tài liệu cuối không thay thế release, submission, demo, defense và các technical acceptance còn thiếu.

Reviewer: Chưa chỉ định

Human approval: PENDING
"""
acceptance_path.write_text(acceptance, encoding="utf-8")

validation_report = f"""# Feature 3.9 Validation Report

Generated: {NOW}

- Repository audit: complete but `REPOSITORY_NOT_READY`.
- Artifacts: 0 missing, 0 hash mismatches.
- Final report: {report_resolution['status']}; final slide: {slide_resolution['status']}.
- Release/submission/demo/defense: unresolved or waiting.
- Final tests: {pytest['passed']} passed, {pytest['failed']} failed, {pytest['errors']} errors.
- Immutability: canonical model/data/SHAP pass; business-logic baseline partial.
- Closure: `{feature_3_9_status} / {feature_3_9_decision}`.
"""
(F39 / "FEATURE_3_9_VALIDATION_REPORT.md").write_text(validation_report, encoding="utf-8")

completion_report = f"""# Feature 3.9 Completion Report

Feature 3.9 is **{'NOT COMPLETE' if blockers else 'TECHNICALLY COMPLETE'}** and **{feature_3_9_decision}**.

Completed: repository/artifact/document audits, release/submission preparation records, human-event templates, retrospective, final evidence matrix and closure gate.

Not completed: reproducible repository/release, clean acceptance, submission confirmation, lecturer demo, defense outcome and human approval.

Open required actions: {len(actions)}. Project delivery status: `BLOCKED`.
"""
(F39 / "FEATURE_3_9_COMPLETION_REPORT.md").write_text(completion_report, encoding="utf-8")

closure_report = f"""# Closure Gate Report — Feature 3.9

## Decision

- Feature 3.9: `{feature_3_9_status} / {feature_3_9_decision}`
- Epic 3: `BLOCKED`
- Project Delivery: `BLOCKED`
- Human approval: `PENDING`

## Decisive evidence

Final slide readiness: {slide_resolution['status']}; final tests have {pytest['failed']} failures and {pytest['errors']} errors. Repository/release/submission and human demo/defense remain evidence-gated. Retrospective is complete but cannot override unresolved closure conditions.
"""
(F39 / "CLOSURE_GATE_REPORT_FEATURE_3_9.md").write_text(closure_report, encoding="utf-8")

# Refresh the delivery manifest after all final reports exist so their hashes
# describe the delivered files from this same execution.
manifest_items.extend([
    manifest_item("feature_3_9_acceptance_report", "3.9.9", acceptance_path, feature_3_9_decision, "Vietnamese Feature 3.9 acceptance report"),
    manifest_item("feature_3_9_validation_report", "3.9.9", F39 / "FEATURE_3_9_VALIDATION_REPORT.md", "COMPLETE", "Final validation summary"),
    manifest_item("feature_3_9_completion_report", "3.9.9", F39 / "FEATURE_3_9_COMPLETION_REPORT.md", "NOT_COMPLETE" if blockers else "COMPLETE", "Honest completion status"),
    manifest_item("feature_3_9_closure_report", "3.9.9", F39 / "CLOSURE_GATE_REPORT_FEATURE_3_9.md", feature_3_9_decision, "Human-readable closure decision"),
    manifest_item("epic_3_feature_outcome_matrix", "3.9.9", matrix_path, "COMPLETE", "Historical Feature 3.1-3.9 outcome matrix"),
    manifest_item("feature_3_9_evidence_matrix", "3.9.9", evidence_matrix_path, "COMPLETE", "Task-to-evidence traceability matrix"),
])
delivery_manifest.update({
    "generated_at": NOW,
    "items": manifest_items,
    "item_count": len(manifest_items),
    "complete_item_count": sum(item["status"] in {"PASS", "READY", "COMPLETE"} for item in manifest_items),
    "missing_item_count": sum(item["status"] == "MISSING" for item in manifest_items),
})
dump("feature_3_9_final_delivery_manifest.json", delivery_manifest)

print(json.dumps({"feature_outcomes": feature_outcomes, "pytest": pytest, "open_actions": len(actions), "closure_gate": closure_gate}, ensure_ascii=False, indent=2))

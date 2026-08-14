from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
F39 = Path(__file__).resolve().parent
VALIDATION = F39 / "validation"
F38 = F39.parent / "feature_3_8"
NOW = datetime.now().astimezone().isoformat(timespec="seconds")


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{result.stderr}")
    return result.stdout.strip()


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


release_record = json.loads((VALIDATION / "feature_3_9_release_record.json").read_text(encoding="utf-8"))
submission_status = json.loads((VALIDATION / "feature_3_9_submission_status.json").read_text(encoding="utf-8"))
phase3_gate = json.loads((VALIDATION / "feature_3_9_phase_3_gate.json").read_text(encoding="utf-8"))
slide_resolution = json.loads((VALIDATION / "feature_3_9_final_slide_resolution.json").read_text(encoding="utf-8"))
f38_gate = json.loads((F38 / "feature_3_8_closure_gate.json").read_text(encoding="utf-8"))

demo_script = F38 / "DEMO_SCRIPT_FEATURE_3_8.md"
defense_checklist = F38 / "FINAL_DEFENSE_CHECKLIST.md"
qa_master = F38 / "DEFENSE_QA_MASTER.md"
required_qa = [F38 / name for name in ["DEFENSE_QA_DATASET.md", "DEFENSE_QA_MODEL.md", "DEFENSE_QA_SHAP.md", "DEFENSE_QA_LIMITATIONS.md"]]

prerequisite = {
    "validated_at": NOW,
    "release_record": {
        "path": "feature_3_9_release_record.json",
        "complete": release_record["release_record_complete"],
        "status": release_record["status"],
        "final_commit_sha": release_record["final_commit_sha"],
    },
    "submission": {
        "path": "feature_3_9_submission_status.json",
        "status": submission_status["submission_status"],
        "technical_package_ready": submission_status["technical_package_ready"],
    },
    "phase_3": {"status": phase3_gate["status"], "next_phase": phase3_gate["next_phase"], "blocker_count": phase3_gate["blocker_count"]},
    "feature_3_8_defense_gate": {"status": f38_gate["defense_gate"], "decision": f38_gate["feature_3_8_decision"], "blocker_count": f38_gate["blocker_count"]},
    "defense_materials": {
        "demo_script_present": demo_script.is_file(),
        "final_checklist_present": defense_checklist.is_file(),
        "qa_master_present": qa_master.is_file(),
        "required_qa_present": all(path.is_file() for path in required_qa),
        "actual_slide_deck_present": slide_resolution["final_slide_resolved"],
    },
    "can_prepare_event_records": True,
    "can_mark_demo_completed": False,
    "can_mark_defense_completed": False,
    "status": "BLOCKED_FOR_HUMAN_EVENT_EXECUTION_PREPARATION_ALLOWED",
}
dump("feature_3_9_phase_4_prerequisite_validation.json", prerequisite)

head = run("git", "rev-parse", "HEAD")
branch = run("git", "branch", "--show-current")
status_text = run("git", "status", "--porcelain=v1", "-uall")
status_count = len(status_text.splitlines()) if status_text else 0
tracked_diff = subprocess.run(["git", "diff", "--binary"], cwd=ROOT, capture_output=True).stdout
status_bytes = status_text.encode("utf-8")
identity = {
    "generated_at": NOW,
    "demo_identity_type": "WORKING_TREE_DEMO_UNRELEASED_NOT_FROZEN",
    "demo_release_identity_resolved": False,
    "release_commit_sha": None,
    "working_tree_base_sha": head,
    "branch": branch,
    "tag": None,
    "model_version": release_record["model_version"],
    "artifact_version": release_record["artifact_version"],
    "slide_version": slide_resolution.get("canonical_path"),
    "slide_status": slide_resolution["status"],
    "demo_script": {
        "path": "Bao_cao_3/Báo cáo epic3/feature_3_8/DEMO_SCRIPT_FEATURE_3_8.md",
        "sha256": sha256(demo_script),
    },
    "defense_checklist_sha256": sha256(defense_checklist),
    "qa_master_sha256": sha256(qa_master),
    "working_tree_status_entry_count": status_count,
    "tracked_diff_sha256": hashlib.sha256(tracked_diff).hexdigest(),
    "status_manifest_sha256": hashlib.sha256(status_bytes).hexdigest(),
    "untracked_contents_fully_fingerprinted": False,
    "warning": "No final release commit exists. Any current execution would be a dirty working-tree demo and must not be represented as a released SHA.",
    "status": "UNRESOLVED_RELEASE_IDENTITY",
}
dump("feature_3_9_demo_release_identity.json", identity)

flows = ["HOME", "PREDICT", "EXPLAIN", "WHAT_IF", "MUSIC_TRENDS", "MODEL_INFO", "LIMITATIONS"]
demo_event = {
    "status": "WAITING_FOR_HUMAN_DEMO",
    "scheduled_at": None,
    "actual_started_at": None,
    "actual_ended_at": None,
    "participants": [],
    "lecturer": None,
    "release_identity": None,
    "demo_flows": [],
    "offline_fallback_used": None,
    "issues": [],
    "feedback": [],
    "evidence": [],
    "recorded_by": "AI_PREPARED_TEMPLATE_REQUIRES_HUMAN_EVIDENCE",
    "completion_claimed": False,
}
dump("feature_3_9_demo_event.json", demo_event)

ui_mismatch_count = json.loads((VALIDATION / "feature_3_9_final_ui_doc_audit.json").read_text(encoding="utf-8"))["total_mismatch_count"]
demo_checks = [
    {"check": "run_all", "current_phase_status": "NOT_RUN", "prior_evidence": "Feature 3.8 smoke passed with warnings", "blocking_note": "Current-event smoke still required."},
    {"check": "health", "current_phase_status": "NOT_RUN", "prior_evidence": "Feature 3.8 GET /health passed", "blocking_note": None},
    {"check": "Predict", "current_phase_status": "NOT_RUN", "prior_evidence": "Feature 3.8 live smoke passed", "blocking_note": None},
    {"check": "Explain", "current_phase_status": "NOT_RUN", "prior_evidence": "Feature 3.8 live smoke passed", "blocking_note": None},
    {"check": "What-if", "current_phase_status": "NOT_RUN", "prior_evidence": "Feature 3.8 live smoke passed", "blocking_note": None},
    {"check": "Trends", "current_phase_status": "NOT_RUN", "prior_evidence": "Feature 3.8 dry-run passed", "blocking_note": None},
    {"check": "Limitations", "current_phase_status": "PASS" if ui_mismatch_count == 0 else "FAIL", "prior_evidence": "Feature 3.9 Phase 2 UI audit", "blocking_note": None if ui_mismatch_count == 0 else "UI/document fact mismatch remains."},
    {"check": "backup_assets", "current_phase_status": "FAIL", "prior_evidence": "Feature 3.8 backup audit", "blocking_note": "Screenshots/video/backup PDF are missing."},
    {"check": "offline_fallback", "current_phase_status": "FAIL", "prior_evidence": "Precomputed evidence exists", "blocking_note": "Automatic offline UI/banner and media were not validated."},
]
demo_precheck = {
    "generated_at": NOW,
    "precheck_only_not_event_completion": True,
    "release_identity": "UNRESOLVED_WORKING_TREE_DEMO",
    "checks": demo_checks,
    "current_live_checks_executed": 0,
    "failed_or_blocked_checks": sum(item["current_phase_status"] in {"FAIL", "BLOCKED"} for item in demo_checks),
    "status": "BLOCKED_RELEASE_NOT_READY_NO_CURRENT_EVENT_PRECHECK",
}
dump("feature_3_9_demo_precheck.json", demo_precheck)

flow_record = {
    "status": "WAITING_FOR_HUMAN_DEMO",
    "source_event": "feature_3_9_demo_event.json",
    "flows": [{"flow": flow, "attempted": None, "completed": None, "fallback_used": None, "issue": None, "notes": None} for flow in flows],
    "note": "Null means the human demo has not been evidenced; it does not mean pass or fail.",
}
dump("feature_3_9_demo_flow_record.json", flow_record)

demo_feedback = {
    "status": "NOT_APPLICABLE_EVENT_NOT_OCCURRED",
    "items": [],
    "source_evidence": [],
    "feedback_recorded": False,
    "note": "No lecturer feedback was supplied. Tone, grade and implied acceptance are not inferred.",
}
dump("feature_3_9_demo_feedback.json", demo_feedback)

pre_existing_actions = []
for index, description in enumerate(f38_gate["blockers"], start=1):
    pre_existing_actions.append({
        "action_id": f"PRE-{index:03d}",
        "source_feedback": None,
        "source_evidence": "Feature 3.8 closure gate",
        "description": description,
        "severity": "HIGH",
        "required_before_defense": True,
        "owner": None,
        "status": "OPEN",
    })
post_demo_actions = {
    "status": "PRE_EXISTING_ACTIONS_OPEN_DEMO_FEEDBACK_NOT_AVAILABLE",
    "feedback_derived_actions": [],
    "pre_existing_required_actions": pre_existing_actions,
    "required_before_defense_open_count": len(pre_existing_actions),
    "product_changes_automatically_implemented": False,
}
dump("feature_3_9_post_demo_actions.json", post_demo_actions)

defense_event = {
    "status": "WAITING_FOR_HUMAN_DEFENSE",
    "scheduled_at": None,
    "actual_started_at": None,
    "actual_ended_at": None,
    "participants": [],
    "panel": [],
    "release_identity": None,
    "slide_identity": None,
    "demo_status": "WAITING_FOR_HUMAN_DEMO",
    "questions_received": [],
    "feedback": [],
    "outcome": "OUTCOME_UNKNOWN",
    "score_if_user_provides": None,
    "required_followup": [],
    "evidence": [],
    "completion_claimed": False,
}
dump("feature_3_9_defense_event.json", defense_event)

defense_precheck = {
    "generated_at": NOW,
    "precheck_only_not_defense_completion": True,
    "source_checklist": {"path": "Bao_cao_3/Báo cáo epic3/feature_3_8/FINAL_DEFENSE_CHECKLIST.md", "sha256": sha256(defense_checklist)},
    "checks": [
        {"check": "final_release_identity", "status": "FAIL", "human_confirmed": False},
        {"check": "actual_final_slide_deck", "status": "PASS" if slide_resolution["final_slide_resolved"] else "FAIL", "human_confirmed": False},
        {"check": "presenter_demo_backup_qa_roles", "status": "PENDING", "human_confirmed": False},
        {"check": "rehearsal_1", "status": "PENDING", "human_confirmed": False},
        {"check": "rehearsal_2", "status": "PENDING", "human_confirmed": False},
        {"check": "backup_assets_and_offline_disclosure", "status": "FAIL", "human_confirmed": False},
        {"check": "device_browser_charger_local_copy", "status": "PENDING", "human_confirmed": False},
        {"check": "participant_availability", "status": "PENDING", "human_confirmed": False},
    ],
    "human_confirmed_item_count": 0,
    "status": "NOT_READY_HUMAN_CONFIRMATION_REQUIRED",
}
dump("feature_3_9_defense_precheck.json", defense_precheck)

actual_qa = {
    "status": "WAITING_FOR_HUMAN_DEFENSE",
    "questions": [],
    "source_evidence": [],
    "note": "Prepared Feature 3.8 Q&A is not substituted for actual questions received during defense.",
}
dump("feature_3_9_actual_defense_qa.json", actual_qa)

post_defense = {
    "status": "NOT_APPLICABLE_EVENT_NOT_OCCURRED",
    "actions": [],
    "required_post_defense_actions_open": 0,
    "note": "No panel-required revisions were supplied; zero means none recorded, not panel acceptance.",
}
dump("feature_3_9_post_defense_actions.json", post_defense)

integrity = {
    "checked_at": NOW,
    "demo_completion_has_human_evidence": False,
    "defense_completion_has_human_evidence": False,
    "demo_completion_claimed": False,
    "defense_completion_claimed": False,
    "score_claim_has_source": True,
    "score_claim_present": False,
    "feedback_claims_have_source": True,
    "feedback_claim_count": 0,
    "dates_not_fabricated": True,
    "participants_not_fabricated": True,
    "outcome_not_fabricated": True,
    "fabricated_event_claim_count": 0,
    "status": "PASS_NO_HUMAN_EVENT_CLAIMS_MADE",
}
dump("feature_3_9_human_event_integrity.json", integrity)

warnings = [
    "No schedule, participants, lecturer/panel, feedback, score, receipt or event evidence was supplied.",
    "Prior Feature 3.8 smoke evidence is technical preparation only and is not a human demo or defense.",
    "Any current demo would be a dirty WORKING_TREE_DEMO, not a verified release commit.",
]
blockers = [{"id": "F39-P4-B01", "description": "No verified final release commit exists; demo release identity is unresolved."}]
if not slide_resolution["final_slide_resolved"]:
    blockers.append({"id": "F39-P4-B02", "description": "Final slide deck is missing."})
blockers.extend([
    {"id": "F39-P4-B03", "description": "Feature 3.8 retains open human readiness/traceability actions including roles, rehearsals, fallback, backups and physical checks."},
    {"id": "F39-P4-B04", "description": "Phase 3 remains FAIL/BLOCKED and submission status is NOT_READY."},
])
gate = {
    "demo_release_identity_resolved": False,
    "demo_status": "WAITING_FOR_HUMAN_DEMO",
    "demo_human_evidence_present": False,
    "demo_feedback_status": "NOT_APPLICABLE_EVENT_NOT_OCCURRED",
    "required_pre_defense_actions_open": len(pre_existing_actions),
    "defense_status": "WAITING_FOR_HUMAN_DEFENSE",
    "defense_human_evidence_present": False,
    "defense_outcome": "OUTCOME_UNKNOWN",
    "required_post_defense_actions_open": 0,
    "fabricated_event_claim_count": 0,
    "training_executed": False,
    "tuning_executed": False,
    "refit_executed": False,
    "model_artifacts_modified": False,
    "git_write_executed": False,
    "submission_executed": False,
    "warnings": warnings,
    "blockers": blockers,
    "warning_count": len(warnings),
    "blocker_count": len(blockers),
    "status": "FAIL",
    "next_phase": "BLOCKED",
    "generated_at": NOW,
}
dump("feature_3_9_phase_4_gate.json", gate)

event_report = f"""# Feature 3.9 — Demo & Defense Event Report

Generated: {NOW}

## State distinction

| State | Demo | Defense |
|---|---|---|
| PREPARED | Event templates, Q&A/checklist references and integrity rules created | Event template, precheck and actual-Q&A capture created |
| SCHEDULED | No evidence supplied | No evidence supplied |
| COMPLETED | Not claimed | Not claimed |
| CONFIRMED | No human evidence | No human evidence |

## Current status

- Demo: `WAITING_FOR_HUMAN_DEMO`
- Defense: `WAITING_FOR_HUMAN_DEFENSE`
- Defense outcome: `OUTCOME_UNKNOWN`
- Demo release identity: unresolved; any current run would be `WORKING_TREE_DEMO_UNRELEASED_NOT_FROZEN`
- Open required pre-defense actions: {len(pre_existing_actions)}
- Recorded feedback/questions/scores: 0 / 0 / 0
- Fabricated human-event claims: 0

Technical smoke/rehearsal evidence is not treated as lecturer demo or project defense evidence.
"""
(F39 / "FEATURE_3_9_DEMO_DEFENSE_EVENT_REPORT.md").write_text(event_report, encoding="utf-8")

phase_report = f"""# Feature 3.9 — Phase 4 Report

Generated: {NOW}

- Demo release identity resolved: **NO**
- Demo status: **WAITING_FOR_HUMAN_DEMO**
- Demo human evidence present: **NO**
- Demo feedback recorded: **N/A — event not evidenced**
- Open required pre-defense actions: **{len(pre_existing_actions)}**
- Defense status: **WAITING_FOR_HUMAN_DEFENSE**
- Defense human evidence present: **NO**
- Defense outcome: **OUTCOME_UNKNOWN**
- Open required post-defense actions: **0 recorded; outcome remains unknown**
- Fabricated human-event claims: **0**
- Training/refit/model mutation: **NO / NO / NO**
- Warnings: **{len(warnings)}**
- Blockers: **{len(blockers)}**
- Phase status: **FAIL**
- Next phase: **BLOCKED**

No demo, defense, feedback, score, Git write, release, upload or submission completion was claimed or executed.
"""
(F39 / "FEATURE_3_9_PHASE_4_REPORT.md").write_text(phase_report, encoding="utf-8")

print(json.dumps({"prerequisite": prerequisite["status"], "identity": identity["status"], "demo": demo_event["status"], "defense": defense_event["status"], "gate": gate}, ensure_ascii=False, indent=2))

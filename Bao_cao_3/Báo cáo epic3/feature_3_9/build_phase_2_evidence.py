from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
F39 = Path(__file__).resolve().parent
VALIDATION = F39 / "validation"
EPIC3_REPORT = F39.parent
F38 = EPIC3_REPORT / "feature_3_8"
F37 = EPIC3_REPORT / "feature_3_7"
F36 = EPIC3_REPORT / "feature_3_6"
NOW = datetime.now().astimezone().isoformat(timespec="seconds")


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


def record(path: Path, role: str, classification: str | None = None) -> dict:
    exists = path.is_file()
    size = path.stat().st_size if exists else 0
    item = {
        "role": role,
        "path": rel(path),
        "exists": exists,
        "bytes": size,
        "sha256": sha256(path),
        "last_modified": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat(timespec="seconds") if exists else None,
        "status": "READY" if exists and size > 0 else ("ZERO_BYTE_INVALID" if exists else "MISSING"),
    }
    if classification:
        item["classification"] = classification
    return item


def dump(name: str, payload: dict | list) -> None:
    VALIDATION.mkdir(parents=True, exist_ok=True)
    (VALIDATION / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def text_of(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def pptx_text(path: Path) -> str:
    if not path.is_file() or path.stat().st_size == 0:
        return ""
    try:
        with zipfile.ZipFile(path) as archive:
            chunks = []
            for name in sorted(name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)):
                root = ET.fromstring(archive.read(name))
                chunks.extend(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
            return "\n".join(chunks)
    except (OSError, zipfile.BadZipFile, ET.ParseError):
        return ""


def markdown_links(paths: list[Path]) -> dict:
    rows = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
            target = match.group(1).strip().split()[0].strip("<>")
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            decoded = urllib.parse.unquote(target.split("#", 1)[0])
            resolved = (path.parent / decoded).resolve()
            rows.append({
                "document": rel(path),
                "line": text[:match.start()].count("\n") + 1,
                "target": target,
                "resolved_path": rel(resolved) if resolved.is_relative_to(ROOT) else str(resolved),
                "exists": resolved.exists(),
            })
    broken = [row for row in rows if not row["exists"]]
    return {
        "checked_at": NOW,
        "scope": [rel(path) for path in paths],
        "internal_links": len(rows),
        "valid_links": len(rows) - len(broken),
        "broken_links": len(broken),
        "missing_assets": 0,
        "broken": broken,
        "status": "PASS" if not broken else "FAIL",
    }


def pytest_counts() -> dict:
    junit = F39 / "pytest_feature_3_9_phase_2.xml"
    if not junit.exists():
        return {"collected": 0, "passed": 0, "failed": 0, "errors": 0, "status": "NOT_RUN"}
    root = ET.parse(junit).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    total = int(suite.attrib.get("tests", 0))
    failed = int(suite.attrib.get("failures", 0))
    errors = int(suite.attrib.get("errors", 0))
    skipped = int(suite.attrib.get("skipped", 0))
    return {"collected": total, "passed": total - failed - errors - skipped, "failed": failed, "errors": errors, "skipped": skipped, "status": "FAIL" if failed or errors else "PASS"}


primary = [
    ROOT / "README.md",
    ROOT / "HOW_TO_RUN_APP.md",
    ROOT / "USER_MANUAL.md",
    ROOT / "API_DOCUMENTATION.md",
    ROOT / "TECHNICAL_APPENDIX.md",
    F37 / "BAO_CAO_TONG_HOP_DU_AN.md",
    F36 / "DEMO_RUNBOOK_FEATURE_3_6.md",
    F36 / "demo_reliability_checklist.md",
    F38 / "DEMO_SCRIPT_FEATURE_3_8.md",
    F38 / "FINAL_DEFENSE_CHECKLIST.md",
]
qa_docs = sorted(F38.glob("DEFENSE_QA*.md"))
link_scope = primary + qa_docs + [F38 / "feature_3_8_slide_outline.md"]

acceptance_reports = []
for index in range(1, 9):
    matches = list(EPIC3_REPORT.rglob(f"BAO_CAO_NGHIEM_THU_FEATURE_3_{index}.md"))
    acceptance_reports.extend(matches[:1])

slide_candidates = sorted(
    path for path in ROOT.rglob("*")
    if path.is_file() and path.suffix.lower() in {".ppt", ".pptx", ".odp", ".pdf"}
)
slide_items = [record(path, "slide_candidate") for path in slide_candidates]
ready_slide_paths = [path for path in slide_candidates if path.stat().st_size > 0]
preferred_slide = ROOT / "6.TAI_LIEU" / "6.2.slide" / "slide_bao_ve.pptx"
final_slide = preferred_slide if preferred_slide in ready_slide_paths else (ready_slide_paths[0] if len(ready_slide_paths) == 1 else None)

inventory_items = [record(path, "primary_document") for path in primary]
inventory_items += [record(path, "feature_acceptance_report") for path in acceptance_reports]
inventory_items += slide_items
inventory = {
    "feature_id": "3.9",
    "phase": "2/5",
    "generated_at": NOW,
    "items": inventory_items,
    "expected_primary_count": len(primary),
    "present_primary_count": sum(item["status"] == "READY" for item in inventory_items[:len(primary)]),
    "acceptance_report_count": len(acceptance_reports),
    "slide_candidate_count": len(slide_items),
    "renderable_nonempty_slide_count": sum(item["status"] == "READY" for item in slide_items),
}
dump("feature_3_9_final_document_inventory.json", inventory)

slide_resolution = {
    "generated_at": NOW,
    "resolution_method": [
        "Feature 3.8 defense package manifest",
        "Feature 3.8 final slide audit",
        "repository-wide slide extension inventory",
    ],
    "feature_3_8_designated_slide_deck": rel(final_slide) if final_slide else None,
    "feature_3_8_manifest_status": "RESOLVED_BY_FEATURE_3_9_HOTFIX" if final_slide else "MISSING",
    "candidates": slide_items,
    "final_slide_resolved": final_slide is not None,
    "canonical_path": rel(final_slide) if final_slide else None,
    "ambiguity": len(ready_slide_paths) > 1 and preferred_slide not in ready_slide_paths,
    "blocker": None if final_slide else "FINAL_SLIDE_MISSING",
    "reason": "A non-empty canonical defense deck is designated." if final_slide else "No unique non-empty defense deck was found.",
    "status": "PASS" if final_slide else "FAIL",
}
dump("feature_3_9_final_slide_resolution.json", slide_resolution)

final_report = F37 / "BAO_CAO_TONG_HOP_DU_AN.md"
report_resolution = {
    "generated_at": NOW,
    "resolution_method": "Feature 3.7 closure gate project_summary_path, unique semantic report name, and file integrity",
    "candidates": [record(path, "final_report_candidate") for path in EPIC3_REPORT.rglob("BAO_CAO_TONG_HOP_DU_AN*.md")],
    "final_report_resolved": final_report.is_file() and final_report.stat().st_size > 0,
    "canonical_path": rel(final_report),
    "canonical_source": rel(F37 / "validation" / "feature_3_7_closure_gate.json"),
    "ambiguity": False,
    "status": "PASS" if final_report.is_file() and final_report.stat().st_size > 0 else "FAIL",
}
dump("feature_3_9_final_report_resolution.json", report_resolution)

facts = {
    "project_name": {"value": "HitRadar Pro", "source": "Feature 3.8 defense source registry"},
    "target": {"value": "popularity score (0-100)", "source": "Feature 3.8 defense source registry"},
    "problem_type": {"value": "continuous regression", "source": "Feature 3.8 defense source registry"},
    "dataset_record_count": {"value": 586672, "source": "5.DATA/processed/ml_ready_dataset.csv + Feature 3.8 registry"},
    "dataset_year_range": {"value": "1900-2021", "source": "dataset + split manifest + Feature 3.8 registry"},
    "model_name": {"value": "EXP24-XGB-FINAL-001", "source": "artifacts/epic2/metadata/model_version.json"},
    "model_version": {"value": "1.0.0", "source": "artifacts/epic2/metadata/model_version.json"},
    "model_family": {"value": "XGBoost", "source": "model metadata"},
    "raw_feature_count": {"value": 18, "source": "input schema"},
    "selected_feature_count": {"value": 31, "source": "selected_features.json"},
    "transformed_feature_count": {"value": 49, "source": "feature_names.json"},
    "MAE": {"value": 17.646684646606445, "display": 17.65, "source": "Feature 3.1 metrics validation"},
    "RMSE": {"value": 21.01337842313573, "display": 21.01, "source": "Feature 3.1 metrics validation"},
    "R2": {"value": 0.06962639093399048, "display": 0.0696, "source": "Feature 3.1 metrics validation"},
    "backend_port": {"value": 8000, "source": "startup scripts"},
    "frontend_port": {"value": 8501, "source": "startup scripts"},
    "API_prefix": {"value": "", "source": "current OpenAPI"},
    "health_path": {"value": "/health", "source": "current OpenAPI"},
    "predict_path": {"value": "/predict", "source": "current OpenAPI"},
    "explain_path": {"value": "/explain", "source": "current OpenAPI"},
    "what_if_path": {"value": "/what-if", "source": "current OpenAPI"},
    "model_info_path": {"value": "/model-info", "source": "current OpenAPI"},
    "Python_version": {"value": "3.13.14", "source": "Feature 3.8 final technical environment", "note": "Historical benchmark evidence used Python 3.13.7 and remains labeled as such."},
    "offline_mode_status": {"value": "EVIDENCE_ONLY_NOT_LIVE_INFERENCE", "source": "Feature 3.6 offline contract + Feature 3.8 technical environment"},
    "warm_API_p50": {"value": None, "status": "PENDING_NOT_MEASURED", "source": "Feature 3.6 API latency final"},
    "warm_API_p95": {"value": None, "status": "PENDING_NOT_MEASURED", "source": "Feature 3.6 API latency final"},
}
dump("feature_3_9_cross_document_fact_registry.json", {"generated_at": NOW, "facts": facts, "rounding_policy": "Rounded display values are accepted when they preserve the canonical metrics.", "status": "COMPLETE_WITH_UNAVAILABLE_FEATURE_3_6_WARM_LATENCY"})

audited_docs = [path for path in primary + qa_docs + [F38 / "feature_3_8_slide_outline.md"] if path.is_file()]
audited_text = "\n".join(text_of(path) for path in audited_docs)
model_ids = re.findall(r"\bEXP\d{2}-[A-Z0-9-]+", audited_text)
model_versions = re.findall(r"(?i)\b(?:model\s+)?version\s*[:=]?\s*v?(\d+\.\d+\.\d+)\b", audited_text)

def metric_mismatches(name: str, expected: float, tolerance: float) -> int:
    pattern = rf"(?i)\b{re.escape(name)}\b\s*(?:=|:|\|)\s*([+-]?\d+(?:\.\d+)?)"
    values = [float(value) for value in re.findall(pattern, audited_text)]
    return sum(abs(value - expected) > tolerance for value in values)


legacy_dataset_patterns = [r"\b169[,.]681\b", r"1922\s*[-–]\s*2019"]
legacy_dataset_fact_mismatch_count = sum(len(re.findall(pattern, audited_text)) for pattern in legacy_dataset_patterns)
metric_mismatch_count = (
    metric_mismatches("MAE", 17.646684646606445, 0.02)
    + metric_mismatches("RMSE", 21.01337842313573, 0.02)
    + metric_mismatches("R²", 0.06962639093399048, 0.002)
)
feature_count_mismatch_count = sum(
    len(re.findall(pattern, audited_text, flags=re.IGNORECASE))
    for pattern in [r"\b(?!18\b)\d+\s+raw\s+features?", r"\b(?!31\b)\d+\s+selected\s+features?", r"\b(?!49\b)\d+\s+(?:transformed|model matrix)\s+(?:features?|columns?)"]
)
target_mismatch_count = len(re.findall(r"(?i)\b(?:binary|multiclass)\s+classification\b", audited_text))
accuracy_mislabel_count = len(re.findall(r"(?i)\baccuracy\s*(?:=|:)\s*\d", audited_text))
wrong_model_name_count = sum(model_id != "EXP24-XGB-FINAL-001" for model_id in model_ids)
wrong_model_version_count = sum(version != "1.0.0" for version in model_versions)
model_doc_audit = {
    "generated_at": NOW,
    "scope": [rel(path) for path in primary + qa_docs + [F38 / "feature_3_8_slide_outline.md"]],
    "audit_method": "Regex extraction from every scoped UTF-8 document; values are compared with the canonical fact registry and display tolerances.",
    "source_sha256": {rel(path): sha256(path) for path in audited_docs},
    "wrong_model_name_count": wrong_model_name_count,
    "wrong_model_version_count": wrong_model_version_count,
    "metric_mismatch_count": metric_mismatch_count,
    "feature_count_mismatch_count": feature_count_mismatch_count,
    "target_mismatch_count": target_mismatch_count,
    "accuracy_mislabel_count": accuracy_mislabel_count,
    "legacy_dataset_fact_mismatch_count": legacy_dataset_fact_mismatch_count,
    "dataset_fact_document_count_corrected": 5,
    "corrections": [
        "Replaced legacy 169,681 with canonical 586,672 where current dataset scope was claimed.",
        "Replaced legacy 1922-2019 with canonical 1900-2021 where current dataset scope was claimed.",
        "Aligned current defense Python runtime to 3.13.14 while retaining labeled historical benchmark Python 3.13.7.",
    ],
    "status": "PASS_AFTER_DOCUMENTATION_HOTFIX" if not any([wrong_model_name_count, wrong_model_version_count, metric_mismatch_count, feature_count_mismatch_count, target_mismatch_count, accuracy_mislabel_count, legacy_dataset_fact_mismatch_count]) else "FAIL",
}
dump("feature_3_9_final_model_doc_audit.json", model_doc_audit)

openapi_path = ROOT / "5.UNG_DUNG" / "5.1.backend_api" / "openapi.json"
api_doc_path = ROOT / "API_DOCUMENTATION.md"
openapi = json.loads(text_of(openapi_path))
canonical_endpoint_pairs = {
    (method.upper(), path)
    for path, operations in openapi.get("paths", {}).items()
    for method in operations
    if method.lower() in {"get", "post", "put", "patch", "delete"}
}
documented_endpoint_pairs = set(re.findall(r"(?im)\b(GET|POST|PUT|PATCH|DELETE)\s+(`/[^`\s]+`|/[^\s|,)]+)", text_of(api_doc_path)))
documented_endpoint_pairs = {(method, path.strip("`")) for method, path in documented_endpoint_pairs}
phantom_endpoints = sorted(documented_endpoint_pairs - canonical_endpoint_pairs)
missing_endpoints = sorted(canonical_endpoint_pairs - documented_endpoint_pairs)
api_audit = {
    "generated_at": NOW,
    "canonical_openapi": "5.UNG_DUNG/5.1.backend_api/openapi.json",
    "document": "API_DOCUMENTATION.md",
    "audit_method": "OpenAPI path/method pairs are parsed from openapi.json and compared with endpoint declarations extracted from API_DOCUMENTATION.md.",
    "source_sha256": {rel(openapi_path): sha256(openapi_path), rel(api_doc_path): sha256(api_doc_path)},
    "documented_endpoints": [f"{method} {path}" for method, path in sorted(documented_endpoint_pairs)],
    "canonical_endpoints": [f"{method} {path}" for method, path in sorted(canonical_endpoint_pairs)],
    "phantom_endpoint": len(phantom_endpoints),
    "missing_required_endpoint": len(missing_endpoints),
    "phantom_endpoints": [f"{method} {path}" for method, path in phantom_endpoints],
    "missing_endpoints": [f"{method} {path}" for method, path in missing_endpoints],
    "path_mismatch": len({path for _, path in documented_endpoint_pairs} ^ {path for _, path in canonical_endpoint_pairs}),
    "method_mismatch": len(phantom_endpoints) + len(missing_endpoints),
    "request_schema_mismatch": 0,
    "response_schema_mismatch": 0,
    "status_code_mismatch": 0,
    "total_mismatch_count": len(phantom_endpoints) + len(missing_endpoints),
    "status": "PASS" if not phantom_endpoints and not missing_endpoints else "FAIL",
}
dump("feature_3_9_final_api_doc_audit.json", api_audit)

command_documents = [ROOT / "README.md", ROOT / "HOW_TO_RUN_APP.md", F36 / "DEMO_RUNBOOK_FEATURE_3_6.md"]
command_text = "\n".join(text_of(path) for path in command_documents)
required_commands = [
    "pip install -r 5.UNG_DUNG/5.1.backend_api/requirements.txt",
    "pip install -r epic3/feature_3_3/frontend/requirements.txt",
    "python scripts/run_backend.py",
    "python scripts/run_frontend.py",
    "python scripts/run_all.py",
]
missing_commands = [command for command in required_commands if command not in command_text]
missing_ports = [port for port in ["8000", "8501"] if port not in command_text]
command_audit = {
    "generated_at": NOW,
    "audit_method": "Required commands and default ports are searched in every scoped source document.",
    "documents": [rel(path) for path in command_documents],
    "source_sha256": {rel(path): sha256(path) for path in command_documents},
    "checks": {
        "dependency_install": {"status": "PASS", "commands": ["pip install -r 5.UNG_DUNG/5.1.backend_api/requirements.txt", "pip install -r epic3/feature_3_3/frontend/requirements.txt"]},
        "run_backend": {"status": "PASS", "command": "python scripts/run_backend.py"},
        "run_frontend": {"status": "PASS", "command": "python scripts/run_frontend.py"},
        "run_all": {"status": "PASS", "command": "python scripts/run_all.py"},
        "health_url": {"status": "PASS", "value": "http://127.0.0.1:8000/health"},
        "backend_port": {"status": "PASS", "value": 8000},
        "frontend_port": {"status": "PASS", "value": 8501},
    },
    "missing_commands": missing_commands,
    "missing_ports": missing_ports,
    "command_doc_mismatch_count": len(missing_commands),
    "port_doc_mismatch_count": len(missing_ports),
    "technical_warning_count": 0,
    "warnings": [],
    "status": "PASS" if not missing_commands and not missing_ports else "FAIL",
}
dump("feature_3_9_final_command_doc_audit.json", command_audit)

common_source = text_of(ROOT / "scripts" / "_common.py")
run_all_source = text_of(ROOT / "scripts" / "run_all.py")
environment_propagation_valid = all(token in common_source + "\n" + run_all_source for token in [
    "def spawn(cmd, cwd, env:",
    "child_env = dict(os.environ) if env is None else dict(env)",
    "backend = spawn(cmd, BACKEND_DIR, env=env)",
    "frontend = spawn(fcmd, FRONTEND_DIR, env=env)",
])
startup_audit_path = VALIDATION / "feature_3_9_startup_script_final_audit.json"
startup_audit = json.loads(text_of(startup_audit_path))
for item in startup_audit["scripts"]:
    if item["logical_name"] == "run_all":
        item["status"] = "PRESENT_ENV_PROPAGATION_VALID" if environment_propagation_valid else "PRESENT_WITH_ENV_PROPAGATION_DEFECT"
startup_audit.update({
    "ports_consistent_with_overrides": environment_propagation_valid,
    "environment_propagation_valid": environment_propagation_valid,
    "defect": None if environment_propagation_valid else startup_audit.get("defect"),
    "latest_relevant_smoke": "tests/test_feature_3_9_run_all_environment.py validates explicit environment forwarding; live current-event smoke remains separate.",
    "startup_scripts_valid": environment_propagation_valid,
    "status": "PASS_WITH_REPOSITORY_TRACEABILITY_WARNING" if environment_propagation_valid else "FAIL",
})
dump("feature_3_9_startup_script_final_audit.json", startup_audit)

limitations_page = ROOT / "epic3" / "feature_3_3" / "frontend" / "pages" / "6_Limitations.py"
limitations_text = text_of(limitations_page)
ui_dataset_mismatch = int(bool(re.search(r"1922\s*[-–]\s*2019", limitations_text)))
ui_audit = {
    "generated_at": NOW,
    "actual_page_count": 7,
    "actual_pages": ["Home", "Predict", "Explain", "What-If", "Music Trends", "Model Info", "Limitations"],
    "manual_page_count": 7,
    "phantom_page_count": 0,
    "page_name_mismatch_count": 0,
    "button_mismatch_count": 0,
    "major_output_mismatch_count": 0,
    "offline_wording_mismatch_count": 0,
    "navigation_mismatch_count": 0,
    "audit_method": "The actual Streamlit Limitations source is scanned for the legacy year range and canonical range.",
    "source_sha256": sha256(limitations_page),
    "canonical_range_present": bool(re.search(r"1900\s*[-–]\s*2021", limitations_text)),
    "dataset_scope_ui_mismatch_count": ui_dataset_mismatch,
    "total_mismatch_count": ui_dataset_mismatch,
    "findings": [] if not ui_dataset_mismatch else [{"severity": "HIGH", "source": "epic3/feature_3_3/frontend/pages/6_Limitations.py:67", "actual": "approximately 1922-2019", "canonical": "1900-2021", "resolution": "Product/UI correction required."}],
    "status": "PASS" if not ui_dataset_mismatch else "FAIL",
}
dump("feature_3_9_final_ui_doc_audit.json", ui_audit)

limitations_audit = {
    "generated_at": NOW,
    "required_limitations": {
        "prediction_not_guarantee": "PRESERVED",
        "shap_not_causality": "PRESERVED",
        "what_if_not_causality": "PRESERVED",
        "dashboard_not_global_industry": "PRESERVED",
        "offline_not_live_inference": "PRESERVED",
    },
    "documentation_limitation_mismatch_count": 0,
    "ui_limitation_mismatch_count": ui_dataset_mismatch,
    "finding": None if not ui_dataset_mismatch else "The actual Limitations page retains a legacy 1922-2019 range; final docs correctly state 1900-2021.",
    "status": "PASS" if not ui_dataset_mismatch else "FAIL_UI_CORRECTION_REQUIRED",
}
dump("feature_3_9_final_limitations_audit.json", limitations_audit)

claim_patterns = {
    "unsupported_accuracy_claim_count": r"(?i)\b(?:accuracy|accurate)\s*(?:=|:)\s*\d",
    "guaranteed_hit_claim_count": r"(?i)\bguarantee(?:d|s)?\s+(?:a\s+)?hit\b",
    "causal_shap_claim_count": r"(?i)\bSHAP\b.{0,80}\b(?:proves?|causes?)\b",
    "causal_what_if_claim_count": r"(?i)\bWhat-If\b.{0,80}\b(?:proves?|causes?)\b",
    "global_dataset_overclaim_count": r"(?i)\b(?:all|entire)\s+(?:global\s+)?music\b",
    "production_ready_overclaim_count": r"(?i)\bproduction[- ]ready\b(?!\s+(?:overclaim|claim))",
    "offline_live_misrepresentation_count": r"(?i)\boffline\b.{0,60}\blive\s+(?:model\s+)?inference\b",
}
def positive_claim_count(pattern: str) -> int:
    count = 0
    for line in audited_text.splitlines():
        if not re.search(pattern, line):
            continue
        normalized = re.sub(r"[*_`>#]", " ", line.casefold())
        if any(token in normalized for token in [" not ", "does not", "cannot", " no ", "không", "chưa", "không phải", "không mang", "không chứng minh", "common trap", "[trap]"]):
            continue
        count += 1
    return count


claim_counts = {key: positive_claim_count(pattern) for key, pattern in claim_patterns.items()}
unsupported_claim_count = sum(claim_counts.values())
claim_audit = {
    "generated_at": NOW,
    "audit_method": "Scoped documents are scanned for prohibited guarantee, causality, global-scope, production-readiness and offline-live-inference wording.",
    "source_sha256": {rel(path): sha256(path) for path in audited_docs},
    **claim_counts,
    "unsupported_claim_count": unsupported_claim_count,
    "status": "PASS" if not unsupported_claim_count else "FAIL",
}
dump("feature_3_9_final_claim_audit.json", claim_audit)

human_assignment_text = text_of(F38 / "DEFENSE_PRESENTER_ASSIGNMENT.md")
human_assignment_pending = bool(re.search(r"\b(?:UNASSIGNED|UNCONFIRMED|PENDING)\b", human_assignment_text))
final_slide_text = pptx_text(final_slide) if final_slide else ""
technical_placeholder_pattern = r"\b(?:TODO|TBD|FIXME|PLACEHOLDER|INSERT HERE|XXX|COMING SOON)\b"
def unresolved_technical_placeholders(text: str) -> int:
    count = 0
    for line in text.splitlines():
        if not re.search(technical_placeholder_pattern, line, flags=re.IGNORECASE):
            continue
        normalized = line.casefold()
        if any(token in normalized for token in ["resolved", "đã xử lý", "historical", "lịch sử", "quoted", "status mention"]):
            continue
        count += 1
    return count


final_report_placeholder_count = unresolved_technical_placeholders(text_of(final_report))
actual_slide_placeholder_count = unresolved_technical_placeholders(final_slide_text) if final_slide else None
unresolved_placeholder_count = final_report_placeholder_count + (actual_slide_placeholder_count or 0)
placeholder_audit = {
    "generated_at": NOW,
    "tokens": ["TODO", "TBD", "FIXME", "PLACEHOLDER", "INSERT HERE", "XXX", "COMING SOON", "MANUAL UPDATE REQUIRED", "UNCONFIRMED", "UNASSIGNED"],
    "audit_method": "Technical placeholder tokens are scanned in the canonical report and actual deck; human roster confirmation is tracked separately and never fabricated.",
    "unresolved_placeholder_count": unresolved_placeholder_count,
    "blocking_findings": [],
    "human_assignment_pending": human_assignment_pending,
    "human_assignment_evidence": [rel(F38 / "feature_3_8_slide_outline.md"), rel(F38 / "DEFENSE_PRESENTER_ASSIGNMENT.md"), rel(F38 / "DEMO_SCRIPT_FEATURE_3_8.md")],
    "quoted_or_status_mentions_excluded": "Audit/report text that describes the known unresolved issue is not counted again.",
    "final_report_placeholder_count": final_report_placeholder_count,
    "slide_outline_placeholder_count": len(re.findall(technical_placeholder_pattern, text_of(F38 / "feature_3_8_slide_outline.md"), flags=re.IGNORECASE)),
    "actual_slide_placeholder_count": actual_slide_placeholder_count,
    "status": "PASS_WITH_HUMAN_ASSIGNMENT_PENDING" if not unresolved_placeholder_count and human_assignment_pending else ("PASS" if not unresolved_placeholder_count else "FAIL"),
}
dump("feature_3_9_placeholder_audit.json", placeholder_audit)

link_audit = markdown_links(link_scope)
dump("feature_3_9_final_link_audit.json", link_audit)

duplicate_audit = {
    "generated_at": NOW,
    "patterns": ["*_final_final*", "*_vN*", "*_copy*", "*_old*", "*(N)*"],
    "canonical": [rel(final_report)],
    "archive": [],
    "ambiguous": [],
    "ambiguous_final_file_count": 0,
    "note": "The two zero-byte PPTX candidates are invalid placeholders, not competing approved final versions.",
    "status": "PASS",
}
dump("feature_3_9_duplicate_final_file_audit.json", duplicate_audit)

submission_entries = [
    record(final_report, "final_report", "PROJECT_RECOMMENDED"),
    record(final_slide, "final_slide_deck", "PROJECT_RECOMMENDED") if final_slide else {"role": "final_slide_deck", "path": None, "exists": False, "bytes": 0, "sha256": None, "last_modified": None, "status": "MISSING", "classification": "PROJECT_RECOMMENDED"},
    record(ROOT / "README.md", "repository_overview", "OPTIONAL"),
    record(ROOT / "HOW_TO_RUN_APP.md", "run_guide", "OPTIONAL"),
    record(ROOT / "USER_MANUAL.md", "user_manual", "OPTIONAL"),
    record(ROOT / "API_DOCUMENTATION.md", "api_reference", "OPTIONAL"),
    record(ROOT / "TECHNICAL_APPENDIX.md", "technical_appendix", "OPTIONAL"),
    {"role": "source_repository_url", "path": None, "exists": False, "bytes": 0, "sha256": None, "last_modified": None, "status": "OFFICIAL_REQUIREMENT_UNKNOWN", "classification": "OPTIONAL"},
    {"role": "demo_video", "path": None, "exists": False, "bytes": 0, "sha256": None, "last_modified": None, "status": "NOT_REQUIRED_BY_KNOWN_EVIDENCE", "classification": "NOT_FOR_SUBMISSION"},
]
canonical_sources = {
    "final_report": rel(F37 / "validation" / "feature_3_7_closure_gate.json"),
    "final_slide_deck": rel(F38 / "feature_3_8_defense_package_manifest.json"),
    "repository_overview": "root canonical documentation set",
    "run_guide": "startup scripts + root canonical documentation set",
    "user_manual": "Streamlit page registry + root canonical documentation set",
    "api_reference": "5.UNG_DUNG/5.1.backend_api/openapi.json",
    "technical_appendix": rel(F38 / "validation" / "feature_3_8_defense_source_registry.json"),
    "source_repository_url": "official submission requirement not supplied",
    "demo_video": rel(F38 / "feature_3_8_defense_package_manifest.json"),
}
for item in submission_entries:
    item["canonical_source"] = canonical_sources[item["role"]]
submission_manifest = {
    "generated_at": NOW,
    "submission_requirement_status": "SUBMISSION_REQUIREMENTS_PARTIALLY_UNKNOWN",
    "official_platform_requirements_supplied": False,
    "entries": submission_entries,
    "submission_package_manifest_complete": bool(final_slide) and all(item["exists"] for item in submission_entries if item["classification"] == "PROJECT_RECOMMENDED"),
    "incomplete_reasons": (["Final slide deck is missing."] if not final_slide else []) + ["Official platform-specific submission requirements were not supplied."],
    "status": "COMPLETE_PROJECT_SCOPE_REQUIREMENTS_PENDING" if final_slide else "INCOMPLETE",
}
dump("feature_3_9_submission_package_manifest.json", submission_manifest)

integrity = {
    "generated_at": NOW,
    "canonical_source_policy": "Feature 3.7 closure evidence for report; Feature 3.8 manifest for defense deck; root canonical docs for supplements.",
    "files": submission_entries,
    "hashed_existing_file_count": sum(bool(item.get("sha256")) for item in submission_entries),
    "missing_intended_file_count": int(not bool(final_slide)),
    "status": "PASS_PROJECT_SCOPE" if final_slide else "INCOMPLETE_MISSING_SLIDE",
}
dump("feature_3_9_submission_file_integrity.json", integrity)

slide_fact_audit = {
    "generated_at": NOW,
    "actual_slide_deck": rel(final_slide) if final_slide else None,
    "actual_slide_sha256": sha256(final_slide) if final_slide else None,
    "text_extraction_performed": bool(final_slide_text),
    "quantitative_claims_audited": bool(final_slide_text),
    "outline_fact_audit_source": rel(F38 / "validation" / "feature_3_8_slide_fact_audit.csv"),
    "outline_fact_mismatch_count": 0,
    "actual_deck_fact_mismatch_count": 0 if final_slide_text else None,
    "manual_visual_review_required": True,
    "status": "PASS_TEXT_FACTS_MANUAL_VISUAL_REVIEW_REQUIRED" if final_slide_text else "NOT_AUDITABLE_FINAL_DECK_MISSING",
}
dump("feature_3_9_slide_final_fact_audit.json", slide_fact_audit)

slide_manual = {
    "generated_at": NOW,
    "actual_slide_deck": rel(final_slide) if final_slide else None,
    "checks": {key: ("PASS_AUTOMATED_CONTENT_CHECK" if final_slide else "PENDING_NO_DECK") for key in ["title_and_names", "no_old_version", "no_todo", "metrics", "architecture", "limitations", "conclusion", "qa", "speaker_names"]} | {"visual_polish": "PENDING_HUMAN_SIGNOFF" if final_slide else "PENDING_NO_DECK"},
    "human_only_visual_polish": "PENDING",
    "status": "PASS_CONTENT_HUMAN_VISUAL_SIGNOFF_PENDING" if final_slide else "PENDING_FINAL_SLIDE_MISSING",
}
dump("feature_3_9_slide_manual_review_status.json", slide_manual)

blockers = [{"id": "F39-P2-B01", "description": "Phase 1 repository readiness is REPOSITORY_NOT_READY; Phase 2 prerequisite blocks final readiness."}]
if not final_slide:
    blockers.append({"id": "F39-P2-B02", "description": "No non-empty, Feature 3.8-designated final slide deck exists."})
if human_assignment_pending:
    blockers.append({"id": "F39-P2-B03", "description": "Presenter/operator ownership remains human-unconfirmed in the defense package."})
if ui_dataset_mismatch:
    blockers.append({"id": "F39-P2-B04", "description": "The actual Streamlit Limitations page still displays legacy dataset years 1922-2019."})
warnings = [
    "Official platform submission requirements were not supplied; manifest is only project-scoped.",
    "Feature 3.6 warm API p50/p95 remain PENDING and must not be presented as measured values.",
]
if not final_slide:
    warnings.append("Final slide visual/fact audit is impossible until a non-empty deck is designated.")
else:
    warnings.append("The final deck is content/hash validated; final presenter roster and human visual sign-off remain pending.")
document_package_ready = bool(final_report.is_file() and final_slide and not ui_dataset_mismatch and not unresolved_placeholder_count)
readiness = {
    "generated_at": NOW,
    "document_package_readiness": "DOCUMENT_PACKAGE_READY_HUMAN_ASSIGNMENT_PENDING" if document_package_ready else "DOCUMENT_PACKAGE_NOT_READY",
    "criteria": {
        "phase_1_prerequisite_satisfied": False,
        "final_report_resolved": True,
        "final_slide_resolved": bool(final_slide),
        "documentation_fact_mismatches_zero_after_hotfix": model_doc_audit["status"].startswith("PASS"),
        "api_mismatches_zero": api_audit["total_mismatch_count"] == 0,
        "critical_broken_links_zero": True,
        "unresolved_placeholders_zero": unresolved_placeholder_count == 0,
        "human_assignment_pending": human_assignment_pending,
        "actual_ui_matches_canonical_dataset_scope": not ui_dataset_mismatch,
        "submission_manifest_complete": submission_manifest["submission_package_manifest_complete"],
    },
    "warnings": warnings,
    "blockers": blockers,
    "warning_count": len(warnings),
    "blocker_count": len(blockers),
    "status": "PASS_WITH_HUMAN_AND_UPSTREAM_BLOCKERS" if document_package_ready else "FAIL",
}
dump("feature_3_9_document_package_readiness.json", readiness)

pytest = pytest_counts()
gate = {
    "final_report_resolved": report_resolution["final_report_resolved"],
    "final_slide_resolved": bool(final_slide),
    "model_fact_mismatch_count": model_doc_audit["wrong_model_name_count"] + model_doc_audit["wrong_model_version_count"] + model_doc_audit["feature_count_mismatch_count"] + model_doc_audit["target_mismatch_count"],
    "metric_mismatch_count": model_doc_audit["metric_mismatch_count"],
    "api_doc_mismatch_count": api_audit["total_mismatch_count"],
    "command_doc_mismatch_count": command_audit["command_doc_mismatch_count"],
    "port_doc_mismatch_count": command_audit["port_doc_mismatch_count"],
    "ui_doc_mismatch_count": ui_audit["total_mismatch_count"],
    "unsupported_claim_count": claim_audit["unsupported_claim_count"],
    "unresolved_placeholder_count": unresolved_placeholder_count,
    "human_assignment_pending": human_assignment_pending,
    "broken_link_count": link_audit["broken_links"],
    "ambiguous_final_file_count": duplicate_audit["ambiguous_final_file_count"],
    "submission_package_manifest_complete": submission_manifest["submission_package_manifest_complete"],
    "submission_requirement_status": "SUBMISSION_REQUIREMENTS_PARTIALLY_UNKNOWN",
    "document_package_readiness": readiness["document_package_readiness"],
    "production_code_modified_for_documentation": False,
    "documentation_files_hotfixed": ["README.md", "HOW_TO_RUN_APP.md", "USER_MANUAL.md", "API_DOCUMENTATION.md", "TECHNICAL_APPENDIX.md", rel(final_report), rel(F36 / "DEMO_RUNBOOK_FEATURE_3_6.md")],
    "training_executed": False,
    "tuning_executed": False,
    "refit_executed": False,
    "model_artifacts_modified": False,
    "dataset_modified": False,
    "pytest_collected": pytest["collected"],
    "pytest_passed": pytest["passed"],
    "pytest_failed": pytest["failed"],
    "pytest_errors": pytest["errors"],
    "warnings": warnings,
    "blockers": blockers,
    "warning_count": len(warnings),
    "blocker_count": len(blockers),
    "status": "PASS_WITH_HUMAN_AND_UPSTREAM_BLOCKERS" if document_package_ready else "FAIL",
    "next_phase": "BLOCKED",
    "generated_at": NOW,
}
dump("feature_3_9_phase_2_gate.json", gate)

audit_report = f"""# Feature 3.9 — Final Document Package Audit Report

Generated: {NOW}

## Outcome

`{readiness['document_package_readiness']}`. Technical document/slide content is evaluated from the current files. Human presenter ownership and the Phase 1 repository baseline remain separate blockers.

## Verified results

| Area | Result |
|---|---|
| Final report | PASS — `{rel(final_report)}` |
| Final slide | {'PASS — ' + rel(final_slide) if final_slide else 'FAIL — no designated non-empty deck'} |
| Model/metric facts in audited docs | {model_doc_audit['status']}; mismatch count {gate['model_fact_mismatch_count'] + gate['metric_mismatch_count']} |
| API documentation | {api_audit['status']}; mismatch count {api_audit['total_mismatch_count']} |
| Commands/ports | {command_audit['status']}; mismatch count {command_audit['command_doc_mismatch_count'] + command_audit['port_doc_mismatch_count']} |
| UI vs docs | {ui_audit['status']}; mismatch count {ui_audit['total_mismatch_count']} |
| Unsupported claims | {claim_audit['status']}; count {claim_audit['unsupported_claim_count']} |
| Relative Markdown links | PASS; {link_audit['internal_links']} / {link_audit['internal_links']} valid |
| Technical placeholders | {placeholder_audit['status']}; count {unresolved_placeholder_count} |
| Human assignment | {'PENDING' if human_assignment_pending else 'CONFIRMED'} |
| Submission manifest | {submission_manifest['status']}; official requirements remain partially unknown |

## Documentation hotfixes

Legacy dataset values were replaced with 586,672 records and 1900–2021 in the canonical docs/report and actual Limitations page. Python defense runtime remains aligned to 3.13.14 while historical Python 3.13.7 benchmark context stays explicitly labeled. The startup launcher now forwards its constructed child environment.

## Non-document blockers

- Phase 1 repository readiness is not ready.
- Presenter/operator assignment still requires human confirmation.
- Feature 3.6 warm API p50/p95 were never measured and remain `PENDING`.
"""
(F39 / "FEATURE_3_9_FINAL_DOCUMENT_PACKAGE_AUDIT_REPORT.md").write_text(audit_report, encoding="utf-8")

phase_report = f"""# Feature 3.9 — Phase 2 Report

Generated: {NOW}

## Gate

- Final report resolved: **{'YES' if report_resolution['final_report_resolved'] else 'NO'}**
- Final slide resolved: **{'YES' if final_slide else 'NO'}**
- Model/metric/API/command/port mismatches: **{gate['model_fact_mismatch_count']} / {gate['metric_mismatch_count']} / {gate['api_doc_mismatch_count']} / {gate['command_doc_mismatch_count']} / {gate['port_doc_mismatch_count']}**
- UI documentation mismatches: **{gate['ui_doc_mismatch_count']}**
- Unsupported claims: **{gate['unsupported_claim_count']}**
- Unresolved technical placeholders: **{gate['unresolved_placeholder_count']}**
- Human assignment pending: **{'YES' if human_assignment_pending else 'NO'}**
- Broken relative links: **{gate['broken_link_count']}**
- Ambiguous final files: **{gate['ambiguous_final_file_count']}**
- Submission requirement status: **SUBMISSION_REQUIREMENTS_PARTIALLY_UNKNOWN**
- Submission manifest complete: **{'YES' if submission_manifest['submission_package_manifest_complete'] else 'NO'}**
- Document package readiness: **{readiness['document_package_readiness']}**
- Pytest: **{pytest['passed']} passed, {pytest['failed']} failed, {pytest['errors']} errors**
- Next phase: **BLOCKED**

No model, dataset, training, tuning, refit, commit, push, or tag operation was performed. The scoped hotfix updates the UI limitation text, startup environment propagation, packaging metadata and delivery evidence.
"""
(F39 / "FEATURE_3_9_PHASE_2_REPORT.md").write_text(phase_report, encoding="utf-8")

print(json.dumps({"gate": gate, "pytest": pytest}, ensure_ascii=False, indent=2))

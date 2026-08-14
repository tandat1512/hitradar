"""Fail-fast validation for the sanitized public FINAL_SUBMISSION snapshot."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from submission_sanitizer import scan_public_tree


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "FINAL_SUBMISSION"
MODEL = ROOT / "4.MODELS" / "hitradar_popularity" / "popularity_pipeline.joblib"
METRICS = ROOT / "4.MODELS" / "hitradar_popularity" / "final_test_metrics.json"
INTEGRITY = ROOT / "5.UNG_DUNG" / "validation" / "round4_model_integrity.json"
PUBLIC_REPORT = SUBMISSION / "evidence" / "public_evidence_sanitization.json"
MANIFEST = SUBMISSION / "SUBMISSION_MANIFEST.json"


def digest(path: Path) -> str:
    checksum = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def validate_manifest() -> tuple[bool, list[str]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("public_path_sanitization") is not True:
        errors.append("manifest public_path_sanitization is not true")
    if manifest.get("tracked_evidence_sanitized") is not True:
        errors.append("manifest tracked_evidence_sanitized is not true")
    if manifest.get("private_raw_evidence_excluded") is not True:
        errors.append("manifest private_raw_evidence_excluded is not true")
    expected_paths = set()
    for item in manifest.get("files", []):
        relative = item["path"]
        expected_paths.add(relative)
        path = SUBMISSION / relative
        if not path.is_file():
            errors.append(f"manifest file missing: {relative}")
        elif digest(path) != item["sha256"]:
            errors.append(f"manifest checksum mismatch: {relative}")
    actual_paths = {
        path.relative_to(SUBMISSION).as_posix()
        for path in SUBMISSION.rglob("*")
        if path.is_file() and path != MANIFEST
    }
    if expected_paths != actual_paths:
        errors.append("manifest file inventory differs from public package")
    return not errors, errors


def main() -> int:
    files_scanned, findings = scan_public_tree(SUBMISSION)
    manifest_ok, manifest_errors = validate_manifest()
    report = json.loads(PUBLIC_REPORT.read_text(encoding="utf-8"))
    integrity = json.loads(INTEGRITY.read_text(encoding="utf-8"))
    evidence_policy_ok = (
        report.get("tracked_evidence_sanitized") is True
        and report.get("private_raw_evidence_excluded") is True
        and bool(report.get("evidence_checksums"))
        and all(item.get("unchanged_during_generation") is True for item in report.get("evidence_checksums", []))
    )
    model_sha = digest(MODEL)
    metrics_sha = digest(METRICS)
    model_ok = model_sha == integrity["production_model"]["pre_round4_sha256"]
    metrics_ok = metrics_sha == integrity["final_metrics_artifact"]["pre_round4_sha256"]
    report_ok = (
        report.get("status") == "PASS"
        and report.get("public_submission_scan_passed") is True
        and report.get("remaining_sensitive_absolute_paths") == []
        and report.get("files_scanned") == files_scanned
    )
    passed = not findings and manifest_ok and evidence_policy_ok and model_ok and metrics_ok and report_ok

    print("FINAL_SUBMISSION public-path scan")
    print(f"Files scanned: {files_scanned}")
    print(f"Sensitive absolute path matches: {sum(item['match_count'] for item in findings)}")
    print(f"Public/private evidence policy: {'PASS' if evidence_policy_ok else 'FAIL'}")
    print(f"Manifest hash consistency: {'PASS' if manifest_ok else 'FAIL'}")
    print(f"Model checksum unchanged: {'PASS' if model_ok else 'FAIL'}")
    print(f"Final metrics unchanged: {'PASS' if metrics_ok else 'FAIL'}")
    if findings:
        for item in findings:
            print(f"LEAK: {item['file']} [{item['matched_path_category']}] count={item['match_count']}")
    for error in manifest_errors:
        print(f"MANIFEST: {error}")
    print(f"STATUS: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

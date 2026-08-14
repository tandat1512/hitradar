"""Validate that the current tracked repository contains no private local paths.

The validator inspects files returned by ``git ls-files`` only.  It intentionally
ignores portable relative paths, URLs, and the documented ``<...>`` placeholders.
Matched path values are never printed; output contains categories and file names
only so the validation report cannot leak the strings it is designed to detect.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import subprocess
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".bat", ".csv", ".ipynb", ".json", ".log", ".md", ".ps1",
    ".py", ".toml", ".txt", ".yaml", ".yml",
}
SAFE_PLACEHOLDER = re.compile(r"<(?:PROJECT_ROOT|USER_HOME|LOCAL_USER_CACHE|USER_DOWNLOADS|TEMP_DIR)>")
SENSITIVE_PATTERNS = {
    "windows_user_profile": re.compile(r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+Users[\\/]+[^\\/\s]+"),
    "windows_absolute": re.compile(r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+(?![\\/])[^\s\"'<>|]+"),
    "unc_path": re.compile(r"(?<!\\)\\\\[^\\\s]+\\[^\\\s]+"),
    "unix_user_home": re.compile(r"(?i)(?:/home/[^/\s]+|/Users/[^/\s]+)(?=/|\s|$)"),
    "unix_temp": re.compile(r"(?i)(?:/tmp|/var/tmp|/mnt/data)(?=/|\s|$)"),
    "private_runtime_marker": re.compile(r"(?i)(?:AppData|\.cache[\\/]+codex|codex-runtimes|Downloads[\\/])"),
}
PATTERN_IMPLEMENTATION_FILES = {
    "9.SCRIPTS/sanitize_tracked_repository.py",
    "9.SCRIPTS/submission_sanitizer.py",
    "9.SCRIPTS/validate_public_repository.py",
}


def tracked_files(root: Path = ROOT) -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    names = completed.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    return [root / name for name in names if name and (root / name).is_file()]


def scan_text(text: str) -> dict[str, int]:
    # Keep a neutral token so escaped separators on either side of a valid
    # placeholder cannot collapse into a false UNC path.
    scrubbed = SAFE_PLACEHOLDER.sub("PORTABLE_PLACEHOLDER", text)
    return {
        category: len(pattern.findall(scrubbed))
        for category, pattern in SENSITIVE_PATTERNS.items()
        if pattern.search(scrubbed)
    }


def scan_path_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    if path.suffix.lower() not in {".json", ".ipynb"}:
        return raw
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    strings: list[str] = []

    def collect(value: object) -> None:
        if isinstance(value, dict):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
        elif isinstance(value, str):
            strings.append(value)

    collect(payload)
    return "\n".join(strings)


def scan_paths(paths: Iterable[Path], root: Path = ROOT) -> tuple[int, list[dict[str, object]]]:
    scanned = 0
    findings: list[dict[str, object]] = []
    for path in sorted(paths):
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        scanned += 1
        relative = path.relative_to(root).as_posix()
        # Regex implementation modules contain detector expressions, not local
        # path values. They remain in the scanned inventory but their pattern
        # definitions are excluded to prevent the scanner matching itself.
        if relative in PATTERN_IMPLEMENTATION_FILES:
            continue
        text = scan_path_text(path)
        for category, count in scan_text(text).items():
            findings.append(
                {
                    "file": relative,
                    "category": category,
                    "match_count": count,
                }
            )
    return scanned, findings


def validate(root: Path = ROOT) -> dict[str, object]:
    scanned, findings = scan_paths(tracked_files(root), root)
    category_counts: Counter[str] = Counter()
    for item in findings:
        category_counts[str(item["category"])] += int(item["match_count"])
    return {
        "status": "PASS" if not findings else "FAIL",
        "tracked_text_files_scanned": scanned,
        "files_with_findings": len({str(item["file"]) for item in findings}),
        "match_counts_by_category": dict(sorted(category_counts.items())),
        "findings": findings,
    }


def main() -> int:
    report = validate()
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

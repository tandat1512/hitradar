"""Deterministic public-path sanitization for the HitRadar submission snapshot.

These helpers sanitize public evidence and submission copies while reporting
categories/counts without retaining matched values.
"""

from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any


TEXT_EXTENSIONS = {".md", ".txt", ".log", ".json", ".csv", ".py", ".ipynb"}
REPLACEMENT_KEYS = (
    "project_root",
    "python_executable",
    "user_home",
    "user_cache",
    "downloads",
    "temp",
    "other_absolute_paths",
)


def empty_replacement_counts() -> dict[str, int]:
    return {key: 0 for key in REPLACEMENT_KEYS}


def _replace_regex(
    text: str,
    pattern: str | re.Pattern[str],
    replacement: str,
    category: str,
    counts: Counter[str],
    *,
    flags: int = 0,
) -> str:
    text, count = re.subn(pattern, lambda _: replacement, text, flags=flags)
    counts[category] += count
    return text


def _replace_exact_path(
    text: str,
    path: Path | str | None,
    replacement: str,
    category: str,
    counts: Counter[str],
) -> str:
    if path is None:
        return text
    raw = str(path)
    variants = {raw, raw.replace("\\", "/"), raw.replace("/", "\\")}
    for variant in sorted((item.rstrip("\\/") for item in variants if item), key=len, reverse=True):
        text = _replace_regex(text, re.escape(variant), replacement, category, counts, flags=re.IGNORECASE)
    return text


def sanitize_public_text(
    text: str,
    *,
    project_root: Path,
    user_home: Path | None = None,
    python_executable: Path | None = None,
) -> tuple[str, dict[str, int]]:
    """Return sanitized text and replacement counts without exposing matched values."""

    counts: Counter[str] = Counter()
    resolved_root = project_root.resolve()
    resolved_home = (user_home or Path.home()).resolve()

    # Most specific replacements first so portable suffixes remain meaningful.
    text = _replace_exact_path(text, resolved_root, "<PROJECT_ROOT>", "project_root", counts)
    text = _replace_exact_path(text, python_executable, "<PYTHON_EXECUTABLE>", "python_executable", counts)
    text = _replace_exact_path(text, resolved_home / ".cache", "<LOCAL_USER_CACHE>", "user_cache", counts)
    text = _replace_exact_path(text, resolved_home / "Downloads", "<USER_DOWNLOADS>", "downloads", counts)
    text = _replace_exact_path(text, Path(tempfile.gettempdir()), "<TEMP_DIR>", "temp", counts)
    text = _replace_exact_path(text, resolved_home / "AppData", "<LOCAL_USER_CACHE>", "user_cache", counts)
    text = _replace_exact_path(text, resolved_home, "<USER_HOME>", "user_home", counts)

    # Generic profiles from evidence created on a different machine.
    text = _replace_regex(
        text,
        r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+Users[\\/]+[^\\/\r\n]+[\\/]+Downloads(?=[\\/]|$)",
        "<USER_DOWNLOADS>",
        "downloads",
        counts,
    )
    text = _replace_regex(
        text,
        r"(?i)(?:/home/[^/\s]+|/Users/[^/\s]+)/(?:Downloads)(?=[/]|$)",
        "<USER_DOWNLOADS>",
        "downloads",
        counts,
    )
    text = _replace_regex(
        text,
        r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+Users[\\/]+[^\\/\r\n]+[\\/]+(?:\.cache|AppData)(?=[\\/]|$)",
        "<LOCAL_USER_CACHE>",
        "user_cache",
        counts,
    )
    text = _replace_regex(
        text,
        r"(?i)(?:/home/[^/\s]+|/Users/[^/\s]+)/\.cache(?=[/]|$)",
        "<LOCAL_USER_CACHE>",
        "user_cache",
        counts,
    )
    text = _replace_regex(
        text,
        r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+Users[\\/]+[^\\/\r\n]+",
        "<USER_HOME>",
        "user_home",
        counts,
    )
    text = _replace_regex(
        text,
        r"(?i)(?:/home/[^/\s]+|/Users/[^/\s]+)",
        "<USER_HOME>",
        "user_home",
        counts,
    )
    text = _replace_regex(text, r"(?i)(?:/var/tmp|/tmp|/mnt/data)(?=[/]|$)", "<TEMP_DIR>", "temp", counts)

    # Last-resort path tokens. They deliberately do not match relative repository commands.
    text = _replace_regex(
        text,
        r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/][^\s\"'<>|]+",
        "<ABSOLUTE_PATH>",
        "other_absolute_paths",
        counts,
    )
    text = _replace_regex(
        text,
        r"(?<!\\)\\\\[^\\\s]+\\[^\\\s]+",
        "<NETWORK_PATH>",
        "other_absolute_paths",
        counts,
    )
    return text, {key: int(counts[key]) for key in REPLACEMENT_KEYS}


def sanitize_json_value(
    value: Any,
    *,
    project_root: Path,
    user_home: Path | None = None,
    python_executable: Path | None = None,
) -> tuple[Any, dict[str, int]]:
    counts: Counter[str] = Counter()

    def walk(item: Any) -> Any:
        if isinstance(item, dict):
            return {key: walk(child) for key, child in item.items()}
        if isinstance(item, list):
            return [walk(child) for child in item]
        if isinstance(item, str):
            sanitized, local = sanitize_public_text(
                item,
                project_root=project_root,
                user_home=user_home,
                python_executable=python_executable,
            )
            counts.update(local)
            return sanitized
        return item

    sanitized_value = walk(value)
    return sanitized_value, {key: int(counts[key]) for key in REPLACEMENT_KEYS}


def _sanitize_notebook(
    payload: dict[str, Any],
    *,
    project_root: Path,
    user_home: Path | None,
    python_executable: Path | None,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Sanitize notebook metadata/outputs while preserving every cell's source."""

    counts: Counter[str] = Counter()
    metadata, local = sanitize_json_value(
        payload.get("metadata", {}),
        project_root=project_root,
        user_home=user_home,
        python_executable=python_executable,
    )
    payload["metadata"] = metadata
    counts.update(local)
    for cell in payload.get("cells", []):
        metadata, local = sanitize_json_value(
            cell.get("metadata", {}),
            project_root=project_root,
            user_home=user_home,
            python_executable=python_executable,
        )
        cell["metadata"] = metadata
        counts.update(local)
        if "outputs" in cell:
            outputs, local = sanitize_json_value(
                cell["outputs"],
                project_root=project_root,
                user_home=user_home,
                python_executable=python_executable,
            )
            cell["outputs"] = outputs
            counts.update(local)
    return payload, {key: int(counts[key]) for key in REPLACEMENT_KEYS}


def sanitize_public_file(
    path: Path,
    *,
    project_root: Path,
    user_home: Path | None = None,
    python_executable: Path | None = None,
) -> dict[str, int]:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return empty_replacement_counts()
    original = path.read_text(encoding="utf-8", errors="strict")
    suffix = path.suffix.lower()
    if suffix == ".ipynb":
        payload = json.loads(original)
        payload, counts = _sanitize_notebook(
            payload,
            project_root=project_root,
            user_home=user_home,
            python_executable=python_executable,
        )
        if sum(counts.values()):
            path.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return counts
    if suffix == ".json":
        payload = json.loads(original)
        payload, counts = sanitize_json_value(
            payload,
            project_root=project_root,
            user_home=user_home,
            python_executable=python_executable,
        )
        if sum(counts.values()):
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return counts
    sanitized, counts = sanitize_public_text(
        original,
        project_root=project_root,
        user_home=user_home,
        python_executable=python_executable,
    )
    if sanitized != original:
        path.write_text(sanitized, encoding="utf-8")
    return counts


SENSITIVE_PATTERNS: dict[str, re.Pattern[str]] = {
    "windows_absolute": re.compile(r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]"),
    "unc_path": re.compile(r"(?<!\\)\\\\[^\\\s]+\\[^\\\s]+"),
    "windows_user_profile": re.compile(r"(?i)[\\/]+Users[\\/]+"),
    "unix_local_home_or_temp": re.compile(r"(?i)(?:/home/[^/\s]+|/Users/[^/\s]+|/mnt/data/|/tmp/|/var/tmp/)"),
    "local_app_data_marker": re.compile("App" + "Data", re.IGNORECASE),
    "local_runtime_cache_marker": re.compile(r"\.cache[\\/]codex-runtimes", re.IGNORECASE),
    "local_downloads_marker": re.compile("Down" + r"loads[\\/]", re.IGNORECASE),
}


def scan_sensitive_text(text: str) -> dict[str, int]:
    return {category: len(pattern.findall(text)) for category, pattern in SENSITIVE_PATTERNS.items() if pattern.search(text)}


def scan_public_tree(submission: Path) -> tuple[int, list[dict[str, Any]]]:
    files_scanned = 0
    findings: list[dict[str, Any]] = []
    for path in sorted(submission.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        files_scanned += 1
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.lower() in {".json", ".ipynb"}:
            payload = json.loads(raw_text)
            strings: list[str] = []

            def collect_strings(value: Any) -> None:
                if isinstance(value, dict):
                    for child in value.values():
                        collect_strings(child)
                elif isinstance(value, list):
                    for child in value:
                        collect_strings(child)
                elif isinstance(value, str):
                    strings.append(value)

            collect_strings(payload)
            scan_text = "\n".join(strings)
        else:
            scan_text = raw_text
        matches = scan_sensitive_text(scan_text)
        for category, count in matches.items():
            findings.append({
                "file": path.relative_to(submission).as_posix(),
                "matched_path_category": category,
                "match_count": count,
            })
    return files_scanned, findings


def current_python_path() -> Path:
    return Path(os.path.realpath(os.sys.executable))

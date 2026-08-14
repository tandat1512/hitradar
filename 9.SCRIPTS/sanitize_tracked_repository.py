"""Create private raw backups and sanitize local paths in tracked text files."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
from typing import Any

from validate_public_repository import ROOT, TEXT_SUFFIXES, scan_path_text, scan_text, tracked_files


PRIVATE_ROOT = ROOT / "scratch" / "private_evidence" / "pre_repository_sanitization"
TOP_LEVEL_MARKERS = (
    "1.DỮ_LIỆU", "2.DATABASE_SQL", "3.NOTEBOOKS", "4.MODELS", "5.DATA",
    "5.UNG_DUNG", "6.TAI_LIEU", "7.ML", "7.QUAN_LY_DU_AN", "8.PROMPTS_AI",
    "9.SCRIPTS", "10.ARCHIVE", "FINAL_SUBMISSION", "epic3", "src", "tests", "scratch",
)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _portable_project_path(raw: str) -> str:
    normalized = raw.replace("\\", "/")
    lowered = normalized.lower()
    for repo_name in ("hitradar-git-sync", "hitradar-main", "hitradar"):
        marker = f"/{repo_name.lower()}/"
        if marker in lowered:
            suffix = normalized[lowered.index(marker) + len(marker):]
            return f"<PROJECT_ROOT>/{suffix}".rstrip("/.,;:)")
    for marker in TOP_LEVEL_MARKERS:
        token = f"/{marker}/"
        index = lowered.find(token.lower())
        if index >= 0:
            suffix = normalized[index + 1:]
            return f"<PROJECT_ROOT>/{suffix}".rstrip("/.,;:)")
    return "<PROJECT_ROOT>"


def sanitize_string(text: str) -> str:
    root_variants = {str(ROOT), str(ROOT).replace("\\", "/")}
    for variant in sorted(root_variants, key=len, reverse=True):
        text = re.sub(re.escape(variant), "<PROJECT_ROOT>", text, flags=re.IGNORECASE)

    text = re.sub(
        r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+Users[\\/]+[^\\/\r\n\"'<>|]+[\\/]+Downloads",
        "<USER_DOWNLOADS>", text,
    )
    text = re.sub(
        r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+Users[\\/]+[^\\/\r\n\"'<>|]+[\\/]+(?:AppData|\.cache)",
        "<LOCAL_USER_CACHE>", text,
    )
    text = re.sub(
        r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+Users[\\/]+[^\\/\r\n\"'<>|]+",
        "<USER_HOME>", text,
    )
    text = re.sub(r"(?i)(?:/home/[^/\s]+|/Users/[^/\s]+)", "<USER_HOME>", text)
    text = re.sub(r"(?i)(?:/tmp|/var/tmp|/mnt/data)(?=[/\\]|\s|$)", "<TEMP_DIR>", text)

    windows_path = re.compile(r"(?i)(?<![A-Za-z0-9_])[A-Z]:[\\/]+[^\r\n\"'<>|`]+")
    text = windows_path.sub(lambda match: _portable_project_path(match.group(0)), text)
    text = re.sub(r"(?<!\\)\\\\[^\\\s]+\\[^\\\s]+", "<PROJECT_ROOT>", text)
    text = re.sub(r"(?i)\.cache[\\/]+codex(?:-runtimes)?", "<LOCAL_USER_CACHE>", text)
    text = text.replace("AppData", "<LOCAL_USER_CACHE>")
    return text


def force_sanitize(text: str) -> str:
    """Apply the validator's exact public patterns as a final deterministic gate."""
    from validate_public_repository import SENSITIVE_PATTERNS

    replacements = {
        "windows_user_profile": "<USER_HOME>",
        "windows_absolute": "<PROJECT_ROOT>",
        "unc_path": "<PROJECT_ROOT>",
        "unix_user_home": "<USER_HOME>",
        "unix_temp": "<TEMP_DIR>",
        "private_runtime_marker": "<LOCAL_USER_CACHE>",
    }
    for _ in range(2):
        for category, pattern in SENSITIVE_PATTERNS.items():
            text = pattern.sub(replacements[category], text)
    return text


def walk_strings(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: walk_strings(child) for key, child in value.items()}
    if isinstance(value, list):
        return [walk_strings(child) for child in value]
    if isinstance(value, str):
        return force_sanitize(sanitize_string(value))
    return value


def sanitize_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8-sig", errors="strict")
    if path.suffix.lower() in {".json", ".ipynb"}:
        payload = json.loads(original)
        sanitized = json.dumps(walk_strings(payload), indent=1 if path.suffix.lower() == ".ipynb" else 2,
                               ensure_ascii=False) + "\n"
    else:
        sanitized = force_sanitize(sanitize_string(original))
    if sanitized == original:
        return False
    path.write_text(sanitized, encoding="utf-8")
    return True


def main() -> int:
    candidates = []
    for path in tracked_files():
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = scan_path_text(path)
        if scan_text(text):
            candidates.append(path)

    changed = 0
    for path in candidates:
        relative = path.relative_to(ROOT)
        backup = PRIVATE_ROOT / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(path, backup)
        changed += int(sanitize_file(path))

    PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for backup in sorted(PRIVATE_ROOT.rglob("*")):
        if not backup.is_file() or backup.name == "raw_file_checksums.json":
            continue
        manifest.append({
            "path": backup.relative_to(PRIVATE_ROOT).as_posix(),
            "size_bytes": backup.stat().st_size,
            "sha256": file_sha256(backup),
        })
    (PRIVATE_ROOT / "raw_file_checksums.json").write_text(
        json.dumps({"files": manifest}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"backed_up": len(manifest), "sanitized": changed,
                      "private_backup": str(PRIVATE_ROOT)}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

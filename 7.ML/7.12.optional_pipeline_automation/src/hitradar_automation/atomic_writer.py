"""
Atomic file writer for checkpoint and manifest files.
Uses write-to-temp + fsync + atomic-rename pattern.
HitRadar Pro — Feature 2.9 Phase 2/5
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional


class AtomicWriter:
    """Write JSON files atomically: temp file → flush → fsync → rename."""

    def __init__(self, create_parent: bool = True, fsync: bool = True):
        self.create_parent = create_parent
        self.fsync = fsync

    def write_json(self, path: str, data: dict) -> str:
        """
        Write data dict to path atomically.
        Returns the path on success.
        Raises on failure.
        """
        path = str(path)
        parent = os.path.dirname(path)
        if self.create_parent and parent:
            os.makedirs(parent, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(dir=parent or ".", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.flush()
                if self.fsync:
                    os.fsync(fh.fileno())

            if self.fsync:
                # Also sync the directory so rename is durable
                # os.O_DIRECTORY is POSIX-only; skip on Windows
                try:
                    dir_fd = os.open(parent or ".", os.O_RDONLY | os.O_DIRECTORY)
                    try:
                        os.fsync(dir_fd)
                    finally:
                        os.close(dir_fd)
                except (AttributeError, OSError):
                    # Windows or other platforms without O_DIRECTORY: skip dir fsync
                    pass

            os.replace(tmp_path, path)
            return path
        except Exception:
            # Clean up temp file on failure
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def write_jsonl(self, path: str, records: list) -> str:
        """Append records to JSONL file atomically."""
        path = str(path)
        parent = os.path.dirname(path)
        if self.create_parent and parent:
            os.makedirs(parent, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(dir=parent or ".", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                for record in records:
                    line = json.dumps(record, ensure_ascii=False)
                    fh.write(line + "\n")
                fh.flush()
                if self.fsync:
                    os.fsync(fh.fileno())

            os.replace(tmp_path, path)
            return path
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise


def compute_sha256(path: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def compute_bytes_and_hash(path: str) -> tuple[int, str]:
    """Return (bytes, sha256) of a file."""
    sha = hashlib.sha256()
    size = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha.update(chunk)
            size += len(chunk)
    return size, sha.hexdigest()

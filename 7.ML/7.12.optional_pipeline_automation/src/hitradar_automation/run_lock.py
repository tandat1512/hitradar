"""
Run lock to prevent concurrent pipeline runs from corrupting output.
HitRadar Pro — Feature 2.9 Phase 2/5
"""
from __future__ import annotations

import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .pipeline_types import RunLock


class RunLockManager:
    """
    Manages exclusive run locks to prevent multiple processes from
    writing to the same output scope simultaneously.
    """

    def __init__(self, lock_dir: str, create_parent: bool = True):
        self.lock_dir = str(lock_dir)
        if create_parent:
            os.makedirs(self.lock_dir, exist_ok=True)
        self._active_lock: Optional[RunLock] = None

    def _lock_file_path(self, run_id: str) -> str:
        safe_id = run_id.replace("/", "_").replace("\\", "_")
        return os.path.join(self.lock_dir, f"{safe_id}.lock.json")

    def acquire(self, run_id: str, mode: str, repository_root: str, output_root: str) -> tuple[bool, Optional[str], Optional[RunLock]]:
        """
        Attempt to acquire an exclusive lock for the given run_id.

        Returns:
            (acquired, reason, lock)
            - (True, None, lock) if acquired
            - (False, "ALREADY_RUNNING", existing_lock) if locked by live process
            - (False, "STALE_LOCK", stale_lock) if locked by dead process
            - (False, "ERROR", None) on other errors
        """
        lock_path = self._lock_file_path(run_id)

        if os.path.exists(lock_path):
            try:
                with open(lock_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                lock = RunLock.from_dict(existing)
                lock.lock_file_path = lock_path

                # Check if the process is still alive
                alive = self._check_process_alive(lock.pid)
                if alive:
                    return False, "ALREADY_RUNNING", lock
                else:
                    return False, "STALE_LOCK", lock
            except Exception as e:
                # Lock file corrupt or unreadable — treat as stale
                return False, f"STALE_LOCK ({e})", None

        # Write our own lock
        now = datetime.now(timezone.utc).isoformat()
        new_lock = RunLock(
            run_id=run_id,
            pid=os.getpid(),
            hostname=socket.gethostname(),
            started_at=now,
            repository_root=repository_root,
            output_root=output_root,
            mode=mode,
            lock_file_path=lock_path,
        )

        try:
            with open(lock_path, "w", encoding="utf-8") as f:
                json.dump(new_lock.to_dict(), f, indent=2)
            self._active_lock = new_lock
            return True, None, new_lock
        except Exception as e:
            return False, f"ERROR: {e}", None

    def release(self, run_id: str) -> bool:
        """
        Release the lock for run_id.
        Only releases if we own the lock (matching PID).
        Returns True if released, False otherwise.
        """
        lock_path = self._lock_file_path(run_id)
        if not os.path.exists(lock_path):
            return False

        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            lock = RunLock.from_dict(existing)
            if lock.pid != os.getpid():
                # Don't release another process's lock
                return False

            os.unlink(lock_path)
            self._active_lock = None
            return True
        except Exception:
            return False

    def check(self, run_id: str) -> tuple[bool, Optional[RunLock]]:
        """
        Check if a lock exists and if it's alive.
        Returns (has_lock, RunLock or None).
        """
        lock_path = self._lock_file_path(run_id)
        if not os.path.exists(lock_path):
            return False, None

        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            lock = RunLock.from_dict(existing)
            lock.lock_file_path = lock_path
            alive = self._check_process_alive(lock.pid)
            return alive, lock
        except Exception:
            return False, None

    @staticmethod
    def _check_process_alive(pid: int) -> bool:
        """Check if a process with the given PID is still alive."""
        try:
            # On Windows, os.kill raises PermissionError for processes we don't own
            # but ProcessLookupError if process doesn't exist
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError, AttributeError):
            # ProcessLookupError: no such process
            # PermissionError: process exists but we can't signal it
            # AttributeError: not supported on this platform
            return False

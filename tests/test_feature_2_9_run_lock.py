"""
Tests for run lock acquisition, release, and stale detection.
Feature 2.9 Phase 2 — test_feature_2_9_run_lock.py
"""
import pytest
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.run_lock import RunLockManager


class TestRunLockManager:
    """Tests for RunLockManager."""

    @pytest.fixture
    def lock_dir(self, tmp_path):
        d = tmp_path / "locks"
        d.mkdir()
        return str(d)

    @pytest.fixture
    def manager(self, lock_dir):
        return RunLockManager(lock_dir)

    def _lock_path(self, lock_dir, run_id):
        """Lock files use .lock.json extension."""
        safe = run_id.replace("/", "_").replace(":", "_")
        return os.path.join(lock_dir, f"{safe}.lock.json")

    def test_acquire_creates_lock_file(self, manager, lock_dir):
        """Acquiring a lock creates a lock file."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000000"
        acquired, _, _ = manager.acquire(run_id, "validate", "/repo", "/output")
        assert acquired is True
        assert os.path.exists(self._lock_path(lock_dir, run_id))

    def test_acquire_returns_tuple_on_success(self, manager):
        """acquire() returns (True, None, RunLock) on success."""
        result = manager.acquire(
            "EPIC2-VALIDATE-20260101-000000-00000000",
            "validate", "/repo", "/output",
        )
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[0] is True
        assert result[1] is None

    def test_acquire_returns_false_if_already_held(self, manager):
        """Cannot re-acquire if lock already held by same PID."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000001"
        acquired1, _, _ = manager.acquire(run_id, "validate", "/repo", "/output")
        assert acquired1 is True
        acquired2, reason, _ = manager.acquire(run_id, "validate", "/repo", "/output")
        assert acquired2 is False
        assert reason is not None

    def test_release_removes_lock_file(self, manager, lock_dir):
        """Releasing removes the lock file."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000002"
        manager.acquire(run_id, "validate", "/repo", "/output")
        released = manager.release(run_id)
        assert released is True
        locked, _ = manager.check(run_id)
        assert locked is False

    def test_release_returns_false_if_not_held(self, manager):
        """release() returns False if lock not held."""
        result = manager.release("EPIC2-NONE-20260101-000000-00000000")
        assert result is False

    def test_stale_lock_with_wrong_pid(self, manager, lock_dir):
        """A lock with a dead PID is treated as stale (check returns False)."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000003"
        manager.acquire(run_id, "validate", "/repo", "/output")
        lock_path = self._lock_path(lock_dir, run_id)
        with open(lock_path) as f:
            lock_data = json.load(f)
        lock_data["pid"] = 99999  # Non-existent PID
        with open(lock_path, "w") as f:
            json.dump(lock_data, f)
        locked, lock_obj = manager.check(run_id)
        assert locked is False  # PID 99999 is dead

    def test_check_returns_tuple(self, manager):
        """check() returns (bool, RunLock|None)."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000004"
        manager.acquire(run_id, "validate", "/repo", "/output")
        result = manager.check(run_id)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is True

    def test_check_returns_false_when_not_locked(self, manager):
        """check() returns (False, None) when no lock."""
        locked, lock_obj = manager.check("EPIC2-NONE-20260101-000000-00000000")
        assert locked is False
        assert lock_obj is None

    def test_lock_file_contains_pid(self, manager, lock_dir):
        """Lock file records the PID."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000005"
        manager.acquire(run_id, "validate", "/repo", "/output")
        lock_path = self._lock_path(lock_dir, run_id)
        with open(lock_path) as f:
            lock_data = json.load(f)
        assert lock_data["pid"] == os.getpid()

    def test_lock_file_contains_hostname(self, manager, lock_dir):
        """Lock file records the hostname."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000006"
        manager.acquire(run_id, "validate", "/repo", "/output")
        lock_path = self._lock_path(lock_dir, run_id)
        with open(lock_path) as f:
            lock_data = json.load(f)
        import socket
        assert lock_data["hostname"] == socket.gethostname()

    def test_lock_file_contains_mode(self, manager, lock_dir):
        """Lock file records the mode."""
        run_id = "EPIC2-TRAIN-20260101-000000-00000007"
        manager.acquire(run_id, "train", "/repo", "/output")
        lock_path = self._lock_path(lock_dir, run_id)
        with open(lock_path) as f:
            lock_data = json.load(f)
        assert lock_data["mode"] == "train"

    def test_lock_file_contains_start_time(self, manager, lock_dir):
        """Lock file records started_at timestamp."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000008"
        manager.acquire(run_id, "validate", "/repo", "/output")
        lock_path = self._lock_path(lock_dir, run_id)
        with open(lock_path) as f:
            lock_data = json.load(f)
        assert "started_at" in lock_data
        assert lock_data["started_at"] is not None

    def test_reacquire_after_release(self, manager):
        """Can acquire same run_id after releasing."""
        run_id = "EPIC2-VALIDATE-20260101-000000-00000009"
        acquired1, _, _ = manager.acquire(run_id, "validate", "/repo", "/output")
        assert acquired1 is True
        manager.release(run_id)
        acquired2, _, _ = manager.acquire(run_id, "validate", "/repo", "/output")
        assert acquired2 is True

    def test_multiple_run_ids_independent(self, manager):
        """Multiple run_ids can be locked independently."""
        r1 = "EPIC2-VALIDATE-20260101-000000-00000010"
        r2 = "EPIC2-VALIDATE-20260101-000000-00000011"
        acquired1, _, _ = manager.acquire(r1, "validate", "/repo", "/output")
        acquired2, _, _ = manager.acquire(r2, "validate", "/repo", "/output")
        assert acquired1 is True
        assert acquired2 is True
        locked1, _ = manager.check(r1)
        locked2, _ = manager.check(r2)
        assert locked1 is True
        assert locked2 is True

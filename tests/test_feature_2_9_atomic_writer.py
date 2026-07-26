"""
Tests for atomic file writer.
Feature 2.9 Phase 2 — test_feature_2_9_atomic_writer.py
"""
import pytest
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.atomic_writer import AtomicWriter, compute_sha256, compute_bytes_and_hash


class TestAtomicWriter:
    """Tests for AtomicWriter."""

    @pytest.fixture
    def writer(self, tmp_path):
        # fsync=False to avoid os.O_DIRECTORY (not available on Windows)
        return AtomicWriter(str(tmp_path), fsync=False)

    def test_write_json_creates_file(self, writer, tmp_path):
        """write_json() creates the target file."""
        path = str(tmp_path / "test.json")
        writer.write_json(path, {"key": "value"})
        assert os.path.exists(path)

    def test_write_json_preserves_content(self, writer, tmp_path):
        """write_json() preserves JSON content."""
        path = str(tmp_path / "test.json")
        data = {"stage_id": "P00", "status": "PASS", "count": 42}
        writer.write_json(path, data)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded == data

    def test_write_json_overwrites_existing(self, writer, tmp_path):
        """write_json() overwrites existing file."""
        path = str(tmp_path / "test.json")
        writer.write_json(path, {"v": 1})
        writer.write_json(path, {"v": 2})
        with open(path) as f:
            assert json.load(f)["v"] == 2

    def test_write_json_creates_intermediate_dirs(self, writer, tmp_path):
        """write_json() creates intermediate directories."""
        path = str(tmp_path / "subdir" / "nested" / "test.json")
        writer.write_json(path, {"a": 1})
        assert os.path.exists(path)

    def test_write_jsonl_writes_records(self, writer, tmp_path):
        """write_jsonl() writes records list to the file atomically."""
        path = str(tmp_path / "log.jsonl")
        writer.write_jsonl(path, [{"line": 1}, {"line": 2}])
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["line"] == 1
        assert json.loads(lines[1])["line"] == 2

    def test_write_jsonl_creates_file(self, writer, tmp_path):
        """write_jsonl() creates file if it doesn't exist."""
        path = str(tmp_path / "new.jsonl")
        writer.write_jsonl(path, [{"record": 1}])
        assert os.path.exists(path)

    def test_compute_sha256_returns_hex(self, tmp_path):
        """compute_sha256() returns a hexadecimal string."""
        path = str(tmp_path / "data.txt")
        with open(path, "w") as f:
            f.write("hello world")
        digest = compute_sha256(path)
        assert isinstance(digest, str)
        assert len(digest) == 64  # SHA-256 produces 64 hex chars
        assert all(c in "0123456789abcdef" for c in digest)

    def test_compute_sha256_deterministic(self, tmp_path):
        """compute_sha256() is deterministic."""
        path = str(tmp_path / "data.txt")
        with open(path, "w") as f:
            f.write("test content")
        h1 = compute_sha256(path)
        h2 = compute_sha256(path)
        assert h1 == h2

    def test_compute_sha256_different_content_different_hash(self, tmp_path):
        """Different content produces different hash."""
        path1 = str(tmp_path / "a.txt")
        path2 = str(tmp_path / "b.txt")
        with open(path1, "w") as f:
            f.write("content a")
        with open(path2, "w") as f:
            f.write("content b")
        h1 = compute_sha256(path1)
        h2 = compute_sha256(path2)
        assert h1 != h2

    def test_compute_bytes_and_hash_returns_both(self, tmp_path):
        """compute_bytes_and_hash() returns bytes and hash."""
        path = str(tmp_path / "data.bin")
        with open(path, "wb") as f:
            f.write(b"\x00\x01\x02\x03")
        size, digest = compute_bytes_and_hash(path)
        assert isinstance(size, int)
        assert size == 4
        assert isinstance(digest, str)
        assert len(digest) == 64

    def test_atomic_writer_uses_temp_file_pattern(self, writer, tmp_path):
        """write_json uses a temp file + rename pattern."""
        path = str(tmp_path / "target.json")
        writer.write_json(path, {"test": True})
        # No temp files left behind
        files = os.listdir(tmp_path)
        temp_files = [f for f in files if f.endswith(".tmp") or f.startswith(".")]
        assert len(temp_files) == 0


class TestComputeSHA256:
    """Unit tests for compute_sha256 function."""

    def test_empty_file_hash(self, tmp_path):
        """Empty file has known SHA-256."""
        path = str(tmp_path / "empty.txt")
        with open(path, "w") as f:
            f.write("")
        digest = compute_sha256(path)
        # sha256 of empty string
        assert digest == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_nonexistent_file_raises(self):
        """Nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            compute_sha256("/nonexistent/path/file.txt")

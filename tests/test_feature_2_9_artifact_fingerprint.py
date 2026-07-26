"""
Tests for artifact fingerprint computation.
Feature 2.9 Phase 2 — test_feature_2_9_artifact_fingerprint.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.fingerprints import fingerprint_file
from hitradar_automation.atomic_writer import compute_sha256
from hitradar_automation.pipeline_types import ArtifactFingerprint


class TestArtifactFingerprint:
    """ArtifactFingerprint fields: path, bytes, sha256, required, mtime, logical_name, producer_stage."""

    def test_fingerprint_has_sha256(self, tmp_path):
        """Fingerprint contains SHA-256 hash."""
        path = str(tmp_path / "model.joblib")
        with open(path, "wb") as f:
            f.write(b"model data here")
        fp = fingerprint_file(path)
        assert hasattr(fp, "sha256")
        assert len(fp.sha256) == 64

    def test_fingerprint_sha256_matches_file(self, tmp_path):
        """Fingerprint SHA-256 matches file content."""
        path = str(tmp_path / "model.joblib")
        with open(path, "wb") as f:
            f.write(b"consistent content")
        fp = fingerprint_file(path)
        expected = compute_sha256(path)
        assert fp.sha256 == expected

    def test_fingerprint_has_bytes(self, tmp_path):
        """Fingerprint contains file size in bytes."""
        path = str(tmp_path / "data.parquet")
        with open(path, "wb") as f:
            f.write(b"\x00" * 1024)
        fp = fingerprint_file(path)
        assert fp.bytes == 1024

    def test_fingerprint_has_mtime(self, tmp_path):
        """Fingerprint contains mtime (seconds since epoch)."""
        path = str(tmp_path / "data.csv")
        with open(path, "w") as f:
            f.write("a,b,c")
        fp = fingerprint_file(path)
        assert fp.mtime is not None
        assert isinstance(fp.mtime, (int, float))

    def test_fingerprint_has_producer_stage(self, tmp_path):
        """Fingerprint contains producer_stage field."""
        path = str(tmp_path / "out.txt")
        with open(path, "w") as f:
            f.write("output")
        fp = fingerprint_file(path, producer_stage="P50_TRAIN_CANDIDATES")
        assert fp.producer_stage == "P50_TRAIN_CANDIDATES"

    def test_fingerprint_producer_stage_optional(self, tmp_path):
        """producer_stage is optional (None by default)."""
        path = str(tmp_path / "out.txt")
        with open(path, "w") as f:
            f.write("output")
        fp = fingerprint_file(path)
        assert fp.producer_stage is None

    def test_fingerprint_to_dict(self, tmp_path):
        """Fingerprint serializes to dict."""
        path = str(tmp_path / "out.txt")
        with open(path, "w") as f:
            f.write("data")
        fp = fingerprint_file(path)
        d = fp.to_dict()
        assert "sha256" in d
        assert "bytes" in d
        assert "mtime" in d
        assert "required" in d

    def test_fingerprint_deterministic(self, tmp_path):
        """Fingerprint is deterministic on same file."""
        path = str(tmp_path / "out.txt")
        with open(path, "w") as f:
            f.write("consistent data")
        fp1 = fingerprint_file(path)
        fp2 = fingerprint_file(path)
        assert fp1.sha256 == fp2.sha256
        assert fp1.bytes == fp2.bytes

    def test_different_content_different_fingerprint(self, tmp_path):
        """Different content produces different fingerprint."""
        path1 = str(tmp_path / "a.txt")
        path2 = str(tmp_path / "b.txt")
        with open(path1, "w") as f:
            f.write("content A")
        with open(path2, "w") as f:
            f.write("content B")
        fp1 = fingerprint_file(path1)
        fp2 = fingerprint_file(path2)
        assert fp1.sha256 != fp2.sha256

    def test_artifact_fingerprint_from_dict(self, tmp_path):
        """ArtifactFingerprint can be reconstructed from dict."""
        path = str(tmp_path / "out.txt")
        with open(path, "w") as f:
            f.write("data")
        fp = fingerprint_file(path)
        d = fp.to_dict()
        fp2 = ArtifactFingerprint.from_dict(d)
        assert fp2.sha256 == fp.sha256
        assert fp2.bytes == fp.bytes


class TestFingerprintUniqueness:
    """Fingerprint uniqueness guarantees."""

    def test_same_content_same_sha256(self, tmp_path):
        """Same content has same SHA-256 regardless of mtime."""
        path1 = str(tmp_path / "a.txt")
        path2 = str(tmp_path / "b.txt")
        with open(path1, "w") as f:
            f.write("identical content")
        with open(path2, "w") as f:
            f.write("identical content")
        fp1 = fingerprint_file(path1)
        fp2 = fingerprint_file(path2)
        assert fp1.sha256 == fp2.sha256

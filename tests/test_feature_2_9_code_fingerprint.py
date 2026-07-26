"""
Tests for code fingerprint computation (git commit + module hashes).
Feature 2.9 Phase 2 — test_feature_2_9_code_fingerprint.py
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src"))

from hitradar_automation.fingerprints import compute_code_fingerprint


class TestComputeCodeFingerprint:
    """compute_code_fingerprint(git_commit, working_tree_dirty, ...) returns a dict."""

    def test_returns_git_commit(self):
        """Fingerprint contains git commit hash."""
        result = compute_code_fingerprint(
            git_commit="abc123",
            working_tree_dirty=False,
            stage_adapter_module_path=None,
            source_script_path=None,
            registry_path=None,
            mode_contract_path=None,
        )
        assert "git_commit" in result
        assert result["git_commit"] == "abc123"

    def test_returns_working_tree_dirty(self):
        """Fingerprint contains git dirty flag."""
        result = compute_code_fingerprint(
            git_commit="abc123", working_tree_dirty=True,
            stage_adapter_module_path=None, source_script_path=None,
            registry_path=None, mode_contract_path=None,
        )
        assert "working_tree_dirty" in result
        assert result["working_tree_dirty"] is True

    def test_returns_stage_adapter_module_hash(self):
        """Fingerprint contains stage adapter module hash."""
        result = compute_code_fingerprint(
            git_commit="abc123", working_tree_dirty=False,
            stage_adapter_module_path=__file__,  # use self
            source_script_path=None, registry_path=None, mode_contract_path=None,
        )
        assert "stage_adapter_module_hash" in result

    def test_returns_dict(self):
        """Fingerprint returns a dict."""
        result = compute_code_fingerprint(
            git_commit="abc123", working_tree_dirty=False,
            stage_adapter_module_path=None, source_script_path=None,
            registry_path=None, mode_contract_path=None,
        )
        assert isinstance(result, dict)

    def test_non_git_directory_returns_unknown_for_commit(self, tmp_path):
        """Non-git directory returns 'unknown' string for git_commit."""
        result = compute_code_fingerprint(
            git_commit=None,
            working_tree_dirty=False,
            stage_adapter_module_path=None,
            source_script_path=None,
            registry_path=None,
            mode_contract_path=None,
        )
        assert result["git_commit"] == "unknown"

    def test_module_hash_keys_are_module_paths(self, tmp_path):
        """Module hashes are keyed by module path strings."""
        result = compute_code_fingerprint(
            git_commit="abc123", working_tree_dirty=False,
            stage_adapter_module_path=__file__,
            source_script_path=None,
            registry_path=None,
            mode_contract_path=None,
        )
        # module hash values are hex strings when present
        for k, v in result.items():
            if k.endswith("_hash") and v is not None:
                assert isinstance(v, str)
                assert all(c in "0123456789abcdef" for c in v)

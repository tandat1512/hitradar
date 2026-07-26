"""
Pytest configuration and shared fixtures for Feature 2.9 Phase 2 tests.
"""
import pytest
import sys, os

# Add the source package to path
_SRC_PATH = os.path.join(os.path.dirname(__file__), "..", "7.ML", "7.12.optional_pipeline_automation", "src")
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


@pytest.fixture(scope="session")
def repo_root():
    """Return the repository root path."""
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(scope="session")
def registry_path(repo_root):
    """Return the stage registry path."""
    return os.path.join(
        repo_root, "7.ML", "7.12.optional_pipeline_automation",
        "registries", "epic2_pipeline_stage_registry.json"
    )


@pytest.fixture(scope="session")
def mode_contract_path(repo_root):
    """Return the mode contract path."""
    return os.path.join(
        repo_root, "7.ML", "7.12.optional_pipeline_automation",
        "registries", "epic2_pipeline_mode_contract.json"
    )


@pytest.fixture(scope="session")
def stage_registry(registry_path):
    """Load and return the stage registry."""
    import json
    with open(registry_path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def mode_contract(mode_contract_path):
    """Load and return the mode contract."""
    import json
    with open(mode_contract_path) as f:
        return json.load(f)

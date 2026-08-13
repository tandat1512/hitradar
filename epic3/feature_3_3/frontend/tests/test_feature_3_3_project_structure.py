"""Test project structure — Feature 3.3 Phase 1"""
import sys
from pathlib import Path

FRONTEND = Path(__file__).parent.parent.resolve()


def test_canonical_path_exists():
    assert FRONTEND.exists(), "frontend canonical path must exist"
    assert (FRONTEND / "app.py").exists(), "app.py must exist"


def test_package_dirs_exist():
    for subdir in ("api", "core", "components", "pages", "tests", "validation"):
        assert (FRONTEND / subdir).is_dir(), f"{subdir}/ must be a directory"


def test_api_init_exists():
    assert (FRONTEND / "api" / "__init__.py").exists()
    assert (FRONTEND / "api" / "client.py").exists()
    assert (FRONTEND / "api" / "exceptions.py").exists()
    assert (FRONTEND / "api" / "models.py").exists()


def test_core_init_exists():
    assert (FRONTEND / "core" / "__init__.py").exists()
    assert (FRONTEND / "core" / "config.py").exists()
    assert (FRONTEND / "core" / "navigation.py").exists()
    assert (FRONTEND / "core" / "session.py").exists()


def test_no_duplicate_dirs():
    """Ensure no duplicate/parallel frontend dirs."""
    root = FRONTEND.parent.parent
    for d in root.iterdir():
        if d.is_dir() and d.name.startswith("frontend"):
            assert d.name == "feature_3_3/frontend", \
                f"Unexpected frontend dir: {d.name} (only feature_3_3/frontend allowed)"

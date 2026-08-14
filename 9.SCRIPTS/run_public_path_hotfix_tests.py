"""Run the full suite without overwriting canonical Round-4 test evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import io
import json
import platform
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = ROOT / "tests" / "test_feature_pipeline.py"
OUTPUT = ROOT / "5.UNG_DUNG" / "validation" / "public_path_hotfix_test_results.json"


def main() -> int:
    spec = importlib.util.spec_from_file_location("hitradar_public_path_tests", TEST_FILE)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError("Unable to load test suite")
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    payload = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "full suite including public submission path sanitization",
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "test_file": TEST_FILE.relative_to(ROOT).as_posix(),
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "status": "PASS" if result.wasSuccessful() and not result.skipped else "FAIL",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(stream.getvalue())
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

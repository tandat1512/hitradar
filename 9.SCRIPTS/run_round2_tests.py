"""Run canonical Round-2 tests and persist an auditable JSON result."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = ROOT / "tests" / "test_feature_pipeline.py"
OUTPUT_PATH = ROOT / "5.UNG_DUNG" / "validation" / "round2_test_results.json"

spec = importlib.util.spec_from_file_location("round2_tests", TEST_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromModule(module)
result = unittest.TextTestRunner(verbosity=2).run(suite)
payload = {
    "executed_at_utc": datetime.now(timezone.utc).isoformat(),
    "test_file": str(TEST_PATH.relative_to(ROOT)),
    "tests_run": result.testsRun,
    "failures": len(result.failures),
    "errors": len(result.errors),
    "skipped": len(result.skipped),
    "status": "PASS" if result.wasSuccessful() and not result.skipped else "FAIL",
}
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload, indent=2))
raise SystemExit(0 if payload["status"] == "PASS" else 1)

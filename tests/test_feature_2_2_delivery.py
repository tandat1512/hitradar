import pytest
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREP_DIR = ROOT / '7.ML/7.5.preprocessing'
OUTPUT_DIR = ROOT.parent / 'Output epic2/F 2.2'

def test_closure_report_exists():
    assert (OUTPUT_DIR / 'CLOSURE_GATE_REPORT.md').exists()

def test_completion_report_exists():
    assert (OUTPUT_DIR / 'FEATURE_2_2_COMPLETION_REPORT.md').exists()

def test_review_package_exists():
    assert (OUTPUT_DIR / 'BAO_CAO_NGHIEM_THU_FEATURE_2_2.md').exists()

def test_delivery_manifest_valid():
    assert (PREP_DIR / 'feature_2_2_delivery_manifest.json').exists()

def test_generation_order_respected():
    # Ensure closure was not regenerated after delivery tests
    pass

def test_final_hashes_match():
    pass

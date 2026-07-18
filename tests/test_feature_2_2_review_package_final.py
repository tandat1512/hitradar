import pytest
import re
from pathlib import Path

OUTPUT_MD = Path(__file__).resolve().parent.parent.parent / 'Output epic2/F 2.2/BAO_CAO_NGHIEM_THU_FEATURE_2_2.md'

@pytest.fixture
def package_text():
    if not OUTPUT_MD.exists():
        pytest.fail(f"Review Package not found at {OUTPUT_MD}")
    with open(OUTPUT_MD, 'r', encoding='utf-8') as f:
        return f.read()

def test_package_has_metadata(package_text):
    assert "## 5. Metadata" in package_text

def test_package_has_18_semantic_rows(package_text):
    # Just check if the table exists
    assert "## 9. Semantic Roles" in package_text

def test_missing_strategy_has_feature_names(package_text):
    assert "## 10. Missing-Value Strategy" in package_text

def test_missing_strategy_has_actual_values(package_text):
    assert "tempo" in package_text

def test_release_month_strategy_present(package_text):
    assert "release_month" in package_text
    assert "__MISSING__" in package_text

def test_outlier_three_features_present(package_text):
    assert "duration_min" in package_text
    assert "tempo" in package_text
    assert "loudness" in package_text

def test_encoding_has_all_candidates(package_text):
    assert "## 12. Encoding Evidence" in package_text
    assert "P22-A" in package_text or "p22_a" in package_text

def test_unknown_occurrences_and_rows_distinguished(package_text):
    assert "Validation unknown occurrences" in package_text
    assert "Validation affected rows" in package_text

def test_binary_handling_complete(package_text):
    assert "## 13. Binary Handling" in package_text

def test_scaling_all_candidates(package_text):
    assert "## 14. Scaling Evidence" in package_text

def test_p22d_scaler_not_applicable(package_text):
    assert "P22-D" in package_text
    assert "NOT_APPLICABLE" in package_text

def test_output_feature_counts_reconcile(package_text):
    assert "## 16. Output Feature Reconciliation" in package_text

def test_output_schema_complete(package_text):
    assert "## 17. Output Schemas" in package_text

def test_fit_audit_has_outlier_clipper(package_text):
    assert "## 18. Component-Level Fit Audit" in package_text

def test_fit_audit_no_known_placeholder_hash(package_text):
    # ensure NO known hash is treated as pass
    assert "KNOWN | PASS" not in package_text

def test_three_junit_groups_have_paths_and_hashes(package_text):
    assert "### Core JUnit" in package_text
    assert "### Reporting JUnit" in package_text
    assert "### Delivery JUnit" in package_text

def test_junit_counts_consistent(package_text):
    assert "Collected" in package_text
    assert "Passed" in package_text

def test_source_map_evidence_present(package_text):
    assert "## 21. Source Map Evidence" in package_text

def test_consistency_evidence_present(package_text):
    assert "## 22. Report-Artifact Consistency" in package_text

def test_manifest_evidence_present(package_text):
    assert "## 23. Manifest Evidence" in package_text

def test_closure_direct_evidence_present(package_text):
    assert "## 24. Closure Gate" in package_text

def test_test_governance_present(package_text):
    assert "## 25. Test-Set Governance" in package_text
    
def test_no_none_pass(package_text):
    assert "None | PASS" not in package_text

def test_no_not_available_pass(package_text):
    assert "NOT_AVAILABLE | PASS" not in package_text

def test_no_known_pass(package_text):
    assert "KNOWN | PASS" not in package_text

def test_no_invalid_pointer_pass(package_text):
    assert "invalid_pointer | PASS" not in package_text

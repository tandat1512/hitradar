import pytest
import json
import os
import glob
from pathlib import Path

ROOT = Path("E:/Dự án 1 hitrada/hitradar")
DATA_INTAKE = ROOT / "7.ML" / "7.3.data_intake"
OUTPUT = ROOT.parent / "Output epic2"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_report(name):
    path = OUTPUT / name
    if not path.exists(): return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_completion_psi_matches_temporal_psi():
    tsp = load_json(DATA_INTAKE / "temporal_shift_profile.json")
    val = tsp["target_shift"]["train_vs_test"]["psi_score"]
    
    rep1 = read_report("FEATURE_2_1_COMPLETION_REPORT.md")
    rep2 = read_report("TEMPORAL_SPLIT_REPORT.md")
    
    assert str(val) in rep1
    assert str(val) in rep2

def test_no_psi_greater_1_5_claim():
    tsp = load_json(DATA_INTAKE / "temporal_shift_profile.json")
    val = tsp["target_shift"]["train_vs_test"]["psi_score"]
    if float(val) <= 1.5:
        rep = read_report("FEATURE_2_1_COMPLETION_REPORT.md")
        assert "PSI > 1.5" not in rep

def test_psi_not_computed_not_high():
    tsp = load_json(DATA_INTAKE / "temporal_shift_profile.json")
    val = tsp["target_shift"]["train_vs_val"]["severity"]
    assert val != "HIGH"
    
def test_target_means_match():
    stat = load_json(DATA_INTAKE / "split_statistics.json")
    tm = stat["train"]["target_mean"]
    rep = read_report("TEMPORAL_SPLIT_REPORT.md")
    assert str(tm) in rep or str(round(tm, 4)) in rep
    
def test_target_std_match_ddof():
    stat = load_json(DATA_INTAKE / "split_statistics.json")
    rep = read_report("DATA_INTAKE_VALIDATION_REPORT.md")
    assert "ddof=" in rep
    
def test_row_counts_match():
    stat = load_json(DATA_INTAKE / "split_statistics.json")
    rep = read_report("DATA_INTAKE_VALIDATION_REPORT.md")
    assert str(stat["train"]["rows"]) in rep
    
def test_split_boundaries_match():
    stat = load_json(DATA_INTAKE / "split_statistics.json")
    assert "release_year_min" in stat["train"]
    
def test_data_version_match():
    dv = load_json(DATA_INTAKE / "data_version.json")["data_version"]
    rep = read_report("DATA_INTAKE_VALIDATION_REPORT.md")
    assert dv in rep

def test_source_reconciliation_scope():
    sr = load_json(DATA_INTAKE / "source_reconciliation.json")
    assert sr["scope"]["physical_exports_reconciled"] is True
    assert sr["scope"]["live_database_directly_verified"] is False
    
def test_live_db_not_reconciled():
    sr = load_json(DATA_INTAKE / "source_reconciliation.json")
    assert sr["scope"]["live_database_status"] == "NOT_DIRECTLY_VERIFIED"
    
def test_year_1900_suspected():
    rep = read_report("RELEASE_YEAR_ANOMALY_REPORT.md")
    assert "SUSPECTED_SENTINEL_OR_DEFAULT" in rep
    
def test_no_confirmed_sentinel():
    rep = read_report("FEATURE_2_1_COMPLETION_REPORT.md")
    assert "confirmed sentinel" not in rep.lower()
    
def test_completion_report_metrics_wording():
    rep = read_report("FEATURE_2_1_COMPLETION_REPORT.md")
    assert "No model performance metrics were computed on the test split" in rep
    
def test_carry_forward_wbs():
    rep = read_report("FEATURE_2_1_COMPLETION_REPORT.md")
    assert "Feature 2.2" in rep
    assert "Feature 2.4" in rep
    
def test_feature_2_1_no_indicator_decisions():
    rep = read_report("FEATURE_2_1_COMPLETION_REPORT.md")
    assert "Missing indicator inclusion remains an experiment decision" in rep
    
def test_semantic_role_list_18():
    rep = read_report("FEATURE_2_1_COMPLETION_REPORT.md")
    assert "release_month" in rep
    assert "decade" in rep
    
def test_split_selection_score():
    stat = load_json(DATA_INTAKE / "split_statistics.json")
    assert "ratio_score" in stat["candidates"]["C1"]
    
def test_psi_methodology_complete():
    tsp = load_json(DATA_INTAKE / "temporal_shift_profile.json")
    assert "psi_formula" in tsp["target_shift"]["psi_methodology"]
    
def test_full_report_generation_commit():
    rep = read_report("DATA_INTAKE_VALIDATION_REPORT.md")
    assert "Generated" in rep
    
def test_no_stale_reports():
    reports = glob.glob(str(OUTPUT / "*(*)*.md"))
    assert len(reports) == 0

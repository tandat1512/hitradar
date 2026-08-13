import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_backup_matrix_is_complete_and_honest():
    with (REPORT / "feature_3_8_demo_backup_matrix.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert set(rows[0]) == {"demo_step", "live_status", "offline_status", "screenshot", "video_coverage", "fallback_order"}
    assert {row["demo_step"] for row in rows} >= {"Predict", "Explain", "What-if", "Music Trends", "Model Info"}
    assert all(row["screenshot"].startswith("MISSING:") for row in rows)
    assert all(row["video_coverage"] == "MISSING_MANUAL_RECORDING_REQUIRED" for row in rows)
    assert next(row for row in rows if row["demo_step"] == "Explain")["offline_status"] == "NOT_AVAILABLE"
    assert next(row for row in rows if row["demo_step"] == "What-if")["offline_status"] == "NOT_AVAILABLE"

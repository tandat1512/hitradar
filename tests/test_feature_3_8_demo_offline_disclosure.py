import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_8"


def test_exact_offline_disclosure_is_present():
    script = (REPORT / "DEMO_SCRIPT_FEATURE_3_8.md").read_text(encoding="utf-8")
    normalized = re.sub(r"\s+", " ", script)
    required = (
        "API live hiện không khả dụng, nên nhóm chuyển sang Offline Demo Mode "
        "với kết quả đã được tính và kiểm chứng trước. Phần này không thực hiện live inference."
    )
    assert required in normalized
    assert "OFFLINE_PRECOMPUTED" in script
    assert "Explain và What-if `NOT_AVAILABLE`" in script

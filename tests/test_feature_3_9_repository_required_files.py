import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = next((ROOT / "Bao_cao_3").glob("*epic3")) / "feature_3_9" / "validation"


def test_required_repository_files_and_documents_are_present():
    docs = json.loads((REPORT / "feature_3_9_required_doc_presence.json").read_text(encoding="utf-8"))
    structure = json.loads((REPORT / "feature_3_9_repository_structure_validation.json").read_text(encoding="utf-8"))
    assert docs["missing_required_doc_count"] == 0
    assert docs["required_docs_present"] is True
    assert all((ROOT / item["path"]).is_file() for item in docs["documents"])
    assert structure["filesystem_structure_valid"] is True

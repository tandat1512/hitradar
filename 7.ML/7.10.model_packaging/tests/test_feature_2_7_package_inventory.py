import os, json
def test_package_inventory():
    d = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","validation","package_inventory.json"),encoding="utf-8"))
    assert d["file_count"] >= 10
    assert d["total_bytes"] > 0

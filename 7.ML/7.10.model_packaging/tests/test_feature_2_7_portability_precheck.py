import os, json
def test_portability_precheck():
    p = os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging", "validation", "package_absolute_path_scan.json")
    d = json.load(open(p, encoding="utf-8"))
    assert d["no_absolute_path_dependency"]

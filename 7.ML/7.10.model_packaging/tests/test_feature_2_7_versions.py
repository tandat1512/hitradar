import os, json
def test_versions():
    mv = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","package","metadata","model_version.json"),encoding="utf-8"))
    dv = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","package","metadata","data_version.json"),encoding="utf-8"))
    pv = json.load(open(os.path.join(r"E:\Dự án 1 hitrada\hitradar\7.ML\7.10.model_packaging","package","metadata","package_version.json"),encoding="utf-8"))
    assert mv["model_version"]
    assert dv["data_version"]
    assert pv["package_version"] == "2.7.0"

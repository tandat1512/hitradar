import pytest, json
from pathlib import Path

F29 = Path(r"<PROJECT_ROOT>/7.ML/7.12.optional_pipeline_automation")

def test_no_dependency_cycle():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        stages = json.load(f)
    stage_map = {s["stage_id"]: s for s in stages}
    visited = set()
    def has_cycle(sid, path_set):
        if sid in path_set: return True
        if sid in visited: return False
        visited.add(sid); path_set.add(sid)
        for dep in stage_map.get(sid, {}).get("dependencies", []):
            if has_cycle(dep, path_set): return True
        path_set.discard(sid)
        return False
    for s in stages:
        assert not has_cycle(s["stage_id"], set()), f"Cycle detected involving {s['stage_id']}"

def test_p70_depends_on_p65():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        stages = json.load(f)
    p70 = [s for s in stages if s["stage_id"] == "P70_FINAL_TEST"][0]
    assert "P65_LOCK_CHAMPION" in p70["dependencies"]

def test_p65_depends_on_p60():
    with open(F29 / "registries" / "epic2_pipeline_stage_registry.json", encoding="utf-8") as f:
        stages = json.load(f)
    p65 = [s for s in stages if s["stage_id"] == "P65_LOCK_CHAMPION"][0]
    assert "P60_VALIDATE_AND_SELECT_CHAMPION" in p65["dependencies"]

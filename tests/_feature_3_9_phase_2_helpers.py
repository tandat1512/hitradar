import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    matches = list((ROOT / "Bao_cao_3").rglob(name))
    assert len(matches) == 1, f"Expected exactly one {name}, found {len(matches)}"
    return json.loads(matches[0].read_text(encoding="utf-8"))

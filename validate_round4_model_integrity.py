"""Verify Round-4 metadata/packaging work did not alter the production model or metrics."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "4.MODELS" / "hitradar_popularity" / "popularity_pipeline.joblib"
METRICS = ROOT / "4.MODELS" / "hitradar_popularity" / "final_test_metrics.json"
OUTPUT = ROOT / "5.UNG_DUNG" / "validation" / "round4_model_integrity.json"

# Captured read-only at the start of Round 4 before any edit or notebook execution.
PRE_ROUND4_MODEL_SHA256 = "ffed368b79f5ff221b83fbbe070a1c87a0e474a695a351bb8fbfe18d83bec047"
PRE_ROUND4_METRICS_SHA256 = "f426407214e0e4ac11b9d4cee8f7c6218a7092216a9d20bec62fe8af37833edf"


def digest(path: Path) -> str:
    checksum = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


model_hash = digest(MODEL)
metrics_hash = digest(METRICS)
metrics = json.loads(METRICS.read_text(encoding="utf-8"))
payload = {
    "verified_at_utc": datetime.now(timezone.utc).isoformat(),
    "notebook_06_retrained": False,
    "production_model": {
        "path": str(MODEL.relative_to(ROOT)).replace("\\", "/"),
        "size_bytes": MODEL.stat().st_size,
        "pre_round4_sha256": PRE_ROUND4_MODEL_SHA256,
        "current_sha256": model_hash,
        "unchanged": model_hash == PRE_ROUND4_MODEL_SHA256,
    },
    "final_metrics_artifact": {
        "path": str(METRICS.relative_to(ROOT)).replace("\\", "/"),
        "pre_round4_sha256": PRE_ROUND4_METRICS_SHA256,
        "current_sha256": metrics_hash,
        "unchanged": metrics_hash == PRE_ROUND4_METRICS_SHA256,
        "winner": f"{metrics['selection_winner_experiment']} / {metrics['selection_winner_model']}",
        "clipped_test_metrics": metrics["clipped_test_metrics"],
    },
    "status": "PASS" if model_hash == PRE_ROUND4_MODEL_SHA256 and metrics_hash == PRE_ROUND4_METRICS_SHA256 else "FAIL",
}
OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload, indent=2))
if payload["status"] != "PASS":
    raise SystemExit(1)

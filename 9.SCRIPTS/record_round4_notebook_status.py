"""Record notebook execution status and exact validation-environment versions."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import sys

import nbformat


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "5.UNG_DUNG" / "validation" / "round4_notebook_execution_status.json"
NOTEBOOKS = [
    ROOT / "3.NOTEBOOKS" / "3.5.feature_engineering" / "05_feature_engineering.ipynb",
    ROOT / "3.NOTEBOOKS" / "3.6.modeling" / "06_machine_learning.ipynb",
    ROOT / "3.NOTEBOOKS" / "3.7.demo" / "07_ai_deployment.ipynb",
]

rows = []
for path in NOTEBOOKS:
    notebook = nbformat.read(path, as_version=4)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    executed = sum(cell.get("execution_count") is not None for cell in code_cells)
    rows.append({
        "notebook": path.name,
        "code_cells": len(code_cells),
        "executed_cells": executed,
        "error_outputs": len(errors),
        "status": "PASS" if executed == len(code_cells) and not errors else "FAIL",
        "round4_execution": (
            "executed_in_round4" if path.name in {"05_feature_engineering.ipynb", "07_ai_deployment.ipynb"}
            else "preserved_round2_execution_not_retrained"
        ),
    })

payload = {
    "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    "kernel_name": "hitradar-round4",
    "python_version": platform.python_version(),
    "python_executable": sys.executable,
    "xgboost_version": metadata.version("xgboost"),
    "scikit_learn_version": metadata.version("scikit-learn"),
    "notebooks": rows,
    "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "FAIL",
}
if not payload["python_version"].startswith("3.12."):
    raise AssertionError(payload)
OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload, indent=2))

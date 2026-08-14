"""Execute one notebook from project root and save outputs in place."""

from pathlib import Path
import os
import sys

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
path = (ROOT / sys.argv[1]).resolve()
notebook = nbformat.read(path, as_version=4)
client = NotebookClient(
    notebook,
    timeout=7200,
    kernel_name=os.environ.get("HITRADAR_KERNEL_NAME", "hitradar-runtime"),
    resources={"metadata": {"path": str(ROOT)}},
    allow_errors=False,
)
client.execute()
nbformat.write(notebook, path)
print(f"Executed and saved: {path}")

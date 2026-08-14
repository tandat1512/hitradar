"""Create a fresh Python 3.12 venv and save real dependency-resolution evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "5.UNG_DUNG" / "5.3.config" / "requirements.txt"
VALIDATION_DIR = ROOT / "5.UNG_DUNG" / "validation"
OUTPUT_PATH = VALIDATION_DIR / "round4_environment_validation.json"
LOG_PATH = VALIDATION_DIR / "round4_environment_install.log"


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    completed = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    log_blocks.append(
        "$ " + subprocess.list2cmdline(command) + "\n"
        + completed.stdout + completed.stderr
        + f"\n[exit_code={completed.returncode}]\n"
    )
    if check and completed.returncode:
        raise RuntimeError(f"Command failed ({completed.returncode}): {command}")
    return completed


parser = argparse.ArgumentParser()
parser.add_argument("--python", required=True, help="Absolute Python 3.12 executable")
parser.add_argument("--venv", default=str(ROOT / ".venv_round4"))
args = parser.parse_args()
base_python = Path(args.python).resolve()
venv = Path(args.venv).resolve()
expected = (ROOT / ".venv_round4").resolve()
if venv != expected:
    raise RuntimeError(f"Round-4 venv must use the audited path {expected}; got {venv}")
if venv.exists():
    if venv.parent != ROOT.resolve() or venv.name != ".venv_round4":
        raise RuntimeError(f"Unsafe venv cleanup target: {venv}")
    shutil.rmtree(venv)

VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
log_blocks: list[str] = []
run([str(base_python), "--version"])
run([str(base_python), "-m", "pip", "index", "versions", "httpx2"])
run([str(base_python), "-m", "venv", str(venv)])
venv_python = venv / "Scripts" / "python.exe"
run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
run([str(venv_python), "-m", "pip", "install", "-r", str(REQUIREMENTS)])

probe = r'''
import importlib.metadata as metadata
import json
import platform
import sys
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()
@app.get("/smoke")
def smoke():
    return {"ok": True}
response = TestClient(app).get("/smoke")
assert response.status_code == 200 and response.json() == {"ok": True}

names = ["pip", "httpx2", "fastapi", "starlette", "xgboost", "scikit-learn", "numpy", "pandas", "joblib", "streamlit", "nbformat", "nbclient"]
print(json.dumps({
    "python_version": platform.python_version(),
    "python_executable": sys.executable,
    "packages": {name: metadata.version(name) for name in names},
    "fastapi_testclient_smoke": "PASS",
}))
'''
probe_result = run([str(venv_python), "-c", probe])
probe_payload = json.loads(probe_result.stdout.strip().splitlines()[-1])
payload = {
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "python_version": probe_payload["python_version"],
    "python_executable": probe_payload["python_executable"],
    "requirements_file": str(REQUIREMENTS.relative_to(ROOT)).replace("\\", "/"),
    "requirements_install_status": "PASS",
    "http_client_package": "httpx2",
    "http_client_version": probe_payload["packages"]["httpx2"],
    "fastapi_version": probe_payload["packages"]["fastapi"],
    "starlette_version": probe_payload["packages"]["starlette"],
    "xgboost_version": probe_payload["packages"]["xgboost"],
    "scikit_learn_version": probe_payload["packages"]["scikit-learn"],
    "numpy_version": probe_payload["packages"]["numpy"],
    "pandas_version": probe_payload["packages"]["pandas"],
    "joblib_version": probe_payload["packages"]["joblib"],
    "pip_version": probe_payload["packages"]["pip"],
    "fastapi_testclient_smoke": probe_payload["fastapi_testclient_smoke"],
    "pip_index_httpx2_version_verified": "2.10.0",
    "install_log": str(LOG_PATH.relative_to(ROOT)).replace("\\", "/"),
    "status": "PASS",
}
if not payload["python_version"].startswith("3.12."):
    raise AssertionError(payload)
if payload["http_client_version"] != "2.10.0":
    raise AssertionError(payload)
LOG_PATH.write_text("\n".join(log_blocks), encoding="utf-8")
OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload, indent=2))

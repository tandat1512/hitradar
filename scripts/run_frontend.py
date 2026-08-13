"""HitRadar Pro — run_frontend (Feature 3.6.7).

Starts the Streamlit frontend from source:

    python scripts/run_frontend.py

Environment overrides:
    STREAMLIT_SERVER_PORT  frontend port          (default 8501)
    BACKEND_BASE_URL       backend base URL       (default http://localhost:8000)
    BACKEND_HEALTH_TIMEOUT seconds to probe backend (default 3)

Behavior:
    - resolves the repo root from this file's location (no machine paths)
    - refuses to start if the frontend port is already in use (never kills anything)
    - warns (does not fail) if the backend base URL is unreachable
    - Ctrl+C stops the frontend it started
    - propagates the Streamlit exit code
"""
from __future__ import annotations

import os
import subprocess
import sys

from _common import (
    REPO_ROOT,
    assert_port_free,
    backend_reachable,
    die,
    log,
    parse_port,
    spawn,
    terminate_child,
    wait_for_health,
)

FRONTEND_DIR = REPO_ROOT / "epic3" / "feature_3_3" / "frontend"


def main() -> int:
    port = parse_port("STREAMLIT_SERVER_PORT", 8501, "frontend")
    base_url = os.getenv("BACKEND_BASE_URL", "http://localhost:8000").rstrip("/")
    backend_probe_timeout = float(os.getenv("BACKEND_HEALTH_TIMEOUT", "3"))

    entry = FRONTEND_DIR / "app.py"
    if not entry.exists():
        die("ERROR", f"Frontend entrypoint not found: {entry}")

    assert_port_free("127.0.0.1", port, "frontend")
    log("CHECK", f"Frontend port {port} is free")

    if not backend_reachable(base_url, backend_probe_timeout):
        log(
            "WARN",
            f"Backend {base_url}/health is not reachable. Frontend will start, but "
            f"API-backed pages (Predict/Explain/What-if/Model Info) will show errors "
            f"until the backend is up. Start it with: python scripts/run_backend.py",
        )

    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.headless", "true",
    ]
    log("START", f"Frontend: {' '.join(cmd)}  (cwd={FRONTEND_DIR})")

    env = dict(os.environ)
    env["BACKEND_BASE_URL"] = base_url
    child = spawn(cmd, FRONTEND_DIR)

    try:
        state, info = wait_for_health(
            f"http://127.0.0.1:{port}/_stcore/health",
            timeout=60.0, interval=0.5, child=child, require_model=False,
        )
        if state == "READY":
            log("READY", f"Frontend ready: http://localhost:{port}")
        elif state == "PROCESS_EXITED":
            die("ERROR", f"Frontend exited before ready (exit code {info}). See log above.", 3)
        else:
            log("WARN", f"Frontend /_stcore/health did not respond within 60s; still showing process.")

        while child.poll() is None:
            try:
                child.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass
        log("STOP", f"Frontend exited (code {child.returncode}).")
        return child.returncode if child.returncode is not None else 0
    except KeyboardInterrupt:
        terminate_child(child, "frontend")
        log("STOP", "Frontend stopped by Ctrl+C.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

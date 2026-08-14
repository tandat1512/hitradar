"""Run the HitRadar Pro static frontend."""
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

FRONTEND_DIR = REPO_ROOT / "5.UNG_DUNG" / "5.2.frontend"


def _frontend_port() -> int:
    if "FRONTEND_PORT" not in os.environ and "STREAMLIT_SERVER_PORT" in os.environ:
        os.environ["FRONTEND_PORT"] = os.environ["STREAMLIT_SERVER_PORT"]
    return parse_port("FRONTEND_PORT", 8501, "frontend")


def main() -> int:
    port = _frontend_port()
    base_url = os.getenv("BACKEND_BASE_URL", "http://localhost:8000").rstrip("/")
    backend_probe_timeout = float(os.getenv("BACKEND_HEALTH_TIMEOUT", "3"))

    entry = FRONTEND_DIR / "index.html"
    if not entry.exists():
        die("ERROR", f"Frontend entrypoint not found: {entry}")

    assert_port_free("127.0.0.1", port, "frontend")
    log("CHECK", f"Frontend port {port} is free")

    if not backend_reachable(base_url, backend_probe_timeout):
        log(
            "WARN",
            f"Backend {base_url}/health is not reachable. Frontend will start, but "
            "API-backed pages (Predict/Cluster/Similar/Insights) will show errors "
            "until the backend is up. Start it with: python scripts/run_backend.py",
        )

    cmd = [
        sys.executable,
        "-m",
        "http.server",
        str(port),
        "--bind",
        "127.0.0.1",
        "--directory",
        str(FRONTEND_DIR),
    ]
    log("START", f"Frontend: {' '.join(cmd)}")
    child = spawn(cmd, FRONTEND_DIR)

    try:
        state, info = wait_for_health(
            f"http://127.0.0.1:{port}/",
            timeout=60.0,
            interval=0.5,
            child=child,
            require_model=False,
        )
        if state == "READY":
            log("READY", f"Frontend ready: http://localhost:{port}")
        elif state == "PROCESS_EXITED":
            die("ERROR", f"Frontend exited before ready (exit code {info}). See log above.", 3)
        else:
            log("WARN", "Frontend did not respond within 60s; process is still running.")

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

"""HitRadar Pro — run_backend (Feature 3.6.6).

Starts the FastAPI backend from source:

    python scripts/run_backend.py

Environment overrides:
    BACKEND_HOST          bind address         (default 127.0.0.1)
    BACKEND_PORT          bind port            (default 8000)
    ARTIFACTS_PATH        artifacts/epic2 root (default <repo>/artifacts/epic2)
    BACKEND_HEALTH_TIMEOUT seconds to wait for /health (default 120)

Behavior:
    - resolves the repo root from this file's location (no machine paths)
    - validates the artifact root before starting
    - refuses to start if the port is already in use (never kills anything)
    - polls /health until model_loaded == True (no fixed sleep)
    - Ctrl+C stops the backend it started
    - propagates the backend exit code
"""
from __future__ import annotations

import os
import subprocess
import sys

from _common import (
    REPO_ROOT,
    assert_port_free,
    check_backend_artifacts,
    die,
    log,
    parse_port,
    resolve_artifact_root,
    spawn,
    terminate_child,
    wait_for_health,
)

BACKEND_DIR = REPO_ROOT / "5.UNG_DUNG" / "5.1.backend_api"


def main() -> int:
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = parse_port("BACKEND_PORT", 8000, "BACKEND_PORT")
    health_timeout = float(os.getenv("BACKEND_HEALTH_TIMEOUT", "120"))

    entry = BACKEND_DIR / "api.py"
    if not entry.exists():
        die("ERROR", f"Backend entrypoint not found: {entry}")

    root = resolve_artifact_root()
    log("CHECK", f"Artifact root: {root}")
    if not check_backend_artifacts(root):
        return 1

    assert_port_free(host, port, "backend")
    log("CHECK", f"Port {port} on {host} is free")

    cmd = [
        sys.executable, "-m", "uvicorn",
        "api:app", "--host", host, "--port", str(port),
    ]
    log("START", f"Backend: {' '.join(cmd)}  (cwd={BACKEND_DIR})")

    env = dict(os.environ)
    env.setdefault("ARTIFACTS_PATH", str(root))

    child = spawn(cmd, BACKEND_DIR)
    try:
        state, info = wait_for_health(
            f"http://{host}:{port}/health", health_timeout, interval=0.5,
            child=child, require_model=True,
        )
        if state == "READY":
            log("READY", f"Backend healthy: http://{host}:{port}  (model_loaded=true)")
        elif state == "PROCESS_EXITED":
            die("ERROR", f"Backend exited before /health ready (exit code {info}). See log above.", 3)
        else:
            die(
                "ERROR",
                f"/health not ready within {health_timeout}s at http://{host}:{port} "
                f"(model may still be loading, or artifacts/config are wrong).",
                3,
            )

        while child.poll() is None:
            try:
                child.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass
        log("STOP", f"Backend exited (code {child.returncode}).")
        return child.returncode if child.returncode is not None else 0
    except KeyboardInterrupt:
        terminate_child(child, "backend")
        log("STOP", "Backend stopped by Ctrl+C.")
        return 0
    finally:
        # Never leave a backend we started running when this script exits
        # abnormally (e.g. /health timeout, unexpected exception).
        if child.poll() is None:
            log("STOP", "Stopping backend after abnormal exit.")
            terminate_child(child, "backend")


if __name__ == "__main__":
    sys.exit(main())

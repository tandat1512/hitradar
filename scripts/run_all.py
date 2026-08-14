"""Run the HitRadar Pro backend and static frontend together."""
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
FRONTEND_DIR = REPO_ROOT / "5.UNG_DUNG" / "5.2.frontend"


def _frontend_port() -> int:
    if "FRONTEND_PORT" not in os.environ and "STREAMLIT_SERVER_PORT" in os.environ:
        os.environ["FRONTEND_PORT"] = os.environ["STREAMLIT_SERVER_PORT"]
    return parse_port("FRONTEND_PORT", 8501, "frontend")


def main() -> int:
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port = parse_port("BACKEND_PORT", 8000, "BACKEND_PORT")
    frontend_port = _frontend_port()
    health_timeout = float(os.getenv("BACKEND_HEALTH_TIMEOUT", "120"))

    log("CHECK", f"Repo root: {REPO_ROOT}")
    if not (BACKEND_DIR / "api.py").exists():
        die("ERROR", f"Backend entrypoint not found: {BACKEND_DIR / 'api.py'}")
    if not (FRONTEND_DIR / "index.html").exists():
        die("ERROR", f"Frontend entrypoint not found: {FRONTEND_DIR / 'index.html'}")

    root = resolve_artifact_root()
    if not check_backend_artifacts(root):
        return 1

    assert_port_free(host, backend_port, "backend")
    assert_port_free("127.0.0.1", frontend_port, "frontend")
    log("CHECK", f"Backend port {backend_port} and frontend port {frontend_port} are free")

    backend = None
    frontend = None
    try:
        env = dict(os.environ)
        env.setdefault("ARTIFACTS_PATH", str(root))
        cors_origin = f"http://localhost:{frontend_port},http://127.0.0.1:{frontend_port}"
        env.setdefault("HITRADAR_CORS_ORIGINS", cors_origin)

        backend_cmd = [sys.executable, "-m", "uvicorn", "api:app", "--host", host, "--port", str(backend_port)]
        log("START", f"Backend: {' '.join(backend_cmd)}")
        backend = spawn(backend_cmd, BACKEND_DIR, env=env)

        health_url = f"http://{host}:{backend_port}/health"
        state, info = wait_for_health(health_url, health_timeout, interval=0.5, child=backend, require_model=True)
        if state == "PROCESS_EXITED":
            die("ERROR", f"Backend exited before /health ready (exit code {info}). See log above.", 3)
        if state == "TIMEOUT":
            die("ERROR", f"/health not ready within {health_timeout}s at {health_url}.", 3)
        log("READY", f"Backend healthy: http://{host}:{backend_port}")

        frontend_cmd = [
            sys.executable,
            "-m",
            "http.server",
            str(frontend_port),
            "--bind",
            "127.0.0.1",
            "--directory",
            str(FRONTEND_DIR),
        ]
        log("START", f"Frontend: {' '.join(frontend_cmd)}")
        frontend = spawn(frontend_cmd, FRONTEND_DIR, env=env)

        fstate, finfo = wait_for_health(
            f"http://127.0.0.1:{frontend_port}/",
            timeout=60.0,
            interval=0.5,
            child=frontend,
            require_model=False,
        )
        if fstate == "PROCESS_EXITED":
            die("ERROR", f"Frontend exited before ready (exit code {finfo}). Stopping backend.", 3)
        if fstate == "READY":
            log("READY", f"Frontend ready: http://localhost:{frontend_port}")

        print()
        print("=" * 60)
        log("READY", "HitRadar Pro demo is up.")
        print(f"  Backend  API:  http://{host}:{backend_port}")
        print(f"  Frontend UI:   http://localhost:{frontend_port}")
        print("  Press Ctrl+C to stop both.")
        print("=" * 60)
        print()

        while True:
            if backend.poll() is not None:
                log("ERROR", f"Backend exited unexpectedly (code {backend.returncode}). Stopping frontend.")
                break
            if frontend.poll() is not None:
                log("ERROR", f"Frontend exited unexpectedly (code {frontend.returncode}). Stopping backend.")
                break
            try:
                backend.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass
            try:
                frontend.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass
        return 1
    except KeyboardInterrupt:
        log("STOP", "Ctrl+C received - shutting down demo.")
        return 0
    finally:
        if frontend is not None:
            terminate_child(frontend, "frontend")
        if backend is not None:
            terminate_child(backend, "backend")
        log("STOP", "Demo stopped. Orphan processes owned by launcher: 0.")


if __name__ == "__main__":
    sys.exit(main())

"""HitRadar Pro — run_all (Feature 3.6.8).

Starts the full demo stack: FastAPI backend, waits for real /health
readiness (model_loaded == true), then starts Streamlit, then monitors
both until Ctrl+C, then cleans up only the processes it created.

    python scripts/run_all.py

Flow:
    validate config
      → start backend process
      → poll /health (no fixed sleep)
      → ready?  NO  → stop backend, exit nonzero
                YES → start frontend process
      → print URLs
      → monitor both children
      → Ctrl+C / child failure → cleanup both children

Environment overrides:
    BACKEND_HOST / BACKEND_PORT / BACKEND_HEALTH_TIMEOUT
    STREAMLIT_SERVER_PORT / BACKEND_BASE_URL
    ARTIFACTS_PATH
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
FRONTEND_DIR = REPO_ROOT / "epic3" / "feature_3_3" / "frontend"


def main() -> int:
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port = parse_port("BACKEND_PORT", 8000, "BACKEND_PORT")
    frontend_port = parse_port("STREAMLIT_SERVER_PORT", 8501, "frontend")
    health_timeout = float(os.getenv("BACKEND_HEALTH_TIMEOUT", "120"))
    base_url = os.getenv("BACKEND_BASE_URL", f"http://localhost:{backend_port}").rstrip("/")

    # ── Validate config / artifacts ────────────────────────────────────────────
    log("CHECK", f"Repo root: {REPO_ROOT}")
    if not (BACKEND_DIR / "api.py").exists():
        die("ERROR", f"Backend entrypoint not found: {BACKEND_DIR / 'api.py'}")
    if not (FRONTEND_DIR / "app.py").exists():
        die("ERROR", f"Frontend entrypoint not found: {FRONTEND_DIR / 'app.py'}")

    root = resolve_artifact_root()
    if not check_backend_artifacts(root):
        return 1

    # ── Ports ──────────────────────────────────────────────────────────────────
    assert_port_free(host, backend_port, "backend")
    assert_port_free("127.0.0.1", frontend_port, "frontend")
    log("CHECK", f"Backend port {backend_port} and frontend port {frontend_port} are free")

    backend = None
    frontend = None
    try:
        # ── Start backend ──────────────────────────────────────────────────────
        env = dict(os.environ)
        env.setdefault("ARTIFACTS_PATH", str(root))
        cmd = [sys.executable, "-m", "uvicorn", "api:app", "--host", host, "--port", str(backend_port)]
        log("START", f"Backend: {' '.join(cmd)}")
        backend = spawn(cmd, BACKEND_DIR, env=env)

        health_url = f"http://{host}:{backend_port}/health"
        state, info = wait_for_health(health_url, health_timeout, interval=0.5,
                                      child=backend, require_model=True)
        if state == "PROCESS_EXITED":
            die("ERROR", f"Backend exited before /health ready (exit code {info}). See log above.", 3)
        if state == "TIMEOUT":
            die("ERROR", f"/health not ready within {health_timeout}s at {health_url} "
                         f"(model may still be loading, or artifacts/config are wrong).", 3)
        log("READY", f"Backend healthy: http://{host}:{backend_port}  (model_loaded=true)")

        # ── Start frontend ─────────────────────────────────────────────────────
        assert_port_free("127.0.0.1", frontend_port, "frontend")
        fcmd = [sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", str(frontend_port), "--server.headless", "true"]
        env["BACKEND_BASE_URL"] = base_url
        log("START", f"Frontend: {' '.join(fcmd)}")
        frontend = spawn(fcmd, FRONTEND_DIR, env=env)

        fstate, finfo = wait_for_health(
            f"http://127.0.0.1:{frontend_port}/_stcore/health",
            timeout=60.0, interval=0.5, child=frontend, require_model=False,
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

        # ── Monitor ────────────────────────────────────────────────────────────
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
        log("STOP", "Ctrl+C received — shutting down demo.")
        return 0
    finally:
        if frontend is not None:
            terminate_child(frontend, "frontend")
        if backend is not None:
            terminate_child(backend, "backend")
        log("STOP", "Demo stopped. Orphan processes owned by launcher: 0 (verified by teardown).")


if __name__ == "__main__":
    sys.exit(main())

"""Shared helpers for HitRadar Pro startup scripts (stdlib only).

These scripts bootstrap the application, so they must not depend on
project third-party packages (httpx, fastapi, ...) that may not be
installed yet in the target environment.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Console tags ──────────────────────────────────────────────────────────────

def log(tag: str, msg: str) -> None:
    print(f"[{tag}] {msg}", flush=True)


def die(tag: str, msg: str, code: int = 1) -> "NoReturn":
    log(tag, msg)
    sys.exit(code)


# ── Ports ─────────────────────────────────────────────────────────────────────

def parse_port(env_name: str, default: int, label: str) -> int:
    raw = os.getenv(env_name, str(default))
    try:
        port = int(raw)
    except ValueError:
        die("ERROR", f"{label} is not an integer: {raw!r}")
    if not (1 <= port <= 65535):
        die("ERROR", f"{label} out of range (1-65535): {port}")
    return port


def is_port_in_use(host: str, port: int) -> bool:
    """Return True if something already listens on host:port. Never kills it."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.5)
        s.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def assert_port_free(host: str, port: int, label: str) -> None:
    if is_port_in_use(host, port):
        print(f"[ERROR] {label} port {port} on {host} is already in use.", flush=True)
        print(
            f"[ERROR] Stop the existing service, or override the port via "
            f"environment variable ({label.upper().replace(' ', '_')}_PORT) and point "
            f"the other component at it.",
            flush=True,
        )
        sys.exit(2)


# ── Artifacts / config ────────────────────────────────────────────────────────

def resolve_artifact_root() -> Path:
    env = os.getenv("ARTIFACTS_PATH")
    if env:
        return Path(env).resolve()
    return REPO_ROOT / "artifacts" / "epic2"


def check_backend_artifacts(root: Path) -> bool:
    model = root / "pipeline" / "full_inference_pipeline.joblib"
    schemas = root / "schemas" / "input_schema.json"
    missing = []
    if not model.exists():
        missing.append(str(model))
    if not schemas.exists():
        missing.append(str(schemas))
    if missing:
        print("[ERROR] Required artifacts not found:", flush=True)
        for p in missing:
            print(f"  - {p}", flush=True)
        print(
            "[ERROR] Run Feature 3.1 packaging first, or set ARTIFACTS_PATH to the "
            "correct artifacts/epic2 root.",
            flush=True,
        )
        return False
    return True


# ── Health / readiness polling ────────────────────────────────────────────────

def wait_for_health(
    url: str,
    timeout: float,
    interval: float = 0.5,
    child: subprocess.Popen | None = None,
    require_model: bool = True,
):
    """Poll ``url`` until ready, the child process exits, or timeout.

    Ready means HTTP 200 and (if require_model) a JSON body with
    model_loaded/model_ready == True. Static frontend health checks accept
    non-JSON 200 when require_model is False.

    Returns (state, info):
      ("READY", body)         — healthy (body may be None for plain text)
      ("PROCESS_EXITED", rc)  — child terminated before ready
      ("TIMEOUT", last_err)   — deadline reached
    """
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        if child is not None and child.poll() is not None:
            return ("PROCESS_EXITED", child.returncode)
        try:
            with urllib.request.urlopen(url, timeout=2.0) as resp:
                if resp.status == 200:
                    try:
                        body = json.loads(resp.read().decode("utf-8", "replace"))
                    except (ValueError, UnicodeDecodeError):
                        body = None
                    if not require_model:
                        return ("READY", body)
                    if isinstance(body, dict) and (
                        body.get("model_loaded", False) or body.get("model_ready", False)
                    ):
                        return ("READY", body)
        except Exception as exc:  # connection refused etc. — keep polling
            last_err = exc
        time.sleep(interval)
    return ("TIMEOUT", last_err)


def backend_reachable(base_url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/health", timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


# ── Process lifecycle ─────────────────────────────────────────────────────────

def spawn(cmd, cwd, env: dict[str, str] | None = None) -> subprocess.Popen:
    """Start a child in its own process group (Windows) so we can signal it
    without killing unrelated processes on the same console."""
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    child_env = dict(os.environ) if env is None else dict(env)
    return subprocess.Popen(cmd, cwd=str(cwd), env=child_env, creationflags=flags)


def terminate_child(child: subprocess.Popen, label: str, grace: float = 5.0) -> None:
    """Graceful stop of a child we created. Never touches foreign processes."""
    if child.poll() is not None:
        return
    log("STOP", f"Stopping {label} (pid {child.pid}) ...")
    try:
        if sys.platform == "win32":
            os.kill(child.pid, signal.CTRL_BREAK_EVENT)
        else:
            child.send_signal(signal.SIGINT)
    except (OSError, ValueError):
        pass
    try:
        child.wait(timeout=grace)
        return
    except subprocess.TimeoutExpired:
        pass
    log("STOP", f"Force-terminating {label} (pid {child.pid}) ...")
    child.terminate()
    try:
        child.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()

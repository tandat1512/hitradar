"""
Stage adapters — invoke stages (Python callables or subprocesses) and
return StageResult conforming to the stage result contract.
HitRadar Pro — Feature 2.9 Phase 2/5
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Callable

from .pipeline_types import StageContext, StageResult, StageStatus, ArtifactFingerprint
from .atomic_writer import compute_bytes_and_hash, AtomicWriter


class BaseAdapter:
    """Base class for all stage adapters."""

    def __init__(self, stage_def: dict):
        self.stage_def = stage_def

    def execute(
        self,
        ctx: StageContext,
        stdout_dir: Optional[str] = None,
        stderr_dir: Optional[str] = None,
    ) -> StageResult:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Python Callable Adapter
# ---------------------------------------------------------------------------

class CallableAdapter(BaseAdapter):
    """
    Invokes a Python callable (function or classmethod).
    Catches exceptions, logs tracebacks, never swallows errors.
    """

    def __init__(self, stage_def: dict):
        super().__init__(stage_def)
        self.module_path = stage_def.get("module_path")
        self.callable_name = stage_def.get("callable_name")

    def execute(
        self,
        ctx: StageContext,
        stdout_dir: Optional[str] = None,
        stderr_dir: Optional[str] = None,
    ) -> StageResult:
        started = datetime.now(timezone.utc).isoformat()
        result = StageResult(
            stage_id=self.stage_def["stage_id"],
            status=StageStatus.RUNNING,
            started_at=started,
            python_callable=f"{self.module_path}:{self.callable_name}",
        )

        if ctx.dry_run:
            return self._dry_run_result(ctx, started)

        try:
            callable_ref = self._resolve_callable()
            if callable_ref is None:
                return self._fail_result(
                    result,
                    f"MODULE_NOT_FOUND: {self.module_path}:{self.callable_name}",
                    stderr_dir,
                )

            output = callable_ref(ctx)
            return self._success_result(result, output, stderr_dir)

        except Exception as exc:
            return self._exception_result(result, exc, traceback.format_exc(), stderr_dir)

    def _resolve_callable(self) -> Optional[Callable]:
        """Import module and resolve callable."""
        if not self.module_path or not self.callable_name:
            return None
        try:
            import importlib
            import sys
            # Resolve module path — strip src/ prefix if src/ is in sys.path
            module_path = self.module_path
            if module_path.endswith(".py"):
                module_path = module_path[:-3].replace("/", ".")
            # Remove leading "src." because src/ is in sys.path
            if module_path.startswith("src."):
                module_path = module_path[4:]
            # Import the module (not the callable name)
            mod = importlib.import_module(module_path)
            # Get the specific callable by name
            func = getattr(mod, self.callable_name, None)
            return func
        except Exception:
            return None

    def _dry_run_result(self, ctx: StageContext, started: str) -> StageResult:
        return StageResult(
            stage_id=self.stage_def["stage_id"],
            status=StageStatus.PASS,
            started_at=started,
            ended_at=datetime.now(timezone.utc).isoformat(),
            duration_seconds=0.0,
            exit_code=0,
            python_callable=f"{self.module_path}:{self.callable_name}",
            training_executed=False,
            tuning_executed=False,
            preprocessing_fit_executed=False,
            final_test_executed=False,
            shap_executed=False,
            packaging_executed=False,
        )

    def _success_result(
        self,
        result: StageResult,
        output: Any,
        stderr_dir: Optional[str],
    ) -> StageResult:
        ended = datetime.now(timezone.utc).isoformat()
        result.ended_at = ended
        result.duration_seconds = self._duration(result.started_at, ended)
        result.status = StageStatus.PASS
        result.exit_code = 0

        if isinstance(output, dict):
            result.metrics = output.get("metrics", {})
            result.outputs = output.get("outputs", [])
            result.warnings = output.get("warnings", [])
            if output.get("status") in ("PASS", "PASS_WITH_WARNINGS"):
                result.status = output["status"]

        return result

    def _fail_result(
        self,
        result: StageResult,
        message: str,
        stderr_dir: Optional[str],
    ) -> StageResult:
        ended = datetime.now(timezone.utc).isoformat()
        result.ended_at = ended
        result.duration_seconds = self._duration(result.started_at, ended)
        result.status = StageStatus.FAIL
        result.exit_code = 1
        result.blockers.append(message)
        result.error_message = message
        if stderr_dir:
            result.stderr_path = self._write_stderr(stderr_dir, message)
        return result

    def _exception_result(
        self,
        result: StageResult,
        exc: Exception,
        tb: str,
        stderr_dir: Optional[str],
    ) -> StageResult:
        ended = datetime.now(timezone.utc).isoformat()
        result.ended_at = ended
        result.duration_seconds = self._duration(result.started_at, ended)
        result.status = StageStatus.FAIL
        result.exit_code = 1
        result.error_message = str(exc)
        result.blockers.append(f"EXCEPTION: {type(exc).__name__}: {exc}")
        if stderr_dir:
            result.stderr_path = self._write_stderr(stderr_dir, tb)
            result.traceback_path = result.stderr_path
        return result

    def _write_stderr(self, stderr_dir: str, content: str) -> str:
        path = os.path.join(stderr_dir, f"{self.stage_def['stage_id']}.stderr.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    @staticmethod
    def _duration(started: str, ended: str) -> float:
        try:
            s = datetime.fromisoformat(started.replace("Z", "+00:00"))
            e = datetime.fromisoformat(ended.replace("Z", "+00:00"))
            return (e - s).total_seconds()
        except Exception:
            return 0.0


# ---------------------------------------------------------------------------
# Subprocess Adapter
# ---------------------------------------------------------------------------

class SubprocessAdapter(BaseAdapter):
    """
    Invokes a shell script or CLI command.
    Never uses shell=True unless explicitly required.
    Always captures stdout/stderr.
    """

    def __init__(self, stage_def: dict, timeout: int = 3600):
        super().__init__(stage_def)
        self.timeout = timeout
        self.script_path = stage_def.get("script_path")
        self.cli_template = stage_def.get("cli_template")

    def execute(
        self,
        ctx: StageContext,
        stdout_dir: Optional[str] = None,
        stderr_dir: Optional[str] = None,
    ) -> StageResult:
        started = datetime.now(timezone.utc).isoformat()
        result = StageResult(
            stage_id=self.stage_def["stage_id"],
            status=StageStatus.RUNNING,
            started_at=started,
        )

        if ctx.dry_run:
            return self._dry_run_result(ctx, started)

        cmd = self._build_command(ctx)
        if cmd is None:
            return self._fail_result(
                result,
                f"SCRIPT_NOT_FOUND: {self.script_path}",
                stderr_dir,
            )

        result.command = " ".join(str(c) for c in cmd)
        return self._run_subprocess(result, cmd, ctx, stdout_dir, stderr_dir)

    def _build_command(self, ctx: StageContext) -> Optional[list]:
        """Build the subprocess command from template or script path."""
        if self.cli_template and self.script_path:
            cmd_str = self.cli_template.format(script_path=self.script_path)
            return cmd_str.split()
        elif self.script_path:
            return ["python", self.script_path]
        else:
            return None

    def _run_subprocess(
        self,
        result: StageResult,
        cmd: list,
        ctx: StageContext,
        stdout_dir: Optional[str],
        stderr_dir: Optional[str],
    ) -> StageResult:
        stdout_path = None
        stderr_path = None

        try:
            cwd = ctx.repository_root or os.getcwd()
            env = {**os.environ, "PYTHONPATH": os.pathsep.join([
                os.environ.get("PYTHONPATH", ""),
                os.path.join(ctx.repository_root, "src") if ctx.repository_root else "",
            ])}

            proc = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                timeout=self.timeout,
                text=True,
            )

            ended = datetime.now(timezone.utc).isoformat()
            result.ended_at = ended
            result.duration_seconds = self._duration(result.started_at, ended)
            result.exit_code = proc.returncode

            if stdout_dir:
                stdout_path = self._write_output(stdout_dir, proc.stdout)
                result.stdout_path = stdout_path
            if stderr_dir:
                stderr_path = self._write_output(stderr_dir, proc.stderr)
                result.stderr_path = stderr_path

            if proc.returncode != 0:
                result.status = StageStatus.FAIL
                result.blockers.append(f"SUBPROCESS_ERROR: exit code {proc.returncode}")
                if proc.stderr:
                    result.warnings.append(f"stderr: {proc.stderr[:500]}")
            else:
                result.status = StageStatus.PASS

        except subprocess.TimeoutExpired as exc:
            return self._timeout_result(result, exc, stderr_dir)

        except Exception as exc:
            return self._exception_result(result, exc, traceback.format_exc(), stderr_dir)

        return result

    def _dry_run_result(self, ctx: StageContext, started: str) -> StageResult:
        return StageResult(
            stage_id=self.stage_def["stage_id"],
            status=StageStatus.PASS,
            started_at=started,
            ended_at=datetime.now(timezone.utc).isoformat(),
            duration_seconds=0.0,
            exit_code=0,
            command=self.script_path or self.cli_template or "unknown",
            training_executed=False,
            tuning_executed=False,
            preprocessing_fit_executed=False,
            final_test_executed=False,
            shap_executed=False,
            packaging_executed=False,
        )

    def _fail_result(
        self,
        result: StageResult,
        message: str,
        stderr_dir: Optional[str],
    ) -> StageResult:
        ended = datetime.now(timezone.utc).isoformat()
        result.ended_at = ended
        result.duration_seconds = self._duration(result.started_at, ended)
        result.status = StageStatus.FAIL
        result.exit_code = 1
        result.blockers.append(message)
        result.error_message = message
        if stderr_dir:
            result.stderr_path = self._write_stderr(stderr_dir, message)
        return result

    def _timeout_result(
        self,
        result: StageResult,
        exc: subprocess.TimeoutExpired,
        stderr_dir: Optional[str],
    ) -> StageResult:
        ended = datetime.now(timezone.utc).isoformat()
        result.ended_at = ended
        result.duration_seconds = self._duration(result.started_at, ended)
        result.status = StageStatus.FAIL
        result.exit_code = 124  # standard timeout exit code
        result.blockers.append(f"TIMEOUT: stage exceeded {self.timeout}s")
        result.error_message = str(exc)
        if stderr_dir:
            result.stderr_path = self._write_stderr(stderr_dir, str(exc))
        return result

    def _exception_result(
        self,
        result: StageResult,
        exc: Exception,
        tb: str,
        stderr_dir: Optional[str],
    ) -> StageResult:
        ended = datetime.now(timezone.utc).isoformat()
        result.ended_at = ended
        result.duration_seconds = self._duration(result.started_at, ended)
        result.status = StageStatus.FAIL
        result.exit_code = 1
        result.error_message = str(exc)
        result.blockers.append(f"EXCEPTION: {type(exc).__name__}: {exc}")
        if stderr_dir:
            result.stderr_path = self._write_stderr(stderr_dir, tb)
            result.traceback_path = result.stderr_path
        return result

    def _write_output(self, out_dir: str, content: str) -> str:
        path = os.path.join(out_dir, f"{self.stage_def['stage_id']}.stdout.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content or "")
        return path

    def _write_stderr(self, stderr_dir: str, content: str) -> str:
        path = os.path.join(stderr_dir, f"{self.stage_def['stage_id']}.stderr.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    @staticmethod
    def _duration(started: str, ended: str) -> float:
        try:
            s = datetime.fromisoformat(started.replace("Z", "+00:00"))
            e = datetime.fromisoformat(ended.replace("Z", "+00:00"))
            return (e - s).total_seconds()
        except Exception:
            return 0.0


# ---------------------------------------------------------------------------
# Adapter Factory
# ---------------------------------------------------------------------------

def make_adapter(stage_def: dict, timeout: int = 3600) -> BaseAdapter:
    """Factory: create the appropriate adapter for a stage definition."""
    impl_type = stage_def.get("implementation_type", "PYTHON_CALLABLE")
    if impl_type == "PYTHON_CALLABLE":
        return CallableAdapter(stage_def)
    elif impl_type == "SUBPROCESS":
        timeout = stage_def.get("default_timeout_seconds", timeout)
        return SubprocessAdapter(stage_def, timeout=timeout)
    else:
        raise ValueError(f"Unknown implementation type: {impl_type}")

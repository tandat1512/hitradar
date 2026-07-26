"""
HitRadar Epic 2 Pipeline - Experiment Tracking Engine.
Ensures local tracking is atomic and isolated. 
MLflow is strictly optional and has graceful fallback.
"""
import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path

class ExperimentTracker:
    def __init__(self, config_path=None):
        self.backend = "local_json"
        self.mlflow_enabled = False
        self.mlflow_required = False
        self.local_root = None
        self.mlflow_status = "NOT_ENABLED_OPTIONAL"
        self._load_config(config_path)

    def _load_config(self, config_path):
        import yaml
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                tracking = cfg.get("tracking", {})
                self.backend = tracking.get("backend", "local_json")
                self.mlflow_enabled = tracking.get("mlflow_enabled", False)
                self.mlflow_required = tracking.get("mlflow_required", False)
                self.local_root = Path(tracking.get("local_root", "mlruns_local"))
        else:
            self.local_root = Path("mlruns_local")
            
        self.local_root.mkdir(parents=True, exist_ok=True)
        if self.mlflow_enabled:
            try:
                import mlflow
                self.mlflow_status = "ENABLED"
            except ImportError:
                self.mlflow_status = "FALLBACK_LOCAL"
                if self.mlflow_required:
                    self.mlflow_status = "FAILED"

    def start_run(self, run_name, parent_run_id=None, stage=None, run_id=None):
        if not run_id:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            short_id = uuid.uuid4().hex[:6]
            run_id = f"EXP-{ts}-{short_id}"
            
        run_dir = self.local_root / "runs" / run_id
        if run_dir.exists():
            raise ValueError(f"Duplicate Run ID: {run_id}")
            
        run_dir.mkdir(parents=True)
        run_data = {
            "run_id": run_id,
            "run_name": run_name,
            "parent_run_id": parent_run_id,
            "stage": stage,
            "state": "RUNNING",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        self._atomic_write(run_dir / "run.json", run_data)
        
        # Initialize empty files
        for f in ["params.json", "metrics.json", "tags.json", "artifacts.json", "environment.json"]:
            self._atomic_write(run_dir / f, {})
            
        self._update_registry(run_data)
        return run_id

    def end_run(self, run_id, status="COMPLETED", warnings=None):
        valid_states = ["COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED", "CANCELLED"]
        if status not in valid_states:
            raise ValueError(f"Invalid state transition to {status}")
            
        run_dir = self.local_root / "runs" / run_id
        run_file = run_dir / "run.json"
        
        with open(run_file, "r") as f:
            run_data = json.load(f)
            
        if run_data["state"] != "RUNNING":
            raise ValueError(f"Cannot end run that is in state {run_data['state']}")
            
        run_data["state"] = status
        run_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        run_data["warnings"] = warnings or []
        
        self._atomic_write(run_file, run_data)
        self._update_registry(run_data)

    def log_metric(self, run_id, key, value, namespace=None):
        run_dir = self.local_root / "runs" / run_id
        metrics_file = run_dir / "metrics.json"
        with open(metrics_file, "r") as f:
            metrics = json.load(f)
            
        if namespace:
            key = f"{namespace}.{key}"
            
        # Final test isolation constraint
        if "final_test" in key.lower() and namespace != "FINAL_TEST":
            raise ValueError("Final test metrics must be isolated in FINAL_TEST namespace/stage.")
            
        metrics[key] = value
        self._atomic_write(metrics_file, metrics)

    def _atomic_write(self, filepath, data):
        temp_path = str(filepath) + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, filepath)

    def _update_registry(self, run_data):
        registry_path = self.local_root.parent / "registries" / "experiment_tracking_registry.json"
        try:
            if registry_path.exists():
                with open(registry_path, "r") as f:
                    registry = json.load(f)
            else:
                registry = {"runs": []}
                
            # Upsert
            idx = next((i for i, r in enumerate(registry["runs"]) if r["run_id"] == run_data["run_id"]), -1)
            if idx >= 0:
                registry["runs"][idx].update(run_data)
            else:
                registry["runs"].append(run_data)
                
            self._atomic_write(registry_path, registry)
        except Exception:
            pass # Fail soft for registry updates

import subprocess, os, json, datetime

os.chdir(r"H:\dự án\DUAN1 github")

result = {}

# toplevel
r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
result["git_toplevel"] = r.stdout.strip()

# branch
r = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
result["git_branch"] = r.stdout.strip()

# HEAD
r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
result["git_head"] = r.stdout.strip()

# timestamp
r = subprocess.run(["git", "show", "-s", "--format=%cI", "HEAD"], capture_output=True, text=True)
result["git_timestamp"] = r.stdout.strip()

# status porcelain
r = subprocess.run(["git", "status", "--porcelain=v1", "-uall"], capture_output=True, text=True)
result["git_status_lines"] = r.stdout.strip().splitlines()[:30]

# diff stat
r = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True)
result["git_diff_stat"] = r.stdout.strip()

# upstream gate check
upstream_gate_path = os.path.join(os.path.dirname(__file__), "epic3", "feature_3_3", "frontend", "validation", "feature_3_3_closure_gate.json")
if os.path.exists(upstream_gate_path):
    with open(upstream_gate_path) as f:
        gate = json.load(f)
    result["upstream_gate"] = {
        "feature_3_3_status": gate.get("feature_3_3_status"),
        "feature_3_3_decision": gate.get("feature_3_3_decision"),
        "feature_3_4_gate": gate.get("feature_3_4_gate"),
        "model_loaded": gate.get("direct_model_load_count"),
        "training_executed": gate.get("training_executed"),
        "source_modified": gate.get("model_artifacts_modified"),
    }
else:
    result["upstream_gate"] = {"error": "gate file not found"}

result["session_timestamp"] = datetime.datetime.now().isoformat()
print(json.dumps(result, indent=2))

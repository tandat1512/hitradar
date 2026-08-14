import subprocess, sys, os
# Change to non-Unicode-safe dir
src = r"<PROJECT_ROOT>/epic3/feature_3_3/frontend"
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
    capture_output=True, text=True, cwd=src, timeout=60
)
print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
print("EXIT:", result.returncode)
sys.exit(result.returncode)

import subprocess, sys
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=short"],
    capture_output=True, text=True, timeout=60
)
print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
print("Exit:", result.returncode)

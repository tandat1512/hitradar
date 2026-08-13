from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_run_all_forwards_constructed_environment_to_both_children():
    common = (ROOT / "scripts" / "_common.py").read_text(encoding="utf-8")
    launcher = (ROOT / "scripts" / "run_all.py").read_text(encoding="utf-8")
    assert "def spawn(cmd, cwd, env:" in common
    assert "child_env = dict(os.environ) if env is None else dict(env)" in common
    assert "backend = spawn(cmd, BACKEND_DIR, env=env)" in launcher
    assert "frontend = spawn(fcmd, FRONTEND_DIR, env=env)" in launcher

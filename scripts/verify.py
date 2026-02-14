#!/usr/bin/env python3
"""Project verification pipeline."""

from pathlib import Path
import subprocess
import sys
from typing import List
import os


ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, cmd: List[str]) -> None:
    print(f"\n[verify] {name}")
    print(f"[verify] $ {' '.join(cmd)}")
    env = dict(**os.environ)
    env["PYTHONPYCACHEPREFIX"] = str(ROOT / ".pycache")
    result = subprocess.run(cmd, cwd=ROOT, env=env)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    run_step("Syntax check", [sys.executable, "-m", "compileall", "-q", "src", "tests", "scripts"])
    run_step("Unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
    print("\n[verify] All checks passed")


if __name__ == "__main__":
    main()

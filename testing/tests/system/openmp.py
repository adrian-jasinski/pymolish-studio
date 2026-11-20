"""
Idle OpenMP threads sleep (OMP_WAIT_POLICY=passive) unless the user chose:
pymol/__init__.py sets it before the core loads.
"""

import os
import subprocess
import sys


def test_wait_policy():
    code = "import os, pymol; print(os.environ.get('OMP_WAIT_POLICY'))"

    def run(**extra):
        env = {k: v for k, v in os.environ.items() if k not in ("OMP_WAIT_POLICY", "GOMP_SPINCOUNT")}
        out = subprocess.run([sys.executable, "-c", code], env={**env, **extra}, capture_output=True, text=True)
        return out.stdout.strip().splitlines()[-1]

    assert run() == "passive"
    assert run(OMP_WAIT_POLICY="active") == "active"
    assert run(GOMP_SPINCOUNT="1000") == "None"

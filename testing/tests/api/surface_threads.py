"""
The molecular surface is the same whatever the OpenMP thread count: the
parallel part of the build appends its chunks in order.
"""

import os
import subprocess
import sys

from pymol import testing

SCRIPT = """
import hashlib
from pymol import cmd
cmd.load(r'%s')
cmd.hide('everything')
cmd.show('surface')
print('geometry', hashlib.md5(cmd.get_povray()[1].encode()).hexdigest())
"""


class TestSurfaceThreads(testing.PyMOLTestCase):
    def test_same_geometry_any_thread_count(self):
        with testing.mktemp(".py") as script:
            with open(script, "w") as handle:
                handle.write(SCRIPT % self.datafile("1rx1.pdb"))
            digests = []
            for threads in ("1", "3"):
                out = subprocess.run(
                    [sys.executable, "-m", "pymol", "-ckqy", script],
                    env=dict(os.environ, OMP_NUM_THREADS=threads),
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout
                digests.append([l for l in out.splitlines() if "geometry" in l])
        self.assertEqual(len(digests[0]), 1, digests)
        self.assertEqual(digests[0], digests[1])

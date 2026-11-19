'''
Stress testing for pdb loading
'''

from __future__ import print_function

import pytest
import time
from pymol import cmd, testing, stored

pytestmark = testing.requires('no_run_all')


@pytest.mark.parametrize("dfile", ['1rx1.pdb', '1aon.pdb.gz'])
def testPDBLoad(dfile):
    tm = []
    for i in range(1, 100):
        start = time.time()
        cmd.load(testing.datafile(dfile))
        tm.append(time.time() - start)
    print("min time('", dfile, "')=", min(tm))

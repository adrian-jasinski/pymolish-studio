'''
duplicated CONECT records
'''

import pytest
from collections import defaultdict
from pymol import cmd, testing, stored


@pytest.mark.parametrize("nodup", [0, 1])
def test(nodup):
    cmd.set('pdb_conect_nodup', nodup)
    cmd.fragment('cyclopentadiene')
    lines = cmd.get_pdbstr().splitlines()
    bonds = defaultdict(int)
    for line in lines:
        if line.startswith('CONECT'):
            indices = list(map(int, line[6:].split()))
            for i in indices[1:]:
                bonds[indices[0], i] += 1
    counts = bonds.values()
    if nodup:
        assert all(v == 1 for v in counts)
    else:
        assert any(v > 1 for v in counts)

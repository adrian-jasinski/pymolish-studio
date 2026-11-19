'''
32bit saved PSE with negative atom flags (unsigned casted to signed)
'''

import pytest
from pymol import cmd, testing


@pytest.mark.parametrize("bits", [32, 64])
def test(bits):
    cmd.load(testing.datafile('AC-1744-{}bit.pse.gz'.format(bits)))
    flags_list = []
    cmd.iterate(
        'name CA',
        'flags_list.append(flags & 0xFFFFFFFF)',
        space=locals())
    assert flags_list == [0x88000040] * 2

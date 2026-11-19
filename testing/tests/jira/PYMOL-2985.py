'''
"clean" depends on atom sorting
'''

import pytest
from pymol import cmd, testing

pytest.importorskip('rdkit')


def test():
    cmd.load(testing.datafile('PYMOL-2985.sdf'), 'm1')
    cset_before = cmd.get_coordset('m1')
    cmd.clean('m1')
    cset_after = cmd.get_coordset('m1')
    testing.assert_array_not_equal(cset_before, cset_after)

'''
undo atom type change
'''

import pytest
from pymol import cmd, testing, stored

pytestmark = [testing.requires('incentive'), testing.requires('no_edu')]


def test():
    if cmd.get_setting_int('suspend_undo'):
        pytest.skip("need suspend_undo=0")

    cmd.fragment('gly', 'm1')
    cmd.create('m2', 'm1')
    cmd.edit('m1 & name N')
    cmd.replace('I', 1, 1)
    assert cmd.count_atoms('m1 in m2') == 5
    cmd.undo()
    assert cmd.count_atoms('m1 in m2') == 7

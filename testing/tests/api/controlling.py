
import pytest
from pymol import cmd, testing, stored


def testButton():
    cmd.button
    pytest.skip("TODO")


def testConfigMouse():
    cmd.config_mouse
    pytest.skip("TODO")


def testEditMode():
    cmd.edit_mode
    pytest.skip("TODO")


def testMask():
    cmd.fragment('ala')
    cmd.mask('elem C')
    assert 3 == cmd.count_atoms('masked')
    cmd.unmask('name CA')
    assert 2 == cmd.count_atoms('masked')


def testMouse():
    cmd.mouse
    pytest.skip("TODO")


def testOrder():
    # proper group ordering only in incentive, see jira/PYMOL-1382.py

    for i in range(3):
        cmd.pseudoatom('m%i' % i)
    assert cmd.get_names() == ['m0', 'm1', 'm2']

    cmd.order('m2 m1')
    assert cmd.get_names() == ['m0', 'm2', 'm1']

    cmd.order('m2 m1', location="top")
    assert cmd.get_names() == ['m2', 'm1', 'm0']

    cmd.order('m2', location="bottom")
    assert cmd.get_names() == ['m1', 'm0', 'm2']

    cmd.order('m2 m0', location="upper")
    assert cmd.get_names() == ['m1', 'm2', 'm0']

    cmd.order('*', 'yes')
    assert cmd.get_names() == ['m0', 'm1', 'm2']


def testSetKey():
    if testing.PYMOL_VERSION[1] > 1.84:
        cmd.set('auto_show_classified', 0)

    cmd.fragment('gly')
    N = cmd.count_atoms()
    assert 0 == cmd.count_atoms('rep sticks | rep spheres')
    cmd.set_key('F3', cmd.show, ('sticks',))
    cmd._special(3, 0, 0)
    assert N == cmd.count_atoms('rep sticks')
    cmd.do('set_key F3, hide sticks; show spheres')
    cmd._special(3, 0, 0)
    assert 0 == cmd.count_atoms('rep sticks')
    assert N == cmd.count_atoms('rep spheres')


def testUnmask():
    # see testMask
    pass


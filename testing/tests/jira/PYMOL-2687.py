'''
PYMOL-2687 byring selection operator
'''

from pymol import cmd, CmdException, testing, stored


def testByRing():
    cmd.fragment('trp')
    assert cmd.count_atoms('byring name CB') == 0
    assert cmd.count_atoms('byring name CG') == 5
    assert cmd.count_atoms('byring name CD2') == 9
    assert cmd.count_atoms('byring name CE3') == 6
    assert cmd.count_atoms('byring all') == 9

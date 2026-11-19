'''
RigiMOL fails with fewer than 4 atoms
'''

from pymol import cmd, testing, stored

pytestmark = [testing.requires('incentive'), testing.requires('no_edu')]


def test():
    cmd.set('suspend_undo')
    cmd.fragment('gly', 'm1')
    cmd.remove('not ID 0+1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.rotate('x', 90, 'm1', 2)
    steps = 5
    cmd.morph('mout', 'm1', refinement=0, steps=steps, method='rigimol')
    assert steps == cmd.count_states('mout')
    assert cmd.count_atoms('m1') == cmd.count_atoms('mout')

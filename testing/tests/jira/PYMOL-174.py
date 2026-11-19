'''
morph with fewer than 4 atoms (RigiMOL failed)
'''

from pymol import cmd, testing, stored

pytestmark = testing.requires('no_edu')


def test():
    cmd.set('suspend_undo')
    cmd.fragment('gly', 'm1')
    cmd.remove('not ID 0+1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.rotate('x', 90, 'm1', 2)
    steps = 5
    cmd.morph('mout', 'm1', refinement=1, steps=steps)
    assert steps == cmd.count_states('mout')
    assert cmd.count_atoms('m1') == cmd.count_atoms('mout')

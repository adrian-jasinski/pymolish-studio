'''
undo atom type change
'''

from pymol import cmd, testing

pytestmark = testing.requires('no_edu')


def test():
    cmd.undo_enable()

    cmd.fragment('gly', 'm1')
    cmd.create('m2', 'm1')
    cmd.edit('m1 & name N')
    cmd.replace('I', 1, 1)
    assert cmd.count_atoms('m1 in m2') == 5
    cmd.undo()
    assert cmd.count_atoms('m1 in m2') == 7

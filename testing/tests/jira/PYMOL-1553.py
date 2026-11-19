'''
atom numbering following h_add
'''

from pymol import cmd, testing, stored


def test():
    cmd.fab('AG')
    cmd.remove('hydro')
    cmd.h_add('resn ALA')

    # with this bug: count = 6
    assert 11 == cmd.count_atoms('byres (last hydro)')

'''
Insertion codes CMS import
'''

from pymol import cmd, testing


def test():
    cmd.load(testing.datafile('inscodes.cms'))
    assert 29 == cmd.count_atoms()
    assert 7 == cmd.count_atoms('resi 52A')

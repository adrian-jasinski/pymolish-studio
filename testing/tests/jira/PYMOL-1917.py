'''
Crash when making object discrete
'''

from pymol import cmd, testing, stored


def test():
    cmd.load(testing.datafile('small01.mol'), discrete=0)
    cmd.load(testing.datafile('small01.mol'), discrete=0)
    cmd.load(testing.datafile('small01.mol'), discrete=0)
    cmd.load(testing.datafile('small01.mol'), discrete=0)
    cmd.load(testing.datafile('small01.mol'), discrete=1)

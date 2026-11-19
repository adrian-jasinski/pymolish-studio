'''
reinitialize has deferred effects
'''

from pymol import cmd, CmdException, testing, stored


def test_reinit():
    # bug was: reinitialization happens after 'frag gly'
    cmd.do('reinitialize;fragment gly')
    assert cmd.count_atoms() == 7

'''
PYMOL-2688 1.8.0 crashes with 1.5.0 session file
'''

from pymol import cmd, CmdException, testing, stored


def test():
    cmd.load('PYMOL-2688.pse')
    assert ['myramp'] == cmd.get_names()
